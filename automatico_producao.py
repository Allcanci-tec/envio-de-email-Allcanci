#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA AUTOMÃTICO DE RASTREAMENTO - PRODUCTION READY
- Sincroniza novos clientes automaticamente do Bling
- Descobre volume_ids automaticamente
- Detecta mudanÃ§as de situaÃ§Ã£o e envia email
- Log detalhado com histÃ³rico completo de envios
- Fonte Ãºnica de verdade: contatos_rastreamento.json
"""

import json
import os
import requests
import smtplib
import imaplib
import time
import logging
import sys
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime, timedelta
from vendedor_service import buscar_vendedor

load_dotenv()

# --------------------------------------------------------------------------
# CONFIGURAÃ‡ÃƒO DE LOG (deve vir ANTES de qualquer uso de logger)
# --------------------------------------------------------------------------
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('rastreamento')
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler('rastreamento.log', encoding='utf-8')
file_handler.setFormatter(log_formatter)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(log_formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# Importar WhatsApp Service (após logger estar configurado)
try:
    from whatsapp_service import enviar_mensagem as enviar_whatsapp
    WHATSAPP_DISPONIVEL = True
except Exception as e:
    logger.warning(f"⚠️ WhatsApp Service indisponível: {e}")
    WHATSAPP_DISPONIVEL = False
    enviar_whatsapp = None

# --------------------------------------------------------------------------
# CONSTANTES
# --------------------------------------------------------------------------
CONTATOS_FILE = 'contatos_rastreamento.json'
BLING_API = 'https://api.bling.com.br/v3'
BLING_TOKEN_URL = 'https://www.bling.com.br/Api/v3/oauth/token'
BLING_CLIENT_ID = os.getenv('BLING_CLIENT_ID', '')
BLING_CLIENT_SECRET = os.getenv('BLING_CLIENT_SECRET', '')
ID_LOGISTICA_CORREIOS = 151483  # ID da logística Correios no Bling

SITUACOES_ENTREGUE = [
    'entregue',
    'devolvido',
    'objeto perdido',
]

# Anti-spam: máximo de emails por ciclo
MAX_EMAILS_POR_CICLO = 50
# Throttling entre emails (evita rate-limit SMTP)
THROTTLE_SEGUNDOS = 1.5


def extrair_celular_do_bling(telefones_array):
    """
    Extrai especificamente o número de CELULAR do array de telefones do Bling.
    O Bling retorna múltiplos telefones com tipos diferentes: Fone, Fax, Celular, etc.
    
    Procura em ordem de prioridade:
    1. Tipo 'Celular' ou 'whatsapp'
    2. Se não encontrar, tenta o primeiro com mais de 10 dígitos (celular tem 11)
    3. Se nenhum for encontrado, retorna 'N/A'
    """
    if not telefones_array:
        return 'N/A'
    
    # 1. Procurar por tipo "Celular" ou "whatsapp"
    for tel in telefones_array:
        tipo = tel.get('tipo', '').lower()
        numero = tel.get('numero', '').strip()
        if tipo in ['celular', 'whatsapp', 'whatsapp business']:
            if numero:
                logger.debug(f'   Celular encontrado (tipo={tipo}): {numero}')
                return numero
    
    # 2. Se não encontrou por tipo, procura por número com 11 dígitos (celular Brasil)
    for tel in telefones_array:
        numero = tel.get('numero', '').strip()
        apenas_num = ''.join(c for c in numero if c.isdigit())
        if len(apenas_num) == 11:  # Celular tem 11 dígitos
            logger.debug(f'   Celular encontrado (11 dígitos): {numero}')
            return numero
    
    # 3. Se nada funcionar, retorna o primeiro disponível (compatibilidade)
    if telefones_array:
        numero = telefones_array[0].get('numero', '').strip()
        if numero:
            logger.debug(f'   Usando primeiro telefone disponível: {numero}')
            return numero
    
    return 'N/A'


# --------------------------------------------------------------------------
# HELPERS: TOKEN
# --------------------------------------------------------------------------
def _renovar_token(dados_atuais):
    """Renova o access_token Bling usando o refresh_token."""
    refresh = dados_atuais.get('refresh_token')
    if not refresh:
        raise RuntimeError('refresh_token não encontrado em tokens.json. Reconecte via bling_oauth_server.py')
    if not BLING_CLIENT_ID or not BLING_CLIENT_SECRET:
        raise RuntimeError('BLING_CLIENT_ID ou BLING_CLIENT_SECRET não configurados no .env')

    resp = requests.post(
        BLING_TOKEN_URL,
        data={'grant_type': 'refresh_token', 'refresh_token': refresh},
        auth=(BLING_CLIENT_ID, BLING_CLIENT_SECRET),
        headers={'Accept': 'application/json'},
        timeout=30,
    )
    if resp.status_code != 200:
        raise RuntimeError(f'Bling retornou {resp.status_code} ao renovar token: {resp.text}')

    data = resp.json()
    novo_dados = {
        'access_token': data['access_token'],
        'refresh_token': data.get('refresh_token', refresh),
        'expires_at': time.time() + data.get('expires_in', 3600),
        'obtained_at': time.time(),
    }
    with open('tokens.json', 'w', encoding='utf-8') as f:
        json.dump(novo_dados, f, indent=2)

    expira_em = int(data.get('expires_in', 3600) / 60)
    logger.info(f'✅ Token Bling renovado! Expira em {expira_em} minutos.')
    return data['access_token']


def carregar_token():
    """Carrega token do Bling de tokens.json, renovando automaticamente se expirado."""
    try:
        if not os.path.exists('tokens.json'):
            logger.error('❌ Arquivo tokens.json não encontrado!')
            raise FileNotFoundError('tokens.json')

        with open('tokens.json', 'r', encoding='utf-8') as f:
            dados = json.load(f)

        token = dados.get('access_token')
        if not token:
            logger.error('❌ Token vazio em tokens.json')
            raise ValueError('access_token vazio')

        # Auto-renovar se expirado ou expirando nos próximos 5 minutos
        expires_at = dados.get('expires_at', 0)
        if expires_at and time.time() >= (expires_at - 300):
            logger.warning('⚠️  Token Bling expirado ou expirando em breve. Renovando automaticamente...')
            token = _renovar_token(dados)

        return token

    except Exception as e:
        logger.error(f'❌ ERRO ao carregar token: {e}')
        raise


def headers_bling():
    """Retorna headers com Authorization para API Bling"""
    try:
        token = carregar_token()
        return {'Authorization': f'Bearer {token}'}
    except Exception as e:
        logger.error(f'❌ Erro ao montar header Bling: {e}')
        raise


def bling_request(method, url, **kwargs):
    """
    Wrapper para chamadas à API Bling com renovação automática em caso de 401.
    Tenta a requisição; se receber 401 (token expirado), força renovação do token
    e tenta mais uma vez antes de devolver a resposta.
    """
    kwargs.setdefault('timeout', 15)
    kwargs['headers'] = headers_bling()
    resp = requests.request(method, url, **kwargs)
    if resp.status_code == 401:
        logger.warning('⚠️  Token Bling rejeitado (401). Forçando renovação e tentando novamente...')
        try:
            with open('tokens.json', 'r', encoding='utf-8') as f:
                dados = json.load(f)
            _renovar_token(dados)
        except Exception as e:
            logger.error(f'❌ Falha ao renovar token após 401: {e}')
            return resp
        kwargs['headers'] = headers_bling()
        resp = requests.request(method, url, **kwargs)
        if resp.status_code == 401:
            logger.error('❌ Token ainda inválido após renovação. Verifique tokens.json e .env')
    return resp


def _iniciar_renovacao_automatica():
    """
    Inicia uma thread daemon que renova o token Bling proativamente a cada 45 min.
    Garante que o sistema nunca dependa de token_renewer.py externo.
    """
    def _loop():
        while True:
            time.sleep(45 * 60)  # aguarda 45 minutos
            try:
                if not os.path.exists('tokens.json'):
                    continue
                with open('tokens.json', 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                expires_at = dados.get('expires_at', 0)
                # Renova se faltar menos de 15 minutos ou já expirado
                if time.time() >= (expires_at - 15 * 60):
                    logger.info('🔄 [AutoRenew] Renovando token Bling proativamente...')
                    _renovar_token(dados)
                else:
                    minutos = int((expires_at - time.time()) / 60)
                    logger.info(f'🔑 [AutoRenew] Token válido por mais ~{minutos} min. Sem necessidade de renovação.')
            except Exception as e:
                logger.error(f'❌ [AutoRenew] Erro ao renovar token: {e}')

    t = threading.Thread(target=_loop, name='BlingTokenRenewer', daemon=True)
    t.start()
    logger.info('✅ Thread de renovação automática de token iniciada (a cada 45 min).')


# --------------------------------------------------------------------------
# HELPERS: VALIDAÇÃO
# --------------------------------------------------------------------------
import re

def validar_email(email):
    """Valida se é um email com formato correto"""
    if not email or not isinstance(email, str):
        return False
    # Regex simples mas eficaz para emails
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validar_telefone(telefone):
    """Valida se é um telefone com formato correto"""
    if not telefone or not isinstance(telefone, str):
        logger.debug(f'⏭️ Telefone inválido (vazio ou não-string): {repr(telefone)}')
        return False
    # Remove caracteres não numéricos
    apenas_numeros = re.sub(r'\D', '', telefone)
    # Brasil: telefones têm 10-11 dígitos (DDD + número)
    valido = len(apenas_numeros) >= 10
    if not valido:
        logger.debug(f'⏭️ Telefone "{telefone}" inválido - apenas {len(apenas_numeros)} dígitos (mínimo 10)')
    return valido


# --------------------------------------------------------------------------
# HELPERS: JSON DE CONTATOS
# --------------------------------------------------------------------------
def carregar_contatos():
    with open(CONTATOS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def salvar_contatos(contatos):
    with open(CONTATOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(contatos, f, indent=2, ensure_ascii=False)


# --------------------------------------------------------------------------
# SINCRONIZAÃ‡ÃƒO: descobre novos pedidos e volume_ids no Bling
# --------------------------------------------------------------------------
# Janela de dias para buscar/monitorar pedidos
DIAS_JANELA = 5


def sincronizar_clientes():
    """Busca pedidos Correios dos ultimos DIAS_JANELA dias no Bling,
    adiciona novos ao JSON e preenche volume_ids que ainda estao null.
    Retorna (contatos, numeros_recentes) onde numeros_recentes sao os
    pedidos que a API retornou (alterados nos ultimos DIAS_JANELA dias)."""
    logger.info('--- SINCRONIZANDO COM BLING API ---')

    contatos = carregar_contatos()
    numeros_existentes = {c['numero'] for c in contatos}
    numeros_recentes = set()  # pedidos retornados pela API (ultimos DIAS_JANELA dias)
    novos = 0
    volume_ids_resolvidos = 0

    # Filtrar apenas pedidos alterados nos ultimos 5 dias
    data_inicio = (datetime.now() - timedelta(days=DIAS_JANELA)).strftime('%Y-%m-%d 00:00:00')
    logger.info(f'   Filtrando pedidos alterados desde: {data_inicio}')

    pagina = 1
    while True:
        try:
            logger.info(f'   Página {pagina}: buscando pedidos...')
            resp = bling_request(
                'GET',
                f'{BLING_API}/pedidos/vendas',
                params={
                    'pagina': pagina,
                    'limite': 100,
                    'idLogistica': ID_LOGISTICA_CORREIOS,
                    'dataAlteracaoInicial': data_inicio,
                },
                timeout=15,
            )
        except Exception as e:
            logger.error(f'   Erro ao buscar pedidos pagina {pagina}: {e}')
            break

        if resp.status_code != 200:
            logger.warning(f'   Bling retornou status {resp.status_code} na pagina {pagina}')
            break

        dados = resp.json().get('data', [])
        if not dados:
            break

        for pedido_resumido in dados:
            numero = pedido_resumido.get('numero')
            pedido_id_interno = pedido_resumido.get('id')
            if not numero or not pedido_id_interno:
                continue

            # A listagem nao retorna volumes — busca detalhe completo pelo id interno
            try:
                logger.info(f'   Processando pedido {numero}...')
                r2 = bling_request(
                    'GET',
                    f'{BLING_API}/pedidos/vendas/{pedido_id_interno}',
                    timeout=10,
                )
            except requests.Timeout:
                logger.warning(f'   TIMEOUT ao buscar detalhe pedido {numero}')
                continue
            except Exception as e:
                logger.warning(f'   Erro detalhe pedido {numero}: {type(e).__name__}: {e}')
                continue

            if r2.status_code != 200:
                continue

            pedido = r2.json().get('data', {})
            volumes = pedido.get('transporte', {}).get('volumes', [])
            if not volumes:
                continue

            volume = volumes[0]
            etiqueta = volume.get('codigoRastreamento', '')
            volume_id = volume.get('id')

            if not etiqueta or not str(etiqueta).startswith('AD'):
                continue

            # Registrar como pedido recente (API retornou nos ultimos DIAS_JANELA dias)
            numeros_recentes.add(numero)

            # SKIP se ja existe E ja tem volume_id E ja tem celular -- sem chamada extra
            if numero in numeros_existentes:
                contato_existente = next((c for c in contatos if c['numero'] == numero), None)
                ja_tem_volume = contato_existente and contato_existente.get('volume_id')
                ja_tem_celular = contato_existente and contato_existente.get('telefone_celular', 'N/A') != 'N/A'
                if ja_tem_volume and ja_tem_celular:
                    continue
                # Tem volume mas celular N/A: atualiza só o celular
                if ja_tem_volume and not ja_tem_celular:
                    contato_id_upd = pedido.get('contato', {}).get('id')
                    if contato_id_upd:
                        try:
                            rc_upd = bling_request('GET', f'{BLING_API}/contatos/{contato_id_upd}', timeout=10)
                            if rc_upd.status_code == 200:
                                cd_upd = rc_upd.json().get('data', {})
                                celular_novo = cd_upd.get('celular', '').strip()
                                if celular_novo:
                                    contato_existente['telefone_celular'] = celular_novo
                                    logger.info(f'   Celular atualizado para pedido {numero}: {celular_novo}')
                        except Exception:
                            pass
                    continue

            if numero not in numeros_existentes:
                # Novo cliente descoberto â€” buscar email no contato
                contato_id = pedido.get('contato', {}).get('id')
                email, telefone, nome_cliente = '', 'N/A', pedido.get('contato', {}).get('nome', 'Desconhecido')
                vendedor_id_contato = None

                cidade_destino = ''
                estado_destino = ''
                if contato_id:
                    try:
                        rc = bling_request(
                            'GET',
                            f'{BLING_API}/contatos/{contato_id}',
                            timeout=10,
                        )
                        if rc.status_code == 200:
                            cd = rc.json().get('data', {})
                            email = cd.get('email', '')
                            # Bling retorna celular como campo direto (não array)
                            telefone = cd.get('celular', '').strip() or 'N/A'
                            logger.info(f'   Celular do Bling: {telefone}')
                            nome_cliente = cd.get('nome', nome_cliente)
                            # Capturar cidade/estado do endereço do contato
                            endereco_geral = cd.get('endereco', {}).get('geral', {})
                            cidade_destino = endereco_geral.get('municipio', '')
                            estado_destino = endereco_geral.get('uf', '')
                            # Vendedor fica no registro do CONTATO (contato.vendedor.id)
                            vendedor_id_contato = cd.get('vendedor', {}).get('id')
                            logger.info(f'   ✅ Contato {contato_id} obtido')
                    except requests.Timeout:
                        logger.warning(f'   TIMEOUT ao buscar contato {contato_id}')
                    except Exception as e:
                        logger.warning(f'   Erro ao buscar contato {contato_id}: {type(e).__name__}')

                # Buscar dados do vendedor (vendedor_id vem do contato, não do pedido)
                vendedor_id = vendedor_id_contato or pedido.get('vendedor', {}).get('id')
                vendedor_nome = ''
                vendedor_email = ''
                if vendedor_id and vendedor_id != 0:
                    try:
                        dados_vendedor = buscar_vendedor(vendedor_id)
                        if dados_vendedor.get('sucesso'):
                            vendedor_nome = dados_vendedor.get('nome', '')
                            vendedor_email = dados_vendedor.get('email', '')
                            logger.info(f'   + Vendedor encontrado: {vendedor_nome} ({vendedor_email or "sem email"})')
                        else:
                            logger.info(f'   + Vendedor nao obtido: {dados_vendedor.get("motivo")}')
                    except Exception as e:
                        logger.warning(f'   Erro ao buscar vendedor {vendedor_id}: {type(e).__name__}: {e}')

                novo_contato = {
                    'numero': numero,
                    'cliente': nome_cliente,
                    'email': email,
                    'telefone_celular': telefone,
                    'etiqueta': etiqueta,
                    'volume_id': volume_id,
                    'ultima_situacao': '',
                    'emails_enviados': [],
                    'vendedor_id': vendedor_id,
                    'vendedor_nome': vendedor_nome,
                    'vendedor_email': vendedor_email,
                    'emails_vendedor_enviados': [],
                    'cidade_destino': cidade_destino,
                    'estado_destino': estado_destino,
                }
                contatos.append(novo_contato)
                numeros_existentes.add(numero)
                novos += 1
                logger.info(f'   + NOVO pedido {numero}: {nome_cliente} | email: {email or "(sem email)"}')
            else:
                # Pedido existente — preencher volume_id se faltando
                for c in contatos:
                    if c['numero'] == numero:
                        if not c.get('volume_id') and volume_id:
                            c['volume_id'] = volume_id
                            volume_ids_resolvidos += 1
                            logger.info(f'   + volume_id resolvido para pedido {numero}')

        pagina += 1

    salvar_contatos(contatos)
    logger.info(f'   Sincronizacao concluida: {novos} novos, {volume_ids_resolvidos} volume_ids resolvidos, {len(numeros_recentes)} pedidos recentes')
    return contatos, numeros_recentes


# --------------------------------------------------------------------------
# RASTREAMENTO: consulta Bling pelo volume_id
# --------------------------------------------------------------------------
def obter_rastreamento_bling(volume_id):
    try:
        resp = bling_request(
            'GET',
            f'{BLING_API}/logisticas/objetos/{volume_id}',
            timeout=10,
        )
        
        if resp.status_code == 200:
            dados = resp.json().get('data', {})
            rastreamento = dados.get('rastreamento', {})
            if rastreamento:
                return rastreamento
            else:
                logger.warning(f'   Volume {volume_id}: sem dados de rastreamento')
                return None
        else:
            logger.warning(f'   Volume {volume_id}: Bling retornou status {resp.status_code}')
            if resp.status_code == 404:
                logger.warning(f'   Volume {volume_id} não encontrado no Bling')
            return None
            
    except requests.Timeout:
        logger.error(f'   Volume {volume_id}: TIMEOUT ao consultar Bling (>10s)')
        return None
    except requests.ConnectionError:
        logger.error(f'   Volume {volume_id}: ERRO DE CONEXÃO com Bling')
        return None
    except Exception as e:
        logger.error(f'   Volume {volume_id}: Erro ao consultar: {type(e).__name__}: {e}')
        return None


def situacao_e_entregue(situacao):
    s = situacao.lower()
    return any(k in s for k in SITUACOES_ENTREGUE)


# --------------------------------------------------------------------------
# SALVAR EMAIL NA PASTA ENVIADOS (IMAP)
# --------------------------------------------------------------------------
def salvar_email_enviados(msg_str, EMAIL_IMAP, EMAIL_IMAP_PORTA, EMAIL_USUARIO, EMAIL_SENHA):
    """Salva email na pasta Enviados usando IMAP"""
    try:
        imap = imaplib.IMAP4_SSL(EMAIL_IMAP, int(EMAIL_IMAP_PORTA))
        imap.login(EMAIL_USUARIO, EMAIL_SENHA)
        
        pasta_usada = 'INBOX.Sent'
        date = imaplib.Time2Internaldate(time.time())
        result = imap.append(pasta_usada, '(\\Seen)', date, msg_str.encode('utf-8'))
        imap.logout()
        
        if result[0] == 'OK':
            logger.info(f'✅ Email salvo em "{pasta_usada}"')
            return True
        else:
            logger.warning(f'⚠️ IMAP append result: {result}')
            return False
    except Exception as e:
        logger.warning(f'⚠️ Não foi possível salvar email nos Enviados: {e}')
        return False


# --------------------------------------------------------------------------
# EMAIL
# --------------------------------------------------------------------------
def enviar_email(numero, cliente, email_destino, status, ultima_alt,
                 EMAIL_USUARIO, EMAIL_SENHA, EMAIL_SMTP, EMAIL_PORTA,
                 vendedor_nome='', destino=''):
    """Envia email de notificação. Se vendedor_nome for passado, é email pro vendedor."""
    if not email_destino:
        return False, 'sem email'
    if not validar_email(email_destino):
        return False, f'email inválido: {email_destino}'
    try:
        time.sleep(THROTTLE_SEGUNDOS)  # Throttling: aguarda entre emails (evita bloqueio)
        data_fmt = datetime.now().strftime('%d/%m/%Y %H:%M')
        
        # Mesmo design para escola e vendedor
        # Se vendedor: saudação ao vendedor + referência ao cliente
        if vendedor_nome:
            saudacao = f'Ol&#225; <strong>{vendedor_nome}</strong>,'
            subtexto = f'O pedido do cliente <strong>{cliente}</strong> teve uma atualiza&#231;&#227;o importante:'
            assunto = f'Pedido {numero} ({cliente}) - {status}'
        else:
            saudacao = f'Ol&#225; <strong>{cliente}</strong>,'
            subtexto = 'Seu pedido teve uma atualiza&#231;&#227;o importante:'
            assunto = f'Pedido {numero} - {status}'
        
        html = f'''<html>
<body style="font-family:Arial;background:#f5f5f5;padding:20px">
<div style="max-width:600px;margin:0 auto;background:white;border-radius:8px;padding:30px">
  <div style="background:linear-gradient(135deg,#0000F3 0%,#0051DB 100%);padding:30px;text-align:center;color:white;border-radius:6px;margin-bottom:30px">
    <h1 style="margin:0;font-size:26px">&#128246; Atualiza&#231;&#227;o de Rastreamento</h1>
  </div>
  <p style="font-size:16px;color:#333">{saudacao}</p>
  <p style="font-size:16px;color:#555;margin:15px 0">{subtexto}</p>
  <div style="background:#4CAF50;padding:25px;border-radius:6px;margin:20px 0;color:white;text-align:center;font-size:20px;font-weight:bold;line-height:1.6">
    &#9989; {status.upper()}
  </div>
  <div style="background:#f9f9f9;padding:20px;border-radius:6px;margin:20px 0;border-left:4px solid #0066cc">
    <p style="margin:10px 0"><strong>&#128456; Pedido:</strong> {numero}</p>
    <p style="margin:10px 0"><strong>&#128226; Rastreamento:</strong> {ultima_alt}</p>
    <p style="margin:10px 0"><strong>&#128205; Origem:</strong> Betim - MG</p>
    <p style="margin:10px 0"><strong>&#128205; Destino:</strong> {destino}</p>
    <p style="margin:10px 0"><strong>&#128197; Atualizado em:</strong> {data_fmt}</p>
    <p style="margin:10px 0"><strong>Descri&#231;&#227;o:</strong> {status}</p>
  </div>
  <div style="padding:15px;text-align:center;font-size:12px;color:#999;border-top:1px solid #e0e0e0">
    Email autom&#225;tico - Allcanci Rastreamento
  </div>
</div>
</body>
</html>'''
        msg = MIMEMultipart('alternative')
        msg['Subject'] = assunto
        msg['From'] = EMAIL_USUARIO
        msg['To'] = email_destino
        msg['Reply-To'] = EMAIL_USUARIO
        msg['X-Mailer'] = 'Allcanci Rastreamento v1.0'
        msg.attach(MIMEText(f'Pedido {numero}\nStatus: {status}', 'plain', 'utf-8'))
        msg.attach(MIMEText(html, 'html', 'utf-8'))

        server = smtplib.SMTP_SSL(EMAIL_SMTP, int(EMAIL_PORTA))
        server.login(EMAIL_USUARIO, EMAIL_SENHA)
        server.send_message(msg)
        server.quit()
        
        # Salvar na pasta Enviados (IMAP)
        EMAIL_IMAP = os.getenv('EMAIL_IMAP', 'imap.gmail.com')
        EMAIL_IMAP_PORTA = os.getenv('EMAIL_IMAP_PORTA', '993')
        salvar_email_enviados(msg.as_string(), EMAIL_IMAP, EMAIL_IMAP_PORTA, EMAIL_USUARIO, EMAIL_SENHA)
        
        return True, 'OK'
    except Exception as e:
        return False, str(e)


# --------------------------------------------------------------------------
# ENVIAR NOTIFICAÃ‡ÃƒO WHATSAPP
# --------------------------------------------------------------------------
def enviar_whatsapp_notificacao(numero, cliente, numero_telefone, status, ultima_alt, destino=''):
    """Envia notificação pelo WhatsApp com formato profissional"""
    logger.debug(f'   [WhatsApp] Telefone recebido: {repr(numero_telefone)} | Cliente: {cliente}')
    
    if not WHATSAPP_DISPONIVEL:
        logger.warning(f'   [WhatsApp] Serviço indisponível')
        return False, 'WhatsApp indisponível'
    
    if not numero_telefone or numero_telefone == 'N/A':
        logger.debug(f'   [WhatsApp] Telefone vazio ou N/A')
        return False, 'Sem telefone'
    
    if not validar_telefone(numero_telefone):
        logger.warning(f'   [WhatsApp] Telefone "{numero_telefone}" falhou na validação')
        return False, f'Telefone inválido: {numero_telefone}'
    
    try:
        data_fmt = datetime.now().strftime('%d/%m/%Y %H:%M')
        
        # Mensagem formatada para WhatsApp (sem HTML, usa emojis)
        mensagem = f"""
📦 *ATUALIZAÇÃO DE RASTREAMENTO*

Olá *{cliente}*,

Seu pedido teve uma atualização importante:

✅ *{status.upper()}*

*Detalhes:*
🔹 Pedido: {numero}
🔹 Rastreamento: {ultima_alt}
📍 Origem: Betim - MG
📍 Destino: {destino}
🔹 Atualizado em: {data_fmt}

🔗 Acompanhe: https://www.correios.com.br

_Allcanci Tecnologia_
        """.strip()
        
        # Enviar via WhatsApp Service (respeita anti-spam automaticamente)
        logger.info(f'   [WhatsApp] Enviando para {numero_telefone}...')
        sucesso, msg = enviar_whatsapp(numero_telefone, mensagem)
        
        if sucesso:
            logger.info(f'   [WhatsApp] ✅ Enviado com sucesso!')
            return True, 'OK'
        else:
            # Se falhar, adiciona à fila (a fila processará respeitando limites)
            logger.info(f'   [WhatsApp] Enfieirado (fila): {msg}')
            return True, 'Enfieirado'  # Retorna True porque foi adicionado à fila
            
    except Exception as e:
        logger.warning(f'   [WhatsApp] Erro ao enviar: {e}')
        return False, str(e)
def logar_historico_completo(contatos):
    logger.info('')
    logger.info('=' * 70)
    logger.info('HISTORICO COMPLETO DE EMAILS ENVIADOS')
    logger.info('=' * 70)

    algum = False
    for c in contatos:
        enviados = c.get('emails_enviados', [])
        if enviados:
            algum = True
            logger.info(f'  Pedido {c["numero"]} - {c["cliente"]}:')
            for e in enviados:
                logger.info(f'    -> {e["situacao"]}  [{e["data"]}]')
        elif not c.get('email'):
            logger.info(f'  Pedido {c["numero"]} - {c["cliente"]}:')
            logger.info(f'    !! SEM EMAIL - nenhuma notificacao enviada')
        else:
            logger.info(f'  Pedido {c["numero"]} - {c["cliente"]}:')
            logger.info(f'    (nenhum email enviado ainda)')

    if not algum:
        logger.info('  Nenhum email enviado ate o momento.')

    logger.info('=' * 70)


# --------------------------------------------------------------------------
# CICLO PRINCIPAL DE MONITORAMENTO
# --------------------------------------------------------------------------
def monitorar(contatos, EMAIL_USUARIO, EMAIL_SENHA, EMAIL_SMTP, EMAIL_PORTA, numeros_recentes=None):
    emails_ciclo = []
    sem_email_atualizados = []
    entregues_ciclo = []
    total_monitorados = 0
    emails_enviados_ciclo = 0  # Counter para anti-spam

    for c in contatos:
        numero = c['numero']
        cliente = c['cliente']
        email = c.get('email', '')
        etiqueta = c.get('etiqueta', '')
        volume_id = c.get('volume_id')
        ultima_situacao = c.get('ultima_situacao', '')

        # Só monitorar pedidos que vieram da API (alterados nos últimos DIAS_JANELA dias)
        if numeros_recentes is not None and numero not in numeros_recentes:
            continue

        total_monitorados += 1
        logger.info(f'Pedido {numero} - {cliente}')

        if not volume_id:
            logger.info(f'   volume_id nao encontrado - aguardando sincronizacao')
            continue

        rastr = obter_rastreamento_bling(volume_id)
        if rastr is None:
            logger.warning(f'   Falha ao consultar Bling')
            continue

        situacao = rastr.get('descricao', '')
        ultima_alt = rastr.get('ultimaAlteracao', '')

        if not situacao:
            logger.info(f'   Sem informacao de rastreamento ainda')
            continue

        # Caso pedido jÃ¡ entregue
        if situacao_e_entregue(situacao):
            logger.info(f'   STATUS FINAL: {situacao}')
            total_emails = len(c.get('emails_enviados', []))
            logger.info(f'   Pedido encerrado. Total de emails enviados: {total_emails}')
            entregues_ciclo.append({'numero': numero, 'cliente': cliente, 'situacao': situacao, 'total_emails': total_emails})
            # Atualiza ultima_situacao mas nÃ£o envia
            c['ultima_situacao'] = situacao
            continue

        # Sem mudanÃ§a
        if situacao == ultima_situacao:
            logger.info(f'   Sem mudanca: "{situacao}"')
            continue

        # MudanÃ§a detectada
        logger.info(f'   MUDANCA: "{ultima_situacao}" -> "{situacao}"')
        c['ultima_situacao'] = situacao

        # Obter dados de contato
        telefone = c.get('telefone_celular', '')
        tem_email = email and validar_email(email)  # Validar formato
        tem_telefone = telefone and telefone != 'N/A' and validar_telefone(telefone)  # Validar formato

        if not (tem_email or tem_telefone):
            logger.info(f'   SEM EMAIL E SEM TELEFONE - nao notificado')
            sem_email_atualizados.append({'numero': numero, 'cliente': cliente, 'situacao': situacao})
            continue

        # Anti-spam: limite de emails por ciclo
        if emails_enviados_ciclo >= MAX_EMAILS_POR_CICLO:
            logger.warning(f'   ⚠️ Limite de {MAX_EMAILS_POR_CICLO} emails por ciclo atingido')
            logger.warning(f'   Pedido {numero} aguardará próximo ciclo')
            continue

        # Enviar Email
        if tem_email:
            # Verificar se já enviou para esta MESMA situação recentemente (deduplicação)
            ja_enviou = any(e.get('situacao') == situacao for e in c.get('emails_enviados', []))
            if ja_enviou:
                logger.info(f'   ℹ️ Email para situação "{situacao}" já foi enviado - pulando')
            else:
                # Montar destino: cidade - estado
                cidade_dest = c.get('cidade_destino', '')
                estado_dest = c.get('estado_destino', '')
                destino_str = f'{cidade_dest} - {estado_dest}' if cidade_dest else ''
                logger.info(f'   📧 Enviando email para: {email}')
                sucesso_email, erro_email = enviar_email(
                    numero, cliente, email, situacao, ultima_alt,
                    EMAIL_USUARIO, EMAIL_SENHA, EMAIL_SMTP, EMAIL_PORTA,
                    destino=destino_str
                )
                if sucesso_email:
                    agora = datetime.now().strftime('%d/%m/%Y %H:%M')
                    c['emails_enviados'].append({'situacao': situacao, 'data': agora})
                    emails_ciclo.append({'numero': numero, 'cliente': cliente, 'email': email, 'situacao': situacao})
                    emails_enviados_ciclo += 1
                    logger.info(f'   ✅ Email enviado com sucesso!')
                else:
                    logger.error(f'   ❌ ERRO ao enviar email: {erro_email}')
        else:
            logger.info(f'   ⏭️ Email inválido ou não cadastrado')

        # Enviar WhatsApp
        if tem_telefone:
            cidade_dest = c.get('cidade_destino', '')
            estado_dest = c.get('estado_destino', '')
            destino_wa = f'{cidade_dest} - {estado_dest}' if cidade_dest else ''
            logger.info(f'   📱 Enviando WhatsApp para: {telefone}')
            sucesso_wa, erro_wa = enviar_whatsapp_notificacao(
                numero, cliente, telefone, situacao, ultima_alt, destino=destino_wa
            )
            if sucesso_wa:
                logger.info(f'   ✅ WhatsApp enviado/enfieirado com sucesso!')
            else:
                logger.error(f'   ❌ ERRO ao enviar WhatsApp: {erro_wa}')
        else:
            logger.info(f'   ⏭️ Sem telefone cadastrado')

        # ENVIAR EMAIL PARA VENDEDOR TAMBEM
        vendedor_email = c.get('vendedor_email', '')
        vendedor_nome = c.get('vendedor_nome', '')
        
        if vendedor_email and validar_email(vendedor_email):
            # Deduplicação: não enviar se já enviou para mesma situação
            ja_enviou_vend = any(e.get('situacao') == situacao for e in c.get('emails_vendedor_enviados', []))
            if ja_enviou_vend:
                logger.info(f'   ℹ️ Email VENDEDOR para situação "{situacao}" já foi enviado - pulando')
            else:
                cidade_dest = c.get('cidade_destino', '')
                estado_dest = c.get('estado_destino', '')
                destino_str = f'{cidade_dest} - {estado_dest}' if cidade_dest else ''
                logger.info(f'   📧 Enviando email PARA VENDEDOR: {vendedor_email} ({vendedor_nome})')
                sucesso_email_vend, erro_email_vend = enviar_email(
                    numero, cliente, vendedor_email, situacao, ultima_alt,
                    EMAIL_USUARIO, EMAIL_SENHA, EMAIL_SMTP, EMAIL_PORTA,
                    vendedor_nome=vendedor_nome, destino=destino_str
                )
                if sucesso_email_vend:
                    agora = datetime.now().strftime('%d/%m/%Y %H:%M')
                    if 'emails_vendedor_enviados' not in c:
                        c['emails_vendedor_enviados'] = []
                    c['emails_vendedor_enviados'].append({'situacao': situacao, 'data': agora, 'vendedor': vendedor_nome})
                    emails_enviados_ciclo += 1
                    logger.info(f'   ✅ Email para vendedor enviado com sucesso!')
                else:
                    logger.error(f'   ❌ ERRO ao enviar email para vendedor: {erro_email_vend}')
        else:
            logger.info(f'   ⏭️ Vendedor sem email cadastrado ou inválido')

    logger.info(f'   Pedidos monitorados (últimos {DIAS_JANELA} dias): {total_monitorados} de {len(contatos)} total')
    return emails_ciclo, sem_email_atualizados, entregues_ciclo


# --------------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------------
def main():
    EMAIL_USUARIO = os.getenv('EMAIL_USUARIO')
    EMAIL_SENHA = os.getenv('EMAIL_SENHA')
    EMAIL_SMTP = os.getenv('EMAIL_SMTP', 'smtp.hostinger.com')
    EMAIL_PORTA = os.getenv('EMAIL_PORTA', '465')

    logger.info('=' * 70)
    logger.info('SISTEMA AUTOMATICO DE RASTREAMENTO - PRODUCTION')
    logger.info('Monitorando todos os clientes a cada 30 minutos')
    logger.info('Pressione Ctrl+C para parar')
    logger.info('=' * 70)

    # Iniciar renovação automática de token em background (sem depender de token_renewer.py)
    _iniciar_renovacao_automatica()

    # Validar credenciais no startup
    logger.info('')
    logger.info('--- VALIDAÇÃO DE CREDENCIAIS ---')
    if not EMAIL_USUARIO:
        logger.error('❌ ERRO: EMAIL_USUARIO não está definido no .env')
        logger.error('Defina: export EMAIL_USUARIO=seu_email@hostinger.com')
        return
    if not EMAIL_SENHA:
        logger.error('❌ ERRO: EMAIL_SENHA não está definido no .env')
        logger.error('Defina: export EMAIL_SENHA=sua_senha')
        return
    if not validar_email(EMAIL_USUARIO):
        logger.error(f'❌ ERRO: EMAIL_USUARIO "{EMAIL_USUARIO}" tem formato inválido')
        return
    logger.info(f'✅ EMAIL_USUARIO: {EMAIL_USUARIO}')
    logger.info(f'✅ EMAIL_SMTP: {EMAIL_SMTP}:{EMAIL_PORTA}')
    logger.info(f'✅ WhatsApp disponível: {WHATSAPP_DISPONIVEL}')
    logger.info(f'✅ Max emails por ciclo: {MAX_EMAILS_POR_CICLO}')
    logger.info(f'✅ Throttle entre emails: {THROTTLE_SEGUNDOS}s')
    logger.info('')

    ciclo = 1

    while True:
        try:
            timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            logger.info('')
            logger.info('=' * 70)
            logger.info(f'CICLO {ciclo} - {timestamp}')
            logger.info('=' * 70)

            # 1. Sincronizar novos clientes e volume_ids
            contatos, numeros_recentes = sincronizar_clientes()

            logger.info('')
            logger.info(f'--- VERIFICANDO RASTREAMENTOS ({len(numeros_recentes)} pedidos recentes) ---')

            # 2. Monitorar somente pedidos recentes (ultimos {DIAS_JANELA} dias)
            emails_ciclo, sem_email_atualizados, entregues_ciclo = monitorar(
                contatos, EMAIL_USUARIO, EMAIL_SENHA, EMAIL_SMTP, EMAIL_PORTA,
                numeros_recentes=numeros_recentes
            )

            # 3. Salvar JSON atualizado
            salvar_contatos(contatos)

            # 4. Resumo do ciclo
            logger.info('')
            logger.info('--- RESUMO DO CICLO ---')
            logger.info(f'   Total de clientes: {len(contatos)}')
            logger.info(f'   Emails enviados neste ciclo: {len(emails_ciclo)}')
            logger.info(f'   Atualizados sem email: {len(sem_email_atualizados)}')
            logger.info(f'   Pedidos encerrados (entregues): {len(entregues_ciclo)}')

            if emails_ciclo:
                logger.info('')
                logger.info('   EMAILS ENVIADOS AGORA:')
                for item in emails_ciclo:
                    logger.info(f'     -> Pedido {item["numero"]} | {item["email"]}')
                    logger.info(f'        Status: {item["situacao"]}')

            if sem_email_atualizados:
                logger.info('')
                logger.info('   ATUALIZADOS SEM EMAIL (nao notificados):')
                for item in sem_email_atualizados:
                    logger.info(f'     -> Pedido {item["numero"]} | {item["cliente"]}')
                    logger.info(f'        Status: {item["situacao"]}')

            if entregues_ciclo:
                logger.info('')
                logger.info('   PEDIDOS JA ENTREGUES (encerrados):')
                for item in entregues_ciclo:
                    logger.info(f'     -> Pedido {item["numero"]} | {item["cliente"]}')
                    logger.info(f'        Status: {item["situacao"]}')
                    logger.info(f'        Total emails enviados no ciclo de vida: {item["total_emails"]}')

            # 5. HistÃ³rico completo de emails
            logar_historico_completo(contatos)

            logger.info(f'   Proximo ciclo em 30 minutos...')
            logger.info('=' * 70)

            ciclo += 1
            time.sleep(1800)  # 30 minutos em vez de 5 (reduz de 288 ciclos/dia para 48)

        except KeyboardInterrupt:
            logger.info('')
            logger.info('Sistema parado pelo usuario.')
            logger.info('=' * 70)
            break
        except Exception as e:
            logger.error(f'Erro geral no ciclo: {e}')
            import traceback
            logger.error(traceback.format_exc())
            time.sleep(60)


if __name__ == '__main__':
    main()

