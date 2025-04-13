# main.py - Main entry point for the QR code generator application

# System imports
from js import document
from pyscript import when

# Import modules from py folder
from event_handlers import (
    handle_private_key_upload,
    handle_public_key_upload,
    generate_qr,
    decode_qr,
    decode_external_qr,
    verify_qr_signature,
    handle_verify_sig_upload,
    handle_file_upload,
    handle_decode_file_upload,
    handle_verify_file_upload,
    preview_watermark
)

# Register event handlers
when('change', '#private-key-input')(handle_private_key_upload)
when('change', '#public-key-input')(handle_public_key_upload)
when('click', '#generate-btn')(generate_qr)
when('click', '#decode-btn')(decode_qr)
when('click', '#decode-external-btn')(decode_external_qr)
when('click', '#verify-signature-btn')(verify_qr_signature)
when('change', '#verify-sig-input')(handle_verify_sig_upload)
when('change', '#file-input')(handle_file_upload)
when('change', '#decode-file-input')(handle_decode_file_upload)
when('change', '#verify-file-input')(handle_verify_file_upload)
when('change', '#watermark-input')(preview_watermark)

# Initialize status messages
document.querySelector("#key-status").textContent = "No key loaded (supports ED25519 and RSA)"
document.querySelector("#verify-key-status").textContent = "No key loaded (supports ED25519 and RSA)"
document.querySelector("#status-message").textContent = "Ready to generate QR code"
document.querySelector("#decoded-message").textContent = "No QR code to decode"
document.querySelector("#decode-decoded-message").textContent = "No QR code to decode"
document.querySelector("#verification-result").textContent = "No QR code to verify"

# Disable verify button until public key is loaded
document.querySelector("#verify-signature-btn").disabled = True

# Hide signature download container initially
document.querySelector("#signature-download-container").style.display = "none"