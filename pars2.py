import openpyxl
from openpyxl import Workbook

workbook_1 = openpyxl.load_workbook('products_modified_2.xlsx')
sheet = workbook_1.active

names_1 = sheet['B']
parametrs_1 = sheet['C']

for num,cell in enumerate(names_1):
    if '1-day Acuvue moist'.lower() in str(cell.value).lower():
        print("до", parametrs_1[num].value)
        q = str(parametrs_1[num].value) 
        if q != 'None':
            q = q.split()
            if ',' in q[1]:
                q[1] = q[1].replace(',', '.')
                q = ' '.join(q)
                parametrs_1[num].value = q
                print("после",cell.value, parametrs_1[num].value)
            

workbook_1.save('products_modified_3.xlsx')


