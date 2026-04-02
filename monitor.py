#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MONITOR DE DIAGNÓSTICO - Sistema Automático de Rastreamento
Mostra status em tempo real do sistema
"""

import json
import os
from datetime import datetime
from pathlib import Path

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def format_time(iso_str):
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime('%d/%m %H:%M')
    except:
        return iso_str[:16] if iso_str else 'N/A'

def main():
    clear_screen()
    
    print("\n" + "="*80)
    print("📊 MONITOR DO SISTEMA - Automático de Rastreamento")
    print("="*80 + "\n")
    
    # Verificar histórico
    historico_file = 'historico_producao.json'
    
    if not os.path.exists(historico_file):
        print("⚠️  Nenhum histórico encontrado. Sistema não foi executado ainda.")
        return
    
    with open(historico_file, 'r', encoding='utf-8') as f:
        historico = json.load(f)
    
    # Contar status
    processados = len(historico)
    com_historico = sum(1 for p in historico.values() if p.get('ultima_situacao'))
    
    print(f"📊 ESTATÍSTICAS:")
    print(f"   ✅ Processados: {processados}")
    print(f"   🔄 Com histórico: {com_historico}")
    
    if processados == 0:
        print("\n⚠️  Nenhum pedido processado ainda.\n")
        return
    
    print("\n" + "="*80)
    print("📋 DETALHES POR PEDIDO:")
    print("="*80 + "\n")
    
    # Mostrar cada pedido
    for chave in sorted(historico.keys()):
        pedido = historico[chave]
        numero = pedido.get('numero', '?')
        cliente = pedido.get('cliente', '?')
        email = pedido.get('email_cliente', '')
        etiqueta = pedido.get('etiqueta', '?')
        situacao = pedido.get('ultima_situacao', 'N/A')
        ultima_consulta = pedido.get('ultima_consulta', '')
        
        # Indicador de email
        email_ind = "📧" if email else "⚠️"
        
        # Status visual
        if 'Entregue' in situacao or 'Devolvido' in situacao:
            status_ind = "✅"
        elif 'transporte' in situacao.lower():
            status_ind = "🚚"
        else:
            status_ind = "🔄"
        
        print(f"{status_ind} Pedido {numero}")
        print(f"   Cliente: {cliente}")
        print(f"   {email_ind} Email: {email if email else '(sem email)'}")
        print(f"   Etiqueta: {etiqueta}")
        print(f"   Status: {situacao}")
        print(f"   Consulta: {format_time(ultima_consulta)}")
        print()
    
    # Verificar log
    log_file = 'rastreamento.log'
    if os.path.exists(log_file):
        print("="*80)
        print("📝 ÚLTIMAS LINHAS DO LOG:")
        print("="*80 + "\n")
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                linhas = f.readlines()
                # Mostrar últimas 10 linhas
                for linha in linhas[-10:]:
                    print(linha.rstrip())
        except:
            print("(Erro ao ler log)")
    
    print("\n" + "="*80)
    print("💡 DICAS:")
    print("="*80)
    print("• Monitore rastreamento.log: tail -f rastreamento.log")
    print("• Reinicie o sistema: python automatico_producao.py")
    print("• Consulte histórico completo: cat historico_producao.json")
    print("="*80 + "\n")

if __name__ == '__main__':
    main()
