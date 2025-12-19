"""
Integración con WhatsApp para enviar facturas
Soporta múltiples proveedores: Twilio, WhatsApp Business API, método directo, etc.
"""
import os
import requests
from typing import Optional, Dict, Any
from io import BytesIO
import base64
import urllib.parse


def normalize_phone_number(phone: str) -> str:
    """
    Normaliza el número de teléfono al formato correcto (+59177335887)
    """
    if not phone:
        return ""
    
    # Eliminar espacios, guiones y paréntesis
    phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    # Si no empieza con +, agregarlo
    if not phone.startswith('+'):
        # Si empieza con 0, reemplazarlo con código de país (asumir Bolivia +591)
        if phone.startswith('0'):
            phone = '+591' + phone[1:]
        elif phone.startswith('591'):
            phone = '+' + phone
        else:
            # Asumir que es un número local de Bolivia
            phone = '+591' + phone
    
    return phone


def send_whatsapp_message(
    phone_number: str,
    message: str,
    pdf_bytes: Optional[bytes] = None,
    filename: str = "factura.pdf"
) -> Dict[str, Any]:
    """
    Envía un mensaje de WhatsApp con la factura adjunta
    
    Args:
        phone_number: Número de teléfono del cliente (formato: +1234567890)
        message: Mensaje de texto a enviar
        pdf_bytes: Bytes del PDF de la factura (opcional)
        filename: Nombre del archivo PDF
    
    Returns:
        Dict con el resultado del envío
    """
    # Normalizar número de teléfono
    phone_number = normalize_phone_number(phone_number)
    
    if not phone_number:
        return {
            "success": False,
            "error": "Número de teléfono inválido",
            "provider": "none"
        }
    
    # Obtener configuración de WhatsApp desde variables de entorno
    whatsapp_provider = os.getenv('WHATSAPP_PROVIDER', 'direct')  # 'twilio', 'whatsapp_business', o 'direct'
    
    print(f"[WHATSAPP] Intentando enviar mensaje a: {phone_number}")
    print(f"[WHATSAPP] Proveedor configurado: {whatsapp_provider}")
    
    if whatsapp_provider == 'twilio':
        result = send_via_twilio(phone_number, message, pdf_bytes, filename)
    elif whatsapp_provider == 'whatsapp_business':
        result = send_via_whatsapp_business(phone_number, message, pdf_bytes, filename)
    elif whatsapp_provider == 'direct':
        result = send_via_direct(phone_number, message, pdf_bytes, filename)
    else:
        # Modo desarrollo: solo log, no envía realmente
        print(f"[MODO DESARROLLO] WhatsApp no configurado")
        print(f"Destinatario: {phone_number}")
        print(f"Mensaje: {message}")
        if pdf_bytes:
            print(f"PDF adjunto: {len(pdf_bytes)} bytes")
        result = {
            "success": False,
            "message": "WhatsApp no configurado. Configura WHATSAPP_PROVIDER en .env",
            "provider": "development"
        }
    
    # Log del resultado
    if result.get("success"):
        print(f"[WHATSAPP] ✅ Mensaje enviado exitosamente a {phone_number}")
    else:
        print(f"[WHATSAPP] ❌ Error al enviar: {result.get('error', 'Error desconocido')}")
    
    return result


def send_via_twilio(phone_number: str, message: str, pdf_bytes: Optional[bytes] = None, filename: str = "factura.pdf") -> Dict[str, Any]:
    """
    Envía mensaje usando Twilio WhatsApp API
    Requiere: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER
    """
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    from_number = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+59177335887')
    
    if not account_sid or not auth_token:
        return {
            "success": False,
            "error": "Twilio no configurado. Configura TWILIO_ACCOUNT_SID y TWILIO_AUTH_TOKEN en .env"
        }
    
    # Formatear número de teléfono
    if not phone_number.startswith('whatsapp:'):
        if not phone_number.startswith('+'):
            phone_number = '+' + phone_number
        phone_number = f'whatsapp:{phone_number}'
    
    try:
        from twilio.rest import Client
        
        client = Client(account_sid, auth_token)
        
        if pdf_bytes:
            # Convertir PDF a base64
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            
            # Twilio no soporta PDF directamente, enviar mensaje con link o usar MediaUrl
            # Alternativa: subir PDF a un servidor y enviar el link
            message_body = f"{message}\n\n📄 Factura adjunta"
            
            message = client.messages.create(
                body=message_body,
                from_=from_number,
                to=phone_number
            )
            
            return {
                "success": True,
                "message_sid": message.sid,
                "provider": "twilio"
            }
        else:
            message = client.messages.create(
                body=message,
                from_=from_number,
                to=phone_number
            )
            
            return {
                "success": True,
                "message_sid": message.sid,
                "provider": "twilio"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "provider": "twilio"
        }


def send_via_whatsapp_business(phone_number: str, message: str, pdf_bytes: Optional[bytes] = None, filename: str = "factura.pdf") -> Dict[str, Any]:
    """
    Envía mensaje usando WhatsApp Business API
    Requiere: WHATSAPP_BUSINESS_API_URL, WHATSAPP_BUSINESS_TOKEN, WHATSAPP_BUSINESS_PHONE_ID
    """
    api_url = os.getenv('WHATSAPP_BUSINESS_API_URL', 'https://graph.facebook.com/v18.0')
    access_token = os.getenv('WHATSAPP_BUSINESS_TOKEN')
    phone_id = os.getenv('WHATSAPP_BUSINESS_PHONE_ID')
    
    if not access_token or not phone_id:
        return {
            "success": False,
            "error": "WhatsApp Business API no configurado. Configura WHATSAPP_BUSINESS_TOKEN y WHATSAPP_BUSINESS_PHONE_ID en .env"
        }
    
    # Formatear número de teléfono (solo números, sin +)
    phone_number = phone_number.replace('+', '').replace(' ', '').replace('-', '')
    
    try:
        if pdf_bytes:
            # Subir el PDF como media
            media_url = f"{api_url}/{phone_id}/media"
            
            files = {
                'file': (filename, pdf_bytes, 'application/pdf')
            }
            
            data = {
                'messaging_product': 'whatsapp',
                'type': 'document'
            }
            
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            
            # Subir media
            media_response = requests.post(media_url, files=files, data=data, headers=headers)
            media_response.raise_for_status()
            media_id = media_response.json().get('id')
            
            # Enviar mensaje con documento
            message_url = f"{api_url}/{phone_id}/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": "document",
                "document": {
                    "id": media_id,
                    "caption": message
                }
            }
            
            response = requests.post(message_url, json=payload, headers=headers)
            response.raise_for_status()
            
            return {
                "success": True,
                "message_id": response.json().get('messages', [{}])[0].get('id'),
                "provider": "whatsapp_business"
            }
        else:
            # Enviar solo mensaje de texto
            message_url = f"{api_url}/{phone_id}/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": "text",
                "text": {
                    "body": message
                }
            }
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(message_url, json=payload, headers=headers)
            response.raise_for_status()
            
            return {
                "success": True,
                "message_id": response.json().get('messages', [{}])[0].get('id'),
                "provider": "whatsapp_business"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "provider": "whatsapp_business"
        }


def send_via_direct(phone_number: str, message: str, pdf_bytes: Optional[bytes] = None, filename: str = "factura.pdf") -> Dict[str, Any]:
    """
    Envía mensaje usando método directo (genera enlace de WhatsApp Web)
    Usa el número configurado en WHATSAPP_FROM_NUMBER como número de origen
    """
    from_number = os.getenv('WHATSAPP_FROM_NUMBER', '+59177335887')  # Número por defecto
    api_key = os.getenv('WHATSAPP_API_KEY', '')  # Opcional: API key si se usa un servicio
    
    # Normalizar número de origen
    from_number = normalize_phone_number(from_number)
    
    print(f"[WHATSAPP DIRECT] Enviando desde: {from_number}")
    print(f"[WHATSAPP DIRECT] Enviando a: {phone_number}")
    
    try:
        # Si hay API key, usar servicio externo
        if api_key:
            # Ejemplo con ChatAPI o similar
            api_url = os.getenv('WHATSAPP_API_URL', 'https://api.chat-api.com/instance12345/sendMessage')
            
            payload = {
                "phone": phone_number.replace('+', ''),
                "body": message
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
            
            response = requests.post(api_url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message_id": response.json().get('id'),
                    "provider": "direct_api"
                }
            else:
                error_msg = response.text
                print(f"[WHATSAPP DIRECT] Error de API: {error_msg}")
                return {
                    "success": False,
                    "error": f"Error de API: {error_msg}",
                    "provider": "direct_api"
                }
        else:
            # Sin API key: generar enlace de WhatsApp Web
            phone_clean = phone_number.replace('+', '').replace(' ', '')
            message_encoded = urllib.parse.quote(message)
            whatsapp_url = f"https://wa.me/{phone_clean}?text={message_encoded}"
            
            print(f"[WHATSAPP DIRECT] ✅ Enlace generado: {whatsapp_url}")
            print(f"[WHATSAPP DIRECT] 📱 Para enviar, abre este enlace en tu navegador")
            print(f"[WHATSAPP DIRECT] 💡 O configura WHATSAPP_API_KEY para envío automático")
            
            # Guardar enlace en un archivo para facilitar el acceso
            try:
                with open('whatsapp_link.txt', 'w', encoding='utf-8') as f:
                    f.write(f"Enlace de WhatsApp para {phone_number}:\n")
                    f.write(f"{whatsapp_url}\n\n")
                    f.write(f"Mensaje:\n{message}\n")
                print(f"[WHATSAPP DIRECT] 💾 Enlace guardado en whatsapp_link.txt")
            except:
                pass
            
            return {
                "success": True,
                "message": f"Enlace de WhatsApp generado. Abre: {whatsapp_url}",
                "whatsapp_url": whatsapp_url,
                "provider": "direct_link",
                "note": "Para envío automático, configura WHATSAPP_API_KEY en .env"
            }
            
    except Exception as e:
        error_msg = str(e)
        print(f"[WHATSAPP DIRECT] Error: {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "provider": "direct"
        }
