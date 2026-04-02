import json
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def enviar_email_rastreamento(numero, cliente, email, rastreamento_data):
    """
    Envia email formatado com dados de rastreamento do Bling
    """
    EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE")
    EMAIL_SENHA = os.getenv("EMAIL_SENHA")
    
    if not EMAIL_REMETENTE or not EMAIL_SENHA:
        return False, "❌ Configure EMAIL_REMETENTE e EMAIL_SENHA no .env"
    
    if not email:
        return False, "❌ Email do cliente não preenchido"
    
    try:
        rastreamento = rastreamento_data
        codigo = rastreamento.get('codigo', 'N/A')
        descricao = rastreamento.get('descricao', 'N/A')
        origem = rastreamento.get('origem', 'N/A')
        destino = rastreamento.get('destino', 'N/A') or 'Na rota'
        ultima_alteracao = rastreamento.get('ultimaAlteracao', '')
        prazo = rastreamento.get('prazoEntregaPrevisto', 0)
        data_saida = rastreamento.get('dataSaida', '')
        url = rastreamento.get('url', '')
        
        # Formatar data/hora
        try:
            dt = datetime.fromisoformat(ultima_alteracao.replace(' ', 'T'))
            data_formatada = dt.strftime("%d/%m/%Y")
            hora_formatada = dt.strftime("%H:%M:%S")
        except:
            data_formatada = ultima_alteracao
            hora_formatada = ""
        
        # cores e status
        cores_status = {
            'Criado': '#FFA500',
            'Saiu para entrega': '#4CAF50',
            'Entregue': '#2196F3',
            'Devolvido': '#F44336',
            'Em trânsito': '#2196F3',
        }
        
        cor = next((v for k, v in cores_status.items() if k in descricao), '#FF9800')
        
        # Template HTML profissional
        html = f"""
        <html>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); overflow: hidden;">
                
                <!-- HEADER -->
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px 20px; text-align: center; color: white;">
                    <h1 style="margin: 0; font-size: 28px; font-weight: 600;">📦 Atualização de Rastreamento</h1>
                    <p style="margin: 10px 0 0 0; font-size: 14px; opacity: 0.9;">Seu pedido está a caminho!</p>
                </div>
                
                <!-- CONTEÚDO -->
                <div style="padding: 30px 20px;">
                    <!-- SAUDAÇÃO -->
                    <p style="font-size: 16px; color: #333; margin: 0 0 25px 0;">Olá <strong>{cliente}</strong>,</p>
                    
                    <!-- STATUS DESTAQUE -->
                    <div style="background-color: {cor}; padding: 20px; border-radius: 6px; margin-bottom: 25px; color: white; text-align: center;">
                        <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">Status Atual</div>
                        <div style="font-size: 20px; font-weight: 600;">{descricao}</div>
                    </div>
                    
                    <!-- INFORMAÇÕES DO PEDIDO -->
                    <div style="background-color: #f9f9f9; padding: 20px; border-radius: 6px; margin-bottom: 25px; border-left: 4px solid #667eea;">
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 10px 0; border-bottom: 1px solid #e0e0e0;">
                                    <span style="color: #666; font-size: 13px;">Número do Pedido</span><br>
                                    <span style="font-size: 16px; font-weight: 600; color: #333;">{numero}</span>
                                </td>
                                <td style="padding: 10px 0 10px 30px; border-bottom: 1px solid #e0e0e0;">
                                    <span style="color: #666; font-size: 13px;">Código de Rastreamento</span><br>
                                    <span style="font-size: 16px; font-weight: 600; color: #333;">{codigo}</span>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 10px 0;">
                                    <span style="color: #666; font-size: 13px;">Data de Saída</span><br>
                                    <span style="font-size: 14px; color: #333;">{data_saida}</span>
                                </td>
                                <td style="padding: 10px 0 10px 30px;">
                                    <span style="color: #666; font-size: 13px;">Prazo de Entrega</span><br>
                                    <span style="font-size: 14px; color: #333;">{prazo} dias</span>
                                </td>
                            </tr>
                        </table>
                    </div>
                    
                    <!-- LOCALIZAÇÃO -->
                    <div style="background-color: #f0f7ff; padding: 20px; border-radius: 6px; margin-bottom: 25px;">
                        <div style="font-size: 13px; color: #666; margin-bottom: 15px;">
                            <strong>Localização de Processamento:</strong>
                        </div>
                        <div style="font-size: 14px; color: #333; line-height: 1.8;">
                            <div style="margin-bottom: 10px;">
                                <span style="color: #667eea; font-weight: 600;">📍 Origem:</span> {origem}
                            </div>
                            <div>
                                <span style="color: #667eea; font-weight: 600;">🎯 Destino:</span> {destino}
                            </div>
                        </div>
                    </div>
                    
                    <!-- ÚLTIMA ATUALIZAÇÃO -->
                    <div style="background-color: #fff3cd; padding: 15px; border-radius: 6px; margin-bottom: 25px; border-left: 4px solid #ffc107;">
                        <div style="font-size: 12px; color: #856404;">
                            ⏰ <strong>Última Atualização:</strong> {data_formatada} às {hora_formatada}
                        </div>
                    </div>
                    
                    <!-- BOTÃO DE AÇÃO -->
                    <div style="text-align: center; margin-bottom: 25px;">
                        <a href="{url}" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; padding: 14px 32px; border-radius: 6px; font-weight: 600; font-size: 15px;">
                            🔍 Acompanhar Entrega em Tempo Real
                        </a>
                    </div>
                    
                    <!-- MENSAGEM -->
                    <div style="background-color: #e8f5e9; padding: 15px; border-radius: 6px; color: #2e7d32; font-size: 14px; line-height: 1.6;">
                        <strong>ℹ️ Informação Importante:</strong><br>
                        Fique atento ao seu telefone! O carteiro pode tentar fazer a entrega sem deixar aviso.
                    </div>
                </div>
                
                <!-- RODAPÉ -->
                <div style="background-color: #f5f5f5; padding: 20px; text-align: center; border-top: 1px solid #e0e0e0; font-size: 12px; color: #999;">
                    <p style="margin: 0;">Este é um email automático gerado pelo sistema de rastreamento.</p>
                    <p style="margin: 8px 0 0 0;">Se recebeu este email por engano, ignore-o.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Preparar email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"📦 Seu pedido {numero} - {descricao}"
        msg['From'] = EMAIL_REMETENTE
        msg['To'] = email
        
        # Versão em texto plano
        texto_plano = f"""
ATUALIZAÇÃO DE RASTREAMENTO

Olá {cliente},

Seu pedido {numero} foi atualizado!

Status Atual: {descricao}
Código de Rastreamento: {codigo}
Data de Saída: {data_saida}
Prazo de Entrega: {prazo} dias

Localização:
Origem: {origem}
Destino: {destino}

Última Atualização: {data_formatada} às {hora_formatada}

Acompanhe em tempo real em: {url}
        """
        
        msg.attach(MIMEText(texto_plano, 'plain'))
        msg.attach(MIMEText(html, 'html'))
        
        # Enviar
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(EMAIL_REMETENTE, EMAIL_SENHA)
        server.send_message(msg)
        server.quit()
        
        return True, f"✅ Email enviado com sucesso para {email}!"
    
    except Exception as e:
        return False, f"❌ Erro ao enviar email: {str(e)}"

def processar_e_enviar_emails():
    """
    Processa arquivo de rastreamentos atualizados e envia emails
    """
    print("\n📧 ENVIANDO EMAILS COM RASTREAMENTO ATUALIZADO\n")
    
    arquivo = 'rastreamentos_atualizados_bling.json'
    
    if not os.path.exists(arquivo):
        print(f"❌ Arquivo {arquivo} não encontrado!")
        print("Execute primeiro: python monitorar_rastreamento_bling.py")
        return
    
    with open(arquivo, 'r', encoding='utf-8') as f:
        rastreamentos = json.load(f)
    
    emails_enviados = 0
    emails_falhados = 0
    
    for rastr in rastreamentos:
        if not rastr['deve_enviar_email']:
            print(f"\n⚠️  Pedido {rastr['numero']} - Sem email para enviar")
            continue
        
        print(f"\n{'='*70}")
        print(f"📬 Enviando email - Pedido {rastr['numero']}")
        print(f"   Cliente: {rastr['cliente']}")
        print(f"   Email: {rastr['email']}")
        print(f"   Status: {rastr['rastreamento']['descricao']}")
        
        sucesso, mensagem = enviar_email_rastreamento(
            rastr['numero'],
            rastr['cliente'],
            rastr['email'],
            rastr['rastreamento']
        )
        
        if sucesso:
            print(f"   ✅ {mensagem}")
            emails_enviados += 1
        else:
            print(f"   {mensagem}")
            emails_falhados += 1
    
    print(f"\n\n{'='*70}")
    print(f"📊 RESUMO:")
    print(f"   ✅ Enviados: {emails_enviados}")
    print(f"   ❌ Falhados: {emails_falhados}")
    print(f"   Total: {len(rastreamentos)}")
    print(f"{'='*70}")

if __name__ == "__main__":
    processar_e_enviar_emails()
