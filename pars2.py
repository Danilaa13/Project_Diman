import openpyxl
from openpyxl import Workbook

workbook_1 = openpyxl.load_workbook('products_modified_2.xlsx')
sheet = workbook_1.active

parametrs_1 = sheet['C']

for cell in parametrs_1:
    name2 = str(cell.value)
    
    if "," in name2.split():
        print(f"до {name2}")
        ls = name2.split()
        idx = ls.index(",")
        name2 = " ".join(name2.split()[:idx]) + " ".join(name2.split()[idx:])
        cell.value = name2
        print(f"после {name2}")
 
            

workbook_1.save('products_modified_3.xlsx')

# pac_volume = 24

# name2 ='8.6, CYL: -0.75 , AXIS: 10, -6.00'



# if "," in name2.split():
#     ls = name2.split()
#     idx = ls.index(",")
#     name2 = " ".join(name2.split()[:idx]) + " ".join(name2.split()[idx:])


# print(name2)


