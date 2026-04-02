#!/usr/bin/env python3
import subprocess
import time
import os
from datetime import datetime

os.chdir('c:\\SISTEMAS\\envio-de-email-Allcanci')

print("="*70)
print("🚀 SISTEMA AUTOMÁTICO DE RASTREAMENTO")
print("="*70)
print("Rodando a cada 5 minutos...")
print("Pressione Ctrl+C para parar\n")

ciclo = 1

while True:
    try:
        print(f"\n{'='*70}")
        print(f"🔃 CICLO {ciclo} - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"{'='*70}\n")
        
        # Monitorar rastreamento
        print("📊 Monitorando Bling...")
        subprocess.run(['python', 'monitorar_rastreamento_bling.py'])
        
        # Enviar emails
        print("\n📧 Enviando emails...")
        subprocess.run(['python', 'enviar_emails_rastreamento.py'])
        
        print(f"\n⏳ Próximo ciclo em 5 minutos...")
        ciclo += 1
        time.sleep(300)
        
    except KeyboardInterrupt:
        print("\n\n❌ Sistema parado")
        break