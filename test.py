def redak_axi_text(q, c, n, pr_num):
        q = q.replace(',', '.')
        q = q.replace('|', '')
        q = q.replace('SPH:', '')
        q = q.replace('Ось:', 'AXIS:')
        q = q.split()
        new_q = q
        new_q.append(q[0])
        new_q[0] = c
        if n == "30" and pr_num == 1:
             new_q.insert(5, n)
        new_q.insert(1, ', ')
        new_q.insert(4, ', ')
        new_q.insert(7, ', ')
        if n == "30" and pr_num == 1:
            new_q.insert(9, ', ')
        new_q.insert(3, ' ')
        new_q.insert(7, ' ')

        return "".join(new_q)

# print(redak_axi_text('SPH: -0,25 | CYL: -0,75 | Ось: 10', '9.0', '60'))



s = "SPH: -2,50 | Аддидация: H"
addid = "8.4, -0.25, HIGH (от +2.00 до +2.50), 8.4 мм"

def addid_redac(s, c):
        wer = {
                "H": "HIGH (от +2.00 до +2.50)",
                "M": "MID (от +1.50 до +1.75)",
                "L": "LOW (от +0.75 до +1.25)"
        }
        s = s.replace(',', '.')
        s = s.replace('| ', '')
        s = s.replace('SPH: ', '')
        s = s.replace('Аддидация: ', '')


        if 'H' in s:
            s = s.replace('H', f"{wer['H']}, ")
        if 'M' in s:
            s = s.replace('M', f"{wer['M']}, ")
        if 'L' in s:
            s = s.replace('L', f"{wer['L']}, ")

        new_s = s.split()
        new_s[0] = f'{new_s[0]},'
        s = ' '.join(new_s)

        return f'{c}, {s} {c} мм'


s2 = 'SPH: -1,25'

def redak_mo(s, c):
     s = s.replace(',', '.')
     s = s.replace('SPH: ', '')
     s = f'{c}, {s}'

     return s


r = "9 из 10 товаров недоступны."
def get_balance(r):
    balance = 0
    if 'недоступны' in r:
        r = r.split()
        balance = int(r[2]) - int(r[0])

    return balance








# tre = ['1-DAY ACUVUE® MOIST with LACREON®', # убираем with LACREON
#         '1-DAY ACUVUE® MOIST for ASTIGMATISM with LACREON®', # убираем with LACREON
#         '1-DAY ACUVUE® TruEye® with HYDRACLEAR®1', # убираем with HYDRACLEAR®1
#         'ACUVUE® 2', # оставляем как есть
#         'ACUVUE OASYS® with HYDRACLEAR® PLUS', # оставляем как есть
#         'ACUVUE OASYS® for Astigmatism with Hydraclear® Plus', # оставляем как есть
#         'ACUVUE OASYS® with HydraLuxe®', # оставляем как есть + после OASYS добавляем 1-day 
#         '1-DAY ACUVUE® MOIST MULTIFOCAL with LACREON®', # убираем with LACREON
#         'ACUVUE OASYS® with HydraLuxe® for ASTIGMATISM',# оставляем как есть + после OASYS добавляем 1-day
#         'ACUVUE® OASYS MULTIFOCAL', # оставляем как есть
#         'ACUVUE® OASYS MAX 1-Day*' # оставляем как есть
#         ]


# for name in tre:
#     name = name.replace('®', "")
#     name = name.replace('*', "")
#     arr = name.split()
#     if 'with LACREON' in name:
#         arr = name.split()[:-2]
#     if 'TruEye' in name:
#         arr = name.split()[:-2]
#         arr[-1] = arr[-1][:-2]
#     if '2' in name:
#         arr = name.split() 
#     if 'HYDRACLEAR' in name:
#         arr = name.split()
#     if 'HydraLuxe' in name:
#         arr = name.split()
#         arr.insert(2, '1-day')       
    
#     print(" ".join(arr).lower())






# s = "1-DAY ACUVUE® MOIST with LACREON® 8,5"
# arr = []

# for w in s.split():
#     sr = f'{w[0]}{w.lower()[1:]}' 
#     arr.append(sr)

# arr[1] = arr[1][:-1]
# print(arr)
# print(" ".join(arr[0:3]))

# lens_name = {1:'1-day acuvue moist',
#                 2:'1-day acuvue moist for astigmatism',
#                 3:'1-day acuvue trueye with hydraclear',
#                 4:'acuvue 2',
#                 5:'acuvue oasys with hydraclear plus',
#                 6:'acuvue oasys for astigmatism with hydraclear plus',
#                 7:'acuvue oasys 1-day with hydraluxe',
#                 8:'1-day acuvue moist multifocal',
#                 9:'acuvue oasys 1-day with hydraluxe for astigmatism',
#                 10:'acuvue oasys multifocal',
#                 11:'acuvue oasys max 1-day',}

# print(lens_name[3])