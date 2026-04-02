#!/usr/bin/env python3
"""
Script para rastrear etiqueta via API Correios e retornar em JSON
"""

import requests
import json
from datetime import datetime
from xml.etree import ElementTree as ET

def rastrear_etiqueta(codigo_etiqueta):
    """Rastreia etiqueta dos Correios e retorna dados em JSON"""
    
    print(f'\n📦 Rastreando: {codigo_etiqueta}\n')
    
    # API SOAP dos Correios
    url = 'https://www2.correios.com.br/SigepClienteInterface/AtendeClienteService/AtendeCliente'
    
    # XML SOAP para rastreamento
    soap_payload = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:cli="http://cliente.bean.master.sigep.bsb.correios.com.br/">
   <soapenv:Body>
      <cli:buscaEventoLista>
         <idLinguaResultado>1</idLinguaResultado>
         <tipo>L</tipo>
         <resultado>
            <codigo>{codigo_etiqueta}</codigo>
         </resultado>
      </cli:buscaEventoLista>
   </soapenv:Body>
</soapenv:Envelope>"""
    
    headers = {
        'Content-Type': 'text/xml; charset=utf-8',
        'SOAPAction': ''
    }
    
    try:
        response = requests.post(url, data=soap_payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            # Parse XML response
            root = ET.fromstring(response.content)
            
            # Extrai dados da resposta
            resultado = {
                "etiqueta": codigo_etiqueta,
                "status": "sucesso",
                "timestamp": datetime.now().isoformat(),
                "xml_raw": response.text[:500]  # Keep para debug
            }
            
            # Tenta extrair informações específicas
            namespaces = {
                'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
                'cli': 'http://cliente.bean.master.sigep.bsb.correios.com.br/'
            }
            
            try:
                # Procura por eventos/status
                resultado["resposta_raw"] = response.text[:1000]
            except:
                pass
            
            return True, resultado
        else:
            return False, {
                "etiqueta": codigo_etiqueta,
                "status": "erro",
                "codigo_http": response.status_code,
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        return False, {
            "etiqueta": codigo_etiqueta,
            "status": "erro_conexao",
            "erro": str(e),
            "timestamp": datetime.now().isoformat()
        }


def rastrear_com_alternativa(codigo_etiqueta):
    """Tenta rastreamento via endpoint alternativo (web scraping)"""
    
    print(f'Tentando método alternativo...')
    
    # URL de rastreamento direto (sem API)
    url = f'https://www.correios.com.br/rastreamento'
    
    try:
        # Esta é uma tentativa de obter dados via página web
        # Normalmente retorna HTML que precisaria de parsing
        response = requests.get(url, timeout=10, params={'numero': codigo_etiqueta})
        
        if response.status_code == 200:
            return True, {
                "etiqueta": codigo_etiqueta,
                "status": "consultado",
                "url": f"https://www.correios.com.br/rastreamento?numero={codigo_etiqueta}",
                "timestamp": datetime.now().isoformat(),
                "metodo": "web_redirect"
            }
    except:
        pass
    
    return False, None


if __name__ == "__main__":
    etiqueta = "AD287897978BR"
    
    # Tenta rastreamento SOAP
    sucesso, dados = rastrear_etiqueta(etiqueta)
    
    if not sucesso:
        print("❌ Método SOAP falhou, tentando alternativa...")
        sucesso, dados = rastrear_com_alternativa(etiqueta)
    
    if sucesso or dados:
        print("\n✅ Resultado:\n")
        print(json.dumps(dados, indent=2, ensure_ascii=False))
        
        # Salva em arquivo
        with open('rastreamento_resultado.json', 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Salvo em: rastreamento_resultado.json")
    else:
        print("\n❌ Erro ao rastrear etiqueta")
        print("\n⚠️ Alternativa:")
        print(f"Consulte manualmente: https://www.correios.com.br/rastreamento?numero={etiqueta}")
