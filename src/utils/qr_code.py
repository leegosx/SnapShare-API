import qrcode
import base64
from io import BytesIO


def create_qr_code_from_url(url):
    """
    The create_qr_code_from_url function takes a URL as input and returns the base64 encoded string of a QR code image.
    
    :param url: Create a qr code from the url
    :return: A string of base64 encoded image data
    :doc-author: Trelent
    """
    # Generate QR code for the transformed URL
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white")
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_byte_arr = img_byte_arr.getvalue()
    return base64.b64encode(img_byte_arr).decode("utf-8")
