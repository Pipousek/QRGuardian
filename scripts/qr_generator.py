from js import document, console, Uint8Array, window, File, URL, FileReader
import io
from PIL import Image
import qrcode
import base64
import json
from crypto import create_signature_download
from stego import encode_signature_in_image

def get_qr_content_by_mode():
    qr_mode = document.querySelector("#qr_mode").value
    
    if qr_mode == "website":
        return document.querySelector("#website_url").value
    
    elif qr_mode == "text":
        return document.querySelector("#text_content").value
    
    elif qr_mode == "email":
        email = document.querySelector("#email_address").value
        subject = document.querySelector("#email_subject").value
        body = document.querySelector("#email_body").value
        
        mailto = f"mailto:{email}"
        params = []
        
        if subject:
            params.append(f"subject={window.encodeURIComponent(subject)}")
        if body:
            params.append(f"body={window.encodeURIComponent(body)}")
        
        if params:
            mailto += "?" + "&".join(params)
        
        return mailto
    
    elif qr_mode == "wifi":
        ssid = document.querySelector("#wifi_ssid").value
        password = document.querySelector("#wifi_password").value
        encryption = document.querySelector("#wifi_encryption").value
        hidden = document.querySelector("#wifi_hidden").value
        
        wifi_string = f"WIFI:T:{encryption};S:{ssid};"
        if password:
            wifi_string += f"P:{password};"
        wifi_string += f"H:{hidden};;"
        
        return wifi_string
    
    elif qr_mode == "location":
        latitude = document.querySelector("#location_latitude").value
        longitude = document.querySelector("#location_longitude").value
        
        return f"geo:{latitude},{longitude}"
    
    elif qr_mode == "bitcoin":
        address = document.querySelector("#bitcoin_address").value
        amount = document.querySelector("#bitcoin_amount").value
        label = document.querySelector("#bitcoin_label").value
        message = document.querySelector("#bitcoin_message").value
        
        bitcoin_string = f"bitcoin:{address}"
        params = []
        
        if amount:
            params.append(f"amount={amount}")
        if label:
            params.append(f"label={window.encodeURIComponent(label)}")
        if message:
            params.append(f"message={window.encodeURIComponent(message)}")
        
        if params:
            bitcoin_string += "?" + "&".join(params)
        
        return bitcoin_string
    
    elif qr_mode == "sms":
        number = document.querySelector("#sms_number").value
        message = document.querySelector("#sms_message").value
        
        sms_string = f"smsto:{number}"
        if message:
            sms_string += f":{window.encodeURIComponent(message)}"
        
        return sms_string
    
    elif qr_mode == "phone":
        number = document.querySelector("#phone_number").value
        return f"tel:{number}"
    
    elif qr_mode == "vcard":
        name = document.querySelector("#vcard_name").value
        work_phone = document.querySelector("#vcard_work_phone").value
        cell_phone = document.querySelector("#vcard_cell_phone").value
        fax_phone = document.querySelector("#vcard_fax").value
        email = document.querySelector("#vcard_email").value
        org = document.querySelector("#vcard_org").value
        title = document.querySelector("#vcard_title").value
        url = document.querySelector("#vcard_url").value
        address = document.querySelector("#vcard_address").value
        note = document.querySelector("#vcard_note").value
        
        # Parse name into first/last
        first_name, last_name = "", ""
        if name:
            name_parts = name.strip().split(" ")
            if len(name_parts) > 1:
                last_name = name_parts.pop()
                first_name = " ".join(name_parts)
            else:
                first_name = name
        
        vcard = ["BEGIN:VCARD", "VERSION:3.0"]
        
        if name:
            vcard.append(f"N:{last_name};{first_name}")
            vcard.append(f"FN:{name}")
        if org:
            vcard.append(f"ORG:{org}")
        if title:
            vcard.append(f"TITLE:{title}")
        if address:
            vcard.append(f"ADR:;;{address}")
        if work_phone:
            vcard.append(f"TEL;WORK;VOICE:{work_phone}")
        if cell_phone:
            vcard.append(f"TEL;CELL:{cell_phone}")
        if fax_phone:
            vcard.append(f"TEL;FAX:{fax_phone}")
        if email:
            vcard.append(f"EMAIL;WORK;INTERNET:{email}")
        if url:
            vcard.append(f"URL:{url}")
        if note:
            vcard.append(f"NOTE:{note}")
        vcard.append("END:VCARD")
        
        return "\n".join(vcard)
    
    elif qr_mode == "json":
        json_content = document.querySelector("#json_content").value
        try:
            # Validate JSON
            json.loads(json_content)
            return json_content
        except ValueError as e:
            document.querySelector("#status-message").textContent = f"Invalid JSON: {str(e)}"
            return ""
    
    return ""

def generate_qr_with_content(content, signature=None):
    # Get the selected steganography method
    use_steganography = document.querySelector("#use-steganography").checked
    steg_method = 'lsb' if use_steganography else None
    
    # Get opacity value
    opacity_slider = document.querySelector("#watermark-opacity")
    opacity = float(opacity_slider.value) if opacity_slider else 0.3

    # Use higher error correction for ECC method
    error_correction = qrcode.constants.ERROR_CORRECT_H
    if steg_method == 'ecc':
        error_correction = qrcode.constants.ERROR_CORRECT_H  # Higher error correction
    
    try:
        # Create QR code using qrcode library
        qr = qrcode.QRCode(
            version=1,
            error_correction=error_correction,
            box_size=10,
            border=4,
        )
        qr.add_data(content)
        qr.make(fit=True)
        
        # Generate the QR code image
        qr_image = qr.make_image(fill_color="black", back_color="white").convert('RGB')
        
        # Check if watermark is selected
        watermark_input = document.querySelector("#watermark-input")
        if watermark_input and watermark_input.files.length > 0:
            # Get the watermark file
            watermark_file = watermark_input.files.item(0)
            
            # Create a reader to read the file
            reader = FileReader.new()
            reader.readAsDataURL(watermark_file)
            
            # Define what to do when file is loaded
            def on_load(event):
                try:
                    # Get base64 data
                    base64_data = reader.result
                    
                    # Apply watermark
                    watermarked_qr = add_image_watermark(qr_image, base64_data, opacity)
                    
                    # Encode the signature in the image if it exists
                    if signature:
                        final_image = encode_signature_in_image(watermarked_qr, signature, method=steg_method)
                        # Create and show signature download link
                        create_signature_download(signature)
                    else:
                        final_image = watermarked_qr
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
                        status_message = "QR code generated"
                        if signature:
                            status_message += " with digital signature"
                        if watermark_input and watermark_input.files.length > 0:
                            status_message += " and watermark"
                        status_msg.textContent = status_message
                    
                    console.log("QR code generated successfully")
                except Exception as e:
                    console.log(f"Error in watermark processing: {e}")
                    document.querySelector("#status-message").textContent = f"Error: {str(e)}"
            
            # Assign the callback
            reader.onload = on_load
        else:
            # Just encode the signature without watermark if it exists
            if signature:
                final_image = encode_signature_in_image(qr_image, signature, method=steg_method)
                # Create and show signature download link
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
                status_message = "QR code generated"
                if signature:
                    status_message += " with digital signature"
                status_msg.textContent = status_message
            
            console.log("QR code generated")
    except Exception as e:
        console.log(f"Error generating QR code: {e}")
        document.querySelector("#status-message").textContent = f"Error: {str(e)}"

def add_image_watermark(qr_image, base64_data, opacity=0.3):
    try:
        # Extract the actual base64 content (remove the data:image/xxx;base64, part)
        if "," in base64_data:
            base64_data = base64_data.split(",")[1]
        
        # Convert base64 to bytes and open as image
        watermark_bytes = base64.b64decode(base64_data)
        watermark = Image.open(io.BytesIO(watermark_bytes))

        # Convert to grayscale for watermark effect
        watermark = watermark.convert("L")
        
        # Resize watermark to match QR code size
        watermark = watermark.resize(qr_image.size)
        
        # Set watermark transparency
        watermark = watermark.point(lambda p: int(p * opacity))
        
        # Create transparent image for watermark
        watermark_rgba = watermark.convert("RGBA")
        watermark_rgba.putalpha(watermark)
        
        # Insert watermark into QR code
        qr_with_watermark = qr_image.convert("RGBA")
        qr_with_watermark.paste(watermark_rgba, (0, 0), watermark_rgba)
        
        return qr_with_watermark.convert("RGB")
    except Exception as e:
        console.log(f"Error applying watermark: {e}")
        document.querySelector("#status-message").textContent = f"Error applying watermark: {str(e)}"
        return qr_image