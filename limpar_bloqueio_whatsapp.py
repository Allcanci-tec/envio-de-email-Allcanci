#!/usr/bin/env python3
"""
🧪 TESTE - LIMPA ANTI-SPAM E FORÇA ENVIO WHATSAPP
Remove bloqueio de 24h para teste
"""

import json
from pathlib import Path

def limpar_anti_spam_numero(numero_para_limpar="5531984163357"):
    """Remove o número do histórico anti-spam"""
    
    stats_file = Path('whatsapp_stats.json')
    
    if not stats_file.exists():
        print(f"⚠️ Arquivo {stats_file} não encontrado")
        return False
    
    try:
        with open(stats_file, 'r', encoding='utf-8') as f:
            stats = json.load(f)
        
        # Remover número do histórico
        if numero_para_limpar in stats.get('historico_contatos', {}):
            del stats['historico_contatos'][numero_para_limpar]
            print(f"✅ Removido do histórico: {numero_para_limpar}")
        else:
            print(f"ℹ️ Número não encontrado no histórico: {numero_para_limpar}")
        
        # Salvar
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print("✅ Anti-spam limpo com sucesso!\n")
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def processar_fila_whatsapp():
    """Processa a fila de WhatsApp imediatamente"""
    
    try:
        print("=" * 70)
        print("📤 PROCESSANDO FILA DE WHATSAPP")
        print("=" * 70 + "\n")
        
        from whatsapp_service import processar_fila, status_fila
        
        status_antes = status_fila()
        print(f"Status ANTES: {status_antes}\n")
        
        print("⏳ Processando fila...")
        processar_fila(max_envios=10)  # Processa até 10 mensagens
        
        status_depois = status_fila()
        print(f"\nStatus DEPOIS: {status_depois}\n")
        
        print("✅ Fila processada!\n")
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    print("\n" + "=" * 70)
    print("🧪 TESTE - LIMPA BLOQUEIO E FORÇA ENVIO WHATSAPP")
    print("=" * 70 + "\n")
    
    numero = "5531984163357"  # PADRE AFONSO
    
    print(f"📱 Limpando bloqueio para: {numero}\n")
    
    # Passo 1: Limpar anti-spam
    if not limpar_anti_spam_numero(numero):
        return
    
    # Passo 2: Processar fila
    print("=" * 70)
    if not processar_fila_whatsapp():
        return
    
    print("=" * 70)
    print("✅ TESTE CONCLUÍDO!")
    print("=" * 70)
    print("""
Resumo:
- ✅ Limpou bloqueio de 24h do número
- ✅ Processou a fila de WhatsApp
- ✅ Mensagens deve ter sido enviada

Se ainda não chegou:
1. Verifique se o navegador WhatsApp está logado
2. Execute: python whatsapp_service.py (em outro terminal)
3. Aguarde o processamento da fila
    """)

if __name__ == "__main__":
    main()
