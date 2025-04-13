<p align="center">
    <img src="img/QRGuardian-logo-wide.png">
</p>

# QRGuardian

A comprehensive web application for creating, securing, and verifying QR codes with advanced cryptographic protection and steganography capabilities.

## Features

- **QR Code Generation**: Create QR codes for various content types:
  - Web URLs
  - Plain text
  - vCards (contact information)
  - Email addresses
  - WiFi credentials
  - Geographic coordinates
  - Bitcoin addresses
  - SMS messages
  - Phone numbers
  - JSON data
- **Clean Security**:
  - Sign QR content with private keys (ED25519 or RSA)
  - Hide signatures using LSB steganography
  - Download signatures as .TXT files for external verification
- **Visual Customization**:
  - Apply watermarks to QR codes
  - Customize appearance with adjustable settings
- **Verification & Analysis**:
  - Verify QR codes using public key pairs (ED25519 or RSA)
  - Upload external signature files for verification
  - Decode hidden steganographic messages
- **Multilingual Support**:
  - English (EN)
  - Czech (CS)
  - Slovak (SK)
- **User-Friendly Interface**:
  - Drag & drop file uploads
  - Intuitive file browser integration
  - Real-time preview


## Companion Applications

For scenarios where you need to extract QR codes from images:

- **QRebuild**: Available as both GUI and CLI applications for:
  - Extracting QR codes from images
  - Generating clean, optimized versions
  - Processing in batch operations

> [!NOTE]
> QRebuild downloads are provided since GitHub Pages only supports static content and cannot run Python code server-side.
> More informations can be found at [QRebuild GitHub](https://github.com/Pipousek/QRebuild)

## Using QRGuardian
1. Select the content type for your QR code
1. Enter your data
1. Choose security options:
  1. Select cryptographic key type
  1. Generate or upload private key
  1. Enable steganographic hiding (optional)
1. Customize appearance and watermark
1. Download your secure QR code

## Verification Process
1. Upload a QR code image
1. Upload or enter public key
1. Upload signature file (if not hidden in QR code)
1. Verify authenticity

## Developer Information
QRGuardian is built as a client-side web application with no server dependencies, ensuring your cryptographic keys never leave your device.

## Licence

MIT Licence - Free for personal/commercial use