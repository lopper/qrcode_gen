import frappe
import pyqrcode
import barcode
from barcode.writer import ImageWriter
import io
import base64



@frappe.whitelist()
def gen_qrcode(text):
    data = pyqrcode.create(text)

    return f'data:image/png;base64,{data.png_as_base64_str(scale=5)}'

@frappe.whitelist()
def gen_code(data, code_type="qrcode"):
    """
    Generate a QR code or barcode as base64 PNG.
    
    :param data: The text or number to encode
    :param code_type: Type of code: 'qrcode', 'code128', 'ean13', 'upc'
    :return: data URI of PNG image
    """
    code_type = code_type.lower()
    
    if code_type == "qrcode":
        qr = pyqrcode.create(data)
        return f"data:image/png;base64,{qr.png_as_base64_str(scale=5)}"
    
    # Barcode types supported by python-barcode
    elif code_type in ["code128", "ean13", "upc"]:
        barcode_obj = barcode.get(code_type, data, writer=ImageWriter())
        buffer = io.BytesIO()
        barcode_obj.write(buffer)
        base64_img = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{base64_img}"
    
    else:
        frappe.throw(f"Unsupported code type: {code_type}")