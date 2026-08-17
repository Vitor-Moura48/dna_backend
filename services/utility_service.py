import pymupdf

from data.dtos.utility.utility_request import PdfToImageRequest

class UtilityService:
    def __init__(self):
        pass

    async def pdf_to_image(self, request: PdfToImageRequest):

        doc = None
        if request.file:
            pdf_bytes = await request.file.read()
            doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")  
        else:
            doc = pymupdf.open(request.file_path)

        page = doc[0]
        tables = page.find_tables() # Encontra as tabelas na página
        
        if tables.tables:
            # Pega a caixa delimitadora (bbox) da primeira tabela encontrada
            page.set_cropbox(tables[0].bbox)

        pix = page.get_pixmap(dpi=300)

        png_bytes = pix.tobytes("png")  # Converte para bytes PNG
        doc.close()

        return png_bytes