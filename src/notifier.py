import os
import requests
from dotenv import load_dotenv

# Carrega as variáveis do ficheiro .env se ele existir localmente
load_dotenv()


def enviar_mensagem_telegram(mensagem: str) -> None:
    """Envia uma mensagem de texto via Telegram usando as variáveis de ambiente."""
    bot_token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        print("-> AVISO: Chaves do Telegram não configuradas. Notificação ignorada.")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": mensagem, "parse_mode": "HTML"}

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("-> Mensagem enviada com sucesso no Telegram!")
    except Exception:
        print(f"-> Erro ao enviar mensagem no Telegram.")
