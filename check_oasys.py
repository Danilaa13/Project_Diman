from openpyxl import load_workbook


# Открываем существующую таблицу
def chek_oasys(file_path: str):

    workbook = load_workbook(file_path)

    # Выбираем активный лист
    sheet = workbook.active

    arr_oasys = []

    arr_num_lines = []

    six_linz = []
    tvelw_linz = []
    twenti_linz = []

    start_row = 0
    end_row = 0

    for i, row in enumerate(sheet.iter_rows(values_only=True)):
        row = list(row)
        
        if 'acuvue oasys with hydraclear plus' in row[0]:
            arr_oasys.append(row)
            arr_num_lines.append(i+1)

    start_row = arr_num_lines[0]
    end_row = arr_num_lines[-1]


    for row in sheet.iter_rows(min_row=start_row, max_row=end_row, values_only=True):
        row = list(row)
        if '6' in row[0]:
            six_linz.append(row)
        elif '12' in row[0]:
            tvelw_linz.append(row)
        elif '24' in row[0]:
            twenti_linz.append(row)


    index = 0

    while index < len(six_linz):

        if tvelw_linz[index][2] == 0:
            count_six = six_linz[index][2]
            if (count_six >= 2) and (tvelw_linz[index][1] == six_linz[index][1]):
                tvelw_linz[index][2] = count_six // 2

        if twenti_linz[index][2] == 0:
            count_six = six_linz[index][2]
            count_tvelw = tvelw_linz[index][2]

            if (count_six >= 4) and (twenti_linz[index][1] == six_linz[index][1]):
                twenti_linz[index][2] = count_six // 4
            elif (count_tvelw >= 2) and (twenti_linz[index][1] == tvelw_linz[index][1]):
                twenti_linz[index][2] = count_tvelw // 2

        index += 1

    rezult_arr = []

    for line in six_linz:
        print(line)
        rezult_arr.append(line)

    for line in tvelw_linz:
        print(line)
        rezult_arr.append(line)

    for line in twenti_linz:
        print(line)
        rezult_arr.append(line)


    # Проверяем, достаточно ли места в таблице
    if end_row > sheet.max_row:
        raise ValueError("Результат выходит за пределы таблицы. Проверьте диапазон.")

    # Записываем данные построчно
    for i, row_data in enumerate(rezult_arr, start=start_row):
        for j, value in enumerate(row_data, start=1):  # Столбцы начинаются с 1
            sheet.cell(row=i, column=j, value=value)

    # Сохраняем изменения
    workbook.save(file_path)
    print(f"Данные успешно записаны в интервал строк {start_row}-{end_row} файла {file_path}")