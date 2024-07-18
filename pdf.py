from fastapi import APIRouter
import base64
import io
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from pydantic import BaseModel
import os


router = APIRouter()


class ClientInfo(BaseModel):
    nome: str
    setor: str
    funcionarios: str
    endereco: str
    
    
def criar_pdf_cliente(client_info: ClientInfo, save_path: str) -> io.BytesIO:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    with open("img.jpg", "rb") as image_file:
        image = Image.open(image_file)
        image_reader = ImageReader(image)
        c.drawImage(image_reader, 0, 0, width=width, height=height, preserveAspectRatio=True, mask='auto')

    text_y_start = height - 283.46

    c.setFont("Helvetica", 20)
    c.drawString(110, text_y_start + 105, "Documento para confirmação de dados")
    c.setFont("Helvetica", 14)
    c.drawString(40, text_y_start + 65, "Por meio desse documento, você confirma o envio dos seguintes dados:")
    c.setFont("Helvetica-Bold", 18)
    c.drawString(40, text_y_start, "Informações do cliente:")
    c.setFont("Helvetica", 14)
    c.drawString(40, text_y_start - 20, f"Nome: {client_info.nome}")
    c.drawString(40, text_y_start - 50, f"Setor: {client_info.setor}")
    c.drawString(40, text_y_start - 80, f"Quantidade de funcionários: {client_info.funcionarios}")
    c.drawString(40, text_y_start - 110, f"Cidade: {client_info.endereco}")
    c.setFont("Helvetica", 10)
    c.drawString(40, text_y_start - 200, "Ao confirmar, você afirma que os dados estão corretos e que podemos dar prosseguimento.")

    c.showPage()
    c.save()

    buffer.seek(0)

    with open(save_path, "wb") as f:
        f.write(buffer.getvalue())

    return buffer

    
    
@router.post("/pdf")
async def gerar_pdf_cliente(client_info: ClientInfo):
    pdf_save_path = os.path.join(os.getcwd(), "coleta-de-dados.pdf")

    pdf_buffer = criar_pdf_cliente(client_info, pdf_save_path)

    pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
    pdf_data_uri = f"data:application/pdf;base64,{pdf_base64}"

    return {"value": "coleta-de-dados.pdf", "key": pdf_data_uri}