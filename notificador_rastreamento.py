#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════╗
║                INTEGRAÇÃO WHATSAPP + RASTREAMENTO                        ║
║                                                                          ║
║  Monitora mudanças de status e envia notificações por WhatsApp           ║
║  Com cache inteligente para evitar gasto desnecessário de créditos       ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

import os
import logging
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dotenv import load_dotenv

# Importar módulos locais
try:
    from rastreio_service import obter_detalhes_completos
    from rastreamento_cache import (
        pode_consultar_api,
        obter_do_cache,
        guardar_no_cache,
        obter_status_recente
    )
    from whatsapp_service import enviar_mensagem
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    print("   Certifique-se que está no diretório correto")
    sys.exit(1)

# ======================================================================
# ⚙️ CONFIGURAÇÕES
# ======================================================================

BASE_DIR = Path(__file__).parent
ENV_FILE = BASE_DIR / '.env'
HISTORICO_FILE = BASE_DIR / 'historico_rastreamento_completo.json'

load_dotenv(ENV_FILE)

# ======================================================================
# 📋 LOGGING
# ======================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(BASE_DIR / 'notificador_rastreamento.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


# ======================================================================
# 📊 GERENCIADOR DE HISTÓRICO
# ======================================================================

class GerenciadorHistorico:
    """
    Mantém histórico de rastreamentos e detecta mudanças de status.
    """

    def __init__(self):
        self.historico = self._carregar_historico()

    def _carregar_historico(self) -> Dict:
        """Carrega histórico de arquivo."""
        if HISTORICO_FILE.exists():
            try:
                with open(HISTORICO_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"⚠️ Erro ao carregar histórico: {e}")

        return {}

    def _salvar_historico(self):
        """Salva histórico em arquivo."""
        try:
            with open(HISTORICO_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.historico, f, indent=2, ensure_ascii=False)
            logger.info(f"💾 Histórico salvo ({len(self.historico)} rastreamentos)")
        except Exception as e:
            logger.error(f"❌ Erro ao salvar histórico: {e}")

    def houve_mudanca(self, etiqueta: str, novo_status: str) -> Tuple[bool, Optional[str]]:
        """
        Verifica se houve mudança de status.

        Args:
            etiqueta: Código da etiqueta
            novo_status: Status atual

        Returns:
            (houve_mudanca: bool, status_anterior: str or None)
        """

        etiqueta_limpa = etiqueta.upper().strip()

        if etiqueta_limpa not in self.historico:
            logger.info(f"   📌 Primeira vez rastreando: {etiqueta_limpa}")
            return False, None

        status_anterior = self.historico[etiqueta_limpa].get('ultimo_status', '')

        if status_anterior != novo_status:
            logger.info(f"   ✨ Status mudou: {status_anterior} → {novo_status}")
            return True, status_anterior

        logger.info(f"   🔄 Status sem mudança: {novo_status}")
        return False, None

    def registrar_rastreamento(self, etiqueta: str, numero_cliente: str, status: str):
        """
        Registra rastreamento no histórico.

        Args:
            etiqueta: Código da etiqueta
            numero_cliente: Número WhatsApp do cliente
            status: Status atual
        """

        etiqueta_limpa = etiqueta.upper().strip()

        self.historico[etiqueta_limpa] = {
            'numero_cliente': numero_cliente,
            'ultimo_status': status,
            'ultima_atualizacao': datetime.now().isoformat(),
        }

        self._salvar_historico()
        logger.info(f"   📝 Registrado: {etiqueta_limpa}")

    def obter_info_rastreamento(self, etiqueta: str) -> Dict:
        """Obtém informações de um rastreamento."""
        etiqueta_limpa = etiqueta.upper().strip()
        return self.historico.get(etiqueta_limpa, {})


# ======================================================================
# 🎯 NOTIFICADOR DE RASTREAMENTO
# ======================================================================

class NotificadorRastreamento:
    """
    Coordena consulta de rastreamento, detecção de mudanças e envio de mensagens.
    """

    def __init__(self):
        self.historico = GerenciadorHistorico()
        logger.info("🚀 Notificador de Rastreamento inicializado")

    def processar_rastreamento(
        self,
        etiqueta: str,
        numero_cliente: str
    ) -> Tuple[bool, str]:
        """
        Processa rastreamento de uma etiqueta e envia notificação se houver mudança.

        Args:
            etiqueta: Código da etiqueta
            numero_cliente: Número WhatsApp do cliente (11984163357 ou +5511984163357)

        Returns:
            (sucesso: bool, mensagem: str)

        Exemplo:
            sucesso, msg = notificador.processar_rastreamento(
                "AA123456789BR",
                "31984163357"
            )
        """

        etiqueta_limpa = etiqueta.upper().strip()
        numero_limpo = ''.join(filter(str.isdigit, numero_cliente))

        logger.info("")
        logger.info("=" * 70)
        logger.info(f"📦 PROCESSANDO: {etiqueta_limpa}")
        logger.info(f"📱 Cliente: {numero_limpo}")
        logger.info("=" * 70)

        # PASSO 1: Verificar se pode consultar API
        # ========================================
        pode_consultar, motivo_cache = pode_consultar_api(etiqueta_limpa)
        logger.info(f"1️⃣ Cache: {motivo_cache}")

        if not pode_consultar:
            # Usar dados em cache
            logger.info("   📦 Usando dados em cache (sem consultar API)")
            dados_cache = obter_do_cache(etiqueta_limpa)

            if dados_cache:
                evento = dados_cache.get('evento_recente', {})
                status_atual = evento.get('status', 'Status desconhecido')

                houve_mudanca, status_anterior = self.historico.houve_mudanca(
                    etiqueta_limpa,
                    status_atual
                )

                if houve_mudanca:
                    # Enviar notificação mesmo usando cache
                    return self._enviar_notificacao(
                        número_limpo,
                        etiqueta_limpa,
                        status_atual,
                        evento,
                        usar_cache=True
                    )

                return True, f"✅ Status em cache (sem mudança): {status_atual}"

        # PASSO 2: Consultar API Wonca
        # =============================
        logger.info("2️⃣ Consultando API...")
        resultado = obter_detalhes_completos(etiqueta_limpa)

        if not resultado['sucesso']:
            logger.error(f"   ❌ {resultado['mensagem']}")
            return False, resultado['mensagem']

        # PASSO 3: Guardar no cache
        # =========================
        logger.info("3️⃣ Armazenando em cache...")
        guardar_no_cache(etiqueta_limpa, resultado)

        # PASSO 4: Extrair evento recente
        # ================================
        evento = resultado.get('evento_recente', {})
        status_atual = evento.get('status', 'Status desconhecido')

        logger.info(f"4️⃣ Status atual: {evento.get('emoji', '❓')} {status_atual}")

        # PASSO 5: Detectar mudança
        # =========================
        houve_mudanca, status_anterior = self.historico.houve_mudanca(
            etiqueta_limpa,
            status_atual
        )

        if not houve_mudanca:
            logger.info("   🔄 Sem mudança de status - não enviando mensagem")
            self.historico.registrar_rastreamento(etiqueta_limpa, numero_limpo, status_atual)
            return True, f"✅ Consultado (sem mudança): {status_atual}"

        # PASSO 6: Enviar notificação
        # ============================
        logger.info("5️⃣ Mudança detectada - enviando notificação!")
        return self._enviar_notificacao(
            numero_limpo,
            etiqueta_limpa,
            status_atual,
            evento,
            usar_cache=False
        )

    def _enviar_notificacao(
        self,
        numero: str,
        etiqueta: str,
        status: str,
        evento: Dict,
        usar_cache: bool = False
    ) -> Tuple[bool, str]:
        """
        Envia notificação por WhatsApp.

        Args:
            numero: Número do cliente
            etiqueta: Código da etiqueta
            status: Status do pacote
            evento: Dicionário com detalhes do evento
            usar_cache: Se foi consultado do cache
        """

        # Formatar mensagem amigável
        emoji = evento.get('emoji', '📦')
        localizacao = evento.get('local', '')
        descricao = evento.get('descricao', '')

        mensagem = f"""Olá! 👋

Seu pedido mudou de status! ✨

📦 Código: {etiqueta}
{emoji} Status: {status}"""

        if localizacao:
            mensagem += f"\n📍 Local: {localizacao}"

        if descricao:
            mensagem += f"\n📝 Detalhes: {descricao}"

        mensagem += f"""

Acompanhe seu rastreamento em tempo real!
🔗 https://www.siterastreio.com.br/

Obrigado por comprar com a Allcanci! 💜
"""

        # Enviar via WhatsApp
        logger.info("6️⃣ Enviando via WhatsApp...")
        logger.info(f"   Mensagem ({len(mensagem)} caracteres)")

        try:
            sucesso, msg_resultado = enviar_mensagem(numero, mensagem, prioridade=5)

            if sucesso:
                logger.info(f"   ✅ {msg_resultado}")
                self.historico.registrar_rastreamento(etiqueta, numero, status)

                origem = "📦 cache" if usar_cache else "🌐 API"
                return True, f"✅ Notificação enviada ({origem})"

            else:
                logger.warning(f"   ⚠️ {msg_resultado}")
                return False, f"⚠️ Falha ao enviar: {msg_resultado}"

        except Exception as e:
            logger.error(f"   ❌ Erro: {e}")
            return False, f"❌ Erro ao enviar: {e}"

    def processar_lote(self, rastreamentos: List[Tuple[str, str]]) -> Dict:
        """
        Processa um lote de rastreamentos.

        Args:
            rastreamentos: Lista de tuplas (etiqueta, numero_cliente)

        Returns:
            Dict com estatísticas do processamento
        """

        logger.info("")
        logger.info("=" * 70)
        logger.info(f"📊 PROCESSANDO LOTE ({len(rastreamentos)} rastreamentos)")
        logger.info("=" * 70)

        stats = {
            'total': len(rastreamentos),
            'sucesso': 0,
            'falha': 0,
            'notificacoes_enviadas': 0,
            'tempo_inicio': datetime.now().isoformat(),
        }

        for etiqueta, numero in rastreamentos:
            try:
                sucesso, msg = self.processar_rastreamento(etiqueta, numero)

                if sucesso:
                    stats['sucesso'] += 1
                    if "enviada" in msg.lower():
                        stats['notificacoes_enviadas'] += 1
                else:
                    stats['falha'] += 1

                logger.info(f"   {msg}\n")

            except Exception as e:
                logger.error(f"   ❌ Erro inesperado: {e}")
                stats['falha'] += 1

        stats['tempo_fim'] = datetime.now().isoformat()

        logger.info("=" * 70)
        logger.info(f"📊 RESULTADO:")
        logger.info(f"   ✅ Sucesso: {stats['sucesso']}/{stats['total']}")
        logger.info(f"   ❌ Falha: {stats['falha']}/{stats['total']}")
        logger.info(f"   📤 Notificações: {stats['notificacoes_enviadas']}")
        logger.info("=" * 70 + "\n")

        return stats


# ======================================================================
# 🎯 API SIMPLES
# ======================================================================

_notificador = NotificadorRastreamento()


def notificar(etiqueta: str, numero_cliente: str) -> Tuple[bool, str]:
    """
    Função simples para processar rastreamento e enviar notificação.

    Args:
        etiqueta: Código da etiqueta
        numero_cliente: Número WhatsApp do cliente

    Returns:
        (sucesso: bool, mensagem: str)

    Exemplo:
        sucesso, msg = notificar("AA123456789BR", "31984163357")
    """
    return _notificador.processar_rastreamento(etiqueta, numero_cliente)


def notificar_lote(rastreamentos: List[Tuple[str, str]]) -> Dict:
    """
    Processa múltiplos rastreamentos.

    Args:
        rastreamentos: [(etiqueta1, numero1), (etiqueta2, numero2), ...]

    Returns:
        Estatísticas do processamento
    """
    return _notificador.processar_lote(rastreamentos)


# ======================================================================
# 🧪 TESTE
# ======================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🧪 TESTE DO NOTIFICADOR DE RASTREAMENTO")
    print("="*70 + "\n")

    print("📚 Instruções de uso:\n")

    print("1️⃣ USO SIMPLES:")
    print("   from notificador_rastreamento import notificar")
    print('   sucesso, msg = notificar("AA123456789BR", "31984163357")')
    print("   print(msg)\n")

    print("2️⃣ PROCESSAMENTO EM LOTE:")
    print("   from notificador_rastreamento import notificar_lote")
    print("   rastreamentos = [")
    print('       ("AA123456789BR", "31984163357"),')
    print('       ("BB987654321BR", "11987654321"),')
    print("   ]")
    print("   stats = notificar_lote(rastreamentos)")
    print("   print(stats)\n")

    print("=" * 70)
    print("Nota: Configure no .env antes de usar em produção")
    print("=" * 70 + "\n")
