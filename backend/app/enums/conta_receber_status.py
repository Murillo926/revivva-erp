from enum import Enum

class ContaReceberStatus(str, Enum):
    PENDENTE = "PENDENTE"
    PARCIAL = "PARCIAL"
    PAGO = "PAGO"
    CANCELADO = "CANCELADO"
