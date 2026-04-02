#!/usr/bin/env python3
"""
🧪 TESTE DE ENVIO MANUAL
Simula envio para um cliente específico - visualize antes de ativar!
"""

import json
from datetime import datetime
from pathlib import Path

def formatar_email_html(numero, cliente, status, ultima_alt):
    """Formata HTML do email como será enviado"""
    data_fmt = datetime.now().strftime('%d/%m/%Y %H:%M')
    
    html = f'''<html>
<body style="font-family:Arial;background:#f5f5f5;padding:20px">
<div style="max-width:600px;margin:0 auto;background:white;border-radius:8px;padding:30px">
  <div style="background:linear-gradient(135deg,#0000F3 0%,#0051DB 100%);padding:30px;text-align:center;color:white;border-radius:6px;margin-bottom:30px">
    <h1 style="margin:0;font-size:26px">📬 Atualização de Rastreamento</h1>
  </div>
  <p style="font-size:16px;color:#333">Olá <strong>{cliente}</strong>,</p>
  <p style="font-size:16px;color:#555;margin:15px 0">Seu pedido teve uma atualização importante:</p>
  <div style="background:#4CAF50;padding:25px;border-radius:6px;margin:20px 0;color:white;text-align:center;font-size:20px;font-weight:bold;line-height:1.6">
    ✅ {status.upper()}
  </div>
  <div style="background:#f9f9f9;padding:20px;border-radius:6px;margin:20px 0;border-left:4px solid #0066cc">
    <p style="margin:10px 0"><strong>📦 Pedido:</strong> {numero}</p>
    <p style="margin:10px 0"><strong>🏷️ Rastreamento:</strong> {ultima_alt}</p>
    <p style="margin:10px 0"><strong>📅 Atualizado em:</strong> {data_fmt}</p>
    <p style="margin:10px 0"><strong>Descrição:</strong> {status}</p>
  </div>
  <div style="padding:15px;text-align:center;font-size:12px;color:#999;border-top:1px solid #e0e0e0">
    Email automático - Allcanci Rastreamento
  </div>
</div>
</body>
</html>'''
    return html

def formatar_whatsapp(numero, cliente, status, ultima_alt):
    """Formata mensagem WhatsApp como será enviada"""
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

_Allcanci_
    """.strip()
    
    return mensagem

def main():
    print("\n" + "=" * 70)
    print("🧪 TESTE DE ENVIO MANUAL")
    print("=" * 70 + "\n")
    
    # Carregar contatos
    try:
        with open('contatos_rastreamento.json', 'r', encoding='utf-8') as f:
            contatos = json.load(f)
    except Exception as e:
        print(f"❌ Erro ao carregar contatos: {e}")
        return
    
    # Encontrar "CAIXA ESCOLAR PADRE AFONSO DE LEMOS"
    cliente_teste = None
    for c in contatos:
        if "PADRE AFONSO" in c['cliente'].upper():
            cliente_teste = c
            break
    
    if not cliente_teste:
        print("❌ Cliente 'CAIXA ESCOLAR PADRE AFONSO DE LEMOS' não encontrado!")
        print("\nClientes disponíveis:")
        for c in contatos:
            print(f"  - {c['cliente']}")
        return
    
    # Dados do cliente
    numero = cliente_teste['numero']
    cliente = cliente_teste['cliente']
    email = cliente_teste.get('email', '')
    telefone = cliente_teste.get('telefone_celular', '')
    etiqueta = cliente_teste.get('etiqueta', '')
    ultima_situacao = cliente_teste.get('ultima_situacao', '')
    
    print(f"✅ Cliente encontrado: {cliente}")
    print(f"   • Pedido: {numero}")
    print(f"   • Email: {email}")
    print(f"   • Telefone: {telefone}")
    print(f"   • Etiqueta: {etiqueta}")
    print(f"   • Último Status: {ultima_situacao}\n")
    
    # Simular novo status
    novo_status = "Saiu para entrega ao destinatário"
    ultima_alt = etiqueta
    
    print("=" * 70)
    print("📨 PRÉVIA DO EMAIL")
    print("=" * 70 + "\n")
    
    html_email = formatar_email_html(numero, cliente, novo_status, ultima_alt)
    print("HTML DO EMAIL:")
    print("-" * 70)
    print(html_email)
    print("-" * 70)
    
    print("\n" + "=" * 70)
    print("📱 PRÉVIA DO WHATSAPP")
    print("=" * 70 + "\n")
    
    msg_whatsapp = formatar_whatsapp(numero, cliente, novo_status, ultima_alt)
    print("MENSAGEM WHATSAPP:")
    print("-" * 70)
    print(msg_whatsapp)
    print("-" * 70)
    
    # Resumo
    print("\n" + "=" * 70)
    print("📊 RESUMO DO TESTE")
    print("=" * 70)
    print(f"""
✅ Cliente: {cliente}
✅ Pedido: {numero}
✅ Status novo: {novo_status}

📧 Email será enviado para: {email if email else '⚠️ SEM EMAIL'}
📱 WhatsApp será enviado para: {telefone if telefone else '⚠️ SEM TELEFONE'}

{f'✅ Ambos os canais ativados!' if (email and telefone) else '⚠️ Alguns canais desativados'}
    """)
    
    print("=" * 70)
    print("✅ TESTE SIMULADO CONCLUÍDO")
    print("=" * 70)
    print("""
Para ativar o envio real, execute:
    python automatico_producao.py
    """)

if __name__ == "__main__":
    main()
