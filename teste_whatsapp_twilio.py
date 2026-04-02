import os
from twilio.rest import Client
from dotenv import load_dotenv

# Carrega as variáveis do seu arquivo .env
load_dotenv()

def enviar_whatsapp_escola():
    # Configurações obtidas do .env
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    from_whatsapp = os.getenv('TWILIO_WHATSAPP_NUMBER') # Ex: whatsapp:+14155238886
    
    # Configurações do Destinatário (Para o teste)
    # Certifique-se de que o número tenha +55 (Brasil) e o DDD
    celular_destino = "whatsapp:+55319XXXXXXXX" 
    nome_escola = "CAIXA ESCOLAR PADRE AFONSO DE LEMOS"

    client = Client(account_sid, auth_token)

    # Corpo da mensagem (Réplica do formato de e-mail)
    corpo_mensagem = (
        f"🔔 *NOTIFICAÇÃO DE SISTEMA*\n\n"
        f"Prezados, *{nome_escola}*.\n\n"
        "Informamos que o processo realizado via e-mail foi concluído com sucesso "
        "e agora está disponível via WhatsApp.\n\n"
        "Este é um envio automático de teste. Não é necessário responder."
    )

    try:
        message = client.messages.create(
            from_=from_whatsapp,
            body=corpo_mensagem,
            to=celular_destino
        )
        print(f"✅ Sucesso! Mensagem enviada para {nome_escola}")
        print(f"ID da mensagem: {message.sid}")
    except Exception as e:
        print(f"❌ Erro ao enviar: {e}")

if __name__ == "__main__":
    # Garante que o teste só rode se você executar este arquivo específico
    enviar_whatsapp_escola()