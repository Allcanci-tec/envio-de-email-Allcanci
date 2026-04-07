#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRIPT DE TESTE - ENVIO DE NOTIFICAÇÃO PARA VENDEDOR
Busca um pedido específico (ou a primeira escola disponível)
Extrai o vendedor e envia email de teste
"""

import json
import os
import requests
import smtplib
import logging
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime
from vendedor_service import buscar_vendedor

load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('teste_vendedor')

# Constantes
BLING_API = 'https://api.bling.com.br/v3'
ID_LOGISTICA_CORREIOS = 151483

def carregar_token():
    """Carrega token do Bling de tokens.json"""
    with open('tokens.json', 'r', encoding='utf-8') as f:
        dados = json.load(f)
    return dados.get('access_token')

def headers_bling():
    """Retorna headers com Authorization para API Bling"""
    token = carregar_token()
    return {'Authorization': f'Bearer {token}'}

def enviar_email_teste(numero_pedido, cliente, email_destino, nome_vendedor, status_teste):
    """Envia email de teste formatado"""
    EMAIL_USUARIO = os.getenv('EMAIL_USUARIO')
    EMAIL_SENHA = os.getenv('EMAIL_SENHA')
    EMAIL_SMTP = os.getenv('EMAIL_SMTP', 'smtp.hostinger.com')
    EMAIL_PORTA = os.getenv('EMAIL_PORTA', '465')
    
    if not email_destino:
        return False, 'Email vazio'
    
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
    <p style="margin:0;color:#E65100"><strong>⚠️ ESTE É UM EMAIL DE TESTE</strong></p>
    <p style="margin:10px 0 0 0;color:#E65100">Este email foi enviado para validar a integração de notificações de vendedores.</p>
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
      <li>📧 Email enviado com sucesso</li>
      <li>🔗 Pedido: {numero_pedido}</li>
      <li>👥 Cliente: {cliente}</li>
      <li>⏰ Data/Hora: {data_fmt}</li>
    </ul>
  </div>
  
  <div style="padding:15px;text-align:center;font-size:12px;color:#999;border-top:1px solid #e0e0e0;margin-top:30px">
    Email de teste automático - Allcanci Rastreamento<br>
    Se você recebeu este email por engano, ignore-o.
  </div>
</div>
</body>
</html>'''
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'[TESTE] Pedido {numero_pedido} - Notificação para Vendedor'
        msg['From'] = EMAIL_USUARIO
        msg['To'] = email_destino
        
        msg.attach(MIMEText(f'Email de teste - Pedido {numero_pedido} - Status: {status_teste}', 'plain', 'utf-8'))
        msg.attach(MIMEText(html, 'html', 'utf-8'))
        
        server = smtplib.SMTP_SSL(EMAIL_SMTP, int(EMAIL_PORTA))
        server.login(EMAIL_USUARIO, EMAIL_SENHA)
        server.send_message(msg)
        server.quit()
        
        return True, 'OK'
    except Exception as e:
        return False, str(e)

def buscar_pedido_com_vendedor_email():
    """Busca um pedido que tem vendedor com email"""
    logger.info('\n' + '=' * 70)
    logger.info('BUSCANDO PEDIDO COM VENDEDOR QUE TEM EMAIL')
    logger.info('=' * 70)
    
    try:
        # Buscar todos os pedidos Correios
        for pagina in range(1, 10):  # Tentar até 10 páginas
            resp = requests.get(
                f'{BLING_API}/pedidos/vendas',
                headers=headers_bling(),
                params={
                    'pagina': pagina,
                    'limite': 50,
                    'idLogistica': ID_LOGISTICA_CORREIOS,
                },
                timeout=15,
            )
            
            if resp.status_code != 200:
                break
            
            dados = resp.json().get('data', [])
            if not dados:
                break
            
            logger.info(f'  Verificando página {pagina}... ({len(dados)} pedidos)')
            
            for pedido_resumido in dados:
                numero = pedido_resumido.get('numero')
                pedido_id_interno = pedido_resumido.get('id')
                
                # Buscar detalhe completo
                try:
                    r2 = requests.get(
                        f'{BLING_API}/pedidos/vendas/{pedido_id_interno}',
                        headers=headers_bling(),
                        timeout=10,
                    )
                    
                    if r2.status_code == 200:
                        pedido = r2.json().get('data', {})
                        vendedor_id = pedido.get('vendedor', {}).get('id')
                        
                        # Se tem vendedor, buscar email
                        if vendedor_id and vendedor_id != 0:
                            dados_vendedor = buscar_vendedor(vendedor_id)
                            if dados_vendedor.get('sucesso') and dados_vendedor.get('email'):
                                # Encontrado!
                                logger.info(f'  ✅ Pedido encontrado!')
                                return pedido
                except:
                    pass
        
        logger.warning('  Nenhum pedido com vendedor com email encontrado')
        return None
        
    except Exception as e:
        logger.error(f'Erro ao buscar pedido: {e}')
        return None

def teste_vendedor():
    """Executa o teste completo"""
    logger.info('\n' + '=' * 70)
    logger.info('TESTE DE NOTIFICAÇÃO PARA VENDEDOR')
    logger.info('=' * 70)
    
    # Buscar pedido que tem vendedor com email
    pedido = buscar_pedido_com_vendedor_email()
    
    if not pedido:
        logger.error('❌ Nenhum pedido com vendedor com email foi encontrado')
        logger.info('Por favor, crie um pedido no Bling com um vendedor que tem email cadastrado')
        return False
    
    # Extrair dados básicos
    numero = pedido.get('numero')
    cliente = pedido.get('contato', {}).get('nome', 'Desconhecido')
    vendedor_id = pedido.get('vendedor', {}).get('id')
    
    logger.info(f'\n📋 DADOS DO PEDIDO:')
    logger.info(f'   Número: {numero}')
    logger.info(f'   Cliente: {cliente}')
    logger.info(f'   Vendedor ID: {vendedor_id}')
    
    # Buscar dados do vendedor
    logger.info(f'\n🔍 BUSCANDO DADOS DO VENDEDOR:')
    logger.info(f'   Vendor ID: {vendedor_id}')
    
    dados_vendedor = buscar_vendedor(vendedor_id)
    
    if not dados_vendedor.get('sucesso'):
        logger.error(f'❌ Erro ao buscar vendedor: {dados_vendedor.get("motivo")}')
        return False
    
    vendedor_nome = dados_vendedor.get('nome', 'Desconhecido')
    vendedor_email = dados_vendedor.get('email', '')
    
    logger.info(f'\n✅ VENDEDOR ENCONTRADO:')
    logger.info(f'   Nome: {vendedor_nome}')
    logger.info(f'   Email: {vendedor_email or "(SEM EMAIL)"}')
    
    if not vendedor_email or not vendedor_email.strip():
        logger.error('❌ Vendedor não tem email cadastrado')
        return False
    
    # Enviar email de teste
    logger.info(f'\n📧 ENVIANDO EMAIL DE TESTE:')
    logger.info(f'   Para: {vendedor_email}')
    logger.info(f'   Assunto: [TESTE] Pedido {numero}')
    
    status_teste = 'Atualização de Rastreamento - Teste'
    sucesso, mensagem = enviar_email_teste(numero, cliente, vendedor_email, vendedor_nome, status_teste)
    
    if sucesso:
        logger.info(f'   ✅ {mensagem}')
        logger.info(f'\n' + '=' * 70)
        logger.info(f'✅ TESTE CONCLUÍDO COM SUCESSO!')
        logger.info(f'=' * 70)
        logger.info(f'\n📊 RESUMO:')
        logger.info(f'   Pedido: {numero}')
        logger.info(f'   Cliente: {cliente}')
        logger.info(f'   Vendedor: {vendedor_nome}')
        logger.info(f'   Email enviado para: {vendedor_email}')
        logger.info(f'   Data/Hora: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
        logger.info(f'\n💡 O vendedor deve receber o email em breve!')
        logger.info(f'=' * 70)
        return True
    else:
        logger.error(f'   ❌ ERRO: {mensagem}')
        return False

if __name__ == '__main__':
    print("""
    
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║          TESTE DE NOTIFICAÇÃO PARA VENDEDOR - ALLCANCI RASTREAMENTO         ║
║                                                                              ║
║  Este script testa se o sistema está enviando notificações corretamente     ║
║  para os vendedores quando há atualização de rastreamento.                  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    sucesso = teste_vendedor()
    sys.exit(0 if sucesso else 1)
