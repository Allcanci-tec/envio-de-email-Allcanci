#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script correto para trazer objetos de postagem com etiquetas reais.
Usando apenas /logisticas/objetos conforme instruido.
"""

import sys
import json
from datetime import datetime
from bling_auth import bling_get, get_token_info

def main():
    print("\n" + "="*120)
    print("  OBJETOS DE POSTAGEM - ETIQUETAS REAIS")
    print("="*120 + "\n")
    
    # Verificar token
    print("1. STATUS DO TOKEN")
    print("-" * 120)
    info = get_token_info()
    print(f"  Status: {info['status']} | Expira em {info['expires_in_minutes']} minutos\n")
    
    # Buscar objetos de postagem
    print("2. BUSCANDO OBJETOS DE POSTAGEM")
    print("-" * 120)
    
    try:
        print("  GET /logisticas/objetos (limite: 1000)\n")
        response = bling_get("/logisticas/objetos", params={"limite": 1000})
        
        objetos = response.get("data", [])
        
        if not objetos:
            print("  Nenhum objeto de postagem encontrado!\n")
            return 1
        
        print(f"  Total de objetos: {len(objetos)}\n")
        
        # 3. Exibir em formato tabular
        print("="*120)
        print("3. DETALHES DOS OBJETOS")
        print("="*120 + "\n")
        
        print(f"{'Etiqueta (Rastreamento)':<30} {'ID Pedido':<15} {'Status':<30} {'Origem':<25} {'Destino':<25}")
        print("-" * 120)
        
        objetos_extraidos = []
        
        for obj in objetos:
            # Extrair dados conforme solicitado
            etiqueta = obj.get("rastreamento", {}).get("codigo", "N/A")
            pedido_id = obj.get("pedido", {}).get("id", "N/A")
            status = obj.get("situacao", {}).get("nome", "N/A")
            origem = obj.get("rastreamento", {}).get("origem", "N/A")
            destino = obj.get("rastreamento", {}).get("destino", "N/A")
            
            # Exibir
            print(f"{etiqueta:<30} {str(pedido_id):<15} {status[:29]:<30} {origem[:24]:<25} {destino[:24]:<25}")
            
            objetos_extraidos.append({
                "etiqueta": etiqueta,
                "rastreamento_codigo": etiqueta,
                "pedido_id": pedido_id,
                "status": status,
                "origem": origem,
                "destino": destino,
                "dado_completo": obj
            })
        
        print("-" * 120 + "\n")
        
        # 4. Exportar dados
        print("4. EXPORTANDO DADOS")
        print("-" * 120)
        
        output_file = "objetos_postagem_completo.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "total_objetos": len(objetos_extraidos),
                "objetos": objetos_extraidos
            }, f, indent=2, ensure_ascii=False)
        
        print(f"  Arquivo exportado: {output_file}\n")
        
        # 5. Resumo
        print("="*120)
        print("5. RESUMO")
        print("="*120 + "\n")
        
        etiquetas_validas = [o for o in objetos_extraidos if o["etiqueta"] != "N/A"]
        print(f"  Total de objetos: {len(objetos_extraidos)}")
        print(f"  Com etiqueta: {len(etiquetas_validas)}")
        print(f"  Sem etiqueta: {len(objetos_extraidos) - len(etiquetas_validas)}\n")
        
        return 0
        
    except Exception as e:
        print(f"  Erro: {e}\n")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
