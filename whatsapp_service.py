"""
╔══════════════════════════════════════════════════════════════════════════╗
║                    WHATSAPP SERVICE - ANTI-SPAM                          ║
║                                                                          ║
║  Sistema robusto para envio de mensagens via WhatsApp Web               ║
║  com proteções contra banimento por spam                               ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

import os
import time
import logging
import json
import sys
import urllib.parse
from pathlib import Path
from datetime import datetime, timedelta
from collections import deque
import random
from typing import Tuple, Dict, List, Optional
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# ======================================================================
# ⚙️ CONFIGURAÇÕES ANTI-SPAM (AJUSTE CONFORME NECESSÁRIO)
# ======================================================================

# Limites seguros do WhatsApp
LIMITE_MENSAGENS_HORA = 30      # Máx 30 msgs/hora
LIMITE_MENSAGENS_DIA = 200      # Máx 200 msgs/dia
INTERVALO_MINIMO_ENTRE_MSGS = 30  # 30 segundos entre mensagens (humanizado)

# Detecção de bloqueio
ERROS_CONSECUTIVOS_PERMITIDOS = 3  # Após 3 erros seguidos, pausar
TEMPO_PAUSA_BLOQUEIO = 1800  # 30 minutos de pausa se detectar bloqueio

# Horário comercial (não enviar fora disso)
HORARIO_INICIO = 8   # 8 da manhã
HORARIO_FIM = 20     # 20:00 (8 da noite)

# Configurações técnicas
AUTO_HEADLESS = True
MAX_RETRIES = 2
RETRY_DELAY = 5
QR_TIMEOUT = 120

BASE_DIR = Path(__file__).parent
WHATSAPP_SESSION_DIR = BASE_DIR / 'whatsapp_session'
SESSION_MARKER = WHATSAPP_SESSION_DIR / '.logged_in'
LOG_FILE = BASE_DIR / 'whatsapp_envios.json'
CHECKPOINT_FILE = BASE_DIR / 'whatsapp_checkpoint.json'
FILA_FILE = BASE_DIR / 'whatsapp_fila.json'
STATS_FILE = BASE_DIR / 'whatsapp_stats.json'

WHATSAPP_SESSION_DIR.mkdir(exist_ok=True, parents=True)

# ======================================================================
# 📋 LOGGING
# ======================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('whatsapp_service.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ======================================================================
# 📊 GERENCIADOR DE ESTATÍSTICAS (ANTI-SPAM)
# ======================================================================

class AntiSpamManager:
    """
    Gerencia limites de envio e detecta bloqueios.
    Garante que não seremos banidos do WhatsApp.
    """

    def __init__(self):
        self.stats = self._carregar_stats()
        self.erros_consecutivos = 0
        self.ultimo_erro = None
        self.em_pausa = False
        self.pausa_ate = None

    def _carregar_stats(self) -> Dict:
        """Carrega estatísticas de envios anteriores."""
        if STATS_FILE.exists():
            try:
                with open(STATS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass

        return {
            'hoje': [],  # Lista de timestamps de hoje
            'hora_atual': [],  # Lista de timestamps da hora atual
            'historico_contatos': {},  # Para evitar duplicatas em 24h
            'bloqueios_detectados': 0,
            'ultimo_bloqueio': None,
        }

    def _salvar_stats(self):
        """Salva estatísticas em arquivo."""
        try:
            with open(STATS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Erro ao salvar stats: {e}")

    def _limpar_timestamps_antigos(self):
        """Remove timestamps de ontem ou de mais de 1 hora atrás."""
        agora = datetime.now()
        hoje = agora.date()

        # Limpar lista de hoje (manter apenas timestamps de hoje)
        self.stats['hoje'] = [
            ts for ts in self.stats['hoje']
            if datetime.fromisoformat(ts).date() == hoje
        ]

        # Limpar lista de hora atual
        uma_hora_atras = agora - timedelta(hours=1)
        self.stats['hora_atual'] = [
            ts for ts in self.stats['hora_atual']
            if datetime.fromisoformat(ts) > uma_hora_atras
        ]

    def pode_enviar(self) -> Tuple[bool, str]:
        """
        Verifica se podemos enviar uma mensagem AGORA.
        Retorna: (pode_enviar, motivo)
        """

        # Verificar se está em pausa por bloqueio
        if self.em_pausa and self.pausa_ate:
            if datetime.now() < self.pausa_ate:
                tempo_restante = (self.pausa_ate - datetime.now()).seconds // 60
                return False, f"⏸️ Em pausa por bloqueio detectado. Reinicia em {tempo_restante}min"
            else:
                self.em_pausa = False
                self.pausa_ate = None

        # Verificar horário comercial
        agora = datetime.now()
        hora = agora.hour
        if not (HORARIO_INICIO <= hora < HORARIO_FIM):
            proxima_hora = HORARIO_INICIO if hora < HORARIO_INICIO else 0
            msg = f"🕐 Fora do horário comercial ({HORARIO_INICIO}h-{HORARIO_FIM}h). Próximo envio: {proxima_hora}:00"
            return False, msg

        # Limpar timestamps antigos
        self._limpar_timestamps_antigos()

        # Verificar limite por dia
        if len(self.stats['hoje']) >= LIMITE_MENSAGENS_DIA:
            return False, f"📊 Limite diário atingido ({LIMITE_MENSAGENS_DIA} mensagens)"

        # Verificar limite por hora
        if len(self.stats['hora_atual']) >= LIMITE_MENSAGENS_HORA:
            proxima_hora = (agora + timedelta(hours=1)).strftime("%H:%M")
            return False, f"⏱️ Limite por hora atingido ({LIMITE_MENSAGENS_HORA}). Próximo: {proxima_hora}"

        return True, "✅ Permitido enviar"

    def registrar_envio_sucesso(self, numero: str):
        """Registra um envio bem-sucedido."""
        agora = datetime.now().isoformat()

        self.stats['hoje'].append(agora)
        self.stats['hora_atual'].append(agora)
        self.stats['historico_contatos'][numero] = agora

        self.erros_consecutivos = 0
        self.ultimo_erro = None

        self._salvar_stats()
        logger.info(f"📊 Envios hoje: {len(self.stats['hoje'])}/{LIMITE_MENSAGENS_DIA}")

    def registrar_erro(self):
        """Registra um erro de envio."""
        self.erros_consecutivos += 1
        self.ultimo_erro = datetime.now()

        if self.erros_consecutivos >= ERROS_CONSECUTIVOS_PERMITIDOS:
            logger.error(f"⚠️ {self.erros_consecutivos} erros consecutivos detectados!")
            self._ativar_pausa_bloqueio()

    def _ativar_pausa_bloqueio(self):
        """Ativa pausa de segurança por 30 minutos."""
        self.em_pausa = True
        self.pausa_ate = datetime.now() + timedelta(seconds=TEMPO_PAUSA_BLOQUEIO)
        self.stats['bloqueios_detectados'] += 1
        self.stats['ultimo_bloqueio'] = datetime.now().isoformat()

        logger.error(
            f"🚨 PAUSA DE BLOQUEIO ATIVADA por 30 minutos! "
            f"(Bloqueios detectados: {self.stats['bloqueios_detectados']})"
        )

        self._salvar_stats()

    def pode_enviar_para_numero(self, numero: str) -> Tuple[bool, str]:
        """Verifica se já enviamos para este número hoje."""
        # ⚠️ COMENTADO PARA TESTES - DESCOMENTE EM PRODUÇÃO
        # if numero not in self.stats['historico_contatos']:
        #     return True, "✅ Primeiro envio para este número"
        # 
        # ultimo_envio = datetime.fromisoformat(self.stats['historico_contatos'][numero])
        # tempo_desde_ultimo = datetime.now() - ultimo_envio
        # 
        # if tempo_desde_ultimo < timedelta(hours=24):
        #     horas_restantes = (24 - tempo_desde_ultimo.total_seconds() / 3600)
        #     return False, f"⏸️ Já enviamos para este número. Próximo em {horas_restantes:.1f}h"
        # 
        # return True, "✅ Permitido enviar"
        
        # MODO TESTE: Sempre permite enviar
        return True, "✅ MODO TESTE - Bloqueio de 24h desativado"


# ======================================================================
# 📦 GERENCIADOR DE FILA
# ======================================================================

class GerenciadorFila:
    """
    Gerencia fila de mensagens para envio controlado.
    Respeita todos os limites anti-spam.
    """

    def __init__(self):
        self.fila = self._carregar_fila()
        self.anti_spam = AntiSpamManager()
        self.ultimo_envio = None

    def _carregar_fila(self) -> List[Dict]:
        """Carrega fila de arquivo."""
        if FILA_FILE.exists():
            try:
                with open(FILA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return []

    def _salvar_fila(self):
        """Salva fila em arquivo."""
        try:
            with open(FILA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.fila, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Erro ao salvar fila: {e}")

    def adicionar(self, numero: str, mensagem: str, prioridade: int = 0):
        """
        Adiciona mensagem à fila.
        
        Args:
            numero: Telefone (com ou sem formatação)
            mensagem: Texto da mensagem
            prioridade: 10=alta, 0=normal, -10=baixa (enviadas primeiro)
        """
        item = {
            'numero': numero,
            'mensagem': mensagem,
            'prioridade': prioridade,
            'criado_em': datetime.now().isoformat(),
            'tentativas': 0,
            'status': 'pendente'  # pendente, enviado, falha
        }

        self.fila.append(item)
        self.fila.sort(key=lambda x: -x['prioridade'])  # Ordenar por prioridade
        self._salvar_fila()

        logger.info(f"📬 Adicionada à fila: {numero} (Pendentes: {len(self.fila)})")

    def obter_proximo(self) -> Optional[Dict]:
        """Retorna próxima mensagem da fila."""
        for item in self.fila:
            if item['status'] == 'pendente':
                return item
        return None

    def aguardar_delay_humanizado(self):
        """Aguarda tempo aleatório entre mensagens (humanizado)."""
        if self.ultimo_envio is None:
            return

        tempo_minimo = INTERVALO_MINIMO_ENTRE_MSGS
        tempo_maximo = tempo_minimo + 60

        delay = random.uniform(tempo_minimo, tempo_maximo)
        logger.info(f"⏳ Aguardando {delay:.0f}s antes do próximo envio...")
        time.sleep(delay)

    def marcar_enviada(self, item: Dict):
        """Marca item como enviado."""
        item['status'] = 'enviado'
        item['enviado_em'] = datetime.now().isoformat()
        self._salvar_fila()

    def marcar_falha(self, item: Dict):
        """Marca item como falha e incrementa tentativas."""
        item['tentativas'] += 1
        if item['tentativas'] >= MAX_RETRIES:
            item['status'] = 'falha'
            logger.error(f"❌ Mensagem para {item['numero']} falhou após {MAX_RETRIES} tentativas")
        self._salvar_fila()

    def status(self) -> Dict:
        """Retorna status da fila."""
        pendentes = sum(1 for i in self.fila if i['status'] == 'pendente')
        enviadas = sum(1 for i in self.fila if i['status'] == 'enviado')
        falhas = sum(1 for i in self.fila if i['status'] == 'falha')

        return {
            'total': len(self.fila),
            'pendentes': pendentes,
            'enviadas': enviadas,
            'falhas': falhas
        }


# ======================================================================
# 🔌 GERENCIADOR DE SESSÃO
# ======================================================================

class WhatsAppSession:
    """Gerencia conexão persistente com WhatsApp Web."""

    def __init__(self):
        self._playwright = None
        self._context = None
        self._page = None
        self._logged_in = False

    @property
    def is_running(self):
        return self._context is not None

    @property
    def has_saved_session(self):
        return SESSION_MARKER.exists() and len(list(WHATSAPP_SESSION_DIR.glob('*'))) > 2

    def _decide_headless(self):
        if self.has_saved_session:
            logger.info(f"📂 Sessão anterior encontrada → headless={AUTO_HEADLESS}")
            return AUTO_HEADLESS
        else:
            logger.info("🆕 Primeira execução → abrindo janela para QR Code")
            return False

    def iniciar(self):
        """Inicia o navegador."""
        if self.is_running:
            logger.info("✓ Sessão já ativa")
            return True

        headless = self._decide_headless()
        primeira_vez = not self.has_saved_session

        logger.info("🔧 Iniciando navegador...")

        try:
            self._playwright = sync_playwright().start()
            self._context = self._playwright.chromium.launch_persistent_context(
                user_data_dir=str(WHATSAPP_SESSION_DIR),
                headless=headless,
                slow_mo=200,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-blink-features=AutomationControlled',
                ],
                locale='pt-BR',
                timezone_id='America/Sao_Paulo',
                user_agent=(
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/120.0.0.0 Safari/537.36'
                ),
            )

            self._page = self._context.pages[0] if self._context.pages else self._context.new_page()

            logger.info("🌐 Abrindo WhatsApp Web...")
            self._page.goto("https://web.whatsapp.com", wait_until='domcontentloaded', timeout=60000)

            if primeira_vez:
                sucesso = self._aguardar_primeiro_login()
            else:
                sucesso = self._aguardar_reconexao()

            if sucesso:
                self._logged_in = True
                SESSION_MARKER.touch()
                logger.info("✅ WhatsApp Web pronto!")
                return True
            else:
                self.fechar()
                return False

        except Exception as e:
            logger.error(f"❌ Erro ao iniciar: {e}")
            self.fechar()
            return False

    def _aguardar_primeiro_login(self) -> bool:
        """Aguarda login com QR Code."""
        logger.info("=" * 70)
        logger.info("🔐 ESCANEIE O QR CODE COM SEU CELULAR")
        logger.info("=" * 70)

        try:
            self._page.wait_for_selector(
                'div[id="side"], div[aria-label="Lista de conversas"]',
                timeout=QR_TIMEOUT * 1000
            )
            logger.info("✅ Login bem-sucedido!")
            return True
        except PlaywrightTimeoutError:
            logger.error("❌ Timeout: QR Code não escaneado")
            return False

    def _aguardar_reconexao(self) -> bool:
        """Aguarda reconexão com sessão anterior."""
        try:
            self._page.wait_for_selector(
                'div[id="side"], div[aria-label="Lista de conversas"]',
                timeout=30000
            )
            logger.info("✅ Reconectado!")
            return True
        except PlaywrightTimeoutError:
            logger.warning("⚠️ Timeout na reconexão (pode continuar mesmo assim)")
            return True  # Continua mesmo assim

    def enviar_para_numero(self, numero: str, mensagem: str) -> bool:
        """Envia mensagem para um número."""
        if not self._page:
            raise RuntimeError("Navegador não inicializado!")

        try:
            mensagem_encoded = urllib.parse.quote(mensagem)
            url = f"https://web.whatsapp.com/send?phone={numero}&text={mensagem_encoded}"

            logger.info(f"📱 Abrindo chat...")
            self._page.goto(url, wait_until='domcontentloaded', timeout=45000)

            time.sleep(2)

            # Aguardar campo de texto
            logger.info("⏳ Aguardando interface...")
            self._page.wait_for_selector('div[contenteditable="true"]', timeout=30000)

            time.sleep(1)

            # Procurar botão enviar
            logger.info("🔍 Procurando botão de envio...")
            send_selectors = [
                'button[aria-label="Enviar"]',
                'button span[data-icon="send"]',
                'button:has(span[data-icon="send"])',
            ]

            encontrou = False
            for selector in send_selectors:
                try:
                    btn = self._page.wait_for_selector(selector, timeout=5000)
                    if btn and btn.is_visible():
                        btn.click()
                        encontrou = True
                        break
                except:
                    continue

            if not encontrou:
                self._page.keyboard.press('Enter')

            logger.info("✓ Mensagem enviada!")
            time.sleep(3)

            return True

        except Exception as e:
            logger.error(f"Erro ao enviar: {e}")
            return False

    def fechar(self):
        """Fecha o navegador."""
        try:
            if self._context:
                self._context.close()
                self._context = None
        except:
            pass

        try:
            if self._playwright:
                self._playwright.stop()
                self._playwright = None
        except:
            pass

        logger.info("✓ Navegador fechado")


# ======================================================================
# 📞 FORMATAÇÃO DE TELEFONE
# ======================================================================

def formatar_numero_telefone(numero: str) -> str:
    """
    Formata número telefônico para padrão internacional WhatsApp.
    
    Aceita AMBOS telefone fixo (10 dígitos) e celular (11 dígitos):
    - "(32) 3213-4086" (fixo MG) → "553232134086"
    - "(31) 98416-3357" (celular MG) → "5531984163357"  
    - "+55 31 98416-3357" → "5531984163357"
    - "555531984163357" → "5531984163357" (remove DDI duplicado)
    
    Args:
        numero: String com número em qualquer formato
        
    Returns:
        String formatada: "55" + DDD (2 dígitos) + número (8-9 dígitos)
        Retorna string vazia se inválido
    """
    
    if not numero or not isinstance(numero, str):
        return ""
    
    # 1. Remove espaços, parênteses, hífens, pontos, sinais de +
    numero_limpo = ''.join(c for c in numero if c.isdigit())
    
    if not numero_limpo:
        return ""
    
    # 2. Remove DDI duplicado (55555...)
    while numero_limpo.startswith('5555'):
        numero_limpo = numero_limpo[2:]
    
    # 3. Se já tem country code (55), valida
    if numero_limpo.startswith('55'):
        # Deve ter 12, 13 ou 14 dígitos no total (55 + 10, 11 ou 12 dígitos)
        if 12 <= len(numero_limpo) <= 14:
            return numero_limpo
        # Se tiver mais, pega os 14 primeiros (55 + DDD + 9 dígitos)
        if len(numero_limpo) > 14:
            return numero_limpo[:14]
        # Se tiver menos de 12, é inválido
        return ""
    
    # 4. Se não tem country code, valida formato brasileiro
    # Aceita AMBOS: 10 (DDD + 8 dígitos FIXO) ou 11 (DDD + 9 dígitos CELULAR)
    if len(numero_limpo) not in [10, 11]:
        return ""
    
    # 5. Valida DDD (11-99)
    try:
        ddd = int(numero_limpo[:2])
        if ddd < 11 or ddd > 99:
            return ""
    except ValueError:
        return ""
    
    # Adiciona country code
    return '55' + numero_limpo


def validar_numero_telefone(numero: str) -> bool:
    """
    Valida se um número pode ser formatado corretamente.
    Aceita telefones fixos (10 dígitos) e celulares (11 dígitos).
    
    Returns:
        True se o número é válido e pode ser formatado
    """
    resultado = bool(formatar_numero_telefone(numero))
    if not resultado:
        logger.debug(f"Validação falhou para: {numero}")
    return resultado


# ======================================================================
# 🎯 API PÚBLICA
# ======================================================================

_session = WhatsAppSession()
_fila = GerenciadorFila()


def enviar_mensagem(numero: str, mensagem: str, prioridade: int = 0) -> Tuple[bool, str]:
    """
    Envia mensagem - INTERFACE SIMPLES (compatível com versão anterior).
    
    Automaticamente verifica anti-spam e pode fila ser usado com processamento.
    
    Args:
        numero: Telefone em qualquer formato (ex: "31984163357", "(31) 98416-3357", "+55 31 98416-3357")
        mensagem: Texto da mensagem
        prioridade: 10=alta, 0=normal, -10=baixa
    
    Returns:
        (sucesso: bool, mensagem: str)
    
    Exemplo:
        sucesso, msg = enviar_mensagem("31984163357", "Olá!")
        if sucesso:
            print("✅ Enviado")
    """

    # Formatar número para padrão internacional
    numero_formatado = formatar_numero_telefone(numero)
    
    if not numero_formatado:
        logger.error(f"❌ Número inválido: {numero}")
        logger.error(f"   Formatos aceitos: '31984163357', '(31) 98416-3357', '+55 31 98416-3357', '5531984163357'")
        return False, f"Número inválido: {numero}"

    logger.info("")
    logger.info("=" * 70)
    logger.info(f"📤 ENVIANDO PARA: {numero_formatado} (origem: {numero})")
    logger.info("=" * 70)

    # Verificar anti-spam
    pode, motivo = _fila.anti_spam.pode_enviar()
    if not pode:
        logger.warning(f"⛔ {motivo}")
        _fila.adicionar(numero_formatado, mensagem, prioridade)
        return False, f"Adicionada à fila. {motivo}"

    pode, motivo = _fila.anti_spam.pode_enviar_para_numero(numero_formatado)
    if not pode:
        logger.warning(f"⛔ {motivo}")
        _fila.adicionar(numero_formatado, mensagem, prioridade)
        return False, f"Adicionada à fila. {motivo}"

    # Iniciar sessão se necessário
    if not _session.is_running:
        if not _session.iniciar():
            return False, "❌ Falha ao conectar WhatsApp"

    # Enviar
    for tentativa in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"🔄 Tentativa {tentativa}/{MAX_RETRIES}...")

            sucesso = _session.enviar_para_numero(numero_formatado, mensagem)

            if sucesso:
                _fila.anti_spam.registrar_envio_sucesso(numero_formatado)
                logger.info("✅ Sucesso!")
                logger.info("=" * 70)

                _fila.ultimo_envio = datetime.now()
                return True, "✅ Enviado com sucesso"
            else:
                _fila.anti_spam.registrar_erro()
                if tentativa < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)

        except Exception as e:
            logger.error(f"Erro: {e}")
            _fila.anti_spam.registrar_erro()
            if tentativa < MAX_RETRIES:
                time.sleep(RETRY_DELAY)

    logger.error("❌ Falha após tentativas")
    logger.info("=" * 70)
    return False, "❌ Falha após tentativas"


def adicionar_fila(numero: str, mensagem: str, prioridade: int = 0):
    """
    Adiciona mensagem à fila para envio controlado.
    
    O número será automaticamente formatado para padrão internacional.
    """
    numero_formatado = formatar_numero_telefone(numero)
    
    if not numero_formatado:
        logger.error(f"❌ Número inválido para fila: {numero}")
        return
    
    _fila.adicionar(numero_formatado, mensagem, prioridade)


def processar_fila(max_envios: Optional[int] = None):
    """
    Processa fila de mensagens respeitando todos os limites.
    
    Args:
        max_envios: Máximo de mensagens a processar (None = processar tudo)
    
    Exemplo:
        processar_fila(max_envios=10)  # Processa até 10 mensagens
    """

    logger.info("")
    logger.info("=" * 70)
    logger.info("🚀 PROCESSANDO FILA")
    logger.info("=" * 70)

    if not _session.is_running:
        if not _session.iniciar():
            logger.error("❌ Falha ao conectar")
            return

    enviadas = 0

    while True:
        # Verificar limites
        pode, motivo = _fila.anti_spam.pode_enviar()
        if not pode:
            logger.warning(f"⛔ {motivo}")
            break

        # Obter próxima mensagem
        item = _fila.obter_proximo()
        if not item:
            logger.info("✅ Fila vazia!")
            break

        # Limite máximo
        if max_envios and enviadas >= max_envios:
            logger.info(f"⏸️ Limite de {max_envios} atingido")
            break

        # Delay humanizado
        _fila.aguardar_delay_humanizado()

        # Enviar
        numero = item['numero']
        mensagem = item['mensagem']

        sucesso = _session.enviar_para_numero(numero, mensagem)

        if sucesso:
            _fila.marcar_enviada(item)
            _fila.anti_spam.registrar_envio_sucesso(numero)
            enviadas += 1
            logger.info(f"✅ Enviada: {numero}")
        else:
            _fila.marcar_falha(item)
            _fila.anti_spam.registrar_erro()
            logger.error(f"❌ Falha: {numero}")

        _fila.ultimo_envio = datetime.now()

    logger.info("")
    logger.info(f"📊 Fila processada: {enviadas} mensagens enviadas")
    logger.info("=" * 70)


def status_fila() -> Dict:
    """Retorna status da fila."""
    return _fila.status()


def stats_anti_spam() -> Dict:
    """Retorna estatísticas anti-spam."""
    return {
        'hoje': len(_fila.anti_spam.stats['hoje']),
        'limite_dia': LIMITE_MENSAGENS_DIA,
        'hora_atual': len(_fila.anti_spam.stats['hora_atual']),
        'limite_hora': LIMITE_MENSAGENS_HORA,
        'bloqueios_detectados': _fila.anti_spam.stats['bloqueios_detectados'],
        'em_pausa': _fila.anti_spam.em_pausa,
    }


def fechar_sessao():
    """Fecha a conexão com WhatsApp."""
    _session.fechar()


# ======================================================================
# 🧪 TESTE
# ======================================================================

if __name__ == "__main__":
    logger.info("")
    logger.info("🚀 TESTE DE WHATSAPP SERVICE COM ANTI-SPAM")
    logger.info("=" * 70)

    try:
        # Teste 1: Envio simples
        sucesso, msg = enviar_mensagem(
            "(31) 98416-3357",
            "Teste Allcanci\nPedido: 2363\nStatus: Saiu para entrega!"
        )
        print(f"RESULTADO: {msg}\n")

        # Teste 2: Ver status
        print(f"Status Fila: {status_fila()}")
        print(f"Stats Anti-Spam: {stats_anti_spam()}\n")

        # Teste 3: Adicionar à fila
        adicionar_fila("(31) 99999-8888", "Teste múltiplo 1", prioridade=10)
        adicionar_fila("(31) 99999-7777", "Teste múltiplo 2")

        # Teste 4: Processar fila
        print(f"Fila agora: {status_fila()}")
        # processar_fila(max_envios=2)  # Descomente para testar

    except KeyboardInterrupt:
        logger.info("\n🛑 Interrompido")
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        fechar_sessao()
