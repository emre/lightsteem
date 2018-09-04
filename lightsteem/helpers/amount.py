
from decimal import Decimal


class Amount:

    def __init__(self, amount_data):
        amount, self.symbol = amount_data.split()
        self.amount = Decimal(amount)
        self.raw_data = amount_data

    def _check_type(self, other):
        if not isinstance(other, Amount):
            raise TypeError(
                "This operation only works with two Amount instances.")

    def __str__(self):
        return f"{self.amount} {self.symbol}"

    def __int__(self):
        raise ValueError("It's not possible to cast Amount instances to int.")

    def __float__(self):
        return float(self.amount)
