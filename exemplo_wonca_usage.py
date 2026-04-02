#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo de uso: Integrar Wonca API ao sistema de rastreamento
"""

from wonca_tracking import rastrear_wonca
import json

# Códigos de rastreio para testar
codigos_teste = [
    'AD292694916BR',
    # Adicione mais códigos aqui
]

print("=" * 70)
print("📦 EXEMPLO: Rastreamento com Wonca API")
print("=" * 70)

for codigo in codigos_teste:
    print(f"\n🔍 Rastreando: {codigo}")
    
    resultado = rastrear_wonca(codigo)
    
    if resultado:
        print(f"   ✅ Situação: {resultado.get('situacao', 'Não disponível')}")
        print(f"   Fonte: {resultado['fonte']}")
        print(f"   Timestamp: {resultado['timestamp']}")
        
        # Salvar resultado completo
        with open(f'rastreio_{codigo}.json', 'w', encoding='utf-8') as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False)
    else:
        print(f"   ❌ Erro ao rastrear")

print("\n" + "=" * 70)
print("📝 PRÓXIMOS PASSOS:")
print("=" * 70)
print("""
1. Adicione crédito à sua conta Wonca Labs para ativar a API
2. Integre ao script automatico_producao.py:
   
   from wonca_tracking import rastrear_wonca
   
   # Dentro do loop de sincronização:
   resultado = rastrear_wonca(codigo_rastreio)
   if resultado:
       situacao_atual = resultado['situacao']
       # Comparar com histórico e notificar

3. Configure o .env com as credenciais corretas

4. Teste com múltiplos códigos de rastreio
""")
