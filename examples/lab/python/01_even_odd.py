# Even or odd with input validation.
try:
    n = int(input("Enter a number: "))
    print(n, "is", "even" if n % 2 == 0 else "odd")
except ValueError:
    print("Please type a whole number")
