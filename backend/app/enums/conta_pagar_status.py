from enum import Enum


class ContaPagarStatus(str, Enum):
    PENDENTE = "PENDENTE"
    PARCIAL = "PARCIAL"
    PAGO = "PAGO"
    CANCELADO = "CANCELADO"
