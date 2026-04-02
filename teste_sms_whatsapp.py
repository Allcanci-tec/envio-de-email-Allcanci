#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE DE ENVIO DE SMS/WHATSAPP - RASTREAMENTO
Envia mensagem de rastreamento para o celular da escola
Teste com: CAIXA ESCOLAR PADRE AFONSO DE LEMOS
"""

import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configurações para diferentes provedores (descomente o que usar)
USAR_TWILIO = False  # SMS via Twilio
USAR_WHATSAPP = False  # WhatsApp via twilio-whatsapp
USAR_MOCK = True  # Apenas exibir a mensagem (para teste)

# Se usar Twilio, instale: pip install twilio
# Se usar WhatsApp nativo, configure credenciais

def carregar_contato_teste():
    """Carrega dados da escola CAIXA ESCOLAR PADRE AFONSO DE LEMOS"""
    try:
        with open('contatos_rastreamento.json', 'r', encoding='utf-8') as f:
            contatos = json.load(f)
        
        # Procura pela escola específica
        for c in contatos:
            if c['numero'] == 2363:  # Pedido da CAIXA ESCOLAR PADRE AFONSO DE LEMOS
                return c
        
        print("❌ Escola não encontrada no JSON")
        return None
    except FileNotFoundError:
        print("❌ Arquivo contatos_rastreamento.json não encontrado")
        return None


def formatar_mensagem_sms(contato, status_exemplo="Saiu para entrega ao destinatario"):
    """Formata mensagem SMS curta para caber nos limites"""
    pedido = contato['numero']
    etiqueta = contato['etiqueta']
    cliente = contato['cliente'].split()[0]  # Primeiro nome
    
    mensagem = f"""[RASTREAMENTO] - Atualizacao

Ola {cliente},

Sua encomenda {pedido} foi atualizada!

{status_exemplo}

Rastreamento: {etiqueta}

Acompanhe via Correios:
https://www.correios.com.br/rastreamento
"""
    return mensagem


def formatar_mensagem_whatsapp(contato, status_exemplo="Saiu para entrega ao destinatario"):
    """Formata mensagem WhatsApp (pode ser mais longa)"""
    pedido = contato['numero']
    etiqueta = contato['etiqueta']
    cliente = contato['cliente']
    data_fmt = datetime.now().strftime('%d/%m/%Y %H:%M')
    
    mensagem = f"""[ATUALIZACAO DE RASTREAMENTO]

Ola {cliente},

Sua encomenda recebeu uma atualizacao importante!

---
{status_exemplo.upper()}
---

Detalhes:
- Pedido: {pedido}
- Rastreamento: {etiqueta}
- Atualizado: {data_fmt}

Rastrear agora:
https://www.correios.com.br/rastreamento

---
Allcanci Rastreamento
"""
    return mensagem


def enviar_via_twilio(telefone, mensagem):
    """Envia SMS via Twilio"""
    try:
        from twilio.rest import Client
        
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        twilio_number = os.getenv('TWILIO_FROM_NUMBER')
        
        if not all([account_sid, auth_token, twilio_number]):
            return False, "Credenciais Twilio não configuradas no .env"
        
        client = Client(account_sid, auth_token)
        msg = client.messages.create(
            body=mensagem,
            from_=twilio_number,
            to=telefone
        )
        
        return True, f"SMS enviado! SID: {msg.sid}"
    except ImportError:
        return False, "Twilio nao instalado. Execute: pip install twilio"
    except Exception as e:
        return False, f"Erro Twilio: {str(e)}"


def enviar_via_whatsapp(telefone, mensagem):
    """Envia WhatsApp via Twilio"""
    try:
        from twilio.rest import Client
        
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        twilio_whatsapp = os.getenv('TWILIO_WHATSAPP_NUMBER')
        
        if not all([account_sid, auth_token, twilio_whatsapp]):
            return False, "Credenciais WhatsApp Twilio não configuradas no .env"
        
        # Formata número para WhatsApp (adiciona whatsapp: prefixo)
        telefone_wa = f"whatsapp:+55{telefone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')}"
        
        client = Client(account_sid, auth_token)
        msg = client.messages.create(
            body=mensagem,
            from_=f"whatsapp:{twilio_whatsapp}",
            to=telefone_wa
        )
        
        return True, f"WhatsApp enviado! SID: {msg.sid}"
    except Exception as e:
        return False, f"Erro WhatsApp: {str(e)}"


def enviar_mock(telefone, mensagem):
    """Apenas exibe a mensagem (teste sem enviar mesmo)"""
    return True, "(TESTE) Mensagem pronta para enviar"


def main():
    print("\n" + "="*70)
    print("TESTE DE ENVIO DE SMS/WHATSAPP - RASTREAMENTO")
    print("="*70)
    
    # Carrega dados da escola
    contato = carregar_contato_teste()
    if not contato:
        return
    
    telefone = contato.get('telefone_celular', '').strip()
    if not telefone or telefone == 'N/A':
        print(f"ERRO: Escola nao tem telefone cadastrado")
        return
    
    print(f"\nDados da Escola:")
    print(f"  Nome: {contato['cliente']}")
    print(f"  Pedido: {contato['numero']}")
    print(f"  Rastreamento: {contato['etiqueta']}")
    print(f"  Telefone: {telefone}")
    
    # Define status de exemplo
    status_exemplo = "Saiu para entrega ao destinatario"
    
    print(f"\nFormatando mensagens...")
    
    # Formata mensagens
    msg_sms = formatar_mensagem_sms(contato, status_exemplo)
    msg_whatsapp = formatar_mensagem_whatsapp(contato, status_exemplo)
    
    print(f"\n{'='*70}")
    print("VERSAO SMS (caracteres: {})".format(len(msg_sms)))
    print("="*70)
    print(msg_sms)
    
    print(f"\n{'='*70}")
    print("VERSAO WHATSAPP (caracteres: {})".format(len(msg_whatsapp)))
    print("="*70)
    print(msg_whatsapp)
    
    # Tenta enviar (conforme configurado)
    print(f"\n{'='*70}")
    print("TENTANDO ENVIAR...")
    print("="*70)
    
    if USAR_TWILIO:
        print("\nEnviando via SMS Twilio...")
        sucesso, msg = enviar_via_twilio(telefone, msg_sms)
        print(f"   {msg}")
    
    elif USAR_WHATSAPP:
        print("\nEnviando via WhatsApp Twilio...")
        sucesso, msg = enviar_via_whatsapp(telefone, msg_whatsapp)
        print(f"   {msg}")
    
    elif USAR_MOCK:
        print("\nMODO TESTE (sem enviar realmente)")
        sucesso, msg = enviar_mock(telefone, msg_whatsapp)
        print(f"   {msg}")
    
    # Instruções para ativar
    print(f"\n{'='*70}")
    print("COMO USAR:")
    print("="*70)
    
    print("""
1. Para usar SMS via Twilio:
   - Instale: pip install twilio
   - Adicione ao .env:
     TWILIO_ACCOUNT_SID=seu_account_sid
     TWILIO_AUTH_TOKEN=seu_auth_token
     TWILIO_FROM_NUMBER=+1234567890
   - Altere USAR_TWILIO = True no script

2. Para usar WhatsApp via Twilio:
   - Mesmo setup do Twilio acima
   - Adicione ao .env:
     TWILIO_WHATSAPP_NUMBER=seu_numero_whatsapp
   - Altere USAR_WHATSAPP = True no script

3. Para testar sem enviar:
   - Deixe USAR_MOCK = True (padrao)
   - Execute: python teste_sms_whatsapp.py
   - Veja como fica a mensagem

4. Depois de funcionar neste teste:
   - Integre a funcao enviar_sms() em automatico_producao.py
    """)
    
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
