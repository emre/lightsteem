
from decimal import Decimal


class Amount:

    ASSETS = {
        "SBD": {"precision": 3, "nai": "@@000000013"},
        "STEEM": {"precision": 3, "nai": "@@000000021"},
        "VESTS": {"precision": 6, "nai": "@@000000037"},
    }

    @classmethod
    def from_asset(cls, asset_dict):
        amount = int(asset_dict["amount"]) / pow(10, asset_dict["precision"])
        asset = cls.get_symbol_from_nai(asset_dict["nai"])
        return Amount(f"{amount} {asset}")

    @staticmethod
    def get_symbol_from_nai(nai):
        for symbol, asset_detail in Amount.ASSETS.items():
            if nai == asset_detail["nai"]:
                return symbol

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

    @property
    def asset(self):
        precision = self.ASSETS.get(self.symbol).get("precision")
        return {
            "amount": str(int(self.amount * pow(10, precision))),
            "precision": precision,
            "nai": self.ASSETS.get(self.symbol).get("nai")
        }
