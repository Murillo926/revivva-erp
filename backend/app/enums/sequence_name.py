from enum import Enum


class SequenceName(str, Enum):
    PRODUCT = "PRODUCT"
    SALE = "SALE"
    PROMISSORY = "PROMISSORY"
    PAYMENT = "PAYMENT"