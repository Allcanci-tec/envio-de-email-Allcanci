#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inspecionar TODAS as chaves e valores de um pedido para encontrar etiqueta.
"""

import json
from bling_auth import bling_get

def extract_all_keys(obj, path="", max_depth=10, current_depth=0):
    """Extrai todas as chaves com seus valores/tipos."""
    results = []
    
    if current_depth >= max_depth:
        return results
    
    if isinstance(obj, dict):
        for key, value in obj.items():
            current_path = f"{path}.{key}" if path else key
            
            if isinstance(value, (dict, list)):
                results.append((current_path, type(value).__name__))
                results.extend(extract_all_keys(value, current_path, max_depth, current_depth + 1))
            else:
                # Mostrar valores string que pareçam etiquetas
                if isinstance(value, str) and len(value) > 3:
                    if any(x in str(value).upper() for x in ['AG', 'BR', 'EC', 'AA', 'CC']):
                        results.append((current_path, f"STRING (POSSÍVEL ETIQUETA): {value[:50]}"))
                    else:
                        results.append((current_path, f"STRING: {value[:40]}"))
                else:
                    results.append((current_path, f"{type(value).__name__}: {value}"))
    
    elif isinstance(obj, list):
        if obj:
            results.append((f"{path}[{len(obj)} items]", "LIST"))
            results.extend(extract_all_keys(obj[0], f"{path}[0]", max_depth, current_depth + 1))
    
    return results

print("\n" + "="*120)
print("  MAPEAMENTO COMPLETO DE CHAVES DO PEDIDO")
print("="*120 + "\n")

try:
    # Pegar um pedido
    pedidos_response = bling_get("/pedidos/vendas", params={"limite": 1})
    
    if not pedidos_response.get("data"):
        print("Nenhum pedido encontrado!")
    else:
        pedido_id = pedidos_response["data"][0]["id"]
        print(f"Inspecionando pedido ID: {pedido_id}\n")
        
        pedido = bling_get(f"/pedidos/vendas/{pedido_id}")
        pedido_data = pedido.get("data", {})
        
        # Extrair todas as chaves
        chaves = extract_all_keys(pedido_data)
        
        # Mostrar tudo
        for chave, info in sorted(chaves):
            print(f"  {chave:<60} : {info}")
        
        print("\n\n" + "="*120)
        print("  PROCURANDO POR ETIQUETA/RASTREAMENTO")
        print("="*120 + "\n")
        
        for chave, info in sorted(chaves):
            if any(x in chave.lower() for x in ['etiqueta', 'rastreamento', 'codigo', 'objeto', 'postagem']):
                print(f"  ✅ {chave:<60} : {info}")

except Exception as e:
    print(f"Erro: {e}")
    import traceback
    traceback.print_exc()
