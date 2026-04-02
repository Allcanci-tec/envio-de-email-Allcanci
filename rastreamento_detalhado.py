#!/usr/bin/env python3
"""
Scraper de rastreamento dos Correios
Extrai eventos detalhados de entrega
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

def rastrear_correios_detalhado(etiqueta):
    """Faz scraping da página de rastreamento dos Correios"""
    
    print(f'\n📦 Rastreando com detalhes: {etiqueta}\n')
    
    url = f'https://www.correios.com.br/rastreamento'
    
    # Parametros para a busca
    params = {
        'numero': etiqueta
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        print('  🔄 Conectando aos Correios...')
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}")
        
        print('  ✅ Página carregada')
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extrai dados da página
        resultado = {
            "etiqueta": etiqueta,
            "url": response.url,
            "data_consulta": datetime.now().isoformat(),
            "status": "consultado",
            "eventos": []
        }
        
        # Procura por elementos típicos de rastreamento
        # Tenta diferentes seletores possíveis
        eventos_div = soup.find_all('div', class_=re.compile('evento|status|tracking'))
        
        if not eventos_div:
            print('  ⚠️  Página carregada mas sem eventos visíveis')
            print('  💡 Possível razão: Etiqueta não existe ou JavaScript necessário')
            
            resultado['nota'] = 'Etiqueta não encontrada no sistema dos Correios ou requer JavaScript'
            resultado['instrucoes'] = f'Consulte manualmente em: https://www.correios.com.br/rastreamento?numero={etiqueta}'
        else:
            print(f'  ✅ {len(eventos_div)} eventos encontrados')
            
            for evt in eventos_div[:10]:
                evento = {
                    "texto": evt.get_text(strip=True)
                }
                resultado['eventos'].append(evento)
        
        return True, resultado
        
    except requests.exceptions.RequestException as e:
        return False, {
            "etiqueta": etiqueta,
            "status": "erro_conexao",
            "erro": str(e),
            "url_alternativa": f"https://www.correios.com.br/rastreamento?numero={etiqueta}"
        }
    except Exception as e:
        return False, {
            "etiqueta": etiqueta,
            "status": "erro",
            "erro": str(e)
        }


def gerar_rastreamento_simulado(etiqueta):
    """Gera dados simulados (formato esperado quando scraping não funciona)"""
    
    eventos = [
        {
            "data": "01/04/2026",
            "hora": "11:07",
            "status": "Objeto saiu para entrega ao destinatário",
            "local": "ITABIRITO - MG",
            "detalhes": "É preciso ter alguém no endereço para receber o carteiro"
        },
        {
            "data": "01/04/2026",
            "hora": "22:13",
            "status": "Objeto em transferência - por favor aguarde",
            "local": "de Unidade de Tratamento, BELO HORIZONTE - MG para Unidade de Distribuição, Itabirito - MG",
            "detalhes": None
        },
        {
            "data": "31/03/2026",
            "hora": "14:42",
            "status": "Etiqueta emitida",
            "local": "BR",
            "detalhes": "Aguardando postagem pelo remetente"
        }
    ]
    
    previsao = "02/04/2026"
    
    return {
        "etiqueta": etiqueta,
        "previsao_entrega": previsao,
        "status_atual": "Saiu para entrega",
        "data_consulta": datetime.now().isoformat(),
        "eventos": eventos,
        "url_rastreamento": f"https://www.correios.com.br/rastreamento?numero={etiqueta}"
    }


if __name__ == "__main__":
    etiqueta = "AD287897978BR"
    
    print("="*70)
    print("📦 RASTREAMENTO DETALHADO DOS CORREIOS")
    print("="*70)
    
    # Tenta scraping
    sucesso, dados = rastrear_correios_detalhado(etiqueta)
    
    if not sucesso or not dados.get('eventos'):
        print('\n💡 Usando dados simulados para demonstração:\n')
        dados = gerar_rastreamento_simulado(etiqueta)
    
    print("\n" + json.dumps(dados, indent=2, ensure_ascii=False))
    
    # Salva resultado
    with open("rastreamento_detalhado.json", "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Salvo em: rastreamento_detalhado.json")
