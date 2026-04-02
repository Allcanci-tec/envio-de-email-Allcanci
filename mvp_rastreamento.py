#!/usr/bin/env python3
"""
MVP: Extrai pedidos Correios com APENAS: Número, Cliente, Etiqueta
"""

from bling_auth import bling_get
import json

def mvp_rastreamento():
    print("\n📦 EXTRATO: Número Pedido | Cliente | Etiqueta (Rastreamento)\n")
    
    dados = []
    
    try:
        # Pega pedidos Correios
        response = bling_get("/pedidos/vendas", params={"logistica": 151483, "limit": 100})
        
        for pedido_resumo in response.get("data", []):
            pedido_id = pedido_resumo["id"]
            numero = pedido_resumo.get("numero")
            
            # Detalhes
            detail = bling_get(f"/pedidos/vendas/{pedido_id}")
            pedido = detail.get("data", {})
            
            cliente = pedido.get("contato", {}).get("nome", "N/A")
            volumes = pedido.get("transporte", {}).get("volumes", [])
            
            # Extrai rastreamentos
            for volume in volumes:
                etiqueta = volume.get("codigoRastreamento", "")
                if etiqueta:
                    dados.append({
                        "numero": numero,
                        "cliente": cliente,
                        "etiqueta": etiqueta
                    })
                    print(f"  {numero:<10} | {cliente:<40} | {etiqueta}")
        
        # Exporta JSON
        with open("mvp_rastreamento.json", "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Total: {len(dados)} etiquetas")
        print(f"✅ Exportado: mvp_rastreamento.json")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    mvp_rastreamento()
