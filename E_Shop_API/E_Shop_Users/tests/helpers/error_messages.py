class ErrorMessages:
    """ Error notification constants """

    # [Price/Count] E_Shop_API.E_Shop_Products.validators
    NEGATIVE_VALUE = "Cannot be negative"

    # [Password]   E_Shop_API.E_Shop_Users.validators
    UPPER_CASE_LETTER = "Password must contain at least one upper case letter"
    AT_LEAST_ONE_DIGIT = "Password must contain at least one digit"
    MIN_8_CHARACTERS = "Password must be at least 8 characters long"

    # [Birthday]   E_Shop_API.E_Shop_Users.validators
    CANNOT_BE_FUTURE = 'Cannot be in the future'
    YEAR_IS_NOT_VALID = 'This year is not valid'
