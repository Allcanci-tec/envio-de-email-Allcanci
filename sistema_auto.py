#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

print("\n" + "="*70)
print("📧 TESTE DE ENVIO DE EMAIL - HOSTINGER")
print("="*70 + "\n")

# Carregar configurações do .env
EMAIL_USUARIO = os.getenv('EMAIL_USUARIO')
EMAIL_SENHA = os.getenv('EMAIL_SENHA')
EMAIL_SMTP = os.getenv('EMAIL_SMTP', 'smtp.hostinger.com')
EMAIL_PORTA = int(os.getenv('EMAIL_PORTA', '465'))

# Dados do pedido
numero = 2363
cliente = "CAIXA ESCOLAR PADRE AFONSO DE LEMOS"
email_destinatario = "professorrennifer10@gmail.com"
etiqueta = "AD287897978BR"
status = "Saiu para entrega ao destinatário"
ultima_alteracao = "2026-04-01 11:07:55"
prazo = 2

print("📋 DADOS DO TESTE:")
print(f"   Pedido: {numero}")
print(f"   Cliente: {cliente}")
print(f"   Email Destino: {email_destinatario}")
print(f"   Etiqueta: {etiqueta}")
print(f"   Status: {status}\n")

print("🔑 CREDENCIAIS CARREGADAS:")
print(f"   EMAIL_USUARIO: {EMAIL_USUARIO if EMAIL_USUARIO else '❌ NÃO CONFIGURADO'}")
print(f"   EMAIL_SENHA: {'✅ Configurada' if EMAIL_SENHA else '❌ NÃO CONFIGURADA'}")
print(f"   EMAIL_SMTP: {EMAIL_SMTP}")
print(f"   EMAIL_PORTA: {EMAIL_PORTA}\n")

if not EMAIL_USUARIO or not EMAIL_SENHA:
    print("❌ ERRO: EMAIL_USUARIO ou EMAIL_SENHA não configurados no .env")
    exit(1)

# Template HTML simples
html = f"""<html><body style="font-family: Arial; background-color: #f5f5f5; padding: 20px;">
<div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; padding: 30px;">
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; color: white; border-radius: 6px; margin-bottom: 30px;">
<h1 style="margin: 0; font-size: 28px;">📦 Atualização de Rastreamento</h1>
</div>
<p style="font-size: 16px; color: #333;">Olá <strong>{cliente}</strong>,</p>
<div style="background-color: #4CAF50; padding: 20px; border-radius: 6px; margin: 20px 0; color: white; text-align: center; font-size: 18px; font-weight: bold;">{status}</div>
<div style="background-color: #f9f9f9; padding: 20px; border-radius: 6px; margin: 20px 0;">
<p><strong>Pedido:</strong> {numero}</p>
<p><strong>Rastreamento:</strong> {etiqueta}</p>
<p><strong>Última Atualização:</strong> {ultima_alteracao}</p>
<p><strong>Prazo:</strong> {prazo} dias</p>
</div>
<div style="background-color: #f5f5f5; padding: 20px; text-align: center; border-top: 1px solid #e0e0e0; font-size: 12px; color: #999;">
<p>Email automático - Sistema de Rastreamento Allcanci</p>
</div>
</div></body></html>"""

try:
    print("🚀 Conectando ao servidor SMTP...")
    print(f"   Servidor: {EMAIL_SMTP}:{EMAIL_PORTA}")
    
    server = smtplib.SMTP_SSL(EMAIL_SMTP, EMAIL_PORTA)
    
    print("🔐 Autenticando...")
    server.login(EMAIL_USUARIO, EMAIL_SENHA)
    
    print("📝 Preparando mensagem...")
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"📦 Seu pedido {numero} - {status}"
    msg['From'] = EMAIL_USUARIO
    msg['To'] = email_destinatario
    
    msg.attach(MIMEText(f"Pedido {numero}\nStatus: {status}\nEtiqueta: {etiqueta}", 'plain'))
    msg.attach(MIMEText(html, 'html'))
    
    print("📤 Enviando email...\n")
    server.send_message(msg)
    server.quit()
    
    print("✅ EMAIL ENVIADO COM SUCESSO!\n")
    print(f"   ✅ De: {EMAIL_USUARIO}")
    print(f"   ✅ Para: {email_destinatario}")
    print(f"   ✅ Assunto: 📦 Seu pedido {numero}")
    print(f"   ✅ Servidor: {EMAIL_SMTP}:{EMAIL_PORTA}\n")
    print("="*70)
    print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
    print("="*70)
    print("\n✅ Sistema pronto para automação!\n")
    
except smtplib.SMTPAuthenticationError as e:
    print(f"❌ ERRO DE AUTENTICAÇÃO: {str(e)}\n")
    print("Verifique no .env:")
    print("   - EMAIL_USUARIO (deve ser suporte1@allcanci.com.br)")
    print("   - EMAIL_SENHA (senha correta)\n")
except Exception as e:
    print(f"❌ ERRO: {str(e)}\n")
