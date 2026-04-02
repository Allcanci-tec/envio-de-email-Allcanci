#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de integração com API Wonca Labs (SiteRastreio)
Fornece rastreamento via API substituindo/complementando o Bling
"""

import os
import requests
import json
import logging
from dotenv import load_dotenv
from datetime import datetime
from typing import Dict, Optional

load_dotenv()

# Logger
logger = logging.getLogger(__name__)

# Configurações da API
WONCA_API_KEY = os.getenv('WONCA_API_KEY')
WONCA_API_URL = os.getenv('WONCA_API_URL', 'https://api-labs.wonca.com.br')
WONCA_SERVICE_PATH = os.getenv('WONCA_SERVICE_PATH', 'wonca.labs.v1.LabsService/Track')

class WoncaTrackingAPI:
    """Cliente para a API Wonca Labs"""
    
    def __init__(self, api_key: str = None, api_url: str = None, service_path: str = None):
        """
        Inicializa o cliente Wonca
        
        Args:
            api_key: Chave de API (default: variável de ambiente)
            api_url: URL da API (default: variável de ambiente)
            service_path: Path do serviço (default: variável de ambiente)
        """
        self.api_key = api_key or WONCA_API_KEY
        self.api_url = api_url or WONCA_API_URL
        self.service_path = service_path or WONCA_SERVICE_PATH
        self.endpoint = f"{self.api_url}/{self.service_path}"
        
        if not self.api_key:
            raise ValueError("WONCA_API_KEY não configurada no .env")
    
    def _make_request(self, tracking_code: str) -> Dict:
        """
        Faz requisição à API Wonca
        
        Args:
            tracking_code: Código de rastreio (ex: AD292694916BR)
            
        Returns:
            Dict com a resposta da API
            
        Raises:
            requests.RequestException: Erro na requisição
        """
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Apikey {self.api_key}'
        }
        
        payload = {"code": tracking_code}
        
        try:
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=15
            )
            
            # Log da requisição
            logger.debug(f"Wonca API - Code: {tracking_code}, Status: {response.status_code}")
            
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.Timeout:
            logger.error(f"Wonca API timeout ao rastrear {tracking_code}")
            raise
        except requests.exceptions.HTTPError as e:
            try:
                error_data = e.response.json()
                logger.error(f"Wonca API Error ({tracking_code}): {error_data}")
            except:
                logger.error(f"Wonca API Error ({tracking_code}): HTTP {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"Wonca API Erro inesperado ({tracking_code}): {str(e)}")
            raise
    
    def rastrear(self, tracking_code: str) -> Optional[Dict]:
        """
        Rastreia um objeto pela API Wonca
        
        Args:
            tracking_code: Código de rastreio
            
        Returns:
            Dict com informações de rastreamento ou None em caso de erro
        """
        try:
            result = self._make_request(tracking_code)
            logger.info(f"✅ Rastreamento obtido de Wonca: {tracking_code}")
            return result
        except Exception as e:
            logger.warning(f"⚠️ Falha ao rastrear {tracking_code} na Wonca: {str(e)}")
            return None
    
    def extrair_situacao(self, dados_rastreamento: Dict) -> Optional[str]:
        """
        Extrai a situação atual do rastreamento
        
        Args:
            dados_rastreamento: Resposta da API
            
        Returns:
            String com a situação ou None
        """
        try:
            # Tenta encontrar a situação em diferentes formatos possíveis
            if isinstance(dados_rastreamento, dict):
                # Possíveis caminhos para situação
                for key in ['status', 'situacao', 'state', 'situation', 'current_status']:
                    if key in dados_rastreamento:
                        return dados_rastreamento[key]
                
                # Se houver histórico de eventos
                if 'events' in dados_rastreamento or 'historico' in dados_rastreamento:
                    eventos = dados_rastreamento.get('events') or dados_rastreamento.get('historico')
                    if isinstance(eventos, list) and len(eventos) > 0:
                        # Pega o primeiro evento (mais recente)
                        evento = eventos[0]
                        if isinstance(evento, dict):
                            for key in ['status', 'situacao', 'status_text', 'description']:
                                if key in evento:
                                    return evento[key]
            
            return None
        except Exception as e:
            logger.warning(f"Erro ao extrair situação: {str(e)}")
            return None
    
    def formatar_resposta(self, tracking_code: str, dados: Dict) -> Dict:
        """
        Formata a resposta da API para uso interno
        
        Args:
            tracking_code: Código de rastreio
            dados: Resposta bruta da API
            
        Returns:
            Dict formatado
        """
        return {
            'codigo': tracking_code,
            'fonte': 'WONCA',
            'timestamp': datetime.now().isoformat(),
            'dados_brutos': dados,
            'situacao': self.extrair_situacao(dados),
            'procesado': True
        }


# Função helper simples
def rastrear_wonca(tracking_code: str) -> Optional[Dict]:
    """
    Função simples para rastrear
    
    Uso:
        resultado = rastrear_wonca('AD292694916BR')
        if resultado:
            print(resultado['situacao'])
    """
    try:
        api = WoncaTrackingAPI()
        dados = api.rastrear(tracking_code)
        if dados:
            return api.formatar_resposta(tracking_code, dados)
    except Exception as e:
        logger.error(f"Erro ao rastrear {tracking_code}: {str(e)}")
    
    return None


if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Teste rápido
    print("🧪 Teste do módulo Wonca Tracking API\n")
    
    tracking_code = 'AD292694916BR'
    print(f"Rastreando: {tracking_code}")
    
    resultado = rastrear_wonca(tracking_code)
    
    if resultado:
        print("\n✅ Sucesso!")
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
    else:
        print("\n⚠️ Falha no rastreamento")
