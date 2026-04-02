#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════╗
║                    CACHE DE RASTREAMENTO                                ║
║                                                                          ║
║  Cache local para evitar consultas repetidas à API Wonca                ║
║  Respeita limite de 4 horas entre consultas por etiqueta                ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

import json
import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

# ======================================================================
# ⚙️ CONFIGURAÇÕES
# ======================================================================

BASE_DIR = Path(__file__).parent
CACHE_FILE = BASE_DIR / 'rastreamento_cache.json'

TEMPO_CACHE_HORAS = 4  # Não consultar a mesma etiqueta em menos de 4 horas
LIMPAR_CACHE_DIAS = 7  # Limpar ent programadosradas com mais de 7 dias

# ======================================================================
# 📋 LOGGING
# ======================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(BASE_DIR / 'rastreamento_cache.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


# ======================================================================
# 💾 GERENCIADOR DE CACHE
# ======================================================================

class GerenciadorCache:
    """
    Gerencia cache de rastreamentos com expiração automática.
    """

    def __init__(self):
        self.cache = self._carregar_cache()
        logger.info(f"📦 Cache carregado ({len(self.cache)} etiquetas)")

    def _carregar_cache(self) -> Dict:
        """Carrega cache do arquivo."""
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"⚠️ Erro ao carregar cache: {e}")

        return {}

    def _salvar_cache(self):
        """Salva cache em arquivo."""
        try:
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
            logger.info(f"💾 Cache salvo ({len(self.cache)} etiquetas)")
        except Exception as e:
            logger.error(f"❌ Erro ao salvar cache: {e}")

    def _limpar_cache_expirado(self):
        """Remove entradas expiradas do cache."""
        agora = datetime.now()
        limite_dias = agora - timedelta(days=LIMPAR_CACHE_DIAS)

        etiquetas_removidas = []

        for etiqueta, dados in list(self.cache.items()):
            try:
                criado_em = datetime.fromisoformat(dados.get('criado_em', ''))

                if criado_em < limite_dias:
                    del self.cache[etiqueta]
                    etiquetas_removidas.append(etiqueta)
            except:
                pass

        if etiquetas_removidas:
            logger.info(f"🗑️ Limpas {len(etiquetas_removidas)} entradas expiradas")
            self._salvar_cache()

        return etiquetas_removidas

    def pode_consultar_api(self, codigo_rastreio: str) -> Tuple[bool, str]:
        """
        Verifica se pode consultar a API para esta etiqueta.
        Respeita limite de 4 horas entre consultas.

        Args:
            codigo_rastreio: Código da etiqueta

        Returns:
            (pode_consultar: bool, motivo: str)
        """

        codigo_limpo = codigo_rastreio.upper().strip()

        # Se não está no cache, pode consultar
        if codigo_limpo not in self.cache:
            return True, "✅ Primeira consulta"

        # Verificar tempo desde última consulta
        try:
            ultimo_acesso = datetime.fromisoformat(
                self.cache[codigo_limpo]['ultimo_acesso']
            )
        except:
            return True, "✅ Dados corrompidos, consultar novamente"

        tempo_decorrido = datetime.now() - ultimo_acesso
        tempo_minimo = timedelta(hours=TEMPO_CACHE_HORAS)

        if tempo_decorrido < tempo_minimo:
            horas_restantes = (tempo_minimo - tempo_decorrido).total_seconds() / 3600
            msg = f"⏳ Cache válido. Próxima consulta em {horas_restantes:.1f}h"
            return False, msg

        return True, "✅ Cache expirado, pode consultar"

    def obter_do_cache(self, codigo_rastreio: str) -> Optional[Dict]:
        """
        Obtém dados do cache se disponíveis.

        Args:
            codigo_rastreio: Código da etiqueta

        Returns:
            Dict com dados em cache ou None
        """

        codigo_limpo = codigo_rastreio.upper().strip()

        if codigo_limpo not in self.cache:
            return None

        try:
            dados = self.cache[codigo_limpo]
            logger.info(f"📦 Usando cache para {codigo_limpo}")
            return dados['resultado']
        except:
            logger.warning(f"⚠️ Erro ao recuperar do cache: {codigo_limpo}")
            return None

    def guardar_no_cache(self, codigo_rastreio: str, dados_resultado: Dict):
        """
        Guarda dados de rastreamento no cache.

        Args:
            codigo_rastreio: Código da etiqueta
            dados_resultado: Dict retornado por rastreio_service.consultar_etiqueta()
        """

        codigo_limpo = codigo_rastreio.upper().strip()

        try:
            self.cache[codigo_limpo] = {
                'criado_em': datetime.now().isoformat(),
                'ultimo_acesso': datetime.now().isoformat(),
                'resultado': dados_resultado,
                'status': dados_resultado.get('evento_recente', {}).get('status', 'DESCONHECIDO')
            }

            self._salvar_cache()
            logger.info(f"💾 Armazenado em cache: {codigo_limpo}")

        except Exception as e:
            logger.error(f"❌ Erro ao guardar no cache: {e}")

    def obter_status_recente(self, codigo_rastreio: str) -> Dict:
        """
        Obtém status recente do cache (muito rápido).

        Args:
            codigo_rastreio: Código da etiqueta

        Returns:
            Dict com evento recente ou vazio
        """

        codigo_limpo = codigo_rastreio.upper().strip()

        if codigo_limpo not in self.cache:
            return {}

        try:
            return self.cache[codigo_limpo].get('resultado', {}).get('evento_recente', {})
        except:
            return {}

    def limpar_tudo(self):
        """Limpa todo o cache."""
        self.cache = {}
        self._salvar_cache()
        logger.info("🗑️ Cache limpo completamente")

    def limpar_etiqueta(self, codigo_rastreio: str):
        """Limpa cache de uma etiqueta específica."""
        codigo_limpo = codigo_rastreio.upper().strip()

        if codigo_limpo in self.cache:
            del self.cache[codigo_limpo]
            self._salvar_cache()
            logger.info(f"🗑️ Limpas dados de: {codigo_limpo}")

    def obter_estatisticas(self) -> Dict:
        """Retorna estatísticas do cache."""
        self._limpar_cache_expirado()

        return {
            'total_etiquetas': len(self.cache),
            'arquivo': str(CACHE_FILE),
            'tempo_expiracao_horas': TEMPO_CACHE_HORAS,
            'tempo_limpeza_dias': LIMPAR_CACHE_DIAS,
        }


# ======================================================================
# 🎯 INSTÂNCIA GLOBAL
# ======================================================================

_cache = GerenciadorCache()


def pode_consultar_api(codigo_rastreio: str) -> Tuple[bool, str]:
    """Wrapper para função global."""
    return _cache.pode_consultar_api(codigo_rastreio)


def obter_do_cache(codigo_rastreio: str) -> Optional[Dict]:
    """Wrapper para função global."""
    return _cache.obter_do_cache(codigo_rastreio)


def guardar_no_cache(codigo_rastreio: str, dados_resultado: Dict):
    """Wrapper para função global."""
    _cache.guardar_no_cache(codigo_rastreio, dados_resultado)


def obter_status_recente(codigo_rastreio: str) -> Dict:
    """Wrapper para função global."""
    return _cache.obter_status_recente(codigo_rastreio)


# ======================================================================
# 🧪 TESTE
# ======================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🧪 TESTE DO CACHE DE RASTREAMENTO")
    print("="*70 + "\n")

    # Teste com dados fictícios
    teste_codigo = "AA123456789BR"
    teste_dados = {
        'sucesso': True,
        'evento_recente': {
            'status': 'Em trânsito',
            'emoji': '🚚',
            'local': 'São Paulo'
        }
    }

    print(f"1️⃣ Guardando dados de {teste_codigo}")
    guardar_no_cache(teste_codigo, teste_dados)

    print(f"2️⃣ Verificando se pode consultar API")
    pode, motivo = pode_consultar_api(teste_codigo)
    print(f"   {motivo}")

    print(f"3️⃣ Obtendo status do cache")
    status = obter_status_recente(teste_codigo)
    print(f"   {status.get('emoji', '❓')} {status.get('status', 'N/A')}")

    print(f"\n4️⃣ Estatísticas do cache:")
    stats = _cache.obter_estatisticas()
    for chave, valor in stats.items():
        print(f"   {chave}: {valor}")

    print("\n" + "="*70 + "\n")
