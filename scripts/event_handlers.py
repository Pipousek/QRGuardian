from js import document, console, Uint8Array, window, File, URL, FileReader, jsQR
from pyscript import when
import asyncio
import io
from PIL import Image
from qr_generator import get_qr_content_by_mode, generate_qr_with_content
from stego import decode_signature_from_image
from crypto import load_and_parse_private_key, load_and_parse_public_key, sign_content, verify_signature, detect_key_type
from ui_handlers import update_status_message, process_image_file, load_key_file, process_verification_result

def sign_and_generate_qr(content):
    private_key_input = document.querySelector("#private-key-input")
    key_file = private_key_input.files.item(0)
    
    reader = FileReader.new()
    reader.readAsArrayBuffer(key_file)
    
    def on_load(event):
        try:
            array_buffer = reader.result
            byte_array = Uint8Array.new(array_buffer)
            key_bytes = byte_array.to_py()
            
            # Load key temporarily
            temp_key, key_type = load_and_parse_private_key(key_bytes)
            if not temp_key:
                document.querySelector("#status-message").textContent = "Failed to load private key"
                return
            
            # Sign the content with the appropriate algorithm
            signature = sign_content(content, temp_key, key_type)
            
            # Clear the key immediately after use
            temp_key = None
            
            if signature:
                # Continue with QR generation using the signature
                generate_qr_with_content(content, signature)
            else:
                document.querySelector("#status-message").textContent = "Failed to sign content"
        except Exception as e:
            console.log(f"Error in signing process: {e}")
            document.querySelector("#status-message").textContent = f"Error: {str(e)}"
    
    reader.onload = on_load

# @when('change', '#private-key-input')
def handle_private_key_upload(event):
    private_key_input = document.querySelector("#private-key-input")
    if private_key_input.files.length == 0:
        private_key_input.removeAttribute("data-key-type")
        update_status_message("No key loaded (supports ED25519 and RSA)", "#key-status")
        return
        
    key_file = private_key_input.files.item(0)
    
    def process_key(key_bytes):
        # Check key type first
        key_type = detect_key_type(key_bytes)
        if not key_type:
            update_status_message("Unsupported key type (only ED25519 or RSA supported)", "#key-status")
            return
        
        # Load the key
        key, key_type = load_and_parse_private_key(key_bytes)
        if key:
            update_status_message(f"{key_type.upper()} private key loaded - will auto-sign QR codes", "#key-status")
            private_key_input.setAttribute("data-key-type", key_type)
        else:
            update_status_message("Failed to load private key", "#key-status")
    
    load_key_file(key_file, process_key)

# @when('change', '#public-key-input')
def handle_public_key_upload(event):
    public_key_input = document.querySelector("#public-key-input")
    if public_key_input.files.length == 0:
        # Clear any existing key data
        public_key_input.removeAttribute("data-key-type")
        public_key_input.removeAttribute("data-valid")
        update_status_message("No key loaded (supports ED25519 and RSA)", "#verify-key-status")
        document.querySelector("#verify-signature-btn").disabled = True
        return
        
    key_file = public_key_input.files.item(0)
    
    def process_key(key_bytes):
        # Check key type first
        key_type = detect_key_type(key_bytes)
        if not key_type:
            update_status_message("Unsupported key type (only ED25519 or RSA supported)", "#verify-key-status")
            document.querySelector("#verify-signature-btn").disabled = True
            return
        
        # Load the key
        key, key_type = load_and_parse_public_key(key_bytes)
        if key:
            public_key_input.setAttribute("data-valid", "true")
            public_key_input.setAttribute("data-key-type", key_type)
        else:
            public_key_input.setAttribute("data-valid", "false")
            document.querySelector("#verify-signature-btn").disabled = True
    
    load_key_file(key_file, process_key)

# @when('click', '#generate-btn')
def generate_qr():
    # Get content based on mode
    content = get_qr_content_by_mode()
    
    if not content:
        document.querySelector("#status-message").textContent = "Please enter content for the QR code"
        return
    
    # Check if private key is loaded
    private_key_input = document.querySelector("#private-key-input")
    if private_key_input.files.length > 0:
        # Key is loaded - sign the content
        sign_and_generate_qr(content)
    else:
        # No key - generate without signature
        generate_qr_with_content(content, None)

# @when('click', '#decode-btn')
def decode_qr():
    # Get the image element
    img_element = document.querySelector("#qr_image")
    
    if not img_element.src:
        document.querySelector("#decoded-message").textContent = "No QR code to decode."
        return
    
    # Process the image
    async def process_image():
        try:
            response = await window.fetch(img_element.src)
            array_buffer = await response.arrayBuffer()
            byte_array = Uint8Array.new(array_buffer)
            img = Image.open(io.BytesIO(byte_array.to_py()))
            
            # Decode the signature
            signature = decode_signature_from_image(img, method='lsb')
            
            if signature:
                document.querySelector("#decoded-message").textContent = f"Signature found: {signature.hex()}"
            else:
                document.querySelector("#decoded-message").textContent = "No digital signature found."
        except Exception as e:
            console.log(f"Error decoding image: {e}")
            document.querySelector("#decoded-message").textContent = f"Error: {str(e)}"
    
    asyncio.ensure_future(process_image())

#@when('click', '#decode-external-btn')
def decode_external_qr():
    # Get the image element
    img_element = document.querySelector("#decode-qr_image")
    
    if not img_element.src:
        document.querySelector("#decode-decoded-message").textContent = "No QR code to decode."
        return
    
    # Process the image
    async def process_image():
        try:
            response = await window.fetch(img_element.src)
            array_buffer = await response.arrayBuffer()
            byte_array = Uint8Array.new(array_buffer)
            img = Image.open(io.BytesIO(byte_array.to_py()))
            
            # Decode the signature
            signature = decode_signature_from_image(img, method='lsb')
            
            if signature:
                document.querySelector("#decode-decoded-message").textContent = f"Signature found: {signature.hex()}"
            else:
                document.querySelector("#decode-decoded-message").textContent = "No digital signature found."
        except Exception as e:
            console.log(f"Error decoding image: {e}")
            document.querySelector("#decode-decoded-message").textContent = f"Error: {str(e)}"
    
    asyncio.ensure_future(process_image())

# @when('click', '#verify-signature-btn')
def verify_qr_signature():
    # Get the image element
    img_element = document.querySelector("#verify-qr_image")
    
    # Check if we have a signature file
    sig_input = document.querySelector("#verify-sig-input")
    has_sig_file = sig_input.files.length > 0
    
    if not img_element.src and not has_sig_file:
        update_status_message("Please load a QR code or signature file.", "#verification-result")
        document.querySelector("#verification-result").style.color = "red"
        return
    
    # Check if public key is available
    public_key_input = document.querySelector("#public-key-input")
    if public_key_input.files.length == 0:
        update_status_message("Please load a public key first.", "#verification-result")
        document.querySelector("#verification-result").style.color = "red"
        return

    async def process_verification():
        try:
            # Load the public key first
            key_file = public_key_input.files.item(0)
            key_reader = FileReader.new()
            key_reader.readAsArrayBuffer(key_file)
            
            # Wait for key to load
            await asyncio.sleep(0.1)  # Small delay to ensure file is read
                
            key_bytes = Uint8Array.new(key_reader.result).to_py()
            public_key, key_type = load_and_parse_public_key(key_bytes)
            
            if not public_key or not key_type:
                update_status_message("Invalid public key.", "#verification-result")
                document.querySelector("#verification-result").style.color = "red"
                return

            # Get QR code content if we have an image
            qr_content = None
            if img_element.src:
                # Load QR code image
                response = await window.fetch(img_element.src)
                array_buffer = await response.arrayBuffer()
                byte_array = Uint8Array.new(array_buffer)
                img_data = byte_array.to_py()
                
                # Decode QR code content
                img = Image.open(io.BytesIO(img_data))
                
                canvas = document.createElement("canvas")
                context = canvas.getContext("2d")
                img_element_js = document.createElement("img")
                img_element_js.src = img_element.src
                
                await asyncio.sleep(0.1)  # Wait for image to load
                
                canvas.width = img_element_js.width
                canvas.height = img_element_js.height
                context.drawImage(img_element_js, 0, 0)
                
                imageData = context.getImageData(0, 0, canvas.width, canvas.height)
                code = jsQR(imageData.data, imageData.width, imageData.height)
                
                if not code:
                    update_status_message("Failed to decode QR code content.", "#verification-result")
                    document.querySelector("#verification-result").style.color = "red"
                    return
                
                qr_content = code.data

            if not qr_content:
                update_status_message("No QR content to verify.", "#verification-result")
                document.querySelector("#verification-result").style.color = "red"
                return

            # Convert content to bytes once
            content_bytes = qr_content.encode('utf-8')
            
            # Initialize verification results
            steg_verified = False
            file_verified = False
            steg_signature = None
            file_signature = None
            result_messages = []

            # Try to verify with steganography signature if available
            if img_element.src:
                steg_signature = decode_signature_from_image(img, method='lsb')
                if steg_signature:
                    steg_verified = verify_signature(public_key, steg_signature, content_bytes, key_type)
                    if not steg_verified:
                        result_messages.append("Steganography signature verification failed")

            # Try to verify with file signature if available
            if has_sig_file:
                sig_file = sig_input.files.item(0)
                sig_reader = FileReader.new()
                sig_reader.readAsText(sig_file)
                await asyncio.sleep(0.1)  # Wait for file to read
                signature_text = sig_reader.result

                try:
                    # Try to convert hex string back to bytes
                    file_signature = bytes.fromhex(signature_text)
                except:
                    # If not hex, try to use as-is
                    file_signature = signature_text.encode('utf-8')

                if file_signature:
                    file_verified = verify_signature(public_key, file_signature, content_bytes, key_type)
                    if not file_verified:
                        result_messages.append("File signature verification failed")

            # Display verification results
            process_verification_result(steg_verified, file_verified, steg_signature, file_signature, result_messages)

        except Exception as e:
            console.log(f"Verification error: {str(e)}")
            update_status_message(f"Error: {str(e)}", "#verification-result")
            document.querySelector("#verification-result").style.color = "red"

    asyncio.ensure_future(process_verification())

# @when('change', '#verify-sig-input')
def handle_verify_sig_upload(event):
    file_input = document.querySelector("#verify-sig-input")
    if file_input.files.length == 0:
        return
        
    # Just indicate we have a signature file, we'll process it during verification
    document.querySelector("#verification-result").textContent = "Signature file loaded. Ready to verify."

# @when('change', '#file-input')
def handle_file_upload(event):
    process_image_file("#file-input", "#qr_image", "#decoded-message", "No QR code to decode.")

# @when('change', '#decode-file-input')
def handle_decode_file_upload(event):
    process_image_file("#decode-file-input", "#decode-qr_image", "#decode-decoded-message", "No QR code to decode.")

# @when('change', '#verify-file-input')
def handle_verify_file_upload(event):
    file_input = document.querySelector("#verify-file-input")
    if file_input.files.length == 0:
        # Clear the image display
        img = document.querySelector("#verify-qr_image")
        img.src = ""
        document.querySelector("#verification-result").textContent = "No QR code to verify."
        return
        
    file = file_input.files.item(0)
    
    # Update the image display
    img = document.querySelector("#verify-qr_image")
    img.src = URL.createObjectURL(file)
    
    # Clear previous message
    document.querySelector("#verification-result").textContent = "Ready to verify. Click 'Verify Signature'."

# Preview watermark when selected
# @when('change', '#watermark-input')
def preview_watermark(event):
    watermark_input = document.querySelector("#watermark-input")
    controls = document.querySelector("#watermark-controls")
    preview = document.querySelector("#watermark-preview")
    
    if watermark_input.files.length == 0:
        # Clear the preview if file is removed
        if preview:
            preview.onerror = None
            preview.src = ""
            preview.style.display = "none"
        
        if controls:
            controls.style.display = "none"
        return
    
    watermark_file = watermark_input.files.item(0)
    
    # Validate file type
    file_type = watermark_file.type
    if not file_type.startswith('image/'):
        document.querySelector("#status-message").textContent = "Error: Please upload an image file"
        return
    
    # Show controls and update the preview image
    if controls:
        controls.style.display = "block"
    
    if preview:
        # Create object URL for the preview
        preview_url = URL.createObjectURL(watermark_file)
        
        # Add error handler for the image
        def handle_image_error(e):
            console.log("Error loading preview image")
            preview.src = ""
            document.querySelector("#status-message").textContent = "Error: Unable to load image"
        
        preview.onerror = handle_image_error
        preview.src = preview_url
        preview.style.display = "block"