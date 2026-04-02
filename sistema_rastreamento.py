#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SISTEMA DE MONITORAMENTO DE RASTREAMENTO - ESTRATÉGIA VENCEDORA

Fluxo:
1. Consulta dados de rastreamento do Bling via: GET /logisticas/objetos/{idObjeto}
2. Detecta atualizações comparando ultimaAlteracao com histórico
3. Envia email formatado com dados sincronizados quando há mudança
4. Salva histórico para próximas execuções

Dados retornados pelo Bling:
- codigo: Etiqueta (ex: AD287897978BR)
- descricao: Status (ex: Saiu para entrega ao destinatário)
- situacao: Número do status
- origem: Local de saída
- destino: Local de chegada
- ultimaAlteracao: Timestamp de sincronização (2026-04-01 11:07:55)
- url: Link de rastreamento
"""

import json
import os
import requests
from dotenv import load_dotenv
from datetime import datetime
import subprocess
import sys

load_dotenv()

ACCESS_TOKEN = None

def carregar_token():
    global ACCESS_TOKEN
    if os.path.exists('tokens.json'):
        with open('tokens.json', 'r') as f:
            tokens = json.load(f)
            ACCESS_TOKEN = tokens.get('access_token')
            return True
    return False

def obter_rastreamento_bling(volume_id):
    """Busca dados sincronizados do Bling via GET /logisticas/objetos/{idObjeto}"""
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    response = requests.get(
        f"https://api.bling.com.br/v3/logisticas/objetos/{volume_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json().get('data', {})
    return None

def main():
    print("\n" + "="*70)
    print("🚀 SISTEMA DE MONITORAMENTO DE RASTREAMENTO")
    print("   Estratégia: Consultar Bling e enviar emails automaticamente")
    print("="*70 + "\n")
    
    # Carregar token
    if not carregar_token():
        print("❌ Erro: Arquivo tokens.json não encontrado")
        print("   Execute: python bling_auth.py")
        return
    
    print("✅ Token carregado com sucesso\n")
    
    # PASSO 1: Monitorar rastreamento
    print("PASSO 1: Consultando Bling para atualizações de rastreamento...")
    print("-" * 70)
    resultado = subprocess.run(['python', 'monitorar_rastreamento_bling.py'], 
                              capture_output=True, text=True)
    print(resultado.stdout)
    
    if resultado.returncode != 0:
        print(f"❌ Erro ao monitorar: {resultado.stderr}")
        return
    
    # PASSO 2: Enviar emails
    if os.path.exists('rastreamentos_atualizados_bling.json'):
        with open('rastreamentos_atualizados_bling.json', 'r', encoding='utf-8') as f:
            rastreamentos = json.load(f)
        
        if rastreamentos:
            print("\n\nPASSO 2: Preparando envio de emails...")
            print("-" * 70)
            
            # Verificar credenciais
            EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE")
            EMAIL_SENHA = os.getenv("EMAIL_SENHA")
            
            if not EMAIL_REMETENTE or not EMAIL_SENHA:
                print("\n⚠️  ATENÇÃO: Credenciais de email não configuradas!")
                print("\n📧 Para ativar o envio de emails, configure no .env:")
                print("   EMAIL_REMETENTE=seu_email@gmail.com")
                print("   EMAIL_SENHA=sua_app_password")
                print("\n💡 Gere uma app password em: https://myaccount.google.com/apppasswords")
                print("\n" + "-" * 70)
                print(f"ℹ️  {len(rastreamentos)} rastreamento(s) com atualização estão prontos!")
                print("   Dados salvos em: rastreamentos_atualizados_bling.json")
                print("\n   Quando configurar as credenciais, execute:")
                print("   python enviar_emails_rastreamento.py")
            else:
                print("✅ Credenciais de email configuradas")
                resultado = subprocess.run(['python', 'enviar_emails_rastreamento.py'],
                                          capture_output=True, text=True)
                print(resultado.stdout)
    else:
        print("\n✅ Monitoramento concluído - Nenhuma atualização nova detectada")
    
    print("\n" + "="*70)
    print("✅ Ciclo de monitoramento concluído!")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
