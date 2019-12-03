
counter = 0
while counter < 21:
    try:
        x  = int(input("Which Box was opened? "))
        counter = counter +1
    except ValueError:
        print("Please enter a valid number between 1 and 20")
    finally:
        print(counter)
