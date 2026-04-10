#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Demonstração: Como a formatação de telefone funciona com automatico_producao.py

Este script mostra como a função formatar_numero_telefone() trata números
que vêm do Bling com diferentes formatos.
"""

from whatsapp_service import formatar_numero_telefone, validar_numero_telefone
import json


def demonstrar_formatacao():
    """Demonstra formatação de números de contato."""
    
    print("\n" + "=" * 80)
    print("DEMONSTRAÇÃO: FORMATAÇÃO DE NÚMEROS DO BLING")
    print("=" * 80)
    print()
    
    # Simula números como vêm do Bling
    numeros_do_bling = [
        "31984163357",           # Sem formatação, sem país
        "(31) 98416-3357",       # Com formatação humana
        "31 98416-3357",         # Espaços
        "5531984163357",         # Já com país
        "+55 (31) 98416-3357",   # Com país e formatação
        "31900000001",           # Antigo (10 dígitos?)
        "319840000001",          # 11 dígitos
        "",                      # Vazio
        "N/A",                   # Invalido
    ]
    
    print("Simulando números que vêm de contatos_rastreamento.json / Bling:\n")
    
    for numero_original in numeros_do_bling:
        numero_formatado = formatar_numero_telefone(numero_original)
        valido = validar_numero_telefone(numero_original)
        
        status = "✅ VÁLIDO" if valido else "❌ INVÁLIDO"
        formatado_str = f"→ {numero_formatado}" if numero_formatado else "→ (rejeitado)"
        
        print(f"{status}")
        print(f"  Original:  '{numero_original}'")
        print(f"  Resultado: '{numero_formatado}'")
        print()
    
    print()
    print("=" * 80)
    print("FLUXO DE INTEGRAÇÃO COM AUTOMATICO_PRODUCAO.PY")
    print("=" * 80)
    print("""
    1. automatico_producao.py lê contatos_rastreamento.json
       └─ campo "telefone_celular" pode ter diferentes formatos
    
    2. Chama: enviar_whatsapp_notificacao(numero, cliente, telefone, ...)
       └─ whatsapp_service.enviar_mensagem(numero) recebe o número
    
    3. A função formatar_numero_telefone() normaliza:
       ✅ "(31) 98416-3357" → "5531984163357"
       ✅ "31984163357"     → "5531984163357"  
       ✅ "+55 31 9..."     → "5531984163357"
       ❌ "123"            → rejeita
       ❌ "abc"            → rejeita
    
    4. Envios são feitos apenas com números válidos:
       └─ Inválidos são logados e descartados (não vão pra fila)
    
    BENEFÍCIOS:
    • Números vêm do Bling sem formatação consistente → agora são tratados
    • Evita erros de envio por formato errado
    • Log claro mostra original vs. formatado
    • Inválidos são bloqueados antes do WhatsApp Web
    """)
    
    print()


def demonstrar_atualizacao_contatos():
    """Mostra como corrigir contatos_rastreamento.json."""
    
    print("=" * 80)
    print("CORRIGINDO CONTATOS_RASTREAMENTO.JSON")
    print("=" * 80)
    print("""
    OPÇÃO 1: Manter números no formato original
    ───────
    A formatação acontece AUTOMATICAMENTE no envio.
    Você pode deixar contatos_rastreamento.json como está:
    
    {
        "numero": "1234",
        "cliente": "Escola xxx",
        "email": "contato@xxx",
        "telefone_celular": "(31) 98416-3357",  ← Qualquer formato
        "vendedor_nome": "Israel"
    }
    
    Quando automatico_producao.py enviar, a função formatar_numero_telefone()
    normalizará automaticamente para "5531984163357".
    
    
    OPÇÃO 2: Normalizar para o padrão (RECOMENDADO)
    ───────────────────────────────
    Execute este script para limpar contatos_rastreamento.json:
    
        from test_normalizar_contatos import normalizar_contatos_arquivo
        normalizar_contatos_arquivo('contatos_rastreamento.json')
    
    Isso versará todos os números para "55DDNNNNNNNNN" no arquivo.
    
    
    RECOMENDAÇÃO:
    → Opção 2 é melhor para visibilidade e debug
    → Todos os números ficarão padronizados no arquivo
    → Logs mostrarão números já corretos
    """)
    
    print()


if __name__ == "__main__":
    demonstrar_formatacao()
    demonstrar_atualizacao_contatos()
    
    print("\n" + "=" * 80)
    print("Para testar: python test_formatar_telefone.py")
    print("=" * 80 + "\n")
