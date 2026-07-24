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
        print("-> Erro ao enviar mensagem no Telegram.")


def notificar_promocao(
    produto_nome: str, preco_atual: float, url_produto: str, motivos: list
) -> None:
    """Formata a mensagem de alerta inteligente combinando os motivos da queda e o link de afiliado."""
    motivos_str = "\n".join([f"• {m}" for m in motivos])

    mensagem = (
        f"🚨 <b>ALERTA DE OPORTUNIDADE: SKINCARE</b>\n\n"
        f"<b>{produto_nome}</b>\n\n"
        f"💰 <b>Preço Atual:</b> R$ {preco_atual:.2f}\n\n"
        f"<b>Por que vale a pena:</b>\n"
        f"{motivos_str}\n\n"
        f"🔗 <a href='{url_produto}'>Compre Aqui</a>"
    )

    enviar_mensagem_telegram(mensagem)
