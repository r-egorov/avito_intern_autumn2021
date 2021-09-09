from .models import Balance


class BalanceDoesNotExist(Balance.DoesNotExist):
    """
    An exception raised when no Balance found with some User's id.
    Stores the input JSON field's name, in which the User's id was passed
    """
    def __init__(self, field_name):
        self.field_name = field_name
