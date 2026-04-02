#!/usr/bin/env python3
"""
Exporta todos os pedidos Correios com etiqueta de rastreamento
"""

from bling_auth import bling_get
import json
from datetime import datetime
import csv

def export_rastreamento_correios():
    print("=" * 100)
    print("EXPORTANDO PEDIDOS CORREIOS COM RASTREAMENTO - ID, ETIQUETA, SITUAÇÃO")
    print("=" * 100)
    
    dados_export = []
    total_pedidos = 0
    pedidos_com_rastreamento = 0
    
    print("\n🔄 Consultando todos os pedidos Correios...")
    
    try:
        # Faz requisição em múltiplas páginas se necessário
        offset = 0
        limit = 100
        
        while True:
            try:
                response = bling_get("/pedidos/vendas", params={
                    "logistica": 151483,
                    "limit": limit,
                    "offset": offset
                })
                
                if not response.get("data") or len(response.get("data", [])) == 0:
                    break
                
                for pedido_resumo in response["data"]:
                    total_pedidos += 1
                    pedido_id = pedido_resumo["id"]
                    numero_pedido = pedido_resumo.get("numero")
                    
                    # Obtém detalhes do pedido
                    try:
                        detail = bling_get(f"/pedidos/vendas/{pedido_id}")
                        if detail.get("data"):
                            pedido = detail["data"]
                            
                            # Extrai volumes com rastreamento
                            volumes = pedido.get("transporte", {}).get("volumes", [])
                            
                            for volume in volumes:
                                codigo_rastreamento = volume.get("codigoRastreamento", "")
                                
                                if codigo_rastreamento:  # Apenas com rastreamento preenchido
                                    pedidos_com_rastreamento += 1
                                    
                                    dados_export.append({
                                        "id_pedido": numero_pedido,
                                        "id_interno": pedido_id,
                                        "etiqueta": codigo_rastreamento,
                                        "servico": volume.get("servico", ""),
                                        "volume_id": volume.get("id", ""),
                                        "data_pedido": pedido.get("data", ""),
                                        "cliente": pedido.get("contato", {}).get("nome", ""),
                                        "total": pedido.get("total", 0)
                                    })
                                    
                                    print(f"✅ Pedido {numero_pedido}: {codigo_rastreamento}")
                    except Exception as e:
                        pass
                
                offset += limit
                
                if len(response.get("data", [])) < limit:
                    break
                    
            except Exception as e:
                print(f"❌ Erro ao processar página: {str(e)[:100]}")
                break
        
        print(f"\n{'='*100}")
        print(f"📊 RESULTADO:")
        print(f"   • Total de pedidos consultados: {total_pedidos}")
        print(f"   • Pedidos COM rastreamento: {pedidos_com_rastreamento}")
        print(f"   • Pedidos SEM rastreamento: {total_pedidos - pedidos_com_rastreamento}")
        print(f"{'='*100}")
        
        if dados_export:
            # Exporta para JSON único
            json_file = "etiquetas_correios_rastreamento.json"
            with open(json_file, "w", encoding="utf-8") as f:
                # Formato simples: lista com apenas ID, Etiqueta, Situacao
                dados_simples = [
                    {
                        "ID": d["id_pedido"],
                        "Etiqueta": d["etiqueta"],
                        "Serviço": d["servico"],
                        "Cliente": d["cliente"]
                    }
                    for d in dados_export
                ]
                json.dump(dados_simples, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ Exportado para JSON: {json_file}")
            
            # Exporta para JSON detalhado
            json_detail = "etiquetas_correios_detalhado.json"
            with open(json_detail, "w", encoding="utf-8") as f:
                json.dump(dados_export, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Exportado detalhado: {json_detail}")
            
            # Exporta para CSV
            csv_file = "etiquetas_correios_rastreamento.csv"
            with open(csv_file, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["ID", "Etiqueta", "Serviço", "Cliente", "Data", "Total"])
                writer.writeheader()
                for d in dados_export:
                    writer.writerow({
                        "ID": d["id_pedido"],
                        "Etiqueta": d["etiqueta"],
                        "Serviço": d["servico"],
                        "Cliente": d["cliente"],
                        "Data": d["data_pedido"],
                        "Total": f"R$ {d['total']}"
                    })
            
            print(f"✅ Exportado para CSV: {csv_file}")
            
            # Exibe preview
            print(f"\n📄 Preview dos dados (primeros 10):")
            print(f"\n{'ID':<12} | {'Etiqueta':<16} | {'Serviço':<20} | {'Cliente':<40}")
            print("-" * 100)
            for d in dados_export[:10]:
                cliente = d["cliente"][:40] if d["cliente"] else "N/A"
                print(f"{str(d['id_pedido']):<12} | {d['etiqueta']:<16} | {d['servico']:<20} | {cliente:<40}")
            
            if len(dados_export) > 10:
                print(f"... e mais {len(dados_export) - 10} registros")
        else:
            print("\n❌ Nenhum pedido com rastreamento encontrado")
            
    except Exception as e:
        print(f"❌ Erro: {str(e)[:200]}")

if __name__ == "__main__":
    export_rastreamento_correios()
