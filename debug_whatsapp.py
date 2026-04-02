#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEBUG: Teste WhatsApp com tela VISIVEL para diagnosticar problemas
Execute este arquivo para ver exatamente o que o navegador esta fazendo
"""

import os
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).parent
WHATSAPP_SESSION_DIR = BASE_DIR / 'whatsapp_session'

numero_whatsapp = "5531984163357"
mensagem_teste = "[TESTE] Mensagem de rastreamento"

print()
print("="*70)
print("DEBUG WHATSAPP - MODO VISIVEL")
print("="*70)
print()
print("Este script vai abrir o navegador VISIVEL para você ver o que está")
print("acontecendo durante o envio da mensagem.")
print()
print(f"Numero: {numero_whatsapp}")
print(f"Mensagem: {mensagem_teste}")
print()
print("INSTRUCOES:")
print("  1. O navegador vai abrir com a sessao salva")
print("  2. Se pedir QR Code, escaneie novamente")
print("  3. Deixe aberto por 1 minuto")
print("  4. Observe o que aparece na tela")
print()

url = f"https://web.whatsapp.com/send?phone={numero_whatsapp}&text={mensagem_teste}"

try:
    print("[1] Iniciando Playwright...")
    playwright = sync_playwright().start()
    
    print("[2] Abrindo navegador (VISIVEL)...")
    browser = playwright.chromium.launch_persistent_context(
        user_data_dir=str(WHATSAPP_SESSION_DIR),
        headless=False,  # VISIVEL
        args=['--no-sandbox', '--disable-setuid-sandbox'],
        slow_mo=100  # Desacelera para você ver melhor
    )
    
    page = browser.new_page()
    
    print("[3] Navegando para WhatsApp Web...")
    page.goto(url, wait_until='networkidle', timeout=30000)
    
    print("[4] Pagina carregada. Deixe aberto...")
    print()
    print("O que você esta vendo?")
    print("  A) Conversa aberta com campo de texto vazio?")
    print("  B) QR Code do WhatsApp Web?")
    print("  C) Mensagem 'Erro' ou 'Numero invalido'?")
    print()
    print("Aguardando 60 segundos para inspecao...")
    time.sleep(60)
    
    print("[5] Procurando botao de envio...")
    
    # Procurar diferentes seletores possiveis
    seletores = [
        'span[data-icon="send"]',
        'button[aria-label="Send"]',
        'button[aria-label="Enviar"]',
        'div[role="button"][aria-label*="send"]',
        'div[role="option"][role*="button"]',
    ]
    
    encontrado = False
    for seletor in seletores:
        try:
            elemento = page.wait_for_selector(seletor, timeout=5000)
            print(f"✓ Encontrou com seletor: {seletor}")
            encontrado = True
            break
        except:
            print(f"✗ Nao encontrou: {seletor}")
    
    if encontrado:
        print()
        print("[6] CLICANDO NO BOTAO DE ENVIO...")
        elemento.click()
        print("✓ Clicado!")
        time.sleep(5)
        print("✓ Mensagem enviada com sucesso!")
    else:
        print()
        print("✗ Nao conseguiu encontrar o botao de envio")
        print()
        print("DIAGNOSTICO:")
        print("Veja a tela do navegador para encontrar o botao.")
        print("Pode estar com outro seletor CSS.")
        print()
        print("Para encontrar o seletor correto:")
        print("  1. Abra o Developer Tools (F12 ou Ctrl+Shift+I)")
        print("  2. Procure pelo botao de envio (icone de seta/aviao)")
        print("  3. Clique com direita e escolha 'Inspect Element'")
        print("  4. Procure por 'span', 'button' ou 'div'")
        print("  5. Anote o data-icon, aria-label ou class")
        print("  6. Atualize o script com o novo seletor")
        print()
        time.sleep(30)
    
    print("[7] Fechando navegador...")
    page.close()
    browser.close()
    playwright.stop()
    
    print("✓ Pronto!")
    print()

except Exception as e:
    print(f"✗ ERRO: {e}")
    print()
    print("POSSIVEL SOLUCAO:")
    print("  - Delete a pasta 'whatsapp_session' e comece do zero")
    print("  - Rode este script novamente")
    print("  - Escaneie o QR Code com calma")

print()
