#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE DIRETO DE EMAIL - Enviar email de teste para rennifer10@gmail.com
Verificar se o email chega corretamente na caixa de entrada
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

print("\n" + "=" * 80)
print("TESTE DE ENTREGA DE EMAIL")
print("=" * 80 + "\n")

EMAIL_REMETENTE = os.getenv('EMAIL_USUARIO')
EMAIL_SENHA = os.getenv('EMAIL_SENHA')
EMAIL_SMTP = os.getenv('EMAIL_SMTP', 'smtp.hostinger.com')
EMAIL_PORTA = os.getenv('EMAIL_PORTA', '465')

# Dados do teste
email_destinatario = 'rennifer10@gmail.com'
assunto_teste = f'[TESTE ALLCANCI] Email de Teste {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}'
nome_vendedor = 'Maurício Ribeiro Júnior'

print(f"📧 Dados de Envio:")
print(f"   De: {EMAIL_REMETENTE}")
print(f"   Para: {email_destinatario}")
print(f"   Assunto: {assunto_teste}")
print(f"   SMTP: {EMAIL_SMTP}:{EMAIL_PORTA}\n")

try:
    # Criar mensagem
    msg = MIMEMultipart('alternative')
    msg['Subject'] = assunto_teste
    msg['From'] = EMAIL_REMETENTE
    msg['To'] = email_destinatario
    msg['X-Mailer'] = 'Allcanci Rastreamento Teste v1.0'
    
    # Conteúdo em texto plano
    texto_plano = f"""
TESTE DE EMAIL - ALLCANCI RASTREAMENTO

Olá {nome_vendedor},

Este é um email de TESTE para verificar se o sistema de notificações está funcionando.

Se você recebeu este email, significa que:
✅ O sistema está ENVIANDO EMAILS com sucesso
✅ O seu email está CADASTRADO corretamente
✅ As notificações de rastreamento chegarão normalmente

Dados do teste:
- Data/Hora: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
- Remetente: {EMAIL_REMETENTE}
- Assunto: {assunto_teste}

Quando houver atualização real de rastreamento, você receberá notificações similares.

Att,
Sistema Allcanci Rastreamento
    """.strip()
    
    # Conteúdo em HTML
    html_conteudo = f"""
<html>
<head>
    <meta charset="utf-8">
</head>
<body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
    <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; color: white; border-radius: 6px; margin-bottom: 30px;">
            <h1 style="margin: 0; font-size: 28px;">🧪 TESTE DE EMAIL</h1>
            <p style="margin: 10px 0 0 0; font-size: 14px; opacity: 0.9;">Verificação do Sistema de Notificações</p>
        </div>
        
        <!-- Conteúdo -->
        <p style="font-size: 16px; color: #333; margin: 0 0 20px 0;">
            Olá <strong>{nome_vendedor}</strong>,
        </p>
        
        <p style="font-size: 14px; color: #555; line-height: 1.6; margin: 0 0 20px 0;">
            Este é um email de <strong>TESTE</strong> para verificar se o sistema de notificações está funcionando corretamente.
        </p>
        
        <!-- Box de sucesso -->
        <div style="background-color: #E8F5E9; padding: 20px; border-radius: 6px; margin: 20px 0; border-left: 4px solid #4CAF50;">
            <p style="margin: 0 0 10px 0; color: #2E7D32;"><strong>✅ Se você recebeu este email:</strong></p>
            <ul style="margin: 0; padding-left: 20px; color: #2E7D32;">
                <li>✅ O sistema está <strong>ENVIANDO EMAILS</strong> corretamente</li>
                <li>✅ Seu email está <strong>CADASTRADO</strong> no sistema</li>
                <li>✅ As notificações de rastreamento <strong>CHEGARÃO</strong> normalmente</li>
            </ul>
        </div>
        
        <!-- Informações do teste -->
        <div style="background-color: #f9f9f9; padding: 20px; border-radius: 6px; margin: 20px 0; border-left: 4px solid #667eea;">
            <p style="margin: 0 0 10px 0; color: #333;"><strong>📋 Dados do Teste:</strong></p>
            <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                <tr>
                    <td style="padding: 5px 0; color: #666;"><strong>Data/Hora:</strong></td>
                    <td style="padding: 5px 0; color: #333;">{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</td>
                </tr>
                <tr style="background-color: #fafafa;">
                    <td style="padding: 5px 0; color: #666;"><strong>Remetente:</strong></td>
                    <td style="padding: 5px 0; color: #333;">{EMAIL_REMETENTE}</td>
                </tr>
                <tr>
                    <td style="padding: 5px 0; color: #666;"><strong>Servidor SMTP:</strong></td>
                    <td style="padding: 5px 0; color: #333;">{EMAIL_SMTP}</td>
                </tr>
                <tr style="background-color: #fafafa;">
                    <td style="padding: 5px 0; color: #666;"><strong>Tipo de Teste:</strong></td>
                    <td style="padding: 5px 0; color: #333;">Verificação de Entrega</td>
                </tr>
            </table>
        </div>
        
        <!-- Próximas etapas -->
        <div style="background-color: #FFF3E0; padding: 20px; border-radius: 6px; margin: 20px 0; border-left: 4px solid #FF9800;">
            <p style="margin: 0 0 10px 0; color: #E65100;"><strong>📌 Próximas Etapas:</strong></p>
            <p style="margin: 0; color: #E65100; font-size: 13px;">
                Quando houver atualização real de rastreamento de pedidos, você receberá notificações similares a este email automaticamente.
            </p>
        </div>
        
        <!-- Rodapé -->
        <div style="padding: 20px 0 0 0; text-align: center; border-top: 1px solid #e0e0e0; margin-top: 30px; font-size: 12px; color: #999;">
            <p style="margin: 0;">Sistema Allcanci - Notificações de Rastreamento</p>
            <p style="margin: 5px 0 0 0;">Este é um email automático. Não responda.</p>
        </div>
        
    </div>
</body>
</html>
    """
    
    # Anexar conteúdo
    msg.attach(MIMEText(texto_plano, 'plain', 'utf-8'))
    msg.attach(MIMEText(html_conteudo, 'html', 'utf-8'))
    
    # Conectar e enviar
    print("🔄 Conectando ao servidor SMTP...\n")
    
    server = smtplib.SMTP_SSL(EMAIL_SMTP, int(EMAIL_PORTA), timeout=10)
    print("✅ Conectado ao servidor SMTP")
    
    print("🔍 Autenticando...")
    server.login(EMAIL_REMETENTE, EMAIL_SENHA)
    print("✅ Autenticado com sucesso")
    
    print("📤 Enviando email...")
    server.send_message(msg)
    print("✅ Email enviado!\n")
    
    server.quit()
    
    # Sucesso
    print("=" * 80)
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 80 + "\n")
    
    print("📊 RESUMO:")
    print(f"   ✅ Email enviado para: {email_destinatario}")
    print(f"   ✅ Assunto: {assunto_teste}")
    print(f"   ✅ Hora de envio: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"   ✅ Status: SUCESSO\n")
    
    print("📬 PRÓXIMOS PASSOS:")
    print(f"   1. Verifique a caixa de entrada de: {email_destinatario}")
    print(f"   2. Procure por um email com assunto contendo '[TESTE ALLCANCI]'")
    print(f"   3. Se chegou = Sistema está funcionando ✅")
    print(f"   4. Se não chegou = Verificar spam ou configurações\n")
    
    print("=" * 80)
    print("💡 IMPORTANTE:")
    print("   Este email foi enviado pelo servidor:", EMAIL_SMTP)
    print("   Se não chegar em 5 minutos, verifique a pasta de SPAM/LIXO")
    print("=" * 80 + "\n")
    
except smtplib.SMTPAuthenticationError:
    print("❌ ERRO: Falha na autenticação")
    print("   Verifique as credenciais no arquivo .env")
    exit(1)

except smtplib.SMTPException as e:
    print(f"❌ ERRO SMTP: {e}")
    exit(1)

except Exception as e:
    print(f"❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
