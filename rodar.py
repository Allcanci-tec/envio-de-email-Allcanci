#!/usr/bin/env python3
import subprocess
import time
import os
import json
from datetime import datetime
from pathlib import Path

os.chdir('c:\\SISTEMAS\\envio-de-email-Allcanci')

print("="*70)
print("🚀 SISTEMA AUTOMÁTICO - EMAIL + RASTREAMENTO + WHATSAPP")
print("="*70)
print("Rodando a cada 5 minutos...")
print("Pressione Ctrl+C para parar\n")

ciclo = 1

# Verificar se há config de rastreamentos
CONFIG_RASTREAMENTOS = Path('config_rastreamentos.json')
RASTREAMENTOS = []

if CONFIG_RASTREAMENTOS.exists():
    try:
        with open(CONFIG_RASTREAMENTOS, 'r', encoding='utf-8') as f:
            config = json.load(f)
            RASTREAMENTOS = config.get('rastreamentos', [])
            print(f"✅ {len(RASTREAMENTOS)} rastreamentos configurados para WhatsApp\n")
    except Exception as e:
        print(f"⚠️  Erro ao carregar configuração: {e}\n")

while True:
    try:
        print(f"\n{'='*70}")
        print(f"🔃 CICLO {ciclo} - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"{'='*70}\n")
        
        # 1. Monitorar rastreamento Bling
        print("📊 Monitorando Bling...")
        subprocess.run(['python', 'monitorar_rastreamento_bling.py'])
        
        # 2. Enviar emails
        print("\n📧 Enviando emails...")
        subprocess.run(['python', 'enviar_emails_rastreamento.py'])
        
        # 3. Notificar via WhatsApp
        if RASTREAMENTOS:
            print("\n💬 Notificando clientes via WhatsApp...")
            try:
                from notificador_rastreamento import notificar_lote
                stats = notificar_lote(RASTREAMENTOS)
                print(f"   📊 {stats['notificacoes_enviadas']} notificações enviadas\n")
            except Exception as e:
                print(f"   ⚠️  Erro ao enviar notificações: {e}\n")
        
        print(f"⏳ Próximo ciclo em 5 minutos...")
        ciclo += 1
        time.sleep(300)
        
    except KeyboardInterrupt:
        print("\n\n❌ Sistema parado")
        break