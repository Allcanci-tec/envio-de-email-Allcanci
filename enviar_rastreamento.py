#!/usr/bin/env python3
"""
Script para enviar email de rastreamento
"""

import smtplib
import os
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def enviar_email_rastreamento(numero, cliente, email, etiqueta, status="Postado", EMAIL_USUARIO=None, EMAIL_SENHA=None, EMAIL_SMTP=None, EMAIL_PORTA=None):
    """Envia email com rastreamento do pedido via Hostinger SMTP"""
    
    if not EMAIL_USUARIO:
        EMAIL_USUARIO = os.getenv('EMAIL_USUARIO')
    if not EMAIL_SENHA:
        EMAIL_SENHA = os.getenv('EMAIL_SENHA')
    if not EMAIL_SMTP:
        EMAIL_SMTP = os.getenv('EMAIL_SMTP', 'smtp.hostinger.com')
    if not EMAIL_PORTA:
        EMAIL_PORTA = os.getenv('EMAIL_PORTA', '465')
    
    if not EMAIL_USUARIO or not EMAIL_SENHA:
        return False, "Configure EMAIL_USUARIO e EMAIL_SENHA no .env"
    
    try:
        # Template HTML do email
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                <div style="background-color: white; padding: 30px; border-radius: 8px; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #333;">📦 Atualização de Rastreamento</h2>
                    
                    <p style="color: #555; font-size: 16px;">
                        Olá <strong>{cliente}</strong>,
                    </p>
                    
                    <p style="color: #555; font-size: 16px;">
                        Seu pedido foi atualizado! Confira os detalhes:
                    </p>
                    
                    <div style="background-color: #f9f9f9; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>Pedido:</strong> {numero}</p>
                        <p><strong>Rastreamento:</strong> <span style="color: #0066cc; font-weight: bold;">{etiqueta}</span></p>
                        <p><strong>Status:</strong> {status}</p>
                        <p><strong>Data/Hora:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                    </div>
                    
                    <p style="color: #555; font-size: 14px;">
                        Rastrear: <a href="https://www.correios.com.br/rastreamento" style="color: #0066cc;">Correios</a>
                    </p>
                    
                    <p style="color: #999; font-size: 12px; margin-top: 30px;">
                        Email automático. Não responda.
                    </p>
                </div>
            </body>
        </html>
        """
        
        # Cria mensagem
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"📦 Pedido {numero} - {etiqueta}"
        msg['From'] = EMAIL_USUARIO
        msg['To'] = email
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # Envia via Hostinger SMTP SSL
        server = smtplib.SMTP_SSL(EMAIL_SMTP, int(EMAIL_PORTA))
        server.login(EMAIL_USUARIO, EMAIL_SENHA)
        server.send_message(msg)
        server.quit()
        
        return True, "✅ Email enviado com sucesso!"
        
    except Exception as e:
        return False, f"❌ Erro ao enviar: {str(e)}"


def enviar_para_todos_contatos(arquivo_contatos="contatos_rastreamento.json"):
    """Envia emails para todos os contatos com rastreamento"""
    
    EMAIL_USUARIO = os.getenv('EMAIL_USUARIO')
    EMAIL_SENHA = os.getenv('EMAIL_SENHA')
    EMAIL_SMTP = os.getenv('EMAIL_SMTP', 'smtp.hostinger.com')
    EMAIL_PORTA = os.getenv('EMAIL_PORTA', '465')
    
    erros_log = []
    
    try:
        with open(arquivo_contatos, 'r', encoding='utf-8') as f:
            contatos = json.load(f)
        
        print(f"\n📧 Enviando emails para {len(contatos)} clientes...\n")
        
        enviados = 0
        erros = 0
        
        for contato in contatos:
            if not contato.get('email') or contato['email'] == '':
                print(f"  ⏭️  {contato['cliente']:<50} - SEM EMAIL")
                continue
            
            sucesso, msg = enviar_email_rastreamento(
                numero=contato['numero'],
                cliente=contato['cliente'],
                email=contato['email'],
                etiqueta=contato['etiqueta'],
                status="Postado nos Correios",
                EMAIL_USUARIO=EMAIL_USUARIO,
                EMAIL_SENHA=EMAIL_SENHA,
                EMAIL_SMTP=EMAIL_SMTP,
                EMAIL_PORTA=EMAIL_PORTA
            )
            
            if sucesso:
                print(f"  ✅ {contato['cliente']:<50} - {contato['email']}")
                enviados += 1
            else:
                print(f"  ❌ {contato['cliente']:<50} - ERRO")
                erros_log.append(f"Pedido {contato['numero']} ({contato['email']}): {msg}")
                erros += 1
        
        print(f"\n📊 Resultado: {enviados} enviados, {erros} erros\n")
        
        if erros_log:
            print("DETALHES DOS ERROS:")
            for erro in erros_log:
                print(f"  - {erro}\n")
        
    except FileNotFoundError:
        print(f"❌ Arquivo {arquivo_contatos} não encontrado")
    except Exception as e:
        print(f"❌ Erro: {str(e)}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("✉️  ENVIO DE EMAIL DE RASTREAMENTO - TODAS AS ESCOLAS")
    print("="*70 + "\n")
    
    # Envia para todos os contatos
    enviar_para_todos_contatos()
    
    # Gera arquivo de log detalhado
    try:
        with open('contatos_rastreamento.json', 'r', encoding='utf-8') as f:
            contatos = json.load(f)
        
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        nome_arquivo_log = f"log_envio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(nome_arquivo_log, 'w', encoding='utf-8') as log:
            log.write("="*70 + "\n")
            log.write("LOG DE ENVIO DE RASTREAMENTO\n")
            log.write("="*70 + "\n")
            log.write(f"Data/Hora: {timestamp}\n")
            log.write(f"Total de escolas: {len(contatos)}\n")
            log.write("="*70 + "\n\n")
            
            com_email = [c for c in contatos if c.get('email') and c['email'] != '']
            sem_email = [c for c in contatos if not c.get('email') or c['email'] == '']
            
            log.write(f"ESCOLAS COM EMAIL ({len(com_email)}):\n")
            log.write("-"*70 + "\n")
            for i, contato in enumerate(com_email, 1):
                log.write(f"{i}. {contato['cliente']}\n")
                log.write(f"   Pedido: {contato['numero']}\n")
                log.write(f"   Email: {contato['email']}\n")
                log.write(f"   Rastreamento: {contato['etiqueta']}\n")
                log.write(f"   Status: Enviado\n\n")
            
            log.write("\n" + "="*70 + "\n")
            log.write(f"ESCOLAS SEM EMAIL ({len(sem_email)}):\n")
            log.write("-"*70 + "\n")
            for i, contato in enumerate(sem_email, 1):
                log.write(f"{i}. {contato['cliente']}\n")
                log.write(f"   Pedido: {contato['numero']}\n")
                log.write(f"   Email: (SEM EMAIL CADASTRADO)\n")
                log.write(f"   Rastreamento: {contato['etiqueta']}\n")
                log.write(f"   Status: Não enviado - sem email\n\n")
            
            log.write("\n" + "="*70 + "\n")
            log.write("RESUMO\n")
            log.write("="*70 + "\n")
            log.write(f"Total de emails enviados: {len(com_email)}\n")
            log.write(f"Total de escolas sem email: {len(sem_email)}\n")
            log.write(f"Arquivo criado: {nome_arquivo_log}\n")
        
        print(f"\n✅ Log detalhado salvo em: {nome_arquivo_log}")
        
    except Exception as e:
        print(f"\n❌ Erro ao criar log: {str(e)}")
