from pydantic import BaseModel, ConfigDict, Field
from fastapi import UploadFile
from typing import List

class HygieneMailingRequest(BaseModel):
    
    # Configuração para permitir tipos arbitrários, como UploadFile
    model_config = ConfigDict(arbitrary_types_allowed=True)

    base_file: UploadFile = Field(description="Arquivo base enviado pelo cliente")
    filter_file: UploadFile = Field(description="Arquivo de filtro enviado pelo cliente")

    def validate_input(self):
        if not self.base_file.filename:
            raise ValueError("O arquivo base precisa ter um nome válido.")
        if not self.filter_file.filename:
            raise ValueError("O arquivo de filtro precisa ter um nome válido.")


class CleanMailingRequest(BaseModel):
    
    # Configuração para permitir tipos arbitrários, como UploadFile
    model_config = ConfigDict(arbitrary_types_allowed=True)

    file: UploadFile = Field(description="Arquivo enviado pelo cliente")

    def validate_input(self):
        if not self.file.filename:
            raise ValueError("O arquivo precisa ter um nome válido.")


class MatchMailingRequest(BaseModel):

    model_config = ConfigDict(arbitrary_types_allowed=True)

    base_file: UploadFile = Field(description="Arquivo base enviado pelo cliente")
    reference_file: UploadFile = Field(description="Arquivo de referência com uma coluna")

    def validate_input(self):
        if not self.base_file.filename:
            raise ValueError("O arquivo base precisa ter um nome válido.")
        if not self.reference_file.filename:
            raise ValueError("O arquivo de referência precisa ter um nome válido.")


class ConcatenateMailingRequest(BaseModel):

    model_config = ConfigDict(arbitrary_types_allowed=True)

    files: List[UploadFile] = Field(description="Arquivos CSV enviados para concatenação")

    def validate_input(self):
        if len(self.files) < 2:
            raise ValueError("É necessário enviar pelo menos dois arquivos.")

        if any(not file.filename for file in self.files):
            raise ValueError("Todos os arquivos precisam ter um nome válido.")