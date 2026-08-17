from pydantic import BaseModel, Field
from fastapi import UploadFile
from typing import Optional

class HygieneMailingRequest(BaseModel):
    base_file_path: Optional[str] = Field(None, description="Caminho local do Arquivo")
    base_file: Optional[UploadFile] = Field(None, description="Arquivo")

    filter_file_path: Optional[str] = Field(None, description="Caminho local do Arquivo")
    filter_file: Optional[UploadFile] = Field(None, description="Arquivo")

    output_dir: str = Field(description="Caminho do diretório onde o arquivo filtrado será salvo")

    def validate_input(self):
        if not self.base_file_path and not self.base_file:
            raise ValueError("É necessário fornecer um caminho de arquivo ou um arquivo CSV.")
        if not self.filter_file_path and not self.filter_file:
            raise ValueError("É necessário fornecer um caminho de arquivo ou um arquivo CSV.")