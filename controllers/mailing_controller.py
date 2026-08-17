from http import HTTPStatus
from fastapi import APIRouter, Depends, Response, Form, UploadFile, File
from typing import Optional
from services.mailing_service import MailingService
from data.dtos.mailing.mailing_request import HygieneMailingRequest

router = APIRouter()

@router.post("/",  status_code=HTTPStatus.CREATED)
async def hygiene_mailing(
    base_file_path: Optional[str] = Form(None),
    base_file: Optional[UploadFile] = File(None),
    filter_file_path: Optional[str] = Form(None),
    filter_file: Optional[UploadFile] = File(None),
    output_dir: str = Form(None),
    mailing_service: MailingService = Depends()
    ):

    # Monta o DTO
    request = HygieneMailingRequest(
        base_file_path=base_file_path,
        base_file=base_file,
        filter_file_path=filter_file_path,
        filter_file=filter_file,
        output_dir=output_dir
    )
    
    # Valida
    request.validate_input()
    
    await mailing_service.hygiene_mailing(request)

    return Response(status_code=HTTPStatus.CREATED)