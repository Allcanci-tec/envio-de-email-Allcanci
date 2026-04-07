#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INICIALIZADOR DE PRODUÇÃO - Sistema de Rastreamento
Inicia a automação com verificações pré-voo
"""

import os
import json
import sys
import subprocess
from datetime import datetime
from pathlib import Path

class Cores:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def verificar_arquivo(caminho, nome):
    """Verifica se arquivo existe"""
    if Path(caminho).exists():
        print(f"  {Cores.GREEN}✓{Cores.RESET} {nome}")
        return True
    else:
        print(f"  {Cores.RED}✗{Cores.RESET} {nome} - NÃO ENCONTRADO")
        return False

def verificar_config_env():
    """Verifica configuração .env"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        reqs = [
            ('EMAIL_REMETENTE', 'Email remetente'),
            ('EMAIL_SENHA', 'Senha email'),
            ('EMAIL_SMTP', 'SMTP'),
            ('BLING_ACCESS_TOKEN', 'Token Bling'),
        ]
        
        todos_ok = True
        for var, desc in reqs:
            if os.getenv(var):
                print(f"  {Cores.GREEN}✓{Cores.RESET} {desc}")
            else:
                print(f"  {Cores.RED}✗{Cores.RESET} {desc} - NÃO CONFIGURADO")
                todos_ok = False
        
        return todos_ok
    except Exception as e:
        print(f"  {Cores.RED}✗{Cores.RESET} Erro ao verificar .env: {e}")
        return False

def main():
    print(f"\n{Cores.BOLD}{Cores.BLUE}")
    print("=" * 80)
    print(" INICIALIZADOR DE PRODUCAO v1.0")
    print(" Sistema de Notificacao de Rastreamento")
    print("=" * 80)
    print(f"{Cores.RESET}\n")
    
    # PRÉ-CHECKLIST
    print(f"{Cores.BOLD}PRÉ-CHECKLIST DE PRODUÇÃO{Cores.RESET}\n")
    
    print("1. Arquivos Essenciais:")
    file_checks = [
        verificar_arquivo('automatico_producao.py', 'Automação principal'),
        verificar_arquivo('enviar_emails_rastreamento.py', 'Sistema de email'),
        verificar_arquivo('whatsapp_service.py', 'Serviço WhatsApp'),
        verificar_arquivo('contatos_rastreamento.json', 'Base de clientes'),
        verificar_arquivo('.env', 'Configuração'),
    ]
    
    print("\n2. Configurações .env:")
    env_ok = verificar_config_env()
    
    print("\n3. Base de Clientes:")
    try:
        with open('contatos_rastreamento.json', 'r', encoding='utf-8') as f:
            clientes = json.load(f)
            print(f"  {Cores.GREEN}✓{Cores.RESET} {len(clientes)} clientes carregados")
    except Exception as e:
        print(f"  {Cores.RED}✗{Cores.RESET} Erro ao carregar clientes: {e}")
        file_checks[-1] = False
    
    # RESULTADO
    print(f"\n{Cores.BOLD}RESULTADO{Cores.RESET}\n")
    
    if all(file_checks) and env_ok:
        print(f"{Cores.GREEN}✓ TODOS OS REQUISITOS ATENDIDOS!{Cores.RESET}\n")
        print(f"{Cores.BOLD}Iniciando automação...{Cores.RESET}\n")
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"Timestamp: {timestamp}")
        print(f"Arquivo de log: rastreamento.log")
        print(f"Status: RODANDO EM MODO CONTÍNUO (5 min por ciclo)")
        print()
        
        # Iniciar automação
        print(f"{Cores.BLUE}{'='*80}{Cores.RESET}\n")
        
        try:
            import automatico_producao
            automatico_producao.main()
        except KeyboardInterrupt:
            print(f"\n{Cores.YELLOW}Automação interrompida pelo usuário{Cores.RESET}")
            sys.exit(0)
        except Exception as e:
            print(f"{Cores.RED}Erro durante automação: {e}{Cores.RESET}")
            sys.exit(1)
    else:
        print(f"{Cores.RED}✗ REQUISITOS NÃO ATENDIDOS!{Cores.RESET}\n")
        print("Corrija os erros acima antes de iniciar.\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
