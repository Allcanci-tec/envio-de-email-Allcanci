#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRIPT DE TESTE - ENVIO DE EMAIL E WHATSAPP
Demonstra os designs e envia notificações para:
1. Cliente/Escola
2. Vendedor  
3. WhatsApp
"""

import os
import re
import sys
import json
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

# =========================================================================
# FUNÇÕES AUXILIARES
# =========================================================================
def validar_email(email):
    """Valida se é um email com formato correto"""
    if not email or not isinstance(email, str):
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validar_telefone(telefone):
    """Valida se é um telefone com formato correto"""
    if not telefone or not isinstance(telefone, str):
        return False
    apenas_numeros = re.sub(r'\D', '', telefone)
    return len(apenas_numeros) >= 10


def salvar_email_imap(msg_str, email_usuario, email_senha):
    """Salva email na pasta Enviados usando IMAP"""
    try:
        imap = imaplib.IMAP4_SSL(EMAIL_IMAP, int(EMAIL_IMAP_PORTA))
        imap.login(email_usuario, email_senha)
        
        # Listar pastas
        retcode, mailboxes = imap.list()
        pastas_disponiveis = [box.decode('utf-8') if isinstance(box, bytes) else box for box in mailboxes]
        
        # Encontrar pasta Enviados
        pasta_usada = 'INBOX.Sent'
        for pasta in pastas_disponiveis:
            if 'Sent' in pasta or 'INBOX.Sent' in pasta:
                partes = pasta.split()
                if len(partes) > 0:
                    pasta_usada = partes[-1].strip('"')
                break
        
        # Selecionar e salvar
        imap.select(pasta_usada)
        imap.append(pasta_usada, '', imaplib.Time2Internaldate(time.time()), msg_str.encode('utf-8'))
        imap.close()
        imap.logout()
        return True, pasta_usada
    except Exception as e:
        return False, str(e)


# =========================================================================
# DESIGNS DE EMAIL
# =========================================================================
def gerar_email_cliente(numero, cliente, status, ultima_alt):
    """Gera HTML do email para o cliente/escola"""
    data_fmt = datetime.now().strftime('%d/%m/%Y %H:%M')
    assunto = f'Pedido {numero} - {status}'
    
    html = f'''<html>
<body style="font-family:Arial;background:#f5f5f5;padding:20px">
<div style="max-width:600px;margin:0 auto;background:white;border-radius:8px;padding:30px">
  <div style="background:linear-gradient(135deg,#0000F3 0%,#0051DB 100%);padding:30px;text-align:center;color:white;border-radius:6px;margin-bottom:30px">
    <h1 style="margin:0;font-size:26px">📦 Atualização de Rastreamento</h1>
  </div>
  <p style="font-size:16px;color:#333">Olá <strong>{cliente}</strong>,</p>
  <p style="font-size:16px;color:#555;margin:15px 0">Seu pedido teve uma atualização importante:</p>
  <div style="background:#4CAF50;padding:25px;border-radius:6px;margin:20px 0;color:white;text-align:center;font-size:20px;font-weight:bold;line-height:1.6">
    ✅ {status.upper()}
  </div>
  <div style="background:#f9f9f9;padding:20px;border-radius:6px;margin:20px 0;border-left:4px solid #0066cc">
    <p style="margin:10px 0"><strong>📦 Pedido:</strong> {numero}</p>
    <p style="margin:10px 0"><strong>📍 Rastreamento:</strong> {ultima_alt}</p>
    <p style="margin:10px 0"><strong>📅 Atualizado em:</strong> {data_fmt}</p>
    <p style="margin:10px 0"><strong>Descrição:</strong> {status}</p>
  </div>
  <div style="padding:15px;text-align:center;font-size:12px;color:#999;border-top:1px solid #e0e0e0">
    Email automático - Allcanci Rastreamento
  </div>
</div>
</body>
</html>'''
    
    return assunto, html


def gerar_email_vendedor(numero, cliente, status, ultima_alt, vendedor_nome):
    """Gera HTML do email para o vendedor"""
    data_fmt = datetime.now().strftime('%d/%m/%Y %H:%M')
    assunto = f'Pedido {numero} ({cliente}) - {status}'
    
    html = f'''<html>
<body style="font-family:Arial;background:#f5f5f5;padding:20px">
<div style="max-width:600px;margin:0 auto;background:white;border-radius:8px;padding:30px">
  <div style="background:linear-gradient(135deg,#FF9C00 0%,#FF6B00 100%);padding:30px;text-align:center;color:white;border-radius:6px;margin-bottom:30px">
    <h1 style="margin:0;font-size:26px">🚀 Atualização de Pedido do Cliente</h1>
  </div>
  <p style="font-size:16px;color:#333">Olá <strong>{vendedor_nome}</strong>,</p>
  <p style="font-size:16px;color:#555;margin:15px 0">O pedido do cliente <strong>{cliente}</strong> teve uma atualização importante:</p>
  <div style="background:#FF9C00;padding:25px;border-radius:6px;margin:20px 0;color:white;text-align:center;font-size:20px;font-weight:bold;line-height:1.6">
    ✅ {status.upper()}
  </div>
  <div style="background:#f9f9f9;padding:20px;border-radius:6px;margin:20px 0;border-left:4px solid #FF9C00">
    <p style="margin:10px 0"><strong>👤 Cliente:</strong> {cliente}</p>
    <p style="margin:10px 0"><strong>📦 Pedido:</strong> {numero}</p>
    <p style="margin:10px 0"><strong>📍 Rastreamento:</strong> {ultima_alt}</p>
    <p style="margin:10px 0"><strong>📅 Atualizado em:</strong> {data_fmt}</p>
    <p style="margin:10px 0"><strong>Descrição:</strong> {status}</p>
  </div>
  <div style="padding:15px;text-align:center;font-size:12px;color:#999;border-top:1px solid #e0e0e0">
    Email automático - Allcanci Rastreamento
  </div>
</div>
</body>
</html>'''
    
    return assunto, html


def gerar_mensagem_whatsapp(numero, cliente, status, ultima_alt):
    """Gera mensagem formatada para WhatsApp"""
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

_Allcanci Tecnologia_
    """.strip()
    
    return mensagem


# =========================================================================
# ENVIO DE EMAILS
# =========================================================================
def enviar_email(email_destino, assunto, html, tipo="cliente"):
    """Envia email via SMTP e salva em Enviados (IMAP)"""
    print(f"\n{'='*70}")
    print(f"📧 ENVIANDO EMAIL - {tipo.upper()}")
    print(f"{'='*70}")
    
    if not validar_email(email_destino):
        print(f"❌ Email inválido: {email_destino}")
        return False
    
    try:
        # Criar mensagem
        msg = MIMEMultipart('alternative')
        msg['Subject'] = assunto
        msg['From'] = EMAIL_USUARIO
        msg['To'] = email_destino
        msg['Reply-To'] = EMAIL_USUARIO
        msg['X-Mailer'] = 'Allcanci Rastreamento v1.0'
        
        # Adicionar partes
        msg.attach(MIMEText('Email de teste', 'plain', 'utf-8'))
        msg.attach(MIMEText(html, 'html', 'utf-8'))
        
        # Enviar via SMTP
        print(f"📤 Conectando ao SMTP: {EMAIL_SMTP}:{EMAIL_PORTA}")
        server = smtplib.SMTP_SSL(EMAIL_SMTP, int(EMAIL_PORTA))
        server.login(EMAIL_USUARIO, EMAIL_SENHA)
        server.send_message(msg)
        server.quit()
        print(f"✅ Email enviado para: {email_destino}")
        
        # Salvar em Enviados (IMAP)
        print(f"📁 Salvando em Enviados (IMAP)...")
        sucesso, resultado = salvar_email_imap(msg.as_string(), EMAIL_USUARIO, EMAIL_SENHA)
        if sucesso:
            print(f"✅ Email salvo em: {resultado}")
        else:
            print(f"⚠️  Aviso ao salvar: {resultado}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao enviar: {e}")
        return False


# =========================================================================
# MAIN
# =========================================================================
def main():
    """Função principal"""
    print("\n" + "="*70)
    print("🧪 TESTE DE ENVIO - EMAIL E WHATSAPP")
    print("="*70)
    
    # Dados de teste
    numero_pedido = "2024001"
    cliente_nome = "Israel Pinheiro"
    vendedor_nome = "Carlos Santos"
    status = "Saiu para entrega"
    rastreamento = "AA123456789BR"
    
    email_cliente = "israel@example.com"
    email_vendedor = "carlos@example.com"
    telefone_cliente = "(85) 98888-9999"
    
    print(f"\n📋 DADOS DE TESTE:")
    print(f"   Pedido: {numero_pedido}")
    print(f"   Cliente: {cliente_nome}")
    print(f"   Vendedor: {vendedor_nome}")
    print(f"   Status: {status}")
    print(f"   Rastreamento: {rastreamento}")
    print(f"   Email Cliente: {email_cliente}")
    print(f"   Email Vendedor: {email_vendedor}")
    print(f"   Telefone: {telefone_cliente}")
    
    # ====================================================================
    # 1. DESIGN DO EMAIL - CLIENTE
    # ====================================================================
    print(f"\n\n{'='*70}")
    print("1️⃣  DESIGN DE EMAIL - CLIENTE/ESCOLA")
    print(f"{'='*70}")
    assunto_cliente, html_cliente = gerar_email_cliente(numero_pedido, cliente_nome, status, rastreamento)
    print(f"\n📧 ASSUNTO: {assunto_cliente}")
    print(f"\n📄 PREVIEW DO HTML:\n")
    print(html_cliente[:500] + "...")
    
    # ====================================================================
    # 2. DESIGN DO EMAIL - VENDEDOR
    # ====================================================================
    print(f"\n\n{'='*70}")
    print("2️⃣  DESIGN DE EMAIL - VENDEDOR")
    print(f"{'='*70}")
    assunto_vendedor, html_vendedor = gerar_email_vendedor(numero_pedido, cliente_nome, status, rastreamento, vendedor_nome)
    print(f"\n📧 ASSUNTO: {assunto_vendedor}")
    print(f"\n📄 PREVIEW DO HTML:\n")
    print(html_vendedor[:500] + "...")
    
    # ====================================================================
    # 3. DESIGN DO WHATSAPP
    # ====================================================================
    print(f"\n\n{'='*70}")
    print("3️⃣  DESIGN DE MENSAGEM - WHATSAPP")
    print(f"{'='*70}")
    mensagem_whatsapp = gerar_mensagem_whatsapp(numero_pedido, cliente_nome, status, rastreamento)
    print(f"\n💬 MENSAGEM:\n")
    print(mensagem_whatsapp)
    
    # ====================================================================
    # 4. VALIDAÇÃO DE DADOS
    # ====================================================================
    print(f"\n\n{'='*70}")
    print("4️⃣  VALIDAÇÃO DE DADOS")
    print(f"{'='*70}")
    
    print(f"\n✅ Email Cliente válido: {validar_email(email_cliente)}")
    print(f"✅ Email Vendedor válido: {validar_email(email_vendedor)}")
    print(f"✅ Telefone válido: {validar_telefone(telefone_cliente)}")
    
    # ====================================================================
    # 5. ENVIAR EMAILS DE TESTE
    # ====================================================================
    print(f"\n\n{'='*70}")
    print("5️⃣  ENVIANDO EMAILS DE TESTE")
    print(f"{'='*70}")
    
    # Perguntar se quer enviar
    print(f"\n⚠️  ATENÇÃO: Isso vai enviar emails REAIS!")
    print(f"   Email Cliente: {email_cliente}")
    print(f"   Email Vendedor: {email_vendedor}")
    
    resposta = input(f"\n🤔 Deseja continuar? (s/n): ").strip().lower()
    
    if resposta == 's':
        print(f"\n🚀 Enviando...")
        
        # Enviar para cliente
        enviar_email(email_cliente, assunto_cliente, html_cliente, tipo="CLIENTE")
        time.sleep(2)
        
        # Enviar para vendedor
        enviar_email(email_vendedor, assunto_vendedor, html_vendedor, tipo="VENDEDOR")
        time.sleep(2)
        
        print(f"\n{'='*70}")
        print("6️⃣  WHATSAPP")
        print(f"{'='*70}")
        print(f"\n💬 Mensagem que seria enviada para: {telefone_cliente}")
        print(f"\n{mensagem_whatsapp}")
        print(f"\n⚠️  WhatsApp requer integração com um serviço externo")
        print(f"   Veja o arquivo: whatsapp_service.py")
        
        print(f"\n{'='*70}")
        print("✅ TESTE CONCLUÍDO!")
        print(f"{'='*70}")
        print(f"\n📧 Verifique os emails em sua caixa de entrada")
        print(f"📁 Verifique a pasta 'Enviados' para confirmar que foram salvos")
    else:
        print(f"\n❌ Envio cancelado pelo usuário")
    
    print(f"\n")


if __name__ == '__main__':
    main()
