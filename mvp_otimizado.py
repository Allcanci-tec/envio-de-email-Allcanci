#!/usr/bin/env python3
"""
MVP Otimizado: Extrai dados em batch - Número, Cliente, Etiqueta
"""

from bling_auth import bling_get
import json

def mvp_otimizado():
    print("\n📦 MVP RASTREAMENTO: Número | Cliente | Etiqueta\n")
    
    dados = []
    
    try:
        # Pega diversos offsets para cobrir mais pedidos sem travar
        offsets = [0, 100]  # 0-100 e 100-200
        
        for offset in offsets:
            print(f"  Processando offset {offset}...", end=" ", flush=True)
            
            response = bling_get("/pedidos/vendas", params={
                "logistica": 151483,
                "limit": 100,
                "offset": offset
            })
            
            count_batch = 0
            for pedido in response.get("data", []):
                numero = pedido.get("numero")
                cliente = pedido.get("contato", {}).get("nome", "N/A")
                
                # Tenta pegar via detalhe se houver volumes
                volumes = pedido.get("transporte", {}).get("volumes", [])
                
                for volume in volumes:
                    etiqueta = volume.get("codigoRastreamento", "")
                    if etiqueta:
                        dados.append({
                            "numero": numero,
                            "cliente": cliente,
                            "etiqueta": etiqueta
                        })
                        count_batch += 1
            
            print(f"✓ {count_batch} etiquetas")
            
            # Se encontrou poucos, tenta próximos em detalhe
            if count_batch < 20:
                for pedido in response.get("data", []):
                    pedido_id = pedido["id"]
                    numero = pedido.get("numero")
                    cliente = pedido.get("contato", {}).get("nome", "N/A")
                    
                    try:
                        detail = bling_get(f"/pedidos/vendas/{pedido_id}")
                        volumes = detail.get("data", {}).get("transporte", {}).get("volumes", [])
                        
                        for volume in volumes:
                            etiqueta = volume.get("codigoRastreamento", "")
                            if etiqueta:
                                # Verifica duplicata
                                if not any(d["etiqueta"] == etiqueta for d in dados):
                                    dados.append({
                                        "numero": numero,
                                        "cliente": cliente,
                                        "etiqueta": etiqueta
                                    })
                    except:
                        pass
        
        # Remove duplicatas
        unique_dados = []
        seen = set()
        for d in dados:
            key = (d["numero"], d["etiqueta"])
            if key not in seen:
                seen.add(key)
                unique_dados.append(d)
                print(f"  {d['numero']:<10} | {d['cliente']:<45} | {d['etiqueta']}")
        
        # Exporta
        with open("mvp_rastreamento.json", "w", encoding="utf-8") as f:
            json.dump(unique_dados, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Total: {len(unique_dados)} etiquetas")
        print(f"✅ Arquivo: mvp_rastreamento.json")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    mvp_otimizado()
