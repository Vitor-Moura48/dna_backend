from pydantic import BaseModel, Field
from fastapi import UploadFile
from typing import Optional

class PdfToImageRequest(BaseModel):
    file_path: Optional[str] = Field(None, description="Caminho local do PDF")
    file: Optional[UploadFile] = Field(None, description="Arquivo PDF")

    def validate_input(self):
        if not self.file_path and not self.file:
            raise ValueError("É necessário fornecer um caminho de arquivo ou um arquivo PDF.")