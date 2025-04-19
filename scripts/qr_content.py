from js import document, window
import json

def get_val(id):
    el = document.querySelector(f"#{id}")
    return el.value if el else ""

def website():
    return get_val("website_url")

def text():
    return get_val("text_content")

def email():
    email = get_val("email_address")
    subject = get_val("email_subject")
    body = get_val("email_body")

    mailto = f"mailto:{email}"
    params = []
    if subject:
        params.append(f"subject={window.encodeURIComponent(subject)}")
    if body:
        params.append(f"body={window.encodeURIComponent(body)}")
    if params:
        mailto += "?" + "&".join(params)
    return mailto

def wifi():
    ssid = get_val("wifi_ssid")
    password = get_val("wifi_password")
    encryption = get_val("wifi_encryption")
    hidden = get_val("wifi_hidden")

    wifi_str = f"WIFI:T:{encryption};S:{ssid};"
    if password:
        wifi_str += f"P:{password};"
    wifi_str += f"H:{hidden};;"
    return wifi_str

def location():
    lat = get_val("location_latitude")
    lon = get_val("location_longitude")
    return f"geo:{lat},{lon}"

def bitcoin():
    address = get_val("bitcoin_address")
    amount = get_val("bitcoin_amount")
    label = get_val("bitcoin_label")
    message = get_val("bitcoin_message")

    bitcoin_str = f"bitcoin:{address}"
    params = []
    if amount:
        params.append(f"amount={amount}")
    if label:
        params.append(f"label={window.encodeURIComponent(label)}")
    if message:
        params.append(f"message={window.encodeURIComponent(message)}")
    if params:
        bitcoin_str += "?" + "&".join(params)
    return bitcoin_str

def sms():
    number = get_val("sms_number")
    message = get_val("sms_message")
    sms_str = f"smsto:{number}"
    if message:
        sms_str += f":{window.encodeURIComponent(message)}"
    return sms_str

def phone():
    return f"tel:{get_val('phone_number')}"

def vcard():
    name = get_val("vcard_name")
    work_phone = get_val("vcard_work_phone")
    cell_phone = get_val("vcard_cell_phone")
    fax_phone = get_val("vcard_fax")
    email = get_val("vcard_email")
    org = get_val("vcard_org")
    title = get_val("vcard_title")
    url = get_val("vcard_url")
    address = get_val("vcard_address")
    note = get_val("vcard_note")

    first_name, last_name = "", ""
    if name:
        parts = name.strip().split(" ")
        if len(parts) > 1:
            last_name = parts.pop()
            first_name = " ".join(parts)
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

def json_content():
    raw = get_val("json_content")
    try:
        json.loads(raw)
        return raw
    except Exception as e:
        document.querySelector("#status-message").textContent = f"Invalid JSON: {e}"
        return ""
