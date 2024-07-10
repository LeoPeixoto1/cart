from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import base64
import io
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from pydantic import BaseModel
from typing import List
import os

router = APIRouter()

class InvoiceInfo(BaseModel):
    nome: str
    endereco: str
    cpf: str
    periodo: str

class Item(BaseModel):
    Descricao: str
    Quantidade: int
    PrecoUnitario: float

def pegar_mes_anterior():
    today = datetime.today()
    first_day_of_current_month = today.replace(day=1)
    last_day_of_last_month = first_day_of_current_month - timedelta(days=1)
    first_day_of_last_month = last_day_of_last_month.replace(day=1)
    return first_day_of_last_month.strftime("%d/%m/%Y"), last_day_of_last_month.strftime("%d/%m/%Y")

def criar_fatura(invoice_info: InvoiceInfo, items: List[Item], save_path: str) -> io.BytesIO:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    with open("img.jpg", "rb") as image_file:
        image = Image.open(image_file)
        image_reader = ImageReader(image)
        c.drawImage(image_reader, 0, 0, width=width, height=height, preserveAspectRatio=True, mask='auto')

    text_y_start = height - 283.46

    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, text_y_start, f"Nome: {invoice_info.nome}")
    c.drawString(40, text_y_start - 20, f"Data: {datetime.today().strftime('%d/%m/%Y')}")
    c.drawString(40, text_y_start - 40, f"Endereço: {invoice_info.endereco}")
    c.drawString(40, text_y_start - 60, f"Período de Consumo: {invoice_info.periodo}")
    c.drawString(40, text_y_start - 80, f"Consumo Total: {250} kWh")

    c.setLineWidth(1)
    c.line(40, text_y_start - 100, width - 40, text_y_start - 100)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, text_y_start - 120, "Descrição")
    c.drawString(300, text_y_start - 120, "Quantidade")
    c.drawString(400, text_y_start - 120, "Preço Unitário")
    c.drawString(500, text_y_start - 120, "Total")

    c.line(40, text_y_start - 125, width - 40, text_y_start - 125)

    c.setFont("Helvetica", 12)
    y = text_y_start - 140
    total = 0
    for item in items:
        c.drawString(40, y, item.Descricao)
        c.drawString(300, y, str(item.Quantidade))
        c.drawString(400, y, f"R$ {item.PrecoUnitario:.2f}")
        item_total = item.Quantidade * item.PrecoUnitario
        c.drawString(500, y, f"R$ {item_total:.2f}")
        total += item_total
        y -= 20

    c.line(40, y - 10, width - 40, y - 10)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(400, y - 30, "Total Geral:")
    c.drawString(500, y - 30, f"R$ {total:.2f}")

    c.showPage()
    c.save()

    buffer.seek(0)

    with open(save_path, "wb") as f:
        f.write(buffer.getvalue())

    return buffer

@router.post("/gerar_fatura")
async def gerar_fatura(invoice_info: InvoiceInfo):
    items = [
        Item(Descricao='Tarifa Básica', Quantidade=1, PrecoUnitario=30.00),
        Item(Descricao='Consumo (kWh)', Quantidade=250, PrecoUnitario=0.75),
        Item(Descricao='Taxa de Iluminação Pública', Quantidade=1, PrecoUnitario=5.00)
    ]

    pdf_save_path = os.path.join(os.getcwd(), "fatura.pdf")

    pdf_buffer = criar_fatura(invoice_info, items, pdf_save_path)

    pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
    pdf_data_uri = f"data:application/pdf;base64,{pdf_base64}"

    return {"value": "fatura.pdf", "key": pdf_data_uri}
