#!/usr/bin/env python3
import json

with open('contatos_rastreamento.json', 'r', encoding='utf-8') as f:
    contatos = json.load(f)

# Procurar pelo cliente específico ou similar
for c in contatos:
    if 'INDUSTRIAL' in c.get('cliente', '').upper() or 'SAO JOSE' in c.get('cliente', '').upper():
        print(f"\n{'='*70}")
        print(f"ENCONTRADO: {c['cliente']}")
        print(f"{'='*70}")
        print(f"Numero:              {c.get('numero')}")
        print(f"Cliente:             {c.get('cliente')}")
        print(f"Email:               {c.get('email', 'N/A')}")
        print(f"Telefone (salvo):    {c.get('telefone_celular', 'N/A')}")
        print(f"Etiqueta:            {c.get('etiqueta', 'N/A')}")
        
        # Mostrar todos os campos disponíveis
        print(f"\nTODOS OS CAMPOS DO CLIENTE:")
        for chave, valor in c.items():
            if isinstance(valor, str) and len(str(valor)) < 100:
                print(f"  {chave}: {valor}")
            elif not isinstance(valor, (list, dict)):
                print(f"  {chave}: {valor}")
