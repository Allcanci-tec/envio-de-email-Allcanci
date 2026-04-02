#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE 2: Enviar mensagem via Python + nosso sistema
Demonstra como usar a funcao enviar_mensagem() em sua aplicacao
"""

import json
from datetime import datetime
from whatsapp_service import enviar_mensagem

print()
print("="*70)
print("TESTE 2: ENVIO VIA SISTEMA (sem precisar do celular)")
print("="*70)
print()

# Dados da escola
numero_teste = "31984163357"
mensagem_teste = f"""[TESTE SISTEMA] {datetime.now().strftime('%d/%m/%Y %H:%M')}

Ola CAIXA ESCOLAR PADRE AFONSO DE LEMOS,

Esta eh uma mensagem enviada diretamente via nosso sistema de rastreamento.

Pedido: 2363
Rastreamento: AD287897978BR
Status: Saiu para entrega

Nao eh necessario ter o WhatsApp do celular aberto para receber esta mensagem.

---
Teste de Integracao - Sistema Allcanci Rastreamento
Projeto: envio-de-email-Allcanci
Teste via: import whatsapp_service"""

print("ENVIANDO MENSAGEM...")
print(f"Para: {numero_teste}")
print(f"Tamanho: {len(mensagem_teste)} caracteres")
print()

# Chamar a funcao
sucesso, mensagem = enviar_mensagem(
    numero=numero_teste,
    mensagem=mensagem_teste,
    headless=True  # Invisivel - rodando em background
)

print()
print("="*70)
print("RESULTADO:")
print("="*70)
print()

if sucesso:
    print(f"✓ SUCESSO!")
    print(f"  Mensagem: {mensagem}")
    print()
    print("A mensagem foi enviada com sucesso para o WhatsApp!")
    print()
    print("VERIFICACAO:")
    print("  1. Abra seu WhatsApp")
    print("  2. Procure pela conversa com CAIXA ESCOLAR PADRE AFONSO DE LEMOS")
    print("  3. Voce deve ver a mensagem que foi enviada agora")
else:
    print(f"✗ ERRO!")
    print(f"  Motivo: {mensagem}")
    print()
    print("Possíveis solucoes:")
    print("  1. Verifique conexao com internet")
    print("  2. Tente novamente em alguns segundos")
    print("  3. Execute: python limpar_sessao_whatsapp.py (para fazer login novamente)")

print()
print("="*70)
print("HISTORICO DE TESTES:")
print("="*70)
print()

# Carregar e mostrar historico
try:
    with open('whatsapp_envios.json', 'r', encoding='utf-8') as f:
        logs = json.load(f)
    
    print(f"Total de testes: {len(logs)}")
    print()
    
    # Ultimos 5 testes
    for i, log in enumerate(logs[-5:], 1):
        status = "✓" if log['sucesso'] else "✗"
        timestamp = log['timestamp'][:19]  # YYYY-MM-DD HH:MM:SS
        
        print(f"{i}. [{timestamp}] {status}")
        print(f"   Numero: {log['numero']}")
        print(f"   Mensagem: {log['mensagem'][:50]}...")
        
        if log['sucesso']:
            print(f"   Status: SUCESSO")
        else:
            print(f"   Erro: {log['erro']}")
        print()

except Exception as e:
    print(f"Erro ao carregar historico: {e}")

print("="*70)
print()
print("PROXIMOS PASSOS:")
print()
print("1. Integrar em seu sistema")
print("   from whatsapp_service import enviar_mensagem")
print()
print("2. Usar em automatico_producao.py")
print("   sucesso, msg = enviar_mensagem(numero, mensagem)")
print()
print("3. Enviar junto com emails")
print("   - Email: via Hostinger SMTP")
print("   - WhatsApp: via nosso sistema")
print()
print("="*70)
print()
