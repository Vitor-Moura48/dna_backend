from pydantic import BaseModel, ConfigDict, Field
from fastapi import UploadFile

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