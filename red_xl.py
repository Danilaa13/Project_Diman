import openpyxl
from openpyxl import Workbook


def red_xl():
    # Открываем файл
    workbook_1 = openpyxl.load_workbook('products_modified_3.xlsx')
    workbook_2 =  openpyxl.load_workbook('rostov.xlsx')
    workbook_3 =  openpyxl.load_workbook('moscow.xlsx')

    # Выбираем активный лист
    sheet = workbook_1.active
    sheet2 = workbook_2.active
    sheet3 = workbook_3.active

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

    names_2 = sheet2['A']
    parametrs_2 = sheet2['B']
    ostatok_2 = sheet2['C']            
    adres_2 = sheet2['D']   


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


    wb2.save(f'rostov_ostatki.xlsx')




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


    wb3 = Workbook()
    ws3 = wb3.active

    ws3.append(['Наименование', 'Наименование артикула',  'Остаток', 'Адрес', 'Код артикула', 'ID артикула', 'Штрихкод'])

    ws3.column_dimensions['A'].width = 50
    ws3.column_dimensions['B'].width = 40
    ws3.column_dimensions['C'].width = 15
    ws3.column_dimensions['D'].width = 15
    ws3.column_dimensions['E'].width = 15
    ws3.column_dimensions['F'].width = 15
    ws3.column_dimensions['G'].width = 15


    names_3 = sheet3['A']
    parametrs_3 = sheet3['B']
    ostatok_3 = sheet3['C']            
    adres_3 = sheet3['D'] 


    arr3 = []
    in3 = 1
    while in3 < len(names_3):
        rez = []
        print(in3)
        for num, par1 in enumerate(arr1):
            name = str(names_3[in3].value).lower()
            name2 = str(par1[0]).lower()
            if (parametrs_3[in3].value in par1) and (name == name2):
                rez.append(par1[0])
                rez.append(par1[1])
                rez.append(ostatok_3[in3].value)
                rez.append(adres_3[in3].value)
                rez.append(par1[2])
                rez.append(par1[3])
                rez.append(par1[4])
                ws3.append(rez)
                arr3.append(rez)

                del arr1[num]
                break
        in3 += 1


    wb3.save(f'moscow_ostatki.xlsx')





