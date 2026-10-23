# Class with methods: a tiny bank account.
class Account:
    def __init__(self, owner, balance=0):
        self.owner, self.balance = owner, balance
    def deposit(self, amount):
        self.balance += amount
    def withdraw(self, amount):
        if amount > self.balance:
            raise ValueError("insufficient balance")
        self.balance -= amount

acc = Account("Kanak", 500)
acc.deposit(250)
try:
    acc.withdraw(1000)
except ValueError as e:
    print("Error:", e)
print(acc.owner, "balance =", acc.balance)
