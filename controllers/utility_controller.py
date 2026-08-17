from http import HTTPStatus
from fastapi import APIRouter, Depends, Response, Form, UploadFile, File
from services.utility_service import UtilityService
from data.dtos.utility.utility_request import PdfToImageRequest
from typing import Optional

router = APIRouter()

@router.post("/pdf-to-image",  status_code=HTTPStatus.CREATED)
async def pdf_to_image(
    file_path: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    utility_service: UtilityService = Depends()
    ):

    # Monta o DTO
    request = PdfToImageRequest(
        file_path=file_path,
        file=file,
    )
    
    # Valida
    request.validate_input()
    
    result = await utility_service.pdf_to_image(request)

    return Response(
        content=result, 
        media_type="image/png", 
        status_code=HTTPStatus.CREATED
        )