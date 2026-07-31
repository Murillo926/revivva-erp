from enum import Enum


class SequenceName(str, Enum):
    PRODUCT = "PRODUCT"
    SELLER = "SELLER"
    SALE = "SALE"
    PROMISSORY = "PROMISSORY"
    PAYMENT = "PAYMENT"
    PURCHASE = "PURCHASE"