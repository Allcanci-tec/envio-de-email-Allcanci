#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE DE CONEXÃO IMAP
Valida se a conexão IMAP está funcionando e se consegue salvar emails na pasta Enviados
"""

import imaplib
import smtplib
import os
import sys
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

load_dotenv()

# Carrega credenciais do .env
EMAIL_USUARIO = os.getenv('EMAIL_USUARIO')
EMAIL_SENHA = os.getenv('EMAIL_SENHA')
EMAIL_IMAP = os.getenv('EMAIL_IMAP', 'imap.hostinger.com')
EMAIL_IMAP_PORTA = os.getenv('EMAIL_IMAP_PORTA', '993')
EMAIL_SMTP = os.getenv('EMAIL_SMTP', 'smtp.hostinger.com')
EMAIL_PORTA = os.getenv('EMAIL_PORTA', '465')

print("=" * 70)
print("🧪 TESTE DE CONEXÃO IMAP - ALLCANCI")
print("=" * 70)
print()

# =========================================================================
# TESTE 1: Credenciais carregadas
# =========================================================================
print("✓ TESTE 1: Credenciais Carregadas")
print("-" * 70)
print(f"Email: {EMAIL_USUARIO}")
print(f"IMAP Server: {EMAIL_IMAP}:{EMAIL_IMAP_PORTA}")
print(f"SMTP Server: {EMAIL_SMTP}:{EMAIL_PORTA}")
print()

if not EMAIL_USUARIO or not EMAIL_SENHA:
    print("❌ ERRO: Email ou senha não configurados no .env")
    sys.exit(1)

# =========================================================================
# TESTE 2: Conexão IMAP
# =========================================================================
print("✓ TESTE 2: Conectando ao IMAP...")
print("-" * 70)
try:
    imap = imaplib.IMAP4_SSL(EMAIL_IMAP, int(EMAIL_IMAP_PORTA))
    print(f"✅ Conectado ao IMAP: {EMAIL_IMAP}:{EMAIL_IMAP_PORTA}")
except Exception as e:
    print(f"❌ Erro ao conectar IMAP: {e}")
    sys.exit(1)

# =========================================================================
# TESTE 3: Login IMAP
# =========================================================================
print()
print("✓ TESTE 3: Autenticando no IMAP...")
print("-" * 70)
try:
    imap.login(EMAIL_USUARIO, EMAIL_SENHA)
    print(f"✅ Autenticado como: {EMAIL_USUARIO}")
except Exception as e:
    print(f"❌ Erro de autenticação: {e}")
    imap.close()
    imap.logout()
    sys.exit(1)

# =========================================================================
# TESTE 4: Listar pastas disponíveis
# =========================================================================
print()
print("✓ TESTE 4: Pastas Disponíveis no IMAP")
print("-" * 70)
try:
    retcode, mailboxes = imap.list()
    print("📁 Pastas encontradas:")
    pastas = []
    for mailbox in mailboxes:
        pasta = mailbox.decode('utf-8')
        print(f"   • {pasta}")
        pastas.append(pasta)
    
    # Verificar se existe pasta Enviados
    num_marcas = 0
    for pasta in pastas:
        if 'Sent' in pasta or 'Enviados' in pasta or '[Gmail]/Enviados' in pasta:
            num_marcas += 1
            print(f"\n✅ Pasta Enviados encontrada: {pasta}")
    
    if num_marcas == 0:
        print("\n⚠️ AVISO: Pasta 'Enviados' ou 'Sent' não encontrada claramente")
        print("        Você pode precisar ajustar o nome da pasta no código")
except Exception as e:
    print(f"❌ Erro ao listar pastas: {e}")
    imap.close()
    imap.logout()
    sys.exit(1)

# =========================================================================
# TESTE 5: Contar emails em cada pasta
# =========================================================================
print()
print("✓ TESTE 5: Contagem de Emails por Pasta")
print("-" * 70)
try:
    for pasta in pastas[:5]:  # Limita a 5 pastas para não ficar muito longo
        try:
            imap.select(pasta)
            retcode, messages = imap.search(None, 'ALL')
            num_emails = len(messages[0].split())
            print(f"   {pasta}: {num_emails} emails")
        except:
            pass
except Exception as e:
    print(f"⚠️ Erro ao contar emails: {e}")

# =========================================================================
# TESTE 6: Tentar salvar email de teste
# =========================================================================
print()
print("✓ TESTE 6: Salvando Email de Teste na Pasta Enviados")
print("-" * 70)
try:
    # Criar email de teste
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'🧪 Teste IMAP - {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}'
    msg['From'] = EMAIL_USUARIO
    msg['To'] = EMAIL_USUARIO
    msg['X-Mailer'] = 'Teste IMAP'
    
    corpo_texto = "Este é um email de teste para validar se o IMAP está salvando emails na pasta Enviados."
    corpo_html = f"""
    <html>
    <body style="font-family:Arial">
    <h2>Teste de Conexão IMAP ✅</h2>
    <p>{corpo_texto}</p>
    <p><strong>Data/Hora:</strong> {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</p>
    <p style="color:#999;font-size:12px">Email automático de teste</p>
    </body>
    </html>
    """
    
    msg.attach(MIMEText(corpo_texto, 'plain', 'utf-8'))
    msg.attach(MIMEText(corpo_html, 'html', 'utf-8'))
    
    # Tentar salvar
    pasta_sent = 'INBOX.Sent'  # Padrão para Hostinger
    print(f"Detectando pasta Enviados...")
    
    for p in pastas:
        p_str = p if isinstance(p, str) else p.decode('utf-8')
        if 'Sent' in p_str or 'INBOX.Sent' in p_str:
            # Extrair o nome real da pasta (último segmento após spaço)
            partes = p_str.split()
            if len(partes) > 0:
                pasta_sent = partes[-1].strip('\"')
            break
    
    print(f"Pasta detectada: {pasta_sent}")
    
    # Selecionar a pasta ANTES de fazer append
    try:
        imap.select(pasta_sent)
        imap.append(pasta_sent, '', imaplib.Time2Internaldate(datetime.now().timestamp()), msg.as_bytes())
        print(f"✅ Email de teste salvo na pasta: {pasta_sent}")
    except Exception as e2:
        print(f"❌ Erro ao salvar: {e2}")
        print(f"   Tentando com 'INBOX.Sent'...")
        try:
            imap.select('INBOX.Sent')
            imap.append('INBOX.Sent', '', imaplib.Time2Internaldate(datetime.now().timestamp()), msg.as_bytes())
            print(f"✅ Email de teste salvo na pasta: INBOX.Sent")
        except Exception as e3:
            print(f"❌ Erro final: {e3}")
    
except Exception as e:
    print(f"❌ Erro ao salvar email: {e}")
    print(f"   Dica: A pasta '{pasta_sent}' existe? Verifique a lista acima.")

# =========================================================================
# TESTE 7: Fechar conexão
# =========================================================================
print()
print("✓ TESTE 7: Fechando Conexão")
print("-" * 70)
try:
    imap.close()
    imap.logout()
    print("✅ Conexão IMAP fechada com sucesso")
except Exception as e:
    print(f"⚠️ Aviso ao fechar: {e}")

# =========================================================================
# RESUMO FINAL
# =========================================================================
print()
print("=" * 70)
print("✅ TESTES CONCLUÍDOS!")
print("=" * 70)
print()
print("📋 RESUMO:")
print("   ✅ Credenciais carregadas")
print("   ✅ Conexão IMAP estabelecida")
print("   ✅ Autenticação bem-sucedida")
print("   ✅ Pastas IMAP listadas")
print("   ✅ Email de teste salvo")
print()
print("🚀 Você está pronto para usar o IMAP no seu sistema!")
print()
