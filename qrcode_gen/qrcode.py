import frappe
import pyqrcode
import barcode
from barcode.writer import ImageWriter, SVGWriter
import io
import base64

@frappe.whitelist()
def gen_qrcode(text, as_svg=True):
    """
    Generate a QR code as SVG (recommended) or PNG.
    
    :param text: Text to encode in QR
    :param as_svg: If True, returns SVG; else PNG
    :return: data URI of the QR code image
    """
    qr = pyqrcode.create(text)

    if as_svg:
        buffer = io.BytesIO()
        qr.svg(buffer, scale=4, quiet_zone=1)  # scale and quiet_zone adjustable
        svg_data = buffer.getvalue().decode()
        # Use base64 for PDF reliability
        svg_base64 = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/svg+xml;base64,{svg_base64}"
    else:
        return f"data:image/png;base64,{qr.png_as_base64_str(scale=5)}"

@frappe.whitelist()
def gen_code(data, code_type="qrcode", as_svg=False):
    """
    Generate a QR code or barcode.
    
    :param data: Text or number to encode
    :param code_type: 'qrcode', 'code128', 'ean13', 'upc'
    :param as_svg: If True, returns SVG; else PNG
    :return: data URI of image
    """
    code_type = code_type.lower()

    if code_type == "qrcode":
        return gen_qrcode(data, as_svg=as_svg)

    elif code_type in ["code128", "ean13", "upc"]:
        # Options to spread out barcode lines
        options = {
            'module_width': 0.4,  # Width of narrowest bar (in mm), increase for wider bars
            'module_height': 10.0,  # Height of bars (in mm)
            'quiet_zone': 6.5,  # Margin on sides (in mm)
            'font_size': 10,  # Text size below barcode
            'text_distance': 5.0,  # Distance between barcode and text
        }
        
        if as_svg:
            # Use SVGWriter for SVG output
            barcode_obj = barcode.get(code_type, data, writer=SVGWriter())
            buffer = io.BytesIO()
            barcode_obj.write(buffer, options=options)
            
            # Add letter-spacing to the SVG text
            svg_content = buffer.getvalue().decode('utf-8')
            # Add letter-spacing style to text elements
            svg_content = svg_content.replace('<text', '<text letter-spacing="2"')
            
            svg_base64 = base64.b64encode(svg_content.encode('utf-8')).decode("utf-8")
            return f"data:image/svg+xml;base64,{svg_base64}"
        else:
            # Use ImageWriter for PNG output
            barcode_obj = barcode.get(code_type, data, writer=ImageWriter())
            buffer = io.BytesIO()
            barcode_obj.write(buffer, options=options)
            base64_img = base64.b64encode(buffer.getvalue()).decode("utf-8")
            return f"data:image/png;base64,{base64_img}"

    else:
        frappe.throw(f"Unsupported code type: {code_type}")