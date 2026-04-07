#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANÁLISE DETALHADA - Extrair vendedor da estrutura completa do pedido
Procurando em: cliente, contato, fornecedor, vendedor, etc.
"""

import json
from bling_auth import bling_get

print("\n" + "=" * 80)
print("ANÁLISE COMPLETA DO PEDIDO 2409 - ESCOLA MUNICIPAL ISRAEL PINHEIRO")
print("=" * 80 + "\n")

try:
    # Buscar pedido completo
    pedido_data = bling_get('/pedidos/vendas', params={'numero': 2409})
    
    if pedido_data.get('data'):
        # Pegar o primeiro resultado
        pedido_resumido = pedido_data['data'][0]
        pedido_id = pedido_resumido.get('id')
        
        print(f"ID do Pedido (interno): {pedido_id}\n")
        
        # Buscar dados completos do pedido
        pedido_completo = bling_get(f'/pedidos/vendas/{pedido_id}')
        pedido = pedido_completo.get('data', {})
        
        # Salvar estrutura completa para análise
        with open('pedido_2409_completo.json', 'w', encoding='utf-8') as f:
            json.dump(pedido, f, indent=2, ensure_ascii=False)
        
        print("✅ Dados salvos em: pedido_2409_completo.json\n")
        
        # Exibir todos os campos principais
        print("=" * 80)
        print("CAMPOS PRINCIPAIS DO PEDIDO:")
        print("=" * 80 + "\n")
        
        # Cliente/Contato
        print("📋 CONTATO/CLIENTE:")
        contato = pedido.get('contato', {})
        print(f"  ID: {contato.get('id')}")
        print(f"  Nome: {contato.get('nome')}")
        print(f"  Tipo: {contato.get('tipoPessoa')}")
        print(f"  Documento: {contato.get('numeroDocumento')}\n")
        
        # Vendedor
        print("👤 VENDEDOR:")
        vendedor = pedido.get('vendedor', {})
        print(f"  ID: {vendedor.get('id')}")
        print(f"  Dados: {vendedor}\n")
        
        # Intermediador
        print("🔗 INTERMEDIADOR:")
        intermediador = pedido.get('intermediador', {})
        print(f"  CNPJ: {intermediador.get('cnpj')}")
        print(f"  Usuário: {intermediador.get('nomeUsuario')}")
        print(f"  Dados: {intermediador}\n")
        
        # Transportador
        print("🚚 TRANSPORTADOR/LOGÍSTICA:")
        transporte = pedido.get('transporte', {})
        print(f"  Transportador: {transporte.get('transportador')}")
        print(f"  Logística: {transporte.get('logistica')}\n")
        
        # Observações
        print("📝 OBSERVAÇÕES:")
        print(f"  Públicas: {pedido.get('observacoes', '(nenhuma)')}")
        print(f"  Internas: {pedido.get('observacoesInternas', '(nenhuma)')}\n")
        
        # Loja
        print("🏪 LOJA:")
        loja = pedido.get('loja', {})
        print(f"  ID: {loja.get('id')}")
        print(f"  Dados: {loja}\n")
        
        # Verificar se tem mais campos
        print("=" * 80)
        print("TODOS OS CAMPOS DISPONÍVEIS:")
        print("=" * 80 + "\n")
        
        for chave in sorted(pedido.keys()):
            valor = pedido.get(chave)
            if isinstance(valor, dict):
                print(f"  ⚙️ {chave}: (objeto com {len(valor)} campos)")
                # Exibir campos da dict
                for sub_chave in sorted(valor.keys()):
                    sub_valor = valor[sub_chave]
                    if not isinstance(sub_valor, (list, dict)):
                        print(f"     - {sub_chave}: {sub_valor}")
            elif isinstance(valor, list):
                print(f"  📦 {chave}: (array com {len(valor)} itens)")
            else:
                print(f"  📄 {chave}: {valor}")
        
        print("\n" + "=" * 80)
        print("INTERPRETAÇÃO:")
        print("=" * 80 + "\n")
        
        # Análise
        if contato.get('id'):
            print(f"✅ Cliente/Escola encontrado:")
            print(f"   ID: {contato.get('id')}")
            print(f"   Nome: {contato.get('nome')}\n")
        
        if vendedor.get('id') and vendedor.get('id') != 0:
            print(f"✅ Vendedor encontrado:")
            print(f"   ID: {vendedor.get('id')}\n")
            
            # Buscar dados do vendedor
            try:
                vend_data = bling_get(f'/vendedores/{vendedor.get("id")}')
                vend = vend_data.get('data', {})
                vend_contato = vend.get('contato', {})
                
                print(f"   Nome do vendedor: {vend_contato.get('nome')}")
                print(f"   ID do contato: {vend_contato.get('id')}\n")
                
                # Buscar email do contato
                if vend_contato.get('id'):
                    contato_vend = bling_get(f'/contatos/{vend_contato.get("id")}')
                    contato_info = contato_vend.get('data', {})
                    print(f"   Email: {contato_info.get('email')}")
                    print(f"   Telefone: {contato_info.get('email')}")
            except Exception as e:
                print(f"   (Erro ao buscar detalhes: {e})")
        else:
            print(f"❌ Nenhum vendedor configurado (ID = 0 ou nulo)\n")
            
            # Procurar em observações
            obs = pedido.get('observacoes', '').lower()
            if 'vendedor' in obs or 'vend' in obs:
                print(f"⚠️ Possível vendedor em observações:")
                print(f"   {pedido.get('observacoes')}\n")
            
            # Procurar em intermediador
            inter = pedido.get('intermediador', {})
            if inter.get('nomeUsuario'):
                print(f"⚠️ Possível vendedor em intermediador:")
                print(f"   {inter.get('nomeUsuario')}\n")
        
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
