from js import document, console, Uint8Array, window, File, URL, FileReader
import io
from PIL import Image
import qrcode
import base64
import json
from crypto import create_signature_download
from stego import encode_signature_in_image
from base64_signed_badge import SIGNED_BADGE_BASE64
import qr_content

def get_qr_content_by_mode():
    qr_mode = document.querySelector("#qr_mode").value

    mode_map = {
        "website": qr_content.website,
        "text": qr_content.text,
        "email": qr_content.email,
        "wifi": qr_content.wifi,
        "location": qr_content.location,
        "bitcoin": qr_content.bitcoin,
        "sms": qr_content.sms,
        "phone": qr_content.phone,
        "vcard": qr_content.vcard,
        "json": qr_content.json_content,
    }

    return mode_map.get(qr_mode, lambda: "")()

def get_error_correction_level():
    # Get selected error correction level
    error_level_map = {
        'L': qrcode.constants.ERROR_CORRECT_L,
        'M': qrcode.constants.ERROR_CORRECT_M,
        'Q': qrcode.constants.ERROR_CORRECT_Q,
        'H': qrcode.constants.ERROR_CORRECT_H
    }
    
    # Default to H if no selection found
    error_level = qrcode.constants.ERROR_CORRECT_H
    
    # Find which radio button is checked
    for level in ['L', 'M', 'Q', 'H']:
        radio_element = document.querySelector(f"#ec-{level.lower()}")
        if radio_element and radio_element.checked:
            error_level = error_level_map[level]
            console.log(level)
            console.log(error_level_map[level])
            break
    console.log(error_level)
    return error_level

def generate_qr_with_content(content, signature=None):
    opacity_slider = document.querySelector("#watermark-opacity")
    opacity = float(opacity_slider.value) if opacity_slider else 0.3
    error_correct = get_error_correction_level()

    steg_method = 'lsb'

    try:
        # Generate basic QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=error_correct,
            box_size=10,
            border=4,
        )
        qr.add_data(content)
        qr.make(fit=True)
        qr_image = qr.make_image(fill_color="black", back_color="white").convert('RGB')

        # Check for watermark upload
        watermark_input = document.querySelector("#watermark-input")
        if watermark_input and watermark_input.files.length > 0:
            file = watermark_input.files.item(0)
            if file.type.startswith("image/"):
                reader = FileReader.new()
                reader.readAsDataURL(file)

                def on_load(event):
                    base64_data = reader.result
                    final_qr = apply_optional_watermark_and_badge(qr_image, base64_data, opacity)
                    complete_qr_generation(final_qr, signature, steg_method)

                reader.onload = on_load
                return
            else:
                document.querySelector("#status-message").textContent = "Error: Invalid watermark file type"

        # No watermark uploaded
        final_qr = apply_optional_watermark_and_badge(qr_image, None, opacity)
        complete_qr_generation(final_qr, signature, steg_method)

    except Exception as e:
        console.log(f"Error generating QR code: {e}")
        document.querySelector("#status-message").textContent = f"Error: {str(e)}"


def complete_qr_generation(qr_image, signature, steg_method):
    """Complete the QR generation process after watermarking stage"""
    use_steganography = document.querySelector("#use-steganography").checked

    try:
        # Encode the signature in the image if it exists
        if signature and use_steganography:
            final_image = encode_signature_in_image(qr_image, signature, method=steg_method)
            # Create and show signature download link
            create_signature_download(signature)
        elif signature and not use_steganography:
            final_image = qr_image
            create_signature_download(signature)
        else:
            final_image = qr_image
            # Hide signature download link if no signature
            document.querySelector("#signature-download-container").style.display = "none"
        
        # Convert to PNG format
        output = io.BytesIO()
        final_image.save(output, format="PNG")
        
        # Create File object and display
        bytes_data = output.getvalue()
        blob = Uint8Array.new(bytes_data)
        image_file = File.new([blob], "qr_code.png", {"type": "image/png"})
        
        # Update the image source
        img = document.querySelector("#qr_image")
        img.src = URL.createObjectURL(image_file)
        
        # Update status message
        status_msg = document.querySelector("#status-message")
        if status_msg:
            status_message = "QR Code Generated"
            if signature and document.querySelector("#watermark-input") and document.querySelector("#watermark-input").files.length > 0:
                status_message += " with Digital Signature and Watermark"
            elif signature:
                status_message += " with Digital Signature"
            elif document.querySelector("#watermark-input") and document.querySelector("#watermark-input").files.length > 0:
                status_message += " with Watermark"
            status_msg.textContent = status_message

        # Show download button for generated QR
        document.querySelector("#download-qr-btn").style.display = "inline-block"
        
        console.log("QR code generated successfully")
    except Exception as e:
        console.log(f"Error finalizing QR generation: {e}")
        document.querySelector("#status-message").textContent = f"Error in QR generation: {str(e)}" 

def apply_optional_watermark_and_badge(qr_image, base64_watermark_data=None, opacity=0.3):
    try:
        qr_size = qr_image.size
        composed_image = Image.new("RGBA", qr_size, (255, 255, 255, 255))  # white bg

        # Add watermark if watermark logo is uploaded
        if base64_watermark_data:
            composed_image = add_watermark(qr_image, base64_watermark_data, opacity)
        else:
            composed_image = Image.new("RGBA", qr_size, (255, 255, 255, 255))

        # Add signed badge if key is uploaded
        private_key_input = document.querySelector("#private-key-input")
        key_type = private_key_input.getAttribute("data-key-type")
        if key_type:
            composed_image = add_signed_badge(composed_image)

        # Add black QR pixels from original QR
        qr_bw = qr_image.convert("L")
        qr_mask = qr_bw.point(lambda p: 255 if p < 128 else 0).convert("1")
        black_layer = Image.new("RGBA", qr_size, (0, 0, 0, 255))
        composed_image.paste(black_layer, mask=qr_mask)

        return composed_image.convert("RGB")

    except Exception as e:
        console.log(f"Error in watermark/badge processing: {e}")
        return qr_image


def add_watermark(qr_image, base64_data, opacity=0.3):
    try:
        if not base64_data:
            return qr_image

        if "," in base64_data:
            base64_data = base64_data.split(",")[1]
        watermark_bytes = base64.b64decode(base64_data)
        watermark = Image.open(io.BytesIO(watermark_bytes)).convert("RGBA")

        # Resize watermark proportionally to fit QR image
        qr_size = qr_image.size
        watermark_aspect = watermark.width / watermark.height
        qr_aspect = qr_size[0] / qr_size[1]

        if watermark_aspect > qr_aspect:
            new_width = qr_size[0]
            new_height = int(new_width / watermark_aspect)
        else:
            new_height = qr_size[1]
            new_width = int(new_height * watermark_aspect)

        watermark = watermark.resize((new_width, new_height), Image.LANCZOS)
        watermark_mask = watermark.getchannel("A").point(lambda p: int(p * opacity))

        # Step 1: White background
        base = Image.new("RGBA", qr_size, (255, 255, 255, 255))

        # Step 2: Paste watermark in the center
        paste_x = (qr_size[0] - watermark.width) // 2
        paste_y = (qr_size[1] - watermark.height) // 2
        base.paste(watermark, (paste_x, paste_y), watermark_mask)

        # Step 3: Return partially composed image (badge will be added later)
        return base

    except Exception as e:
        console.log(f"Error applying watermark: {e}")
        document.querySelector("#status-message").textContent = f"Error applying watermark: {str(e)}"
        return qr_image

def add_signed_badge(image):
    try:
        signed_img_bytes = base64.b64decode(SIGNED_BADGE_BASE64)
        signed_img = Image.open(io.BytesIO(signed_img_bytes)).convert("RGBA")

        # Resize
        qr_width, qr_height = image.size
        badge_size = int(min(qr_width, qr_height) * 0.33)
        signed_img = signed_img.resize((badge_size, badge_size), Image.LANCZOS)

        # Opacity
        opacity = 0.66
        signed_mask = signed_img.getchannel("A").point(lambda p: int(p * opacity))

        # Paste at bottom-right
        position = (qr_width - badge_size - 5, qr_height - badge_size - 5)
        image.paste(signed_img, position, signed_mask)

        return image

    except Exception as e:
        console.log(f"Error adding signed badge: {e}")
        return image
