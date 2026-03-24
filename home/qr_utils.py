import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
import os
from PIL import Image, ImageDraw

def generate_qr_code(data, box_size=10, border=4):
    """Generate QR code from data"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to BytesIO
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    
    return img_io

def create_hall_ticket_qr(hall_ticket):
    """Create and save QR code for hall ticket"""
    qr_data = hall_ticket.get_qr_data()
    qr_img = generate_qr_code(qr_data)
    
    filename = f"hallticket_{hall_ticket.ticket_number}.png"
    hall_ticket.qr_code.save(filename, ContentFile(qr_img.read()), save=False)
