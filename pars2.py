

while True:
    try:
        print(1/0)
    except Exception as ex:
        print("на ноль делить нельзя")
        continue

    