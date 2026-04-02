#!/usr/bin/env python3
"""
🧪 TESTE DE ENVIO MANUAL - ATUALIZADO
Sempre carrega dados FRESCOS do arquivo
Simula envio para um cliente específico
"""

import json
from datetime import datetime

def carregar_cliente_fresco(numero_cliente=2363):
    """Carrega dados FRESCOS do arquivo JSON"""
    try:
        with open('contatos_rastreamento.json', 'r', encoding='utf-8') as f:
            contatos = json.load(f)
        
        # Encontrar cliente por número
        for c in contatos:
            if c['numero'] == numero_cliente:
                return c
        
        return None
    except Exception as e:
        print(f"❌ Erro ao carregar: {e}")
        return None

def formatar_email_html(numero, cliente, status, ultima_alt):
    """Formata HTML do email"""
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
    """Formata mensagem WhatsApp"""
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
    print("🧪 TESTE DE ENVIO MANUAL - CARREGAR DADOS FRESCOS")
    print("=" * 70 + "\n")
    
    # Carregar cliente SEMPRE FRESCO do arquivo
    print("📂 Carregando dados do arquivo contatos_rastreamento.json...")
    cliente_teste = carregar_cliente_fresco(numero_cliente=2363)
    
    if not cliente_teste:
        print("❌ Cliente com pedido #2363 (PADRE AFONSO) não encontrado!")
        return
    
    # Dados atualizados
    numero = cliente_teste['numero']
    cliente = cliente_teste['cliente']
    email = cliente_teste.get('email', '')
    telefone = cliente_teste.get('telefone_celular', '')
    etiqueta = cliente_teste.get('etiqueta', '')
    ultima_situacao = cliente_teste.get('ultima_situacao', '')
    
    print(f"\n✅ Cliente carregado com DADOS FRESCOS:")
    print(f"   • Nome: {cliente}")
    print(f"   • Pedido: {numero}")
    print(f"   • Email: {email if email else '❌ SEM EMAIL'}")
    print(f"   • Telefone: {telefone if telefone else '❌ SEM TELEFONE'}")
    print(f"   • Etiqueta: {etiqueta}")
    print(f"   • Último Status: {ultima_situacao}\n")
    
    # Simular novo status
    novo_status = "Saiu para entrega ao destinatário"
    ultima_alt = etiqueta
    
    # EMAIL
    print("\n" + "=" * 70)
    print("📧 PRÉVIA DO EMAIL")
    print("=" * 70 + "\n")
    
    if email:
        html_email = formatar_email_html(numero, cliente, novo_status, ultima_alt)
        print("SERÁ ENVIADO PARA:", email)
        print("\nCONTEÚDO HTML:")
        print("-" * 70)
        print(html_email)
        print("-" * 70)
    else:
        print("❌ SEM EMAIL - Email NÃO será enviado")
    
    # WHATSAPP
    print("\n" + "=" * 70)
    print("📱 PRÉVIA DO WHATSAPP")
    print("=" * 70 + "\n")
    
    if telefone and telefone != 'N/A':
        msg_whatsapp = formatar_whatsapp(numero, cliente, novo_status, ultima_alt)
        print("SERÁ ENVIADO PARA:", telefone)
        print("\nCONTEÚDO DA MENSAGEM:")
        print("-" * 70)
        print(msg_whatsapp)
        print("-" * 70)
    else:
        print("❌ SEM TELEFONE - WhatsApp NÃO será enviado")
    
    # RESUMO
    print("\n" + "=" * 70)
    print("📊 RESUMO DO TESTE")
    print("=" * 70)
    
    tem_email = bool(email)
    tem_telefone = bool(telefone) and telefone != 'N/A'
    
    print(f"""
Cliente: {cliente}
Pedido: {numero}
Novo Status: {novo_status}

🔔 NOTIFICAÇÕES A ENVIAR:
   {'✅ EMAIL' if tem_email else '❌ EMAIL'}
   {'✅ WHATSAPP' if tem_telefone else '❌ WHATSAPP'}
    """)
    
    if tem_email and tem_telefone:
        print("✨ AMBOS OS CANAIS ATIVADOS - Cliente receberá notificação dupla!")
    elif tem_email:
        print("⚠️ Apenas EMAIL - Sem telefone para WhatsApp")
    elif tem_telefone:
        print("⚠️ Apenas WHATSAPP - Sem email para notificação por email")
    else:
        print("❌ NENHUM CANAL - Cliente não receberá notificação")
    
    print("\n" + "=" * 70)
    print("✅ TESTE SIMULADO - DADOS CARREGADOS COM SUCESSO")
    print("=" * 70)
    print("""
Se os dados estão corretos, execute:

    python automatico_producao.py

Isso ativará o envio automático REAL!
    """)


if __name__ == "__main__":
    main()
