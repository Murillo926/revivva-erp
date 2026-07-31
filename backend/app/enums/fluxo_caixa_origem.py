from enum import Enum

class FluxoCaixaOrigem(str, Enum):
    VENDA = "VENDA"
    DESPESA = "DESPESA"
    COMISSAO = "COMISSAO"
    AJUSTE = "AJUSTE"
