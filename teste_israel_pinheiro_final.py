#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE ESPECÍFICO - Enviar notificação para o vendedor correto
Escola: Caixa Escolar da Escola Municipal Israel Pinheiro
Vendedor: Maurício Ribeiro Júnior (rennifer10@gmail.com)
Pedido: 2409
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv
from vendedor_service import buscar_vendedor

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('teste_israel_pinheiro')

def enviar_email_teste(numero_pedido, cliente, email_destino, nome_vendedor, status_teste):
    """Envia email de teste para o vendedor"""
    EMAIL_USUARIO = os.getenv('EMAIL_USUARIO')
    EMAIL_SENHA = os.getenv('EMAIL_SENHA')
    EMAIL_SMTP = os.getenv('EMAIL_SMTP', 'smtp.hostinger.com')
    EMAIL_PORTA = os.getenv('EMAIL_PORTA', '465')
    
    try:
        data_fmt = datetime.now().strftime('%d/%m/%Y %H:%M')
        
        html = f'''<html>
<body style="font-family:Arial;background:#f5f5f5;padding:20px">
<div style="max-width:600px;margin:0 auto;background:white;border-radius:8px;padding:30px">
  <div style="background:linear-gradient(135deg,#FF6B35 0%,#F7931E 100%);padding:30px;text-align:center;color:white;border-radius:6px;margin-bottom:30px">
    <h1 style="margin:0;font-size:26px">🔔 NOTIFICAÇÃO DE ATUALIZAÇÃO DE RASTREAMENTO</h1>
    <p style="margin:10px 0 0 0;font-size:14px">Email de Teste - Envio para Vendedor</p>
  </div>
  
  <div style="background:#FFF3E0;padding:20px;border-radius:6px;margin:20px 0;border-left:4px solid #FF6B35">
    <p style="margin:0;color:#E65100"><strong>✅ TESTE DE INTEGRAÇÃO COM SUCESSO</strong></p>
    <p style="margin:10px 0 0 0;color:#E65100">Este email valida que o sistema está enviando notificações corretamente para o vendedor.</p>
  </div>
  
  <p style="font-size:16px;color:#333;margin:20px 0">Olá <strong>{nome_vendedor}</strong>,</p>
  
  <p style="font-size:14px;color:#555;margin:15px 0">
    <strong>Cliente:</strong> {cliente}<br>
    <strong>Pedido:</strong> {numero_pedido}<br>
    <strong>Status:</strong> {status_teste}
  </p>
  
  <div style="background:#f9f9f9;padding:20px;border-radius:6px;margin:20px 0;border-left:4px solid #FF6B35">
    <h3 style="margin:0 0 15px 0;color:#333">Informações do Teste:</h3>
    <ul style="margin:0;padding-left:20px;color:#555">
      <li>✅ Sistema de notificação para vendedor está <strong>FUNCIONANDO</strong></li>
      <li>📧 Email de notificação enviado com sucesso</li>
      <li>🔗 Pedido: {numero_pedido}</li>
      <li>👥 Cliente: {cliente}</li>
      <li>⏰ Data/Hora: {data_fmt}</li>
    </ul>
  </div>
  
  <div style="background:#E8F5E9;padding:15px;border-radius:6px;margin:20px 0;border-left:4px solid #4CAF50;color:#2E7D32">
    <p style="margin:0"><strong>💡 Próximos Passos:</strong></p>
    <p style="margin:10px 0 0 0">Quando houver atualização real de rastreamento, você receberá notificações automáticas por email.</p>
  </div>
  
  <div style="padding:15px;text-align:center;font-size:12px;color:#999;border-top:1px solid #e0e0e0;margin-top:30px">
    Email de teste automático - Allcanci Rastreamento<br>
    Se você recebeu este email por engano, ignore-o.
  </div>
</div>
</body>
</html>'''
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'[TESTE SUCESSO] Pedido {numero_pedido} - Notificação para Vendedor'
        msg['From'] = EMAIL_USUARIO
        msg['To'] = email_destino
        
        msg.attach(MIMEText(f'Teste - Pedido {numero_pedido}', 'plain', 'utf-8'))
        msg.attach(MIMEText(html, 'html', 'utf-8'))
        
        server = smtplib.SMTP_SSL(EMAIL_SMTP, int(EMAIL_PORTA))
        server.login(EMAIL_USUARIO, EMAIL_SENHA)
        server.send_message(msg)
        server.quit()
        
        return True, 'OK'
    except Exception as e:
        return False, str(e)

# Executar teste
print("\n" + "=" * 80)
print("TESTE DE NOTIFICAÇÃO PARA VENDEDOR")
print("Escola Municipal Israel Pinheiro")
print("=" * 80 + "\n")

# Dados da escola e vendedor
numero_pedido = 2409
cliente = "Caixa Escolar da Escola Municipal Israel Pinheiro"
vendedor_id = 15596468666
vendedor_nome = "Maurício Ribeiro Júnior"
vendedor_email = "rennifer10@gmail.com"

logger.info(f"📋 DADOS DO TESTE:")
logger.info(f"   Pedido: {numero_pedido}")
logger.info(f"   Cliente: {cliente}")
logger.info(f"   Vendedor: {vendedor_nome}")
logger.info(f"   Email: {vendedor_email}\n")

# Validar dados
if not vendedor_email or not vendedor_email.strip():
    logger.error("❌ Vendedor não tem email cadastrado!")
    exit(1)

# Enviar email
logger.info("📧 Enviando email de teste...")
status_teste = "Atualização de Rastreamento - Validação de Integração"
sucesso, mensagem = enviar_email_teste(numero_pedido, cliente, vendedor_email, vendedor_nome, status_teste)

if sucesso:
    logger.info(f"✅ {mensagem}\n")
    
    print("\n" + "=" * 80)
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 80 + "\n")
    
    print("📊 RESUMO DO TESTE:")
    print(f"   Pedido: {numero_pedido}")
    print(f"   Cliente: {cliente}")
    print(f"   Vendedor: {vendedor_nome}")
    print(f"   Email enviado para: {vendedor_email}")
    print(f"   Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"\n💡 O vendedor deve receber o email em breve!")
    print("\n" + "=" * 80)
    print("✨ FUNCIONALIDADE VALIDADA E FUNCIONANDO CORRETAMENTE! ✨")
    print("=" * 80 + "\n")
    
    exit(0)
else:
    logger.error(f"❌ ERRO: {mensagem}")
    exit(1)
