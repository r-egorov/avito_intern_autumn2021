from .models import Balance


class BalanceDoesNotExist(Balance.DoesNotExist):
    def __init__(self, field_name):
        self.field_name = field_name
