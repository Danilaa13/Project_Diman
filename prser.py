import requests
import time
import schedule
import os
from test import redak_axi_text, addid_redac, redak_mo, get_balance
from red_xl import red_xl
from send_mail import send_email
from openpyxl import Workbook
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager




def autorization(url, driver, username, password):
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    input_login = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="userID"]')))
    input_password = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"]')))
    btn_input = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Войти') and @class='btn']")))

    input_login.send_keys(username)
    input_password.send_keys(password)
    btn_input.click()

    return driver


def start_order(driver, wait):
    order_lenses_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//a[@title='Заказать линзы' and @id='link1']")))
    order_lenses_btn.click()
    order_entry = wait.until(EC.presence_of_element_located((By.XPATH, "//a[@id='menu-ordering-touch' and contains(text(), 'Ввод заказа')]")))
    order_entry.click()

    return driver


def get_product_selection(driver, wait):
    select_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'select[name="selectedBrandCode"]')))
    product_names = select_box.find_elements(By.TAG_NAME, 'option')
    
    return {
        'driver': driver,
        'product_names': product_names[1:] 
    }

    

def set_parametr_product(driver, test_quantity):
    wait = WebDriverWait(driver, 10)
    select_all_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "Выбрать все")]')))
    select_all_btn.click()
    time.sleep(1)
    #ищем окошечки для ввода количества
    windows_for_number = driver.find_elements(By.CLASS_NAME, 'drawer-line-quantity-halo')
    for window in windows_for_number:
        input_number = window.find_element(By.TAG_NAME, 'input')
        input_number.clear()
        input_number.send_keys(str(test_quantity))

    #ищем чекбокс "Выбрать все" и кликаем на него
    checkbox_select_all = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[id="drawer-select-all-check"]')))
    checkbox_select_all.click()
    time.sleep(2)


def add_to_cart(driver):
    wait = WebDriverWait(driver, 10)
    #ищем кнопку "Добавить в корзину" и кликаем на неё
    add_to_cart_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[id="add-to-cart-button-rx"]')))
    add_to_cart_btn.click()
    


def empty_cart(driver, url, wait):
    driver.get(url)
    select_all_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[title="Удалить"]')))
    select_all_btn.click()


def check_style(driver, css_selector, styles_to_check:dict):
    #css_selector = 'your_css_selector'
    #styles_to_check = {'color': 'red', 'font-size': '16px'}
    # Формирование JavaScript-кода для проверки стилей
    script = f"""
    var element = document.querySelector('{css_selector}');
    var styles = window.getComputedStyle(element);
    """

    # Добавление условий для каждого стиля
    for style, value in styles_to_check.items():
        script += f"if (styles.{style} !== '{value}') return false;"

    # Возвращение true, если все стили соответствуют
    script += "return true;"

    # Выполнение JavaScript-кода
    result = driver.execute_script(script)

    # Проверка результата
    return result


def is_element_present_by_id(driver, element_id, styles_to_check:dict):
    
    try:
        driver.find_element(By.ID, f'{element_id}')
        x = check_style(driver, f'#{element_id}', styles_to_check)
        return True and x
    except NoSuchElementException:
        return False
    

def is_element_by_id(element_id, driver):
    try:
        driver.find_element(By.ID, f'{element_id}')
        return True 
    except NoSuchElementException:
        return False




def main():
    start_time = time.time()
    load_dotenv()
    options = Options()
    options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    wb = Workbook()
    ws = wb.active

    ws.append(['Наименование', 'Наименование артикула', 'Остаток', 'Адрес'])

    wb2 = Workbook()
    ws2 = wb2.active

    ws2.append(['Наименование', 'Наименование артикула', 'Остаток', 'Адрес'])

    username = os.getenv("LOGIN")
    password = os.getenv("PASS")
    url = "https://www.jnjvision.com/eocs-rwd/startExternal.xo?salesOrg=0020&localeID=ru_RU"
    url_order = "https://www.jnjvision.com/eocs-rwd/shipToSelection.xo?actionString=continueToCheckout"
    url_cart = "https://www.jnjvision.com/eocs-rwd/viewCart.xo?formAction=clearCartWarning"
    
    

    driver = autorization(url, driver, username, password)
    print("Авторизация прошла успешно")

    home_page = driver.current_url
    

    addresses = {
        0:'RU14102', 
        1:'RU39813'}
    
    lens_name = {
                0:'1-day Acuvue moist',
                1:'1-day Acuvue moist for astigmatism',
                2:'1-day Acuvue trueye', 
                3:'Acuvue 2', 
                4:'Acuvue Oasys with hydraclear plus',
                5:'Acuvue Oasys for astigmatism with hydraclear plus',
                6:'Acuvue Oasys 1-day with hydraluxe',
                7:'1-day Acuvue moist multifocal',
                8:'Acuvue Oasys 1-day with hydraluxe for astigmatism',
                9:'Acuvue Oasys multifocal',
                10:'Acuvue Oasys max 1-day',
                11:'Acuvue Oasys Max 1-Day Multifocal',
                }

    product_change = "Новый"
    product_number = 0
    # product_end_number = 11
    curves_number = 0
    blister_number = 0
    cylinder_number = 0
    axis_number = 0
    addidation_number = 0
    test_quntity = 100

    while True:
        wait = WebDriverWait(driver, 10)

        try:
            if is_element_by_id('cartCount', driver):
                empty_cart(driver, url_cart, wait)
                
            startpage_order_driver = start_order(driver, wait)
            product_selection = get_product_selection(startpage_order_driver, wait)

            
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'span[role="presentation"]'))).click()
            product_names = product_selection['product_names']

            cylinder_presence = False
            addid_presence = False

            while product_number < len(product_names):

                product_names[product_number].click()
                print("Выбрал продукт")
                #выбираем комерческую поставку
                commercial_order_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[id="id_revenue_button"]')))

                commercial_order_btn.click()
                print("Выбрал поставку")
                #выбираем кривизну
                
                base_curves_btn = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[id="id_revenue_basecurves"]')))
                curves_btns = base_curves_btn.find_elements(By.TAG_NAME, 'a')

                if curves_number < len(curves_btns):
                    curves_btns[curves_number].click()
                    print("Выбрал кривизну")
                    time.sleep(1)
                    
                    #проверяем есть ли цилиндры и оси для выбора
                    if is_element_present_by_id(driver, 'id_cylinders_and_axes', {'display': 'block'}):
                        print("цилиндры есть")
                        cylinder_presence = True
                        cylinders_window = driver.find_element(By.CSS_SELECTOR, 'select[id="id_cylinder_select"]')
                        cylinders = cylinders_window.find_elements(By.TAG_NAME, 'option')[1:]

                        if cylinder_number < len(cylinders):
                            cylinders[cylinder_number].click()
                            print("Выбрал цилиндр")
                            time.sleep(1)

                        axis_window = driver.find_element(By.CSS_SELECTOR, 'select[id="id_axis_select"]')
                        axis = axis_window.find_elements(By.TAG_NAME, 'option')[1:]

                        if axis_number < len(axis):
                            axis[axis_number].click()
                            print("Выбрал ось")
                            time.sleep(1)


                    #проверяем есть ли адддация 
                    if is_element_present_by_id(driver, 'id_add_powers', {'display': 'block'}):
                        print("аддидация есть")
                        addid_presence = True
                        addidations_window = driver.find_element(By.CSS_SELECTOR, 'div[id="id_add_power_buttons"]')
                        addidation_btns = addidations_window.find_elements(By.TAG_NAME, 'a')

                        if addidation_number < len(addidation_btns):
                            addidation_btns[addidation_number].click()
                            print("Выбрал аддидацию")
                            time.sleep(1)
                    
                    #проверяем есть ли блистеры для выбора
                    if is_element_present_by_id(driver, 'id_single_uom_buttons', {'display': 'block'}):
                        print("блистеры есть")
                        blister_window = driver.find_element(By.CSS_SELECTOR, 'div[id="id_single_uom_buttons"]')
                        blisters = blister_window.find_elements(By.TAG_NAME, 'a')

                        if blister_number < len(blisters):
                            package_volume = blisters[blister_number].text
                            blisters[blister_number].click()
                            print("Выбрал блистер")
                            time.sleep(1)
                            set_parametr_product(driver, test_quntity)
                            print("Выбрал все варианты")
                            time.sleep(1)
                            add_to_cart(driver)
                            print("Добавил в корзину")
                            time.sleep(1)

                    # добавили продукт в корзину
                    # переходим к оформлению заказа 
                    
                    adres = 0
                    while adres < len(addresses):
                        
                        driver.get(url_order)
                        time.sleep(2)
                        print("начинаю цикл")
                        print("страница с адресом")
                        
                        wait.until(EC.element_to_be_clickable((By.XPATH, f'//label[contains(text(), "{addresses[adres]}")]'))).click()
                        print("раз")
                        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[title="Продолжить"]'))).click()
                        print("два")
                        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[title="Продолжить"]'))).click()
                        print("три")

                        try:
                            elem2 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[title="Продолжить"]')))
                            elem2.click()
                        except TimeoutException:
                            print("Предварительной страницы с отсутствующими позициями не было.")

                        print('отсюда собираем информацию') 
                        products_text = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[class="table-item stack"]')))

                        
                        for num, text_in in enumerate(products_text):
                            print(addresses[adres])
                            lines = text_in.text.split('\n')
                            curvature = lines[0].split()[-1].replace(',', '.')

                            lines[0] = lens_name[product_number]
                            if package_volume == '24':
                                lines[0] = f'{lines[0]} ({package_volume} линзы)'
                            else:
                                lines[0] = f'{lines[0]} ({package_volume} линз)'

                            if 'Ось' in lines[1]:
                                lines[1] = redak_axi_text(lines[1], curvature, package_volume, product_number)
                                if lines[1].endswith("+0.00"):
                                    e = lines[1].split()
                                    e[-1] = '0.00'
                                    lines[1] = ' '.join(e)
                            elif 'Аддидация' in lines[1]:
                                lines[1] = addid_redac(lines[1], curvature)
                            else:
                                lines[1] = redak_mo(lines[1], curvature)


                            if len(lines) == 2:
                                lines.append(test_quntity)
                            else:
                                lines[2] = get_balance(lines[2])
                            
                            if len(lines) == 4:
                                lines = lines[:-1]

                            if adres == 0:
                                lines.append('Шолохова')
                                ws.append(lines)
                            else:
                                lines.append('Островитянова')
                                ws2.append(lines)
                            
                            

                            print(num, lines)
                            print()

                        adres += 1
                        if adres == len(addresses):
                            break
                        else:
                            print("идем на следующий круг")
                            driver.get(url_order)

                    blister_number += 1

                    if cylinder_presence:
                        if blister_number == len(blisters):
                            blister_number = 0
                            axis_number += 1

                        if axis_number == len(axis):
                            axis_number = 0
                            cylinder_number += 1
                        
                        if cylinder_number == len(cylinders):
                            cylinder_number = 0
                            curves_number += 1

                        if curves_number == len(curves_btns):
                            product_number += 1
                            product_change = "Новый"
                            blister_number = 0
                            curves_number = 0
                        else:
                            product_change = "Старый"

                    elif addid_presence:
                        if blister_number == len(blisters):
                            blister_number = 0
                            addidation_number += 1
                        if addidation_number == len(addidation_btns):
                            addidation_number = 0
                            curves_number += 1
                        if curves_number == len(curves_btns):
                            product_number += 1
                            product_change = "Новый"
                            blister_number = 0
                            curves_number = 0
                        else:
                            product_change = "Старый"

                    else:
                        if blister_number == len(blisters):
                            curves_number += 1
                            blister_number = 0
                                
                        if curves_number == len(curves_btns):
                            product_number += 1
                            product_change = "Новый"
                            blister_number = 0
                            curves_number = 0
                        else:
                            product_change = "Старый"
                        

                    empty_cart(driver, url_cart, wait)
                    print("Очистили корзину")
                    break

            
            print("Вышли из цикла")
            
            

            print(f"Продукт {product_number}.{product_change}")
            print(f"Кривизна {curves_number}")
            print(f"Цилиндр {cylinder_number}")
            print(f"Ось {axis_number}")
            print(f"Блистер {blister_number}")
            
            

            if product_number == len(product_names):
                print("Прошлись по всем продуктам")
                wb.save('rostov.xlsx')
                wb2.save('moscow.xlsx')
                break
        except Exception as ex:
            print(ex)
            print("Что-то пошло не так, начну этот круг заново")

            driver.close()
            driver.quit()

            time.sleep(1)

            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            driver = autorization(url, driver, username, password)

            while True:
                if driver.current_url == home_page:
                    print("Мы на главной странице")
                    break
                time.sleep(1)
            continue
        

    time.sleep(5)

    driver.close()
    driver.quit()

    red_xl()

    send_email('moscow_ostatki.xlsx', 'Москва')
    send_email('rostov_ostatki.xlsx', 'Ростов')

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Время выполнения программы: {execution_time} секунд")

        





if __name__ == "__main__":

    main()

    schedule.every(4).hours.do(main)

    while True:
         schedule.run_pending()
         time.sleep(1)