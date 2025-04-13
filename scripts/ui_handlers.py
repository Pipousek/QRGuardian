from js import document, console, URL, FileReader, Uint8Array

def update_status_message(message, element_id="#status-message"):
    """Update status message on the UI."""
    document.querySelector(element_id).textContent = message

def process_image_file(file_input_selector, image_selector, message_selector, default_message=""):
    """Handle file upload for QR code images and update UI elements."""
    file_input = document.querySelector(file_input_selector)
    if file_input.files.length == 0:
        # Clear the image display
        img = document.querySelector(image_selector)
        img.src = ""
        if message_selector:
            document.querySelector(message_selector).textContent = default_message
        return None
        
    file = file_input.files.item(0)
    
    # Update the image display
    img = document.querySelector(image_selector)
    img.src = URL.createObjectURL(file)
    
    # Clear previous message if provided
    if message_selector:
        document.querySelector(message_selector).textContent = "Ready to decode. Click 'Decode QR Code'."
    
    return file

def load_key_file(key_file, callback):
    """Load a key file as array buffer and process it with the callback function."""
    reader = FileReader.new()
    reader.readAsArrayBuffer(key_file)
    
    def on_load(event):
        try:
            array_buffer = reader.result
            byte_array = Uint8Array.new(array_buffer)
            key_bytes = byte_array.to_py()
            callback(key_bytes)
        except Exception as e:
            console.log(f"Error processing key: {e}")
    
    reader.onload = on_load

def process_verification_result(steg_verified, file_verified, steg_signature, file_signature, result_messages):
    """Process verification results and update UI with appropriate message."""
    result_element = document.querySelector("#verification-result")
    
    if not steg_signature and not file_signature:
        result_element.textContent = "✗ No valid signatures found for verification."
        result_element.style.color = "#dc3545"  # Red
    elif steg_verified and file_verified:
        result_element.textContent = "✓ Both signatures verified successfully! Content is authentic."
        result_element.style.color = "#4CAF50"  # Green
    elif steg_verified:
        result_element.textContent = "✓ Steganography signature verified! Content is authentic."
        result_element.style.color = "#4CAF50"  # Green
    elif file_verified:
        result_element.textContent = "✓ File signature verified! Content is authentic."
        result_element.style.color = "#4CAF50"  # Green
    else:
        # Neither verified, show all error messages
        error_msg = "✗ Verification failed:\n" + "\n".join(result_messages)
        result_element.textContent = error_msg
        result_element.style.color = "#dc3545"  # Red