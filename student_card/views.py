from base64 import b64encode
from io import BytesIO

from django.shortcuts import render, get_object_or_404
import qrcode
from django.template.loader import render_to_string

from data_management.models import Student

def generate_student_card(request):
    student = get_object_or_404(Student, pk=request.user.id)

    qr_data = f"Name: {student.full_name}\nEmail: {student.email}\nWhatsApp: {student.whatsapp_number}\nBirth Date: {student.birth_date}"
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)

    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_code_base64 = b64encode(buffer.getvalue()).decode("utf-8")

    context = {
        'name': student.full_name,
        'student_id': student.user_id,
        'department': student.major,
        'address': student.home_location,
        'email': student.email,
        'whatsapp': student.whatsapp_number,
        'qr_code': f"data:image/png;base64,{qr_code_base64}",
    }

    html_string = render_to_string("student_card.html", context)
