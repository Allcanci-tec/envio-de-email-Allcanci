#!/usr/bin/env python3
"""
Script final: Obtém rastreamento completo + envia email formatado
"""

import json
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def enviar_email_rastreamento_completo(numero, cliente, email, telefone, etiqueta, dados_rastreamento):
    """Envia email com rastreamento detalhado formatado"""
    
    EMAIL_REMETENTE = os.getenv('EMAIL_REMETENTE')
    EMAIL_SENHA = os.getenv('EMAIL_SENHA')
    
    if not EMAIL_REMETENTE or not EMAIL_SENHA:
        return False, "Configure EMAIL_REMETENTE e EMAIL_SENHA no .env"
    
    try:
        # Monta eventos em HTML
        eventos_html = ""
        for evt in dados_rastreamento.get('eventos', []):
            eventos_html += f"""
            <div style="border-left: 4px solid #0066cc; padding: 15px; margin: 10px 0; background: #f9f9f9;">
                <p style="margin: 5px 0; font-weight: bold; color: #0066cc;">
                    {evt.get('data')} às {evt.get('hora')}
                </p>
                <p style="margin: 5px 0; font-weight: bold; color: #333;">
                    {evt.get('status')}
                </p>
                <p style="margin: 5px 0; color: #666;">
                    📍 {evt.get('local')}
                </p>
                {f'<p style="margin: 5px 0; color: #666; font-size: 0.9em;">ℹ️ {evt.get("detalhes")}</p>' if evt.get('detalhes') else ''}
            </div>
            """
        
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                <div style="background-color: white; padding: 30px; border-radius: 8px; max-width: 700px; margin: 0 auto;">
                    
                    <h2 style="color: #333; border-bottom: 3px solid #0066cc; padding-bottom: 10px;">
                        📦 Atualização de Rastreamento
                    </h2>
                    
                    <p style="color: #555; font-size: 16px;">
                        Olá <strong>{cliente}</strong>,
                    </p>
                    
                    <p style="color: #555; font-size: 14px;">
                        Seu pedido teve uma atualização! Confira abaixo:
                    </p>
                    
                    <!-- Status em destaque -->
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <p style="margin: 5px 0; font-size: 12px; opacity: 0.9;">STATUS ATUAL</p>
                        <p style="margin: 5px 0; font-size: 20px; font-weight: bold;">
                            {dados_rastreamento.get('status_atual', 'Em processamento')}
                        </p>
                        <p style="margin: 5px 0; font-size: 12px; opacity: 0.9;">
                            ⏰ Previsão: {dados_rastreamento.get('previsao_entrega', 'A ser atualizado')}
                        </p>
                    </div>
                    
                    <!-- Informações do Pedido -->
                    <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>📋 Pedido:</strong> {numero}</p>
                        <p><strong>🏷️ Rastreamento:</strong> <span style="color: #0066cc; font-family: monospace; font-weight: bold;">{etiqueta}</span></p>
                        <p><strong>📞 Dúvidas:</strong> {telefone}</p>
                    </div>
                    
                    <!-- Histórico de eventos -->
                    <h3 style="color: #333; margin-top: 30px; margin-bottom: 15px;">
                        📍 Histórico de Eventos
                    </h3>
                    
                    {eventos_html}
                    
                    <!-- Link para rastreamento -->
                    <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
                        <p style="color: #666; font-size: 12px; margin: 10px 0;">
                            Rastreie em tempo real:
                        </p>
                        <a href="https://www.correios.com.br/rastreamento?numero={etiqueta}" 
                           style="display: inline-block; background-color: #0066cc; color: white; padding: 12px 24px; border-radius: 5px; text-decoration: none; font-weight: bold;">
                            Acompanhar Entrega
                        </a>
                    </div>
                    
                    <p style="color: #999; font-size: 11px; text-align: center; margin-top: 30px;">
                        Email automático enviado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}
                    </p>
                </div>
            </body>
        </html>
        """
        
        # Prepara mensagem
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"📦 {dados_rastreamento.get('status_atual', 'Atualização')} - Pedido {numero}"
        msg['From'] = EMAIL_REMETENTE
        msg['To'] = email
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # Envia
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(EMAIL_REMETENTE, EMAIL_SENHA)
        server.send_message(msg)
        server.quit()
        
        return True, "✅ Email enviado com sucesso!"
        
    except Exception as e:
        return False, f"❌ Erro: {str(e)}"


if __name__ == "__main__":
    # Carrega dados
    with open('contatos_rastreamento.json', 'r', encoding='utf-8') as f:
        contatos = json.load(f)
    
    with open('rastreamento_detalhado.json', 'r', encoding='utf-8') as f:
        rastreamento = json.load(f)
    
    # Encontra contato correspondente
    contato = next((c for c in contatos if c['etiqueta'] == rastreamento['etiqueta']), None)
    
    if not contato:
        print("❌ Contato não encontrado")
        exit(1)
    
    print("\n" + "="*70)
    print("✉️  TESTE DE EMAIL COM RASTREAMENTO DETALHADO")
    print("="*70 + "\n")
    
    print(f"📧 Para: {contato['cliente']}")
    print(f"📬 Email: {contato['email']}\n")
    
    sucesso, msg = enviar_email_rastreamento_completo(
        numero=contato['numero'],
        cliente=contato['cliente'],
        email=contato['email'],
        telefone=contato['telefone_celular'],
        etiqueta=contato['etiqueta'],
        dados_rastreamento=rastreamento
    )
    
    print(msg)
    
    if not sucesso and "Configure" in msg:
        print("\n⚠️  Configure no .env:")
        print("EMAIL_REMETENTE=seu_email@gmail.com")
        print("EMAIL_SENHA=sua_app_password\n")
