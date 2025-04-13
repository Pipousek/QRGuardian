from js import console
import numpy as np
from PIL import Image

def encode_signature_in_image(image, signature, method='lsb'):
    if not signature:
        return image
    
    try:
        return encode_lsb(image, signature)
    except Exception as e:
        console.log(f"Error in {method} encoding: {e}")
        return image

def decode_signature_from_image(image, method='lsb'):
    try:
        return decode_lsb(image)
    except Exception as e:
        console.log(f"Error in {method} decoding: {e}")
        return None

def encode_lsb(image, signature):
    if not signature:
        return image
        
    # Convert signature to hex string and add EOF marker
    signature_hex = signature.hex()
    binary_signature = ''.join(format(ord(char), '08b') for char in signature_hex)
    binary_signature += '1111111111111110'  # Add EOF marker

    # Convert image to RGB if not already
    image = image.convert("RGB")
    
    # Convert image to numpy array for efficient processing
    img_array = np.array(image)
    
    # Get dimensions for faster access
    height, width, channels = img_array.shape
    sig_len = len(binary_signature)

    # Store the signature in LSB of pixels
    sig_index = 0
    for i in range(height):
        if sig_index >= sig_len:
            break
        for j in range(width):
            if sig_index >= sig_len:
                break
            for k in range(channels):  # For each channel (R, G, B)
                if sig_index < sig_len:
                    # Change LSB more efficiently
                    img_array[i, j, k] = (img_array[i, j, k] & 0xFE) | int(binary_signature[sig_index])
                    sig_index += 1
                else:
                    break

    return Image.fromarray(img_array)

def decode_lsb(image):
    # Convert image to numpy array
    img_array = np.array(image)
    height, width, channels = img_array.shape
    
    # EOF marker
    EOF_MARKER = '1111111111111110'
    
    # Extract binary signature from LSB of pixels
    binary_signature = ''
    for i in range(height):
        for j in range(width):
            for k in range(channels):  # For each channel (R, G, B)
                binary_signature += str(img_array[i, j, k] & 1)
                
                # Check for EOF marker
                if len(binary_signature) >= len(EOF_MARKER) and binary_signature[-16:] == EOF_MARKER:
                    # Remove marker
                    binary_signature = binary_signature[:-16]
                    
                    # Convert binary signature to hex string
                    signature_hex = ''
                    for l in range(0, len(binary_signature), 8):
                        if l + 8 <= len(binary_signature):  # Ensure we have a full byte
                            byte = binary_signature[l:l+8]
                            signature_hex += chr(int(byte, 2))
                    
                    try:
                        return bytes.fromhex(signature_hex)
                    except ValueError:
                        return None
    
    return None