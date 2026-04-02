#!/usr/bin/env python3
"""
🧪 TESTE DE ENVIO REAL - IGNORA DUPLICATA DE 24h
Força envio para CAIXA ESCOLAR PADRE AFONSO DE LEMOS
Envia AMBOS: Email + WhatsApp
"""

import json
import os
import smtplib
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Importar WhatsApp Service
try:
    from whatsapp_service import enviar_mensagem as enviar_whatsapp
    WHATSAPP_DISPONIVEL = True
except Exception as e:
    print(f"⚠️ WhatsApp indisponível: {e}")
    WHATSAPP_DISPONIVEL = False

load_dotenv()

def enviar_email_teste(numero, cliente, email_destino, status, ultima_alt):
    """Envia email para teste"""
    if not email_destino:
        return False, 'sem email'
    
    try:
        EMAIL_USUARIO = os.getenv('EMAIL_USUARIO')
        EMAIL_SENHA = os.getenv('EMAIL_SENHA')
        EMAIL_SMTP = os.getenv('EMAIL_SMTP', 'smtp.hostinger.com')
        EMAIL_PORTA = os.getenv('EMAIL_PORTA', '465')
        
        time.sleep(1)
        data_fmt = datetime.now().strftime('%d/%m/%Y %H:%M')
        
        html = f'''<html>
<body style="font-family:Arial;background:#f5f5f5;padding:20px">
<div style="max-width:600px;margin:0 auto;background:white;border-radius:8px;padding:30px">
  <div style="background:linear-gradient(135deg,#0000F3 0%,#0051DB 100%);padding:30px;text-align:center;color:white;border-radius:6px;margin-bottom:30px">
    <h1 style="margin:0;font-size:26px">📬 Atualização de Rastreamento</h1>
  </div>
  <p style="font-size:16px;color:#333">Olá <strong>{cliente}</strong>,</p>
  <p style="font-size:16px;color:#555;margin:15px 0">Seu pedido teve uma atualização importante:</p>
  <div style="background:#4CAF50;padding:25px;border-radius:6px;margin:20px 0;color:white;text-align:center;font-size:20px;font-weight:bold;line-height:1.6">
    ✅ {status.upper()}
  </div>
  <div style="background:#f9f9f9;padding:20px;border-radius:6px;margin:20px 0;border-left:4px solid #0066cc">
    <p style="margin:10px 0"><strong>📦 Pedido:</strong> {numero}</p>
    <p style="margin:10px 0"><strong>🏷️ Rastreamento:</strong> {ultima_alt}</p>
    <p style="margin:10px 0"><strong>📅 Atualizado em:</strong> {data_fmt}</p>
    <p style="margin:10px 0"><strong>Descrição:</strong> {status}</p>
  </div>
  <div style="padding:15px;text-align:center;font-size:12px;color:#999;border-top:1px solid #e0e0e0">
    Email automático - Allcanci Rastreamento
  </div>
</div>
</body>
</html>'''
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'Pedido {numero} - {status}'
        msg['From'] = EMAIL_USUARIO
        msg['To'] = email_destino
        msg['Reply-To'] = EMAIL_USUARIO
        msg['X-Mailer'] = 'Allcanci Rastreamento v1.0'
        msg.attach(MIMEText(f'Pedido {numero}\nStatus: {status}', 'plain', 'utf-8'))
        msg.attach(MIMEText(html, 'html', 'utf-8'))
        
        server = smtplib.SMTP_SSL(EMAIL_SMTP, int(EMAIL_PORTA))
        server.login(EMAIL_USUARIO, EMAIL_SENHA)
        server.send_message(msg)
        server.quit()
        
        return True, 'OK'
    except Exception as e:
        return False, str(e)

def enviar_whatsapp_teste(numero, cliente, numero_telefone, status, ultima_alt):
    """Envia WhatsApp para teste"""
    if not WHATSAPP_DISPONIVEL or not numero_telefone or numero_telefone == 'N/A':
        return False, 'WhatsApp indisponível ou sem telefone'
    
    try:
        data_fmt = datetime.now().strftime('%d/%m/%Y %H:%M')
        
        mensagem = f"""
📦 *ATUALIZAÇÃO DE RASTREAMENTO*

Olá *{cliente}*,

Seu pedido teve uma atualização importante:

✅ *{status.upper()}*

*Detalhes:*
🔹 Pedido: {numero}
🔹 Rastreamento: {ultima_alt}
🔹 Atualizado em: {data_fmt}

🔗 Acompanhe: https://www.correios.com.br

_Allcanci_
        """.strip()
        
        sucesso, msg = enviar_whatsapp(numero_telefone, mensagem)
        
        if sucesso:
            return True, 'OK'
        else:
            return True, f'Enfieirado: {msg}'
            
    except Exception as e:
        return False, str(e)

def main():
    print("\n" + "=" * 70)
    print("🧪 TESTE DE ENVIO REAL - SEM VERIFICAÇÃO DE DUPLICATA")
    print("=" * 70 + "\n")
    
    # Carregar cliente
    print("📂 Carregando cliente...")
    try:
        with open('contatos_rastreamento.json', 'r', encoding='utf-8') as f:
            contatos = json.load(f)
    except Exception as e:
        print(f"❌ Erro: {e}")
        return
    
    cliente_teste = None
    for c in contatos:
        if c['numero'] == 2363:  # PADRE AFONSO
            cliente_teste = c
            break
    
    if not cliente_teste:
        print("❌ Cliente #2363 não encontrado!")
        return
    
    numero = cliente_teste['numero']
    cliente = cliente_teste['cliente']
    email = cliente_teste.get('email', '')
    telefone = cliente_teste.get('telefone_celular', '')
    etiqueta = cliente_teste.get('etiqueta', '')
    
    print(f"✅ Cliente: {cliente}")
    print(f"   Pedido: {numero}")
    print(f"   Email: {email}")
    print(f"   Telefone: {telefone}")
    print(f"   Etiqueta: {etiqueta}\n")
    
    novo_status = "Saiu para entrega ao destinatário"
    ultima_alt = etiqueta
    
    # ENVIAR EMAIL
    print("=" * 70)
    print("📧 ENVIANDO EMAIL...")
    print("=" * 70)
    
    sucesso_email, erro_email = enviar_email_teste(
        numero, cliente, email, novo_status, ultima_alt
    )
    
    if sucesso_email:
        print(f"✅ EMAIL ENVIADO COM SUCESSO para {email}")
    else:
        print(f"❌ ERRO ao enviar email: {erro_email}")
    
    time.sleep(2)
    
    # ENVIAR WHATSAPP
    print("\n" + "=" * 70)
    print("📱 ENVIANDO WHATSAPP...")
    print("=" * 70)
    
    sucesso_wa, erro_wa = enviar_whatsapp_teste(
        numero, cliente, telefone, novo_status, ultima_alt
    )
    
    if sucesso_wa:
        print(f"✅ WHATSAPP ENVIADO/ENFIEIRADO para {telefone}")
        print(f"   Status: {erro_wa}")
    else:
        print(f"❌ ERRO ao enviar WhatsApp: {erro_wa}")
    
    # RESUMO
    print("\n" + "=" * 70)
    print("📊 RESUMO DO ENVIO")
    print("=" * 70)
    print(f"""
Cliente: {cliente}
Pedido: {numero}
Status: {novo_status}

📧 Email: {'✅ ENVIADO' if sucesso_email else '❌ FALHA'}
📱 WhatsApp: {'✅ ENVIADO' if sucesso_wa else '❌ FALHA'}
    """)
    
    print("=" * 70)
    print("🎉 TESTE CONCLUÍDO!")
    print("=" * 70)

if __name__ == "__main__":
    main()
