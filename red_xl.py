import openpyxl
from openpyxl import Workbook


def red_xl(ostatok_table:str):
    # Открываем файл
    workbook_1 = openpyxl.load_workbook('products_modified_3.xlsx')
    workbook_ostatok =  openpyxl.load_workbook(ostatok_table)

    name_city = ostatok_table.split('.')[0]

    # Выбираем активный лист
    sheet = workbook_1.active
    sheet_rostov = workbook_ostatok.active

    # Выбираем столбец (например, столбец A)
    names_1 = sheet['B']
    parametrs_1 = sheet['C']
    cod_art_1 = sheet['D']
    id_art_1 = sheet['F']
    shtrih_1 = sheet['AO']


    arr1 = []
    index = 0
    while index < len(names_1):
        row = []
        row.append(str(names_1[index].value).lower())
        row.append(parametrs_1[index].value)
        row.append(cod_art_1[index].value)
        row.append(id_art_1[index].value)
        row.append(shtrih_1[index].value)
        arr1.append(row)
        index += 1


    wb2 = Workbook()
    ws2 = wb2.active

    ws2.append(['Наименование', 'Наименование артикула',  'Остаток', 'Адрес', 'Код артикула', 'ID артикула', 'Штрихкод'])

    ws2.column_dimensions['A'].width = 50
    ws2.column_dimensions['B'].width = 40
    ws2.column_dimensions['C'].width = 15
    ws2.column_dimensions['D'].width = 15
    ws2.column_dimensions['E'].width = 15
    ws2.column_dimensions['F'].width = 15
    ws2.column_dimensions['G'].width = 15

    names_2 = sheet_rostov['A']
    parametrs_2 = sheet_rostov['B']
    ostatok_2 = sheet_rostov['C']            
    adres_2 = sheet_rostov['D']   


    arr2 = []
    in2 = 1
    while in2 < len(names_2):
        rez = []
        print(in2)
        for num, par1 in enumerate(arr1):
            name = str(names_2[in2].value).lower()
            name2 = str(par1[0]).lower()

            if (parametrs_2[in2].value in par1) and (name == name2):
                rez.append(par1[0])
                rez.append(par1[1])
                rez.append(ostatok_2[in2].value)
                rez.append(adres_2[in2].value)
                rez.append(par1[2])
                rez.append(par1[3])
                rez.append(par1[4])
                ws2.append(rez)
                arr2.append(rez)

                del arr1[num]
                break
        in2 += 1


    wb2.save(f'{name_city}_ostatki.xlsx')





