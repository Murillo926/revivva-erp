import re

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.client_address import ClientAddress
from app.repositores.client_repository import ClientRepository
from app.schemas.client import ClientCreate


class ClientService:
    def __init__(self) -> None:
        self.repository = ClientRepository()

    def create(
        self,
        db: Session,
        data: ClientCreate,
    ) -> Client:
        normalized_cpf = re.sub(r"\D", "", data.cpf)
        normalized_phone = re.sub(r"\D", "", data.telefone)

        if len(normalized_cpf) != 11:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="O CPF deve possuir 11 números.",
            )

        existing_client = self.repository.get_by_cpf(
            db=db,
            cpf=normalized_cpf,
        )

        if existing_client is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe um cliente cadastrado com este CPF.",
            )

        client = Client(
            nome=data.nome.strip(),
            cpf=normalized_cpf,
            telefone=normalized_phone,
            ativo=True,
        )

        client.enderecos = [
            ClientAddress(
                tipo=address.tipo.value,
                rua=address.rua.strip(),
                numero=address.numero.strip(),
                bairro=address.bairro.strip(),
                cidade=address.cidade.strip(),
                complemento=(
                    address.complemento.strip()
                    if address.complemento
                    else None
                ),
                referencia=(
                    address.referencia.strip()
                    if address.referencia
                    else None
                ),
            )
            for address in data.enderecos
        ]

        return self.repository.create(
            db=db,
            client=client,
        )