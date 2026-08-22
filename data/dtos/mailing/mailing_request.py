from pydantic import BaseModel, ConfigDict, Field
from fastapi import UploadFile
from typing import List

class TwoFilesRequest(BaseModel):
    
    # Configuração para permitir tipos arbitrários, como UploadFile
    model_config = ConfigDict(arbitrary_types_allowed=True)

    first_file: UploadFile = Field(description="Primeiro arquivo enviado pelo cliente")
    second_file: UploadFile = Field(description="Segundo arquivo enviado pelo cliente")

    def validate_input(self):
        if not self.first_file.filename or not self.second_file.filename:
            raise ValueError("Os dois arquivos precisam ter nomes válidos.")


class SingleFileRequest(BaseModel):
    
    # Configuração para permitir tipos arbitrários, como UploadFile
    model_config = ConfigDict(arbitrary_types_allowed=True)

    file: UploadFile = Field(description="Arquivo enviado pelo cliente")

    def validate_input(self):
        if not self.file.filename:
            raise ValueError("O arquivo precisa ter um nome válido.")


class MultipleFilesRequest(BaseModel):

    model_config = ConfigDict(arbitrary_types_allowed=True)

    files: List[UploadFile] = Field(description="Arquivos CSV enviados para concatenação")

    def validate_input(self):
        if len(self.files) < 2:
            raise ValueError("É necessário enviar pelo menos dois arquivos.")

        if any(not file.filename for file in self.files):
            raise ValueError("Todos os arquivos precisam ter um nome válido.")