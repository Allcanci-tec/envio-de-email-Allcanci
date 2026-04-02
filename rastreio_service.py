#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════╗
║                   RASTREAMENTO DE ENCOMENDAS SERVICE                     ║
║                                                                          ║
║  Consulta status de rastreamento via API Wonca (SiteRastreio)           ║
║  Retorna apenas o evento mais recente de forma amigável                 ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

import os
import logging
import requests
import sys
import time
from pathlib import Path
from typing import Dict, Tuple, Optional, List
from datetime import datetime
from dotenv import load_dotenv

# ======================================================================
# ⚙️ CONFIGURAÇÕES
# ======================================================================

BASE_DIR = Path(__file__).parent
ENV_FILE = BASE_DIR / '.env'

# Carregar variáveis de ambiente
load_dotenv(ENV_FILE)

WONCA_API_KEY = os.getenv('WONCA_API_KEY')
WONCA_API_URL = os.getenv('WONCA_API_URL', 'https://api-labs.wonca.com.br')
WONCA_SERVICE_PATH = os.getenv('WONCA_SERVICE_PATH', 'wonca.labs.v1.LabsService/Track')

TIMEOUT_REQUISICAO = 15  # seconds (aumentado)
MAX_RETRIES = 3  # retries com backoff
RETRY_DELAY = 3
BACKOFF_FACTOR = 1.5  # Multiplicador para retry (3s, 4.5s, 6.75s)

# ======================================================================
# 📋 LOGGING
# ======================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(BASE_DIR / 'rastreio_service.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


# ======================================================================
# 🔍 MAPEAMENTO DE STATUS AMIGÁVEIS
# ======================================================================

MAPEAMENTO_STATUS = {
    'Posted': {
        'pt_br': 'Objeto postado',
        'emoji': '📤',
        'prioridade': 1
    },
    'Forwarded': {
        'pt_br': 'Objeto em trânsito',
        'emoji': '🚚',
        'prioridade': 2
    },
    'In Delivery': {
        'pt_br': 'Objeto saiu para entrega',
        'emoji': '🚗',
        'prioridade': 3
    },
    'Delivered': {
        'pt_br': 'Objeto entregue',
        'emoji': '✅',
        'prioridade': 10
    },
    'Exception': {
        'pt_br': 'Problema na entrega',
        'emoji': '⚠️',
        'prioridade': 5
    },
    'Returned': {
        'pt_br': 'Objeto devolvido',
        'emoji': '↩️',
        'prioridade': 9
    },
    'Held': {
        'pt_br': 'Objeto retido',
        'emoji': '🔒',
        'prioridade': 5
    },
}


# ======================================================================
# 🎯 CONSULTA DE RASTREAMENTO
# ======================================================================

class RastreioService:
    """
    Serviço para consultar rastreamento via API Wonca.
    """

    def __init__(self):
        if not WONCA_API_KEY:
            logger.error("❌ WONCA_API_KEY não configurada no .env!")
            raise ValueError("WONCA_API_KEY obrigatória")

        self.api_key = WONCA_API_KEY
        self.api_url = WONCA_API_URL
        self.service_path = WONCA_SERVICE_PATH
        self.endpoint = f"{self.api_url}/{self.service_path}"

    def consultar_etiqueta(self, codigo_rastreio: str) -> Dict:
        """
        Consulta o status de uma etiqueta na API Wonca.

        Args:
            codigo_rastreio: Código da etiqueta (ex: "AA123456789BR")

        Returns:
            Dict com estrutura:
            {
                'sucesso': bool,
                'evento_recente': {
                    'status': str (em português),
                    'status_original': str (em inglês),
                    'data': str (ISO format),
                    'descricao': str,
                    'local': str,
                    'emoji': str
                },
                'historico': list (todos os eventos),
                'codigo_rastreio': str,
                'mensagem': str (para erros)
            }
        """

        logger.info(f"🔍 Consultando: {codigo_rastreio}")

        for tentativa in range(1, MAX_RETRIES + 1):
            try:
                # Preparar requisição com headers anti-bloqueio
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'application/json',
                    'Accept-Language': 'pt-BR,pt;q=0.9',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Cache-Control': 'no-cache',
                }

                payload = {
                    'code': codigo_rastreio.upper().strip()
                }

                tempo_espera = RETRY_DELAY * (BACKOFF_FACTOR ** (tentativa - 1))
                logger.info(f"   Tentativa {tentativa}/{MAX_RETRIES}...")

                # Fazer requisição
                response = requests.post(
                    self.endpoint,
                    headers=headers,
                    json=payload,
                    timeout=TIMEOUT_REQUISICAO
                )

                # Status HTTP
                if response.status_code == 401:
                    logger.error("❌ Erro 401: Token de API inválido ou expirado")
                    return {
                        'sucesso': False,
                        'codigo_rastreio': codigo_rastreio,
                        'mensagem': 'Token de API inválido. Verifique WONCA_API_KEY no .env',
                        'evento_recente': None,
                        'historico': []
                    }

                if response.status_code == 404:
                    logger.warning(f"⚠️ Etiqueta não encontrada: {codigo_rastreio}")
                    return {
                        'sucesso': False,
                        'codigo_rastreio': codigo_rastreio,
                        'mensagem': f'Etiqueta {codigo_rastreio} não encontrada no sistema',
                        'evento_recente': None,
                        'historico': []
                    }

                if response.status_code not in (200, 201):
                    logger.warning(f"⚠️ Status HTTP {response.status_code}: {response.text}")
                    if tentativa < MAX_RETRIES:
                        logger.info(f"   ⏳ Aguardando {tempo_espera:.1f}s antes de retry...")
                        time.sleep(tempo_espera)
                        continue
                    return {
                        'sucesso': False,
                        'codigo_rastreio': codigo_rastreio,
                        'mensagem': f'Erro HTTP {response.status_code}',
                        'evento_recente': None,
                        'historico': []
                    }

                # Parsear resposta
                dados = response.json()
                logger.info(f"✅ Resposta recebida")

                # Extrair eventos e ordenar por data (mais recente primeiro)
                eventos = self._processar_eventos(dados)

                if not eventos:
                    logger.warning("⚠️ Nenhum evento encontrado")
                    return {
                        'sucesso': False,
                        'codigo_rastreio': codigo_rastreio,
                        'mensagem': 'Nenhum evento de rastreamento disponível',
                        'evento_recente': None,
                        'historico': []
                    }

                # Pegar evento mais recente
                evento_recente = eventos[0]
                logger.info(f"📊 Status: {evento_recente['status']} ({evento_recente['emoji']})")

                return {
                    'sucesso': True,
                    'codigo_rastreio': codigo_rastreio,
                    'evento_recente': evento_recente,
                    'historico': eventos,
                    'mensagem': None
                }

            except requests.exceptions.Timeout:
                logger.warning(f"⏱️ Timeout na tentativa {tentativa}/{MAX_RETRIES}")
                if tentativa < MAX_RETRIES:
                    tempo_espera = RETRY_DELAY * (BACKOFF_FACTOR ** (tentativa - 1))
                    logger.info(f"   ⏳ Aguardando {tempo_espera:.1f}s antes de retry...")
                    time.sleep(tempo_espera)
                    continue

            except requests.exceptions.ConnectionError:
                logger.warning(f"🌐 Erro de conexão na tentativa {tentativa}/{MAX_RETRIES}")
                if tentativa < MAX_RETRIES:
                    tempo_espera = RETRY_DELAY * (BACKOFF_FACTOR ** (tentativa - 1))
                    logger.info(f"   ⏳ Aguardando {tempo_espera:.1f}s antes de retry...")
                    time.sleep(tempo_espera)
                    continue

            except Exception as e:
                logger.error(f"❌ Erro inesperado: {e}")
                if tentativa < MAX_RETRIES:
                    tempo_espera = RETRY_DELAY * (BACKOFF_FACTOR ** (tentativa - 1))
                    logger.info(f"   ⏳ Aguardando {tempo_espera:.1f}s antes de retry...")
                    time.sleep(tempo_espera)
                    continue
                import traceback
                traceback.print_exc()

        return {
            'sucesso': False,
            'codigo_rastreio': codigo_rastreio,
            'mensagem': f'Falha após {MAX_RETRIES} tentativas',
            'evento_recente': None,
            'historico': []
        }

    def _processar_eventos(self, dados: Dict) -> List[Dict]:
        """
        Processa eventos da resposta da API Wonca.
        Retorna lista ordenada por data (mais recente primeiro).
        """

        eventos = []

        # Estrutura pode variar - tenta diferentes caminhos
        historico = []

        if isinstance(dados, dict):
            # Tenta: dados['result']['events']
            if 'result' in dados and 'events' in dados['result']:
                historico = dados['result']['events']
            # Tenta: dados['events']
            elif 'events' in dados:
                historico = dados['events']
            # Tenta: dados['track']['events']
            elif 'track' in dados and 'events' in dados['track']:
                historico = dados['track']['events']

        if not historico:
            logger.warning("⚠️ Não foi possível localizar eventos na resposta")
            return []

        # Processar cada evento
        for evento in historico:
            try:
                status_original = evento.get('status', 'DESCONHECIDO')
                data_evento = evento.get('date', evento.get('timestamp', ''))
                descricao = evento.get('detail', evento.get('description', ''))
                local = evento.get('location', evento.get('local', ''))

                # Traduzir status usando mapa
                status_traduzido = MAPEAMENTO_STATUS.get(status_original, {})
                status_pt = status_traduzido.get('pt_br', status_original)
                emoji = status_traduzido.get('emoji', '📦')
                prioridade = status_traduzido.get('prioridade', 0)

                evento_processado = {
                    'status': status_pt,
                    'status_original': status_original,
                    'data': data_evento,
                    'descricao': descricao,
                    'local': local,
                    'emoji': emoji,
                    'prioridade': prioridade
                }

                eventos.append(evento_processado)

            except Exception as e:
                logger.warning(f"⚠️ Erro ao processar evento: {e}")
                continue

        # Ordenar por data (mais recente primeiro) e depois por prioridade
        eventos.sort(key=lambda x: x['prioridade'], reverse=True)

        return eventos


# ======================================================================
# 🎯 FUNÇÕES AUXILIARES (API SIMPLES)
# ======================================================================

def obter_status_atual(codigo_rastreio: str) -> Tuple[bool, str]:
    """
    Função simples para obter status atual de uma etiqueta.

    Args:
        codigo_rastreio: Código da etiqueta

    Returns:
        (sucesso: bool, status: str)

    Exemplo:
        sucesso, status = obter_status_atual("AA123456789BR")
        if sucesso:
            print(status)  # "✅ Objeto entregue"
    """

    try:
        servico = RastreioService()
        resultado = servico.consultar_etiqueta(codigo_rastreio)

        if not resultado['sucesso']:
            return False, resultado['mensagem']

        evento = resultado['evento_recente']
        msg = f"{evento['emoji']} {evento['status']}"

        if evento['local']:
            msg += f" - {evento['local']}"

        return True, msg

    except Exception as e:
        logger.error(f"Erro ao obter status: {e}")
        return False, f"Erro ao consultar rastreamento: {e}"


def obter_detalhes_completos(codigo_rastreio: str) -> Dict:
    """
    Função para obter detalhes completos do rastreamento.

    Args:
        codigo_rastreio: Código da etiqueta

    Returns:
        Dict com informações completas

    Exemplo:
        dados = obter_detalhes_completos("AA123456789BR")
        print(dados['evento_recente']['status'])
    """

    try:
        servico = RastreioService()
        return servico.consultar_etiqueta(codigo_rastreio)

    except Exception as e:
        logger.error(f"Erro ao obter detalhes: {e}")
        return {
            'sucesso': False,
            'mensagem': str(e),
            'evento_recente': None,
            'historico': []
        }


# ======================================================================
# 🧪 TESTE
# ======================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🧪 TESTE DO SERVIÇO DE RASTREAMENTO")
    print("="*70 + "\n")

    # Teste com etiqueta de exemplo
    codigo_teste = "AA123456789BR"

    print(f"Consultando: {codigo_teste}\n")

    sucesso, status = obter_status_atual(codigo_teste)
    if sucesso:
        print(f"✅ Status: {status}\n")
    else:
        print(f"❌ Erro: {status}\n")

    print("=" * 70)
    print("Nota: Use uma etiqueta válida para teste completo")
    print("=" * 70 + "\n")
