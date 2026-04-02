#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para listar todas as etiquetas de rastreamento de objetos de postagem no Bling.
"""

import sys
import json
from datetime import datetime
from bling_auth import bling_get, get_token_info

def format_object(obj):
    """Formata um objeto de logística para exibição."""
    try:
        rastreamento = obj.get("rastreamento", {})
        pedido = obj.get("pedidoVenda", {})
        nota = obj.get("notaFiscal", {})
        dimensao = obj.get("dimensao", {})
        
        return {
            "id_pedido": pedido.get("id", "N/A"),
            "id_nota": nota.get("id", "N/A"),
            "etiqueta": rastreamento.get("codigo", "N/A"),
            "status": rastreamento.get("descricao", "N/A"),
            "origem": rastreamento.get("origem", "N/A"),
            "destino": rastreamento.get("destino", "N/A"),
            "ultima_alteracao": rastreamento.get("ultimaAlteracao", "N/A"),
            "data_saida": obj.get("dataSaida", "N/A"),
            "prazo_entrega": obj.get("prazoEntregaPrevisto", "N/A"),
            "peso": dimensao.get("peso", "N/A"),
            "frete_previsto": obj.get("fretePrevisto", "N/A"),
            "url_rastreamento": rastreamento.get("url", "N/A"),
        }
    except Exception as e:
        print(f"⚠️  Erro ao processar objeto: {e}")
        return None

def main():
    print("\n" + "="*90)
    print("  📦 LISTAGEM DE TODAS AS ETIQUETAS DE POSTAGEM - BLING")
    print("="*90 + "\n")
    
    # 1. Verificar status do token
    print("1️⃣  STATUS DO TOKEN")
    print("-" * 90)
    info = get_token_info()
    print(f"  Status: {info['status']} | Expira em {info['expires_in_minutes']} minutos\n")
    
    # 2. Listar objetos de logística
    print("2️⃣  BUSCANDO OBJETOS DE LOGÍSTICA")
    print("-" * 90)
    
    try:
        print("  📤 GET /logisticas (limite: 100)\n")
        
        response = bling_get("/logisticas", params={"limite": 100})
        
        objetos = response.get("data", [])
        
        if not objetos:
            print("  ❌ Nenhum objeto de logística encontrado.\n")
            return 1
        
        print(f"  ✅ Total de objetos encontrados: {len(objetos)}\n")
        
        # 3. Exibir detalhes de cada objeto
        print("3️⃣  DETALHES DAS ETIQUETAS")
        print("="*90 + "\n")
        
        objetos_formatados = []
        
        for idx, obj in enumerate(objetos, 1):
            formatado = format_object(obj)
            if formatado:
                objetos_formatados.append(formatado)
                
                print(f"📦 OBJETO #{idx}")
                print(f"   ID Pedido:         {formatado['id_pedido']}")
                print(f"   ID Nota Fiscal:    {formatado['id_nota']}")
                print(f"   Etiqueta:          {formatado['etiqueta']}")
                print(f"   Status:            {formatado['status']}")
                print(f"   Origem:            {formatado['origem']}")
                print(f"   Destino:           {formatado['destino']}")
                print(f"   Última Alteração:  {formatado['ultima_alteracao']}")
                print(f"   Data de Saída:     {formatado['data_saida']}")
                print(f"   Prazo Entrega:     {formatado['prazo_entrega']} dias")
                print(f"   Peso:              {formatado['peso']} kg")
                print(f"   Frete Previsto:    R$ {formatado['frete_previsto']}")
                print(f"   URL Rastreamento:  {formatado['url_rastreamento']}")
                print()
        
        # 4. Relatório consolidado
        print("\n" + "="*90)
        print("  📊 RELATÓRIO CONSOLIDADO")
        print("="*90 + "\n")
        
        print(f"  Total de objetos: {len(objetos_formatados)}")
        print(f"\n  Etiquetas encontradas:")
        for idx, obj in enumerate(objetos_formatados, 1):
            print(f"    {idx}. {obj['etiqueta']:20} | Status: {obj['status']:15} | Origem: {obj['origem']}")
        
        # 5. Exportar para JSON
        print("\n" + "="*90)
        print("  💾 EXPORTANDO DADOS")
        print("="*90 + "\n")
        
        output_file = "objetos_logistica.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "total_objetos": len(objetos_formatados),
                "objetos": objetos_formatados
            }, f, indent=2, ensure_ascii=False)
        
        print(f"  ✅ Dados exportados para: {output_file}\n")
        
        return 0
        
    except Exception as e:
        print(f"  ❌ Erro ao buscar objetos: {e}\n")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
