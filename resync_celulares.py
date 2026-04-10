#!/usr/bin/env python3
"""
RESINCRONIZAR CELULARES DO BLING
Remove os dados antigos e força uma nova sincronização
"""

import json
import os
from datetime import datetime

json_file = 'contatos_rastreamento.json'

# Fazer backup
if os.path.exists(json_file):
    backup_file = f'contatos_rastreamento_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(json_file, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Backup criado: {backup_file}")
    print(f"\n📝 Removendo dados antigos do arquivo...")
    
    # Limpar completamente
    for c in dados:
        c['telefone_celular'] = 'N/A'  # Zerar o celular para forçar releitura
    
    # Salvar versão "limpa"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Arquivo {json_file} foi resetado com celulares 'N/A'")
    print(f"   Próxima vez que automatico_producao.py rodar, irá:")
    print(f"   1️⃣  Buscar cada contato no Bling")
    print(f"   2️⃣  Extrair especificamente o campo 'Celular'")
    print(f"   3️⃣  Atualizar os dados com os novos celulares")
    print(f"\n🚀 Próximo passo: inicie o automatico_producao.py normalmente!")
else:
    print(f"❌ Arquivo {json_file} não encontrado")
