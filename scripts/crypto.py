from js import document, console, Uint8Array, window, File, URL
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding, ed25519

def detect_key_type(key_bytes):
    try:
        # Try loading as ED25519 private key
        key = serialization.load_ssh_private_key(key_bytes, password=None)
        if isinstance(key, ed25519.Ed25519PrivateKey):
            return 'ed25519'
    except:
        pass
    
    try:
        # Try loading as RSA private key
        key = serialization.load_ssh_private_key(key_bytes, password=None)
        if isinstance(key, rsa.RSAPrivateKey):
            return 'rsa'
    except:
        pass
    
    try:
        # Try loading as ED25519 public key
        key = serialization.load_ssh_public_key(key_bytes)
        if isinstance(key, ed25519.Ed25519PublicKey):  # ED25519 public key
            return 'ed25519'
    except:
        pass
    
    try:
        # Try loading as RSA public key
        key = serialization.load_ssh_public_key(key_bytes)
        if isinstance(key, rsa.RSAPublicKey):
            return 'rsa'
    except:
        pass
    
    return None

def load_and_parse_private_key(key_bytes):
    try:
        # Check if running in secure context
        if not window.isSecureContext:
            document.querySelector("#key-status").textContent = "Warning: Not running in secure context (HTTPS)"
        
        # Try to load with password if needed
        try:
            password = window.prompt("Enter key password (leave empty if none):")
            password_bytes = password.encode('utf-8') if password else None
            key = serialization.load_ssh_private_key(
                key_bytes,
                password=password_bytes,
            )
        except Exception:
            # Fallback to no password
            key = serialization.load_ssh_private_key(
                key_bytes,
                password=None,
            )
        
        # Determine key type
        if isinstance(key, ed25519.Ed25519PrivateKey):
            key_type = 'ed25519'
        elif isinstance(key, rsa.RSAPrivateKey):
            key_type = 'rsa'
        else:
            document.querySelector("#key-status").textContent = "Unsupported key type"
            return None, None
        
        document.querySelector("#key-status").textContent = f"{key_type.upper()} private key loaded successfully"
        
        return key, key_type
    except Exception as e:
        console.log(f"Error loading private key: {e}")
        document.querySelector("#key-status").textContent = f"Error loading private key: {str(e)}"
        return None, None

def load_and_parse_public_key(key_bytes):
    try:
        key = serialization.load_ssh_public_key(key_bytes)
        
        # Determine key type
        if isinstance(key, ed25519.Ed25519PublicKey):
            key_type = 'ed25519'
        elif isinstance(key, rsa.RSAPublicKey):
            key_type = 'rsa'
        else:
            document.querySelector("#verify-key-status").textContent = "Unsupported key type"
            return None, None
        
        document.querySelector("#verify-key-status").textContent = f"{key_type.upper()} public key loaded successfully"
        document.querySelector("#verify-signature-btn").disabled = False
        return key, key_type
    except Exception as e:
        console.log(f"Error loading public key: {e}")
        document.querySelector("#verify-key-status").textContent = f"Error loading public key: {str(e)}"
        return None, None

def sign_content(content, private_key, key_type):
    if not private_key:
        return None
   
    try:
        if key_type == 'ed25519':
            signature = private_key.sign(content.encode('utf-8'))
        elif key_type == 'rsa':
            # Compute hash first
            hash_algorithm = hashes.SHA256()
            hasher = hashes.Hash(hash_algorithm)
            hasher.update(content.encode('utf-8'))
            computed_hash = hasher.finalize()
            
            # Sign the hash
            signature = private_key.sign(
                computed_hash,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
        else:
            console.log(f"Unsupported key type for signing: {key_type}")
            return None
           
        return signature
    except Exception as e:
        console.log(f"Error signing content: {e}")
        document.querySelector("#key-status").textContent = f"Error signing content: {str(e)}"
        return None
    
def verify_signature(public_key, signature, content_bytes, key_type):
    """Verify a signature using the appropriate algorithm based on key type."""
    try:
        if key_type == 'ed25519':
            public_key.verify(signature, content_bytes)
            return True
        elif key_type == 'rsa':
            public_key.verify(
                signature,
                content_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
    except Exception:
        return False
    return False

def create_signature_download(signature):
    try:
        # Convert signature to hex string if it's bytes
        if isinstance(signature, bytes):
            signature_text = signature.hex()
        else:
            signature_text = str(signature)
        
        # Create a blob from the signature text
        signature_blob = Uint8Array.new(signature_text.encode('utf-8'))
        signature_file = File.new([signature_blob], "signature.txt", {"type": "text/plain"})
        
        # Create object URL for the signature file
        signature_url = URL.createObjectURL(signature_file)
        
        # Update the download link
        download_link = document.querySelector("#signature-download-link")
        download_link.href = signature_url
        download_link.setAttribute("download", "signature.txt")
        
        # Show the download container
        document.querySelector("#signature-download-container").style.display = "block"
        
        console.log("Plain text signature download created")
    except Exception as e:
        console.log(f"Error creating signature download: {e}")
        document.querySelector("#status-message").textContent = f"Error creating signature download: {str(e)}"