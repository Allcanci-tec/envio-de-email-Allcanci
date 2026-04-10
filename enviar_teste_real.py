#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Envio REAL de email - teste com dados reais do sistema
Envia para professorrennifer10@gmail.com como VENDEDOR (Maurício Ribeiro Júnior)
Envia WhatsApp para 31984163357
Usa o design EXATO de produção (automatico_producao.py)
"""

import smtplib
import imaplib
import os
import sys
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

EMAIL_USUARIO = os.getenv('EMAIL_USUARIO')
EMAIL_SENHA = os.getenv('EMAIL_SENHA')
EMAIL_SMTP = os.getenv('EMAIL_SMTP')
EMAIL_PORTA = int(os.getenv('EMAIL_PORTA', 465))
EMAIL_IMAP = os.getenv('EMAIL_IMAP', 'imap.hostinger.com')
EMAIL_IMAP_PORTA = int(os.getenv('EMAIL_IMAP_PORTA', 993))

DESTINO = 'professorrennifer10@gmail.com'
WHATSAPP_NUMERO = '5531984163357'

# =====================================================================
# DADOS REAIS DO PEDIDO (como vem do contatos_rastreamento.json)
# =====================================================================
PEDIDO = {
    'numero': 2363,
    'cliente': 'CAIXA ESCOLAR PADRE AFONSO DE LEMOS',
    'etiqueta': 'AD287897978BR',
    'situacao': 'Objeto saiu para entrega ao destinatário',
    'ultima_alt': 'AD287897978BR - Atualizado via Correios',
    'origem': 'Betim - MG',
    'destino': 'Juiz de Fora - MG',
    'vendedor_nome': 'Maurício Ribeiro Júnior',
}


def salvar_email_enviados(email_string):
    """Salva email na pasta Enviados via IMAP."""
    try:
        imap = imaplib.IMAP4_SSL(EMAIL_IMAP, EMAIL_IMAP_PORTA)
        imap.login(EMAIL_USUARIO, EMAIL_SENHA)
        
        pasta_sent = 'INBOX.Sent'
        date = imaplib.Time2Internaldate(time.time())
        result = imap.append(pasta_sent, '(\\Seen)', date, email_string.encode('utf-8'))
        imap.logout()
        
        if result[0] == 'OK':
            print(f'   ✅ Salvo em Enviados ({pasta_sent})')
        else:
            print(f'   ⚠️ IMAP result: {result}')
    except Exception as e:
        print(f'   ⚠️ Erro ao salvar em Enviados: {e}')


def montar_email(tipo='escola'):
    """Monta email usando o DESIGN EXATO de produção."""
    
    numero = PEDIDO['numero']
    cliente = PEDIDO['cliente']
    situacao = PEDIDO['situacao']
    etiqueta = PEDIDO['etiqueta']
    origem = PEDIDO['origem']
    destino = PEDIDO['destino']
    vendedor_nome = PEDIDO['vendedor_nome']
    data_fmt = datetime.now().strftime('%d/%m/%Y %H:%M')
    
    if tipo == 'vendedor':
        saudacao = f'Ol&#225; <strong>{vendedor_nome}</strong>,'
        subtexto = f'O pedido do cliente <strong>{cliente}</strong> teve uma atualiza&#231;&#227;o importante:'
        assunto = f'Pedido {numero} ({cliente}) - {situacao}'
    else:
        saudacao = f'Ol&#225; <strong>{cliente}</strong>,'
        subtexto = 'Seu pedido teve uma atualiza&#231;&#227;o importante:'
        assunto = f'Pedido {numero} - {situacao}'
    
    # DESIGN EXATO DE PRODUÇÃO (automatico_producao.py)
    html = f'''<html>
<body style="font-family:Arial;background:#f5f5f5;padding:20px">
<div style="max-width:600px;margin:0 auto;background:white;border-radius:8px;padding:30px">
  <div style="background:linear-gradient(135deg,#0000F3 0%,#0051DB 100%);padding:30px;text-align:center;color:white;border-radius:6px;margin-bottom:30px">
    <h1 style="margin:0;font-size:26px">&#128246; Atualiza&#231;&#227;o de Rastreamento</h1>
  </div>
  <p style="font-size:16px;color:#333">{saudacao}</p>
  <p style="font-size:16px;color:#555;margin:15px 0">{subtexto}</p>
  <div style="background:#4CAF50;padding:25px;border-radius:6px;margin:20px 0;color:white;text-align:center;font-size:20px;font-weight:bold;line-height:1.6">
    &#9989; {situacao.upper()}
  </div>
  <div style="background:#f9f9f9;padding:20px;border-radius:6px;margin:20px 0;border-left:4px solid #0066cc">
    <p style="margin:10px 0"><strong>&#128456; Pedido:</strong> {numero}</p>
    <p style="margin:10px 0"><strong>&#128226; Rastreamento:</strong> {etiqueta}</p>
    <p style="margin:10px 0"><strong>&#128205; Origem:</strong> {origem}</p>
    <p style="margin:10px 0"><strong>&#128205; Destino:</strong> {destino}</p>
    <p style="margin:10px 0"><strong>&#128197; Atualizado em:</strong> {data_fmt}</p>
    <p style="margin:10px 0"><strong>Descri&#231;&#227;o:</strong> {situacao}</p>
  </div>
  <div style="padding:15px;text-align:center;font-size:12px;color:#999;border-top:1px solid #e0e0e0">
    Email autom&#225;tico - Allcanci Rastreamento
  </div>
</div>
</body>
</html>'''
    
    return assunto, html


def enviar(tipo):
    """Envia email real."""
    
    label = 'ESCOLA (Cliente)' if tipo == 'escola' else 'VENDEDOR'
    print(f'\n{"="*60}')
    print(f'📧 ENVIANDO EMAIL {label}')
    print(f'{"="*60}')
    print(f'   De: {EMAIL_USUARIO}')
    print(f'   Para: {DESTINO}')
    print(f'   Pedido: {PEDIDO["numero"]} - {PEDIDO["cliente"]}')
    print(f'   Situação: {PEDIDO["situacao"]}')
    print(f'   Origem: {PEDIDO["origem"]}')
    print(f'   Destino: {PEDIDO["destino"]}')
    if tipo == 'vendedor':
        print(f'   Vendedor: {PEDIDO["vendedor_nome"]}')
    
    assunto, html = montar_email(tipo)
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = assunto
    msg['From'] = EMAIL_USUARIO
    msg['To'] = DESTINO
    msg['Reply-To'] = EMAIL_USUARIO
    msg['X-Mailer'] = 'Allcanci Rastreamento v1.0'
    msg.attach(MIMEText(f'Pedido {PEDIDO["numero"]}\nStatus: {PEDIDO["situacao"]}', 'plain', 'utf-8'))
    msg.attach(MIMEText(html, 'html', 'utf-8'))
    
    try:
        print(f'\n   Conectando ao SMTP ({EMAIL_SMTP}:{EMAIL_PORTA})...')
        server = smtplib.SMTP_SSL(EMAIL_SMTP, EMAIL_PORTA)
        server.login(EMAIL_USUARIO, EMAIL_SENHA)
        server.send_message(msg)
        server.quit()
        print(f'   ✅ Email {label} ENVIADO com sucesso!')
        
        # Salvar em Enviados
        salvar_email_enviados(msg.as_string())
        
        return True
    except Exception as e:
        print(f'   ❌ ERRO: {e}')
        return False


def enviar_whatsapp_teste():
    """Envia mensagem WhatsApp com dados reais do pedido."""
    print(f'\n{"="*60}')
    print(f'📱 ENVIANDO WHATSAPP')
    print(f'{"="*60}')
    print(f'   Para: {WHATSAPP_NUMERO}')
    print(f'   Pedido: {PEDIDO["numero"]} - {PEDIDO["cliente"]}')
    
    try:
        from whatsapp_service import enviar_mensagem as enviar_whatsapp
    except Exception as e:
        print(f'   ❌ WhatsApp Service indisponível: {e}')
        return False
    
    data_fmt = datetime.now().strftime('%d/%m/%Y %H:%M')
    
    mensagem = f"""📦 *ATUALIZAÇÃO DE RASTREAMENTO*

Olá *{PEDIDO['cliente']}*,

Seu pedido teve uma atualização importante:

✅ *{PEDIDO['situacao'].upper()}*

*Detalhes:*
🔹 Pedido: {PEDIDO['numero']}
🔹 Rastreamento: {PEDIDO['etiqueta']}
📍 Origem: {PEDIDO['origem']}
📍 Destino: {PEDIDO['destino']}
🔹 Atualizado em: {data_fmt}

🔗 Acompanhe: https://www.correios.com.br

_Allcanci Tecnologia_""".strip()
    
    print(f'\n   Mensagem:')
    for linha in mensagem.split('\n'):
        print(f'   | {linha}')
    
    try:
        sucesso, msg = enviar_whatsapp(WHATSAPP_NUMERO, mensagem)
        if sucesso:
            print(f'   ✅ WhatsApp ENVIADO com sucesso!')
            return True
        else:
            print(f'   ❌ WhatsApp falhou: {msg}')
            return False
    except Exception as e:
        print(f'   ❌ Erro ao enviar WhatsApp: {e}')
        return False


if __name__ == '__main__':
    print('\n' + '='*60)
    print('ENVIO REAL DE EMAIL - ALLCANCI RASTREAMENTO')
    print(f'Remetente: {EMAIL_USUARIO}')
    print(f'Destinatário: {DESTINO}')
    print(f'Vendedor: {PEDIDO["vendedor_nome"]}')
    print('='*60)
    
    # 1. Enviar email como VENDEDOR (Maurício Ribeiro Júnior)
    ok_vendedor = enviar('vendedor')
    
    # 2. Enviar WhatsApp
    ok_whatsapp = enviar_whatsapp_teste()
    
    # Resumo
    print(f'\n{"="*60}')
    print('RESUMO')
    print(f'{"="*60}')
    print(f'   Email Vendedor ({PEDIDO["vendedor_nome"]}): {"✅ ENVIADO" if ok_vendedor else "❌ FALHOU"}')
    print(f'   WhatsApp ({WHATSAPP_NUMERO}): {"✅ ENVIADO" if ok_whatsapp else "❌ FALHOU"}')
    print(f'   Verifique email: {DESTINO}')
    print(f'   Verifique WhatsApp: {WHATSAPP_NUMERO}')
    print(f'{"="*60}\n')
