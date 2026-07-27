from enum import Enum


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    GERENTE = "GERENTE"
    FUNCIONARIO = "FUNCIONARIO"
    VENDEDOR = "VENDEDOR"