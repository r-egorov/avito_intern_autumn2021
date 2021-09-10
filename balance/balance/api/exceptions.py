from .models import Balance


class BalanceDoesNotExist(Balance.DoesNotExist):
    """
    An exception raised when no Balance found with some User's id.
    Stores the input JSON field's name, in which the User's id was passed
    """
    def __init__(self, field_name):
        self.field_name = field_name


class InvalidSortField(Exception):
    """
    An exception raised when `sort_by` field in get-transactions request
    is not `amount` or `date`
    """
    pass

class ConvertResultNone(Exception):
    """
    An exception raised when the result of currency conversion
    is None
    """
    pass
