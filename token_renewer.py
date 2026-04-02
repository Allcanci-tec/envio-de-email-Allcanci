#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script daemon para renovação automática de tokens Bling em background.
Roda continuamente e renova o token 10 minutos antes de expirar.

Uso:
    # Terminal 1 - Rodar o daemon
    python token_renewer.py

    # Terminal 2 - Sua aplicação
    from bling_auth import bling_get
    contatos = bling_get("/contatos")
"""

import os
import time
import sys
from datetime import datetime
from bling_auth import get_token_info, _token_cache, _refresh_token

def format_time(seconds):
    """Formata segundos em horas:minutos:segundos."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def main():
    print("\n" + "="*70)
    print("  🔄 DAEMON DE RENOVAÇÃO AUTOMÁTICA DE TOKENS BLING")
    print("="*70)
    print(f"\n  ⏰ Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("  📌 Rodando em background...")
    print("  📌 Renova 10 minutos antes da expiração")
    print("  📌 Pressione Ctrl+C para parar\n")
    print("="*70 + "\n")
    
    check_interval = 60  # Verificar a cada 1 minuto
    warning_threshold = 600  # Avisar faltando 10 minutos

    try:
        while True:
            current_time = time.time()
            expires_at = _token_cache.get("expires_at", 0)
            time_remaining = expires_at - current_time

            # Status atual
            info = get_token_info()
            status = info["status"]
            expires_in_min = info["expires_in_minutes"]
            
            # Exibir status
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            if time_remaining <= 0:
                # Token expirou, renovar immediato
                print(f"[{timestamp}] ⚠️  Token expirado! Renovando agora...")
                try:
                    _refresh_token()
                    print(f"[{timestamp}] ✅ Token renovado com sucesso!\n")
                except Exception as e:
                    print(f"[{timestamp}] ❌ Erro ao renovar: {e}\n")
                    
            elif time_remaining <= warning_threshold:
                # Faltam 10 minutos, renovar proativamente
                print(f"[{timestamp}] 🔄 Renovando proativamente (expira em {expires_in_min} min)...")
                try:
                    _refresh_token()
                    print(f"[{timestamp}] ✅ Token renovado com sucesso!\n")
                except Exception as e:
                    print(f"[{timestamp}] ❌ Erro ao renovar: {e}\n")
            else:
                # Token ainda é válido, apenas informativos
                time_str = format_time(time_remaining)
                print(f"[{timestamp}] {status} | Expira em {expires_in_min} min ({time_str})")
            
            # Aguardar próxima verificação
            time.sleep(check_interval)
            
    except KeyboardInterrupt:
        print(f"\n\n[{datetime.now().strftime('%H:%M:%S')}] ⏹️  Daemon parado pelo usuário")
        print("="*70 + "\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
