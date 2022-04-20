import datetime
import io

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def download_pdf(items):
    buffer = io.BytesIO()
    products_to_buy = canvas.Canvas(buffer)

    line = 800
    pdfmetrics.registerFont(TTFont('FreeSans', 'FreeSans.ttf'))

    products_to_buy.setFont('FreeSans', 16)
    products_to_buy.drawString(15, line, "Список покупок:")
    products_to_buy.setFont('FreeSans', 12)
    line -= 20
    for item in items:
        line -= 20
        to_print = f'{item}'
        products_to_buy.drawString(15, line, to_print.capitalize())
    line -= 55
    products_to_buy.setFont('FreeSans', 10)
    today = datetime.date.today()
    products_to_buy.drawString(
        15, line, 'From FoodGram:  Приятных покупок!'
    )
    line -= 20
    products_to_buy.setFont('FreeSans', 9)
    products_to_buy.drawString(15, line, F'{today}')

    products_to_buy.showPage()
    products_to_buy.save()

    buffer.seek(0)
    return buffer
