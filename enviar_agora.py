#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ENVIO DIRETO - EMAIL E WHATSAPP
Envia para contatos específicos sem perguntas
"""

import os
import re
import sys
import smtplib
import imaplib
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

# =========================================================================
# CONFIGURAÇÕES
# =========================================================================
EMAIL_USUARIO = os.getenv('EMAIL_USUARIO')
EMAIL_SENHA = os.getenv('EMAIL_SENHA')
EMAIL_SMTP = os.getenv('EMAIL_SMTP', 'smtp.hostinger.com')
EMAIL_PORTA = os.getenv('EMAIL_PORTA', '465')
EMAIL_IMAP = os.getenv('EMAIL_IMAP', 'imap.hostinger.com')
EMAIL_IMAP_PORTA = os.getenv('EMAIL_IMAP_PORTA', '993')

print("=" * 80)
print("📧🤖 ENVIO DIRETO - EMAIL E WHATSAPP")
print("=" * 80)
print()

# =========================================================================
# FUNÇÕES
# =========================================================================
def validar_email(email):
    if not email or not isinstance(email, str):
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validar_telefone(telefone):
    if not telefone or not isinstance(telefone, str):
        return False
    apenas_numeros = re.sub(r'\D', '', telefone)
    return len(apenas_numeros) >= 10


def salvar_email_imap(msg_str, email_usuario, email_senha):
    """Salva email na pasta Enviados"""
    try:
        imap = imaplib.IMAP4_SSL(EMAIL_IMAP, int(EMAIL_IMAP_PORTA))
        imap.login(email_usuario, email_senha)
        
        retcode, mailboxes = imap.list()
        pastas_disponiveis = [box.decode('utf-8') if isinstance(box, bytes) else box for box in mailboxes]
        
        pasta_usada = 'INBOX.Sent'
        for pasta in pastas_disponiveis:
            if 'Sent' in pasta or 'INBOX.Sent' in pasta:
                partes = pasta.split()
                if len(partes) > 0:
                    pasta_usada = partes[-1].strip('"')
                break
        
        imap.select(pasta_usada)
        imap.append(pasta_usada, '', imaplib.Time2Internaldate(time.time()), msg_str.encode('utf-8'))
        imap.close()
        imap.logout()
        return True, pasta_usada
    except Exception as e:
        return False, str(e)


def enviar_email(email_destino, assunto, html, nome_cliente, tipo=""):
    """Envia email"""
    print(f"\n{'─' * 80}")
    print(f"📧 Enviando para {tipo.upper()}: {email_destino}")
    print(f"{'─' * 80}")
    
    if not validar_email(email_destino):
        print(f"❌ Email inválido!")
        return False
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = assunto
        msg['From'] = EMAIL_USUARIO
        msg['To'] = email_destino
        msg['Reply-To'] = EMAIL_USUARIO
        msg['X-Mailer'] = 'Allcanci Rastreamento v1.0'
        
        msg.attach(MIMEText(f'Pedido teste\nStatus: teste', 'plain', 'utf-8'))
        msg.attach(MIMEText(html, 'html', 'utf-8'))
        
        print(f"📤 Conectando a {EMAIL_SMTP}:{EMAIL_PORTA}")
        server = smtplib.SMTP_SSL(EMAIL_SMTP, int(EMAIL_PORTA))
        server.login(EMAIL_USUARIO, EMAIL_SENHA)
        server.send_message(msg)
        server.quit()
        print(f"✅ Email enviado com sucesso!")
        
        print(f"📁 Salvando em Enviados (IMAP)...")
        sucesso, resultado = salvar_email_imap(msg.as_string(), EMAIL_USUARIO, EMAIL_SENHA)
        if sucesso:
            print(f"✅ Email salvo em: {resultado}")
        else:
            print(f"⚠️  Aviso ao salvar: {resultado}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


# =========================================================================
# DADOS DO ENVIO
# =========================================================================
email_destino = "rennifer10@gmail.com"
telefone = "31984163357"
numero_pedido = "TEST-001"
cliente_nome = "Teste Allcanci"
vendedor_nome = "Sistema Automático"
status = "Teste de Sistema"
rastreamento = "TEST123456789BR"

print(f"📋 DADOS DO ENVIO:")
print(f"   📧 Email: {email_destino}")
print(f"   📱 Telefone: {telefone}")
print(f"   📦 Pedido: {numero_pedido}")
print(f"   👤 Cliente: {cliente_nome}")
print(f"   📊 Status: {status}")
print()

# =========================================================================
# VALIDAÇÕES
# =========================================================================
print(f"✅ VALIDAÇÕES:")
print(f"   Email válido: {validar_email(email_destino)}")
print(f"   Telefone válido: {validar_telefone(telefone)}")
print()

if not validar_email(email_destino):
    print("❌ Email inválido!")
    sys.exit(1)

# =========================================================================
# 1. EMAIL PARA CLIENTE
# =========================================================================
print(f"\n{'=' * 80}")
print(f"1️⃣  ENVIANDO EMAIL COMO CLIENTE")
print(f"{'=' * 80}")

data_fmt = datetime.now().strftime('%d/%m/%Y %H:%M')
assunto_cliente = f'Pedido {numero_pedido} - {status}'

html_cliente = f'''<html>
<body style="font-family:Arial;background:#f5f5f5;padding:20px">
<div style="max-width:600px;margin:0 auto;background:white;border-radius:8px;padding:30px">
  <div style="background:linear-gradient(135deg,#0000F3 0%,#0051DB 100%);padding:30px;text-align:center;color:white;border-radius:6px;margin-bottom:30px">
    <h1 style="margin:0;font-size:26px">📦 Atualização de Rastreamento</h1>
  </div>
  <p style="font-size:16px;color:#333">Olá <strong>{cliente_nome}</strong>,</p>
  <p style="font-size:16px;color:#555;margin:15px 0">Seu pedido teve uma atualização importante:</p>
  <div style="background:#4CAF50;padding:25px;border-radius:6px;margin:20px 0;color:white;text-align:center;font-size:20px;font-weight:bold;line-height:1.6">
    ✅ {status.upper()}
  </div>
  <div style="background:#f9f9f9;padding:20px;border-radius:6px;margin:20px 0;border-left:4px solid #0066cc">
    <p style="margin:10px 0"><strong>📦 Pedido:</strong> {numero_pedido}</p>
    <p style="margin:10px 0"><strong>📍 Rastreamento:</strong> {rastreamento}</p>
    <p style="margin:10px 0"><strong>📅 Atualizado em:</strong> {data_fmt}</p>
    <p style="margin:10px 0"><strong>Descrição:</strong> {status}</p>
  </div>
  <div style="padding:15px;text-align:center;font-size:12px;color:#999;border-top:1px solid #e0e0e0">
    Email automático - Allcanci Rastreamento
  </div>
</div>
</body>
</html>'''

enviar_email(email_destino, assunto_cliente, html_cliente, cliente_nome, tipo="CLIENTE")
time.sleep(2)

# =========================================================================
# 2. EMAIL PARA VENDEDOR
# =========================================================================
print(f"\n{'=' * 80}")
print(f"2️⃣  ENVIANDO EMAIL COMO VENDEDOR")
print(f"{'=' * 80}")

assunto_vendedor = f'Pedido {numero_pedido} ({cliente_nome}) - {status}'

html_vendedor = f'''<html>
<body style="font-family:Arial;background:#f5f5f5;padding:20px">
<div style="max-width:600px;margin:0 auto;background:white;border-radius:8px;padding:30px">
  <div style="background:linear-gradient(135deg,#FF9C00 0%,#FF6B00 100%);padding:30px;text-align:center;color:white;border-radius:6px;margin-bottom:30px">
    <h1 style="margin:0;font-size:26px">🚀 Atualização de Pedido do Cliente</h1>
  </div>
  <p style="font-size:16px;color:#333">Olá <strong>{vendedor_nome}</strong>,</p>
  <p style="font-size:16px;color:#555;margin:15px 0">O pedido do cliente <strong>{cliente_nome}</strong> teve uma atualização importante:</p>
  <div style="background:#FF9C00;padding:25px;border-radius:6px;margin:20px 0;color:white;text-align:center;font-size:20px;font-weight:bold;line-height:1.6">
    ✅ {status.upper()}
  </div>
  <div style="background:#f9f9f9;padding:20px;border-radius:6px;margin:20px 0;border-left:4px solid #FF9C00">
    <p style="margin:10px 0"><strong>👤 Cliente:</strong> {cliente_nome}</p>
    <p style="margin:10px 0"><strong>📦 Pedido:</strong> {numero_pedido}</p>
    <p style="margin:10px 0"><strong>📍 Rastreamento:</strong> {rastreamento}</p>
    <p style="margin:10px 0"><strong>📅 Atualizado em:</strong> {data_fmt}</p>
    <p style="margin:10px 0"><strong>Descrição:</strong> {status}</p>
  </div>
  <div style="padding:15px;text-align:center;font-size:12px;color:#999;border-top:1px solid #e0e0e0">
    Email automático - Allcanci Rastreamento
  </div>
</div>
</body>
</html>'''

enviar_email(email_destino, assunto_vendedor, html_vendedor, vendedor_nome, tipo="VENDEDOR")
time.sleep(2)

# =========================================================================
# 3. WHATSAPP
# =========================================================================
print(f"\n{'=' * 80}")
print(f"3️⃣  MENSAGEM WHATSAPP")
print(f"{'=' * 80}")

mensagem_whatsapp = f"""
📦 *ATUALIZAÇÃO DE RASTREAMENTO*

Olá *{cliente_nome}*,

Seu pedido teve uma atualização importante:

✅ *{status.upper()}*

*Detalhes:*
🔹 Pedido: {numero_pedido}
🔹 Rastreamento: {rastreamento}
🔹 Atualizado em: {data_fmt}

🔗 Acompanhe: https://www.correios.com.br

_Allcanci Tecnologia_
""".strip()

print(f"\n📱 Telefone: {telefone}")
print(f"✅ Telefone válido: {validar_telefone(telefone)}")
print(f"\n💬 MENSAGEM:")
print(f"\n{mensagem_whatsapp}")

print(f"\n\n⚠️  NOTA IMPORTANTE:")
print(f"   WhatsApp requer integração com whatsapp_service.py")
print(f"   Para enviar, você precisa:")
print(f"   1. Configurar WhatsApp Business API")
print(f"   2. Verificar arquivo: whatsapp_service.py")

# =========================================================================
# RESUMO
# =========================================================================
print(f"\n\n{'=' * 80}")
print(f"✅ ENVIO COMPLETADO!")
print(f"{'=' * 80}")
print(f"\n📊 RESUMO:")
print(f"   ✅ Email CLIENTE enviado para: {email_destino}")
print(f"   ✅ Email VENDEDOR enviado para: {email_destino}")
print(f"   📱 Mensagem WhatsApp pronta para: {telefone}")
print(f"\n📋 PRÓXIMOS PASSOS:")
print(f"   1. Verifique seu email: {email_destino}")
print(f"   2. Confirme recebimento dos 2 emails")
print(f"   3. Verifique pasta 'Enviados'")
print(f"   4. Para ativar WhatsApp, configure whatsapp_service.py")
print(f"\n")
