import time
import os
import traceback
import requests
import random
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from test import redak_axi_text, addid_redac, redak_mo, get_balance
from red_xl import red_xl
from send_mail import send_email
from openpyxl import Workbook
from dotenv import load_dotenv
from check_oasys import chek_oasys
from check_hydraluxe import chek_hydraluxe
from get_rastvor import add_rastvor


def autorization(page, url, username, password):
    """Авторизация на сайте"""
    page.goto(url)
    time.sleep(2)
    
    while True:
        try:
            # Ждем появления полей ввода
            page.wait_for_selector('input[name="userID"]', timeout=10000)
            page.wait_for_selector('input[name="password"]', timeout=10000)
            
            # Вводим логин
            page.fill('input[name="userID"]', username)
            time.sleep(1)
            
            # Проверяем, что логин введен
            login_value = page.input_value('input[name="userID"]')
            if login_value == username:
                print("Ввел логин")
                
                # Вводим пароль
                page.fill('input[name="password"]', password)
                time.sleep(1)
                
                # Проверяем, что пароль введен
                password_value = page.input_value('input[name="password"]')
                if password_value == password:
                    print("Ввел пароль")
                else:
                    page.reload()
                    time.sleep(2)
                    continue
            else:
                page.reload()
                time.sleep(2)
                continue
            
            # Нажимаем кнопку входа
            page.click('//a[contains(text(), "Войти") and @class="btn"]')
            print('Нажал на кнопку входа')
            break
            
        except PlaywrightTimeoutError:
            print("Таймаут при авторизации, перезагружаю страницу")
            page.reload()
            time.sleep(2)
    
    return page


def start_order(page):
    """Начало оформления заказа"""
    page.click('//a[@title="Заказать линзы" and @id="link1"]')
    page.click('//a[@id="menu-ordering-touch" and contains(text(), "Ввод заказа")]')
    return page


def get_product_selection(page):
    """Получение списка продуктов"""
    page.wait_for_selector('select[name="selectedBrandCode"]', timeout=10000)
    
    # Получаем все элементы option
    option_elements = page.query_selector_all('select[name="selectedBrandCode"] option')
    
    # Пропускаем первый элемент (пустой или placeholder)
    product_elements = option_elements[1:] if len(option_elements) > 1 else []
    
    return product_elements


def set_parametr_product(page, test_quantity):
    """Установка параметров продукта"""
    # Нажимаем "Выбрать все"
    page.click('//a[contains(text(), "Выбрать все")]')
    time.sleep(1)
    
    # Заполняем все поля с количеством
    quantity_inputs = page.locator('.drawer-line-quantity-halo input').all()
    for input_field in quantity_inputs:
        input_field.fill(str(test_quantity))
    
    # Кликаем чекбокс "Выбрать все"
    page.check('input[id="drawer-select-all-check"]')
    time.sleep(2)


def add_to_cart(page):
    """Добавление в корзину"""
    page.click('a[id="add-to-cart-button-rx"]')
    time.sleep(1)


def empty_cart_safe(page, url_cart):
    """Умная очистка корзины с проверками"""
    
    # 1. Проверяем, не находимся ли мы УЖЕ на странице корзины
    if 'viewCart.xo' in page.url:
        print("Уже на странице корзины, проверяю содержимое...")
    else:
        # 2. Пытаемся перейти на страницу корзины
        try:
            page.goto(url_cart, timeout=10000, wait_until='domcontentloaded')
        except Exception as e:
            print(f"Ошибка перехода в корзину: {e}")
            print("Возможно, сессия устарела. Пропускаю очистку.")
            return
    
    # 3. Пытаемся найти и нажать кнопку удаления (если есть)
    try:
        # Даем странице время на полную загрузку динамического контента
        page.wait_for_load_state('networkidle', timeout=2000)
        
        delete_btn = page.wait_for_selector('a[title="Удалить"]', timeout=3000)
        if delete_btn.is_visible():
            delete_btn.click()
            # Ждем подтверждения или обновления страницы
            page.wait_for_timeout(1000)
            print("✓ Корзина очищена")
        else:
            print("Кнопка удаления не видима")
    except:
        print("Корзина уже пуста или элементы управления изменились")


def check_element_visible(page, selector, attribute=None, expected_value=None):
    """Проверка видимости элемента и его атрибутов"""
    try:
        element = page.locator(selector)
        if element.is_visible():
            if attribute and expected_value:
                actual_value = element.get_attribute(attribute)
                return actual_value == expected_value
            return True
        return False
    except:
        return False


def is_element_present_by_id(page, element_id, styles_to_check=None):
    """Проверка наличия элемента по ID и его стилей"""
    try:
        element = page.locator(f'#{element_id}')
        if element.is_visible():
            if styles_to_check:
                # Проверяем стили через JavaScript
                script = f"""
                var element = document.querySelector('#{element_id}');
                if (!element) return false;
                var styles = window.getComputedStyle(element);
                """
                for style, value in styles_to_check.items():
                    script += f"if (styles.{style} !== '{value}') return false;"
                script += "return true;"
                
                result = page.evaluate(script)
                return result
            return True
        return False
    except:
        return False



def goto_with_timeout(page, url, timeout=3000):
    """Загрузка с остановкой если долго"""
    try:
        # Запускаем навигацию
        response = page.goto(url, timeout=timeout)
        return response
    except Exception as e:
        print(f"Таймаут {timeout}мс истек, останавливаем загрузку...")
        
        # Останавливаем загрузку через JavaScript
        page.evaluate("""
            // 1. Останавливаем все загрузки
            window.stop();
            
            // 2. Очищаем таймеры и интервалы
            const highestId = window.setTimeout(() => {}, 0);
            for (let i = 0; i < highestId; i++) {
                window.clearTimeout(i);
                window.clearInterval(i);
            }
            
            // 3. Отменяем все запросы fetch
            if (window.fetch) {
                const originalFetch = window.fetch;
                window.fetch = function() {
                    return Promise.reject(new Error('Fetch cancelled'));
                };
            }
            
            // 4. Останавливаем XHR запросы
            if (window.XMLHttpRequest) {
                const originalXHR = window.XMLHttpRequest.prototype.open;
                window.XMLHttpRequest.prototype.open = function() {
                    this.addEventListener('loadstart', function() {
                        this.abort();
                    });
                    originalXHR.apply(this, arguments);
                };
            }
        """)
        
        # Ждем немного и пробуем снова
        page.wait_for_timeout(1000)
        return None



def is_element_by_id(page, element_id):
    """Проверка наличия элемента по ID"""
    try:
        element = page.locator(f'#{element_id}')
        return element.is_visible()
    except:
        return False
    

def create_browser_with_settings(p):
    """Создает браузер со всеми настройками для сервера"""
    return p.chromium.launch(
            headless=True,  # Видимый браузер
            args=[
                # === КРИТИЧЕСКИ ВАЖНЫЕ ДЛЯ LINUX ===
                '--no-sandbox',                    # Обязательно для контейнеров/серверов
                '--disable-dev-shm-usage',         # Решает 90% проблем с памятью на Linux
                '--disable-gpu',                   # На сервере нет GPU
                
                # === Для стабильности и памяти ===
                '--disable-software-rasterizer',
                '--disable-accelerated-2d-canvas',
                '--disable-accelerated-video-decode',
                '--disable-accelerated-video-encode',
                
                # === Для обхода блокировок ===
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-web-security',          # Осторожно: только для тестов!
                '--disable-site-isolation-trials',
                
                # === Оптимизация производительности ===
                '--single-process',                # Экономит память (но менее стабильно)
                '--disable-setuid-sandbox',
                '--disable-background-networking',
                '--disable-default-apps',
                '--disable-extensions',
                '--disable-sync',
                '--disable-translate',
                '--metrics-recording-only',
                '--no-first-run',
                '--no-default-browser-check',
                '--no-pings',
                
                # === Для стабильности сети ===
                '--disable-domain-reliability',
                '--disable-features=AudioServiceOutOfProcess',
                '--disable-client-side-phishing-detection',
                '--disable-component-update',
                
                # === Размер окна (важно даже для headless) ===
                '--window-size=1920,1080',
                '--start-maximized',
                
                # === Язык и локаль (чтобы сайт думал что вы в РФ) ===
                '--lang=ru-RU',
                '--accept-lang=ru-RU,ru;q=0.9',

                # f"--disable-extensions-except=proxi_extension",
                # f"--load-extension=proxi_extension"
            ]
        )



def main():
    start_time = time.time()
    load_dotenv()
    
    # Создаем рабочие книги
    wb = Workbook()  # Москва
    ws = wb.active
    ws.append(['Наименование', 'Наименование артикула', 'Остаток', 'Адрес'])

    wb2 = Workbook()  # Ростов
    ws2 = wb2.active
    ws2.append(['Наименование', 'Наименование артикула', 'Остаток', 'Адрес'])

    wb3 = Workbook()  # Казань
    ws3 = wb3.active
    ws3.append(['Наименование', 'Наименование артикула', 'Остаток', 'Адрес'])

    wb4 = Workbook()  # СПБ
    ws4 = wb4.active
    ws4.append(['Наименование', 'Наименование артикула', 'Остаток', 'Адрес'])

    wb5 = Workbook()  # Новосибирск
    ws5 = wb5.active
    ws5.append(['Наименование', 'Наименование артикула', 'Остаток', 'Адрес'])

    wb6 = Workbook()  # Екатеринбург
    ws6 = wb6.active
    ws6.append(['Наименование', 'Наименование артикула', 'Остаток', 'Адрес'])

    # workbooks = [wb, wb2, wb3, wb4, wb5, wb6]
    # worksheets = [ws, ws2, ws3, ws4, ws5, ws6]
    workbooks = [wb2,]
    worksheets = [ws2,]
    
    # Настройки
    username = os.getenv("LOGIN")
    password = os.getenv("PASS")
    start_url = "https://www.jnjvision.com/eocs-rwd/startExternal.xo"
    url = "https://www.jnjvision.com/eocs-rwd/startExternal.xo?salesOrg=0020&localeID=ru_RU"
    url_order = "https://www.jnjvision.com/eocs-rwd/shipToSelection.xo?actionString=continueToCheckout"
    url_cart = "https://www.jnjvision.com/eocs-rwd/viewCart.xo?formAction=clearCartWarning"
    url_prod = "https://www.jnjvision.com/eocs-rwd/touchProductOrder.xo?formAction=showProducts"
    
    # Адреса и названия линз
    addresses = {
        0: 'RU14102',  # Ростов
        # 0: 'RU39813',  # Москва
        # 2: 'RU51798',  # Казань
        # 3: 'RU51799',  # СПБ
        # 4: 'RU51797',  # Новосибирск
        # 5: 'RU51814',  # Екатеринбург
    }
    
    lens_name = {
        0: '1-day Acuvue moist',
        1: '1-day Acuvue moist for astigmatism',
        2: 'Acuvue 2',
        3: 'Acuvue Oasys with hydraclear plus',
        4: 'Acuvue Oasys for astigmatism with hydraclear plus',
        5: 'Acuvue Oasys 1-day with hydraluxe',
        6: '1-day Acuvue moist multifocal',
        7: 'Acuvue Oasys 1-day with hydraluxe for astigmatism',
        8: 'Acuvue Oasys max 1-day',
        9: 'Acuvue Oasys multifocal',
        10: 'Acuvue Oasys Max 1-Day Multifocal',
    }
    
    product_change = "Новый"
    product_number = 0
    end_number = 2
    curves_number = 0
    blister_number = 0
    cylinder_number = 0
    axis_number = 0
    addidation_number = 0
    test_quantity = 100
    num_miopii = 8
    count_except = 0
    
    # Запускаем Playwright
    with sync_playwright() as p:
        # Запускаем браузер в видимом режиме
        browser = create_browser_with_settings(p)

        
        # Создаем контекст и страницу
        # Создаем контекст, имитирующий локальную машину
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='ru-RU',
            timezone_id='Europe/Moscow',
            # Указываем геолокацию (координаты Москвы)
            geolocation={'latitude': 55.7558, 'longitude': 37.6173},
            permissions=['geolocation']
        )
        
        # Убираем следы автоматизации через JavaScript
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            // Убираем другие признаки
            window.chrome = { runtime: {} };
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)
        page = context.new_page()
        
        # Авторизация
        autorization(page, url, username, password)
        time.sleep(2)
        print("Авторизация прошла успешно")
        
        home_page = page.url
        
        if is_element_by_id(page, 'cartCount'):
            empty_cart_safe(page, url_cart)
        
        while True:
            current_url = page.url
            print(f"Текущий URL: {current_url}")
            
            
            try:
                # Проверяем и очищаем корзину если нужно
                if is_element_by_id(page, 'cartCount'):
                    empty_cart_safe(page, url_cart)
                
                # ПЕРЕХОД НА СТРАНИЦУ ПРОДУКТА - ОПТИМИЗИРУЕМ
                
                while True:
                    try:
                        print("➡️ Переходим на страницу продукта...")
                        
                    
                        # 2. Только ОДНА попытка навигации
                        response = goto_with_timeout(page, url_prod, timeout=3000)
                        if 'touchProductOrder.xo' in page.url:
                            print("✅ Мы на странице оформления заказа")
                        time.sleep(1)
                        break
                          
                        
                    except Exception as e:
                        print(f"⚠ Не дождались загрузки ")
                        print("→ Но продолжаем выполнение...")
                        
                        
                        time.sleep(1)
                        continue
                        
                
                # Открываем выпадающий список
                page.click('span[role="presentation"]')  
                
                # Получаем список продуктов как элементы
                product_elements = get_product_selection(page)
                
                # Пропускаем миопию (удаляем 8-й элемент если есть)
                if len(product_elements) > num_miopii:
                    del product_elements[num_miopii]
                
                print(f"Найдено продуктов: {len(product_elements)}")
                
                cylinder_presence = False
                addid_presence = False
                count_exept_order = 0

                exept_count = 0
                
                
                while product_number < len(product_elements):
                    if exept_count == 3:
                        break

                    # Сравнить с нужным адресом URL
                    current_url = page.url
                    print(f"Текущий URL: {current_url}")
                    
                    # Кликаем на продукт (используем JavaScript для надежности)
                    try:
                        print(f"Выбираю продукт {product_number}...")
                        
                        # Пробуем через select_option с expect_navigation (ПРЯМО СНАЧАЛА)
                        try:
                            page.wait_for_selector('select[name="selectedBrandCode"]', state='visible', timeout=5000)
                            select_element = page.query_selector('select[name="selectedBrandCode"]')
                            
                            # ВАЖНО: Если ожидаем навигацию - она должна охватывать ВСЕ способы выбора
                            with page.expect_navigation(timeout=5000, wait_until='domcontentloaded'):
                                # Способ 1: select_option (основной)
                                html_index = product_number + 1
                                if product_number >= num_miopii:
                                    html_index += 1
                                select_element.select_option(index=html_index)
                            
                            print(f"✓ Выбрал продукт через select_option с навигацией")
                            
                            
                        except Exception as e1:
                            print(f"Способ 1 не сработал: {e1}")
                            
                            # Способ 2: JavaScript (тоже внутри expect_navigation если нужен)
                            try:
                                product_value = product_elements[product_number].get_attribute('value')
                                if product_value:
                                    with page.expect_navigation(timeout=5000, wait_until='domcontentloaded'):
                                        page.evaluate(f"""
                                            document.querySelector('select[name="selectedBrandCode"]').value = '{product_value}';
                                            document.querySelector('select[name="selectedBrandCode"]').dispatchEvent(new Event('change', {{ bubbles: true }}));
                                        """)
                                    print(f"✓ Выбрал продукт через JavaScript с навигацией")
                                    
                                else:
                                    raise ValueError("Нет value у элемента")
                                    
                            except Exception as e2:
                                print(f"Способ 2 не сработал: {e2}")
                                
                                # Способ 3: Прямой клик
                                try:
                                    with page.expect_navigation(timeout=5000, wait_until='domcontentloaded'):
                                        product_elements[product_number].click()
                                    print(f"✓ Выбрал продукт через клик с навигацией")
                                    
                                except Exception as e3:
                                    print(f"Все способы не сработали: {e3}")
                                    exept_count += 1
                                    page.reload()
                                    if 'startExternal.xo' in page.url:
                                        exept_count = 3
                                    continue

                    except Exception as e:
                        print(f"Общая ошибка выбора продукта: {e}")
                        exept_count += 1
                        continue
                    
                    # Проверяем, активировалась ли кнопка коммерческой поставки
                    
                    
                    # Выбираем коммерческую поставку
                    try:
                        page.wait_for_selector('a[id="id_revenue_button"]', state='visible', timeout=5000)
                        commercial_order_btn = page.query_selector('a[id="id_revenue_button"]')
                        if commercial_order_btn and commercial_order_btn.is_visible():
                            commercial_order_btn.click()
                            print("Выбрал поставку")
                            
                        else:
                            print("Кнопка коммерческой поставки не найдена")
                            product_number += 1
                            continue
                    except Exception as e:
                        print(f"Ошибка выбора поставки: {e}")
                        exept_count += 1
                        page.reload()
                        if 'startExternal.xo' in page.url:
                            exept_count = 3
                        continue
                    
                    # Выбираем кривизну
                    try:
                        page.wait_for_selector('div[id="id_revenue_basecurves"]', state='visible', timeout=10000)
                        base_curves_div = page.query_selector('div[id="id_revenue_basecurves"]')
                        if base_curves_div and base_curves_div.is_visible():
                            curves_btns = base_curves_div.query_selector_all('a')
                            print(f"Найдено кривизн: {len(curves_btns)}")
                            
                            if curves_number < len(curves_btns):
                                curves_btns[curves_number].click()
                                print(f"Выбрал кривизну {curves_number}")
                                time.sleep(1)
                            else:
                                print(f"Кривизна {curves_number} не найдена")
                                curves_number = 0
                                product_number += 1
                                continue
                        else:
                            print("Блок кривизн не найден")
                            product_number += 1
                            continue
                    except Exception as e:
                        print(f"Ошибка выбора кривизны: {e}")
                        page.reload()
                        print('ПЕРЕЗАГРУЗИЛИСЬ')
                        time.sleep(1)

                        exept_count += 1
                        page.reload()
                        if 'startExternal.xo' in page.url:
                            exept_count = 3
                        continue
                    
                    # Проверяем есть ли цилиндры и оси
                    cylinder_presence = False
                    try:
                        
                        cylinders_and_axes = page.query_selector('#id_cylinders_and_axes')
                        if cylinders_and_axes and cylinders_and_axes.is_visible():
                            style = cylinders_and_axes.get_attribute('style')
                            if style and 'display: block' in style:
                                print("цилиндры есть")
                                cylinder_presence = True
                                
                                # Выбираем цилиндр
                                page.wait_for_selector('select[id="id_cylinder_select"]', state='visible', timeout=5000)
                                cylinders_select = page.query_selector('select[id="id_cylinder_select"]')
                                cylinder = cylinders_select.query_selector_all('option')[1:]
                                if cylinders_select:
                                    # Получаем все опции
                                    cylinders_options = cylinders_select.query_selector_all('option')
                                    
                                    if len(cylinders_options) > 1 and cylinder_number < len(cylinder):  # Есть опции кроме placeholder
                                        # Выбираем по индексу (индексы начинаются с 0)
                                        cylinders_select.select_option(index=cylinder_number + 1)  # +1 потому что первый option обычно пустой
                                        print(f"Выбрал цилиндр {cylinder_number} через select_option")
                                        time.sleep(1)
                                    else:
                                        print(f"Опции цилиндров не найдены")
                                        cylinder_number = 0
                                
                                # Выбираем ось
                                page.wait_for_selector('select[id="id_axis_select"]', state='visible', timeout=5000)
                                axis_select = page.query_selector('select[id="id_axis_select"]')
                                axis = axis_select.query_selector_all('option')[1:]
                                if axis_select:
                                    # Получаем все оси
                                    axis_options = axis_select.query_selector_all('option')
                                    
                                    if len(axis_options) > 1 and axis_number < len(axis): # Есть оси кроме placeholder
                                        # Выбираем по индексу (индексы начинаются с 0)
                                        axis_select.select_option(index=axis_number + 1)  # +1 потому что первый option обычно пустой
                                        print(f"Выбрал ось {axis_number} через select_option")
                                        time.sleep(1)
                                    else:
                                        print(f"Ось {axis_number} не найдена")
                                        axis_number = 0
                    except Exception as e:
                        print(f"Ошибка обработки цилиндров: {e}")
                    
                    # Проверяем есть ли аддидация
                    addid_presence = False
                    try:
                        
                        add_powers = page.query_selector('#id_add_powers')
                        if add_powers and add_powers.is_visible():
                            style = add_powers.get_attribute('style')
                            if style and 'display: block' in style:
                                print("аддидация есть")
                                addid_presence = True
                                
                                page.wait_for_selector('div[id="id_add_power_buttons"]', timeout=5000)
                                add_power_buttons = page.query_selector('div[id="id_add_power_buttons"]')
                                if add_power_buttons:
                                    addidation_btns = add_power_buttons.query_selector_all('a')
                                    
                                    if addidation_number < len(addidation_btns):
                                        addidation_btns[addidation_number].click()
                                        print(f"Выбрал аддидацию {addidation_number}")
                                        
                                    else:
                                        print(f"Аддидация {addidation_number} не найдена")
                                        addidation_number = 0
                    except Exception as e:
                        print(f"Ошибка обработки аддидации: {e}")
                    
                    # Проверяем есть ли блистеры
                    package_volume = "30"  # значение по умолчанию
                    
                    page.wait_for_selector('#id_single_uom_buttons', timeout=10000)
                    single_uom_buttons = page.query_selector('#id_single_uom_buttons')
                    if single_uom_buttons and single_uom_buttons.is_visible():
                        style = single_uom_buttons.get_attribute('style')
                        if style and 'display: block' in style:
                            print("блистеры есть")
                            
                            page.wait_for_selector('div[id="id_single_uom_buttons"]', timeout=5000)
                            blister_div = page.query_selector('div[id="id_single_uom_buttons"]')
                            if blister_div:
                                blisters = blister_div.query_selector_all('a')
                                print(f"Найдено блистеров: {len(blisters)}")
                                
                                if blister_number < len(blisters):
                                    package_volume = blisters[blister_number].text_content().strip()
                                    blisters[blister_number].click()
                                    print(f"Выбрал блистер {blister_number}: {package_volume}")
                                    
                                    
                                    set_parametr_product(page, test_quantity)
                                    print("Выбрал все варианты")
                                    
                                    
                                    add_to_cart(page)
                                    print("Добавил в корзину")
                                   
                                    
                                    # Обрабатываем заказы для всех адресов
                                    adres = 0
                                    
                                    while adres < len(addresses):
                                        if count_exept_order == 3:
                                            print("Не смог пройти процесс оформления заказа")
                                            current_url = page.url
                                            print(f"Текущий URL: {current_url}")
                                            break

                                        try:
                                            # Ждем навигации, а не просто делаем sleep
                                            response = page.goto(url_order, wait_until="networkidle", timeout=10000)
                                            if response and response.ok:
                                                print(f"Успешно перешли на страницу выбора адреса. URL: {page.url}")
                                            else:
                                                print("⚠️ Предупреждение: страница загрузилась, но статус ответа не OK.")
                                        except Exception as nav_error:
                                            print(f"⛔ Критическая ошибка навигации: {nav_error}")
                                            count_exept_order += 1
                                            # Можно попробовать перезагрузить всю сессию
                                            # reset_session(...)
                                            continue
                                        time.sleep(2)

                                        current_url = page.url
                                        if "shipToSelection.xo" not in current_url:
                                            print(f"❓ Мы не на целевой странице. Текущий URL: {current_url}")
                                            print("Пробую принудительный переход заново...")
                                            # Можно добавить page.reload() или повторный goto
                                            count_exept_order += 1
                                            continue

                                        # Сравнить с нужным адресом URL
                                        
                                        print(f"Обрабатываю адрес: {addresses[adres]}")
                                        
                                        
                                        try:
                                            # Ищем элемент с адресом
                                            page.wait_for_selector(f'//label[contains(text(), "{addresses[adres]}")]', timeout=5000)
                                            address_label = page.query_selector(f'//label[contains(text(), "{addresses[adres]}")]')
                                            if address_label:
                                                address_label.click()
                                                print("выбрал адрес")
                                            else:
                                                print(f"Адрес {addresses[adres]} не найден")
                                                count_exept_order += 1
                                                continue
                                        except Exception as ex:
                                            print(f"Ошибка выбора адреса: {ex}")
                                            count_exept_order += 1
                                            continue
                                        
                                        # Первая кнопка "Продолжить"
                                        try:
                                            page.wait_for_selector('a[title="Продолжить"]', timeout=10000)
                                            continue_btns = page.query_selector_all('a[title="Продолжить"]')
                                            if continue_btns:
                                                continue_btns[0].click()
                                                print("нажал кнопку продолжить (этап 1)")
                                            else:
                                                print("Кнопка продолжить не найдена")
                                                count_exept_order += 1
                                                continue
                                        except Exception as ex:
                                            print(f"Ошибка кнопки 1: {ex}")
                                            count_exept_order += 1
                                            continue
                                        
                                        # Вторая кнопка "Продолжить"
                                        try:
                                            time.sleep(1)
                                            page.wait_for_selector('a[title="Продолжить"]', timeout=10000)
                                            continue_btns = page.query_selector_all('a[title="Продолжить"]')
                                            if continue_btns:
                                                continue_btns[0].click()
                                                print("нажал кнопку продолжить (этап 2)")
                                            else:
                                                print("Вторая кнопка продолжить не найдена")
                                        except Exception as ex:
                                            print(f"Ошибка кнопки 2: {ex}")
                                            count_exept_order += 1
                                            continue
                                        
                                        # Третья кнопка "Продолжить" (если есть)
                                        try:
                                            time.sleep(1)
                                            page.wait_for_selector('a[title="Продолжить"]', timeout=10000)
                                            continue_btns = page.query_selector_all('a[title="Продолжить"]')
                                            if continue_btns:
                                                continue_btns[0].click()
                                                print("нажал кнопку продолжить (этап 3)")
                                        except:
                                            print("Третьей кнопки продолжить не было")
                                            current_url = page.url
                                            print(f"Текущий URL: {current_url}")
                                            if 'startExternal.xo' in page.url:
                                                count_exept_order = 3
                                                break
                                        
                                        print('собираем информацию')
                                        
                                        try:
                                            while True:
                                                page.wait_for_selector('div[class="table-item stack"]', timeout=5000)
                                                products_text = page.query_selector_all('div[class="table-item stack"]')
                                                if product_number == 0 and len(products_text) < 50 and ('proceedToCheckout.xo' in page.url):
                                                    time.sleep(1)
                                                    page.reload()
                                                    time.sleep(1)
                                                    continue
                                                else:
                                                    break
                                        except:
                                            print("⛔ Нет информации")
                                            if 'startExternal.xo' in page.url:
                                                count_exept_order = 3
                                                break
                                            current_url = page.url
                                            print(f"Текущий URL: {current_url}")
                                            time.sleep(5)
                                            continue

                                        arr_check_dublikat = []
                                        
                                        if products_text:
                                            for num, text_in in enumerate(products_text):
                                                text_content = text_in.text_content().strip()
                                                lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                                                

                                                if "SPH" in lines[0]:
                                                    lines[0] = lines[0].replace("SPH", '').replace(',', '.')

                                                if len(lines) == 1:
                                                    lines.append(lines[0].split('\xa0')[-1].split(':'))
                                                    lines[1] = ','.join(lines[1])
                                                    lines.append(test_quantity)
                                                
                                                elif len(lines) >= 2:
                                                    lines.append(lines[1].split('.')[0])
                                                    lines[1] = lines[0].split('\xa0')[-1].split(':')
                                                    lines[1] = ','.join(lines[1])

                                                    # Добавляем количество
                                                    if len(lines) == 2:
                                                        lines.append(test_quantity)
                                                    else:
                                                        lines[2] = get_balance(lines[2])
                                                        
                                                    
                                                # Обрабатываем специфичные поля
                                                if 'Ось' in lines[1]:
                                                    lines[1] = redak_axi_text(lines[1], package_volume, product_number)
                                                    if lines[1].endswith("+0.00"):
                                                        e = lines[1].split()
                                                        e[-1] = '0.00'
                                                        lines[1] = ' '.join(e)
                                                elif 'Аддидация' in lines[1]:
                                                    lines[1] = addid_redac(lines[1])
                                                else:
                                                    pass
                                                    # lines[1] = redak_mo(lines[1], curvature)
                                                    
                                                
                                                    
                                                # Убираем лишние элементы
                                                if len(lines) == 4:
                                                    lines = lines[:-1]


                                                # Форматируем название продукта
                                                product_name = lens_name.get(product_number, f"Продукт {product_number}")
                                                lines[0] = product_name
                                                if package_volume == '24':
                                                    lines[0] = f'{lines[0]} (24 линзы)'
                                                else:
                                                    lines[0] = f'{lines[0]} ({package_volume} линз)'
                                                    
                                                # Добавляем адрес
                                                address_names = [
                                                        'Шолохова', 
                                                ]
                                                    
                                                if adres < len(address_names):
                                                    lines.append(address_names[adres])
                                                    
                                                
                                                
                                                if lines in arr_check_dublikat:
                                                    continue
                                                arr_check_dublikat.append(lines)
                                                # print(f"Адрес {adres}, строка {num}: {lines}")
                                        else:
                                            print("Не найдены элементы с информацией о продуктах")

                                        #   Добавляем в соответствующую таблицу

                                        tupled = [tuple(lst) for lst in arr_check_dublikat]

                                        # Удаляем дубликаты (сохраняем порядок)
                                        unique_tuples = list(dict.fromkeys(tupled))

                                        # Если нужно вернуть к спискам
                                        unique_lists = [list(t) for t in unique_tuples]

                                        for num, lines in enumerate(unique_lists):
                                            worksheets[adres].append(lines)
                                            print(num, lines)
                                        
                                        adres += 1
                                        if adres == len(addresses):
                                            break
                                    
                                    if count_exept_order == 3:
                                        raise ValueError('Столкнулись с непрогрузом страницы. Делаем перезагрузку.')

                                    current_url = page.url
                                    print(f"Текущий URL: {current_url}")
                                    if current_url == start_url:
                                        print("Мы на странице авторизации.")
                                        time.sleep(10)

                                        autorization(page, url, username, password)
                                        time.sleep(2)
                                        print("Авторизация прошла успешно")
                                        continue
                                    
                                    # Обновляем индексы
                                    blister_number += 1
                                    
                                    # Сбрасываем счетчики если достигли предела
                                    if cylinder_presence:
                                        if blister_number >= len(blisters):
                                            blister_number = 0
                                            axis_number += 1
                                        
                                        if axis_number >= len(axis):
                                            axis_number = 0
                                            cylinder_number += 1
                                        
                                        if cylinder_number >= len(cylinder):
                                            cylinder_number = 0
                                            curves_number += 1
                                        
                                        if curves_number >= len(curves_btns):
                                            product_number += 1
                                            product_change = "Новый"
                                            blister_number = 0
                                            curves_number = 0
                                            cylinder_number = 0
                                            axis_number = 0
                                        else:
                                            product_change = "Старый"
                                    
                                    elif addid_presence:
                                        if blister_number >= len(blisters):
                                            blister_number = 0
                                            addidation_number += 1
                                        
                                        if addidation_number >= len(addidation_btns):
                                            addidation_number = 0
                                            curves_number += 1
                                        
                                        if curves_number >= len(curves_btns):
                                            product_number += 1
                                            product_change = "Новый"
                                            blister_number = 0
                                            curves_number = 0
                                            addidation_number = 0
                                        else:
                                            product_change = "Старый"
                                    
                                    else:
                                        if blister_number >= len(blisters):
                                            curves_number += 1
                                            blister_number = 0
                                        
                                        if curves_number >= len(curves_btns):
                                            product_number += 1
                                            product_change = "Новый"
                                            blister_number = 0
                                            curves_number = 0
                                        else:
                                            product_change = "Старый"
                                    
                                    # Очищаем корзину

                                    if is_element_by_id(page, 'cartCount'):
                                        empty_cart_safe(page, url_cart)
                                        print("Очистили корзину")
                                    break
                                else:
                                    print(f"Блистер {blister_number} не найден")
                                    blister_number = 0
                                    curves_number += 1
                            else:
                                print("Блок блистеров не найден")
                                curves_number += 1
                        else:
                            print("Блистеры не видны")
                            curves_number += 1
                    else:
                        print("Элемент блистеров не найден")
                        curves_number += 1
                    
                    
                    # Если не нашли блистеры, переходим к следующей кривизне
                    if curves_number >= len(curves_btns):
                        product_number += 1
                        product_change = "Новый"
                        blister_number = 0
                        curves_number = 0
                        cylinder_number = 0
                        axis_number = 0
                        addidation_number = 0
                    else:
                        product_change = "Старый"

                if exept_count == 3:
                    raise ValueError('Ошибка при выборе параметров. Скорее всего вылетело.')
                    
                print(f"Продукт {product_number}.{product_change}")
                print(f"Кривизна {curves_number}")
                print(f"Цилиндр {cylinder_number}")
                print(f"Ось {axis_number}")
                print(f"Блистер {blister_number}")
                print(f"Аддидация {addidation_number}")
                print()
                
                print("Вышли из цикла продуктов")
                print(f"⛔ Критических сбоев {count_except}")
                
                if product_number >= len(product_elements):
                    print("Прошлись по всем продуктам")
                    
                    # Сохраняем файлы
                    # filenames = ['moscow.xlsx', 'rostov.xlsx', 'kazan.xlsx', 'spb.xlsx', 'novosib.xlsx', 'ekb.xlsx']
                    filenames = ['rostov.xlsx',]
                    for wb_file, filename in zip(workbooks, filenames):
                        wb_file.save(filename)
                    
                    break
            
            except Exception as ex:
                tb = traceback.extract_tb(ex.__traceback__)
                if tb:
                    # Последний вызов в стеке - где произошла ошибка
                    last_call = tb[-1]
                    line_no = last_call.lineno
                    filename = last_call.filename
                    func_name = last_call.name
                    
                    print(f"Ошибка в файле {filename}, строка {line_no}, функция {func_name}: {ex}")
                    count_except += 1
                else:
                    print(f"Ошибка: {ex}")
                    print("Что-то пошло не так, начну этот круг заново")
                    count_except += 1
                
                # Закрываем браузер и перезапускаем
                try:
                    browser.close()
                except:
                    pass
                
                time.sleep(10)
                
                good_avtoriz = 0
                while True:
                    try:
                        # response = requests.get("http://91.77.161.132:13200/proxy/WY8Iktuw/", timeout=10)
                        browser = create_browser_with_settings(p)
                        # Создаем контекст и страницу
                        # Создаем контекст, имитирующий локальную машину
                        context = browser.new_context(
                            viewport={'width': 1920, 'height': 1080},
                            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                            locale='ru-RU',
                            timezone_id='Europe/Moscow',
                            # Указываем геолокацию (координаты Москвы)
                            geolocation={'latitude': 55.7558, 'longitude': 37.6173},
                            permissions=['geolocation']
                        )
                        
                        # Убираем следы автоматизации через JavaScript
                        context.add_init_script("""
                            Object.defineProperty(navigator, 'webdriver', {
                                get: () => undefined
                            });
                            // Убираем другие признаки
                            window.chrome = { runtime: {} };
                            const originalQuery = window.navigator.permissions.query;
                            window.navigator.permissions.query = (parameters) => (
                                parameters.name === 'notifications' ?
                                    Promise.resolve({ state: Notification.permission }) :
                                    originalQuery(parameters)
                            );
                        """)
                        page = context.new_page()
                        

                        autorization(page, url, username, password)
                        good_avtoriz = 1
                    except Exception as ex:
                        print(f"Ошибка перезапуска: {ex}")
                        try:
                            browser.close()
                        except:
                            pass
                        time.sleep(20)
                        continue
                    
                    if good_avtoriz:
                        break
                
                # Ждем загрузки главной страницы
                while page.url != home_page:
                    time.sleep(1)
                print("Мы на главной странице")

                
                empty_cart_safe(page, url_cart)
                print("🗑 Очистили корзину ПОСЛЕ ПОВТОРНОГО ВХОДА")
                continue
        
        time.sleep(5)
        browser.close()
    
    # Обработка файлов
    # filenames = ['moscow.xlsx', 'rostov.xlsx', 'kazan.xlsx', 'spb.xlsx', 'novosib.xlsx', 'ekb.xlsx']
    filenames = ['rostov.xlsx',]
    for filename in filenames:
        red_xl(filename)
        processed_filename = filename.replace('.xlsx', '_ostatki.xlsx')
        
        try:
            chek_oasys(processed_filename)
        except Exception as e:
            print(f"⚠ Ошибка в chek_oasys: {e}")
            # Можно записать в лог или продолжить
        
        try:
            chek_hydraluxe(processed_filename)
        except Exception as e:
            print(f"⚠ Ошибка в chek_hydraluxe: {e}")
            
        # Продолжаем выполнение
        add_rastvor(processed_filename)
        
        city_name = filename.replace('.xlsx', '').capitalize()
        if city_name == 'Spb':
            city_name = 'Питер'
        elif city_name == 'Novosib':
            city_name = 'Новосибирск'
        elif city_name == 'Ekb':
            city_name = 'Екатеринбург'
        elif city_name == 'Rostov':
            city_name = 'Ростов'
        elif city_name == 'Moscow':
            city_name = 'Москва' 

        send_email(processed_filename, city_name)
    
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Время выполнения программы: {execution_time} секунд")


if __name__ == "__main__":
    while True:
        main()
        time.sleep(30)