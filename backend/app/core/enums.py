from enum import Enum


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    GERENTE = "GERENTE"
    FUNCIONARIO = "FUNCIONARIO"
    VENDEDOR = "VENDEDOR"

class AddressType(str, Enum):
    RESIDENCIAL = "RESIDENCIAL"
    TRABALHO = "TRABALHO"

class StockMovementType(str, Enum):
    ENTRADA = "ENTRADA"
    TRANSFERENCIA = "TRANSFERENCIA"
    VENDA = "VENDA"
    DEVOLUCAO = "DEVOLUCAO"
    CANCELAMENTO = "CANCELAMENTO"
    AJUSTE = "AJUSTE"