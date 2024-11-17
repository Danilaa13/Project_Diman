from openpyxl import load_workbook

def chek_hydraluxe(file_path: str):
    file_path_2 = "products_modified_3.xlsx" 

    print('загружаю файлы')

    workbook = load_workbook(file_path)
    modi_workbook2 = load_workbook(file_path_2)

    sheet_modi = modi_workbook2.active
    sheet_ostat = workbook.active

    hydra_30_arr = []
    hydra_90_arr = []
    hydra_180_arr = []

    arr_num_lines_ostatok = []

    for i, row in enumerate(sheet_ostat.iter_rows(values_only=True)):
            row = list(row)
            print(i)
            if ('hydraluxe (30 линз)' in row[0]) and not('for astigmatism' in row[0]):
                hydra_30_arr.append(row)
                arr_num_lines_ostatok.append(i+1)
            if ('hydraluxe (90 линз)' in row[0]) and not('for astigmatism' in row[0]):
                hydra_90_arr.append(row)
                arr_num_lines_ostatok.append(i+1)


    adres = hydra_30_arr[0][3]
    arr_num_lines = []

    end_row = arr_num_lines_ostatok[-1]

    for i, row in enumerate(sheet_modi.iter_rows(values_only=True)):
            row = list(row)
            line_row = []
            if row[1] is not None and 'hydraluxe (180 линз)' in row[1] and row[2] is not None:
                name = row[1].lower()
                name_art = row[2]
                cod_art = row[3]
                id_art = row[5]
                shtrih_cod = row[40]
                ostatok = 0

                line_row.append(name)
                line_row.append(name_art)
                line_row.append(ostatok)
                line_row.append(adres)
                line_row.append(cod_art)
                line_row.append(id_art)
                line_row.append(shtrih_cod)

                hydra_180_arr.append(line_row)
                arr_num_lines.append(i+1)

    index = 0
    len_hydra_arr = max(len(hydra_30_arr), len(hydra_90_arr), len(hydra_180_arr))

    while index < len_hydra_arr:
        if hydra_90_arr[index][2] == 0:
            for line in hydra_30_arr:
                if (line[2] >= 3) and (hydra_90_arr[index][1] == line[1]):
                    hydra_90_arr[index][2] = line[2] // 3
                    break
        count = 0
        if hydra_180_arr[index][2] == 0:
            for i, line2 in enumerate(hydra_30_arr):
                if (line2[2] >= 6) and (hydra_180_arr[index][1] == line2[1]):
                    hydra_180_arr[index][2] = line2[2] // 6
                    count += 1
                    break

            if count == 1:
                continue

            for i, line3 in enumerate(hydra_90_arr):
                if (line3[2] >= 2) and (hydra_180_arr[index][1] == line3[1]):
                    hydra_180_arr[index][2] = line3[2] // 2
                    break

        index += 1
            

    for i, line in enumerate(hydra_30_arr):
        print(i, line)

    for i, line in enumerate(hydra_90_arr):
        print(i, line)

    for i, line in enumerate(hydra_180_arr):
        print(i, line)


    # Проверяем, достаточно ли места в таблице
    if end_row > sheet_ostat.max_row:
        raise ValueError("Результат выходит за пределы таблицы. Проверьте диапазон.")

    insert_row = end_row + 1
    sheet_ostat.insert_rows(insert_row, amount=len(hydra_180_arr))

    # Записываем данные построчно
    for i, row_data in enumerate(hydra_180_arr, start=insert_row):
        for j, value in enumerate(row_data, start=1):  # Столбцы начинаются с 1
            sheet_ostat.cell(row=i, column=j, value=value)

    # Сохраняем изменения
    workbook.save(file_path)
    print(f"Данные успешно записаны в интервал строк {insert_row}-{insert_row+len(hydra_180_arr)} файла {file_path}")

