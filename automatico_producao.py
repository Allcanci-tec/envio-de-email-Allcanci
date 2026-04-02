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
import time
import logging
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Importar WhatsApp Service
try:
    from whatsapp_service import enviar_mensagem as enviar_whatsapp
    WHATSAPP_DISPONIVEL = True
except Exception as e:
    logger.warning(f"⚠️ WhatsApp Service indisponível: {e}")
    WHATSAPP_DISPONIVEL = False

# --------------------------------------------------------------------------
# CONFIGURAÃ‡ÃƒO DE LOG
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

# --------------------------------------------------------------------------
# CONSTANTES
# --------------------------------------------------------------------------
CONTATOS_FILE = 'contatos_rastreamento.json'
BLING_API = 'https://api.bling.com.br/v3'
ID_LOGISTICA_CORREIOS = 151483  # ID da logÃ­stica Correios no Bling

SITUACOES_ENTREGUE = [
    'entregue',
    'devolvido',
    'objeto perdido',
]


# --------------------------------------------------------------------------
# HELPERS: TOKEN
# --------------------------------------------------------------------------
def carregar_token():
    with open('tokens.json', 'r') as f:
        return json.load(f)['access_token']


def headers_bling():
    return {'Authorization': f'Bearer {carregar_token()}'}


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
def sincronizar_clientes():
    """Busca todos os pedidos Correios no Bling, adiciona novos ao JSON
    e preenche volume_ids que ainda estÃ£o null."""
    logger.info('--- SINCRONIZANDO COM BLING API ---')

    contatos = carregar_contatos()
    numeros_existentes = {c['numero'] for c in contatos}
    novos = 0
    volume_ids_resolvidos = 0

    pagina = 1
    while True:
        try:
            resp = requests.get(
                f'{BLING_API}/pedidos/vendas',
                headers=headers_bling(),
                params={
                    'pagina': pagina,
                    'limite': 100,
                    'idLogistica': ID_LOGISTICA_CORREIOS,
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
                r2 = requests.get(
                    f'{BLING_API}/pedidos/vendas/{pedido_id_interno}',
                    headers=headers_bling(),
                    timeout=10,
                )
            except Exception as e:
                logger.warning(f'   Erro detalhe pedido {numero}: {e}')
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

            # SKIP se ja existe E ja tem volume_id -- sem chamada extra
            if numero in numeros_existentes:
                ja_tem_volume = any(c.get('volume_id') for c in contatos if c['numero'] == numero)
                if ja_tem_volume:
                    continue

            if numero not in numeros_existentes:
                # Novo cliente descoberto â€” buscar email no contato
                contato_id = pedido.get('contato', {}).get('id')
                email, telefone, nome_cliente = '', 'N/A', pedido.get('contato', {}).get('nome', 'Desconhecido')

                if contato_id:
                    try:
                        rc = requests.get(
                            f'{BLING_API}/contatos/{contato_id}',
                            headers=headers_bling(),
                            timeout=10,
                        )
                        if rc.status_code == 200:
                            cd = rc.json().get('data', {})
                            email = cd.get('email', '')
                            telefones = cd.get('telefones', [])
                            if telefones:
                                tel = telefones[0]
                                telefone = tel.get('numero', 'N/A')
                            nome_cliente = cd.get('nome', nome_cliente)
                    except Exception:
                        pass

                novo_contato = {
                    'numero': numero,
                    'cliente': nome_cliente,
                    'email': email,
                    'telefone_celular': telefone,
                    'etiqueta': etiqueta,
                    'volume_id': volume_id,
                    'ultima_situacao': '',
                    'emails_enviados': [],
                }
                contatos.append(novo_contato)
                numeros_existentes.add(numero)
                novos += 1
                logger.info(f'   + NOVO pedido {numero}: {nome_cliente} | email: {email or "(sem email)"}')
            else:
                # Pedido existente â€” apenas preencher volume_id se faltando
                for c in contatos:
                    if c['numero'] == numero and not c.get('volume_id') and volume_id:
                        c['volume_id'] = volume_id
                        volume_ids_resolvidos += 1
                        logger.info(f'   + volume_id resolvido para pedido {numero}')

        pagina += 1

    salvar_contatos(contatos)
    logger.info(f'   Sincronizacao concluida: {novos} novos, {volume_ids_resolvidos} volume_ids resolvidos')
    return contatos


# --------------------------------------------------------------------------
# RASTREAMENTO: consulta Bling pelo volume_id
# --------------------------------------------------------------------------
def obter_rastreamento_bling(volume_id):
    try:
        resp = requests.get(
            f'{BLING_API}/logisticas/objetos/{volume_id}',
            headers=headers_bling(),
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json().get('data', {}).get('rastreamento', {})
    except Exception as e:
        logger.error(f'   Erro ao consultar rastreamento {volume_id}: {e}')
    return None


def situacao_e_entregue(situacao):
    s = situacao.lower()
    return any(k in s for k in SITUACOES_ENTREGUE)


# --------------------------------------------------------------------------
# EMAIL
# --------------------------------------------------------------------------
def enviar_email(numero, cliente, email_destino, status, ultima_alt,
                 EMAIL_USUARIO, EMAIL_SENHA, EMAIL_SMTP, EMAIL_PORTA):
    if not email_destino:
        return False, 'sem email'
    try:
        time.sleep(1)  # Throttling: aguarda 1 segundo entre emails (evita bloqueio)
        data_fmt = datetime.now().strftime('%d/%m/%Y %H:%M')
        html = f'''<html>
<body style="font-family:Arial;background:#f5f5f5;padding:20px">
<div style="max-width:600px;margin:0 auto;background:white;border-radius:8px;padding:30px">
  <div style="background:linear-gradient(135deg,#0000F3 0%,#0051DB 100%);padding:30px;text-align:center;color:white;border-radius:6px;margin-bottom:30px">
    <h1 style="margin:0;font-size:26px">&#128246; Atualiza&#231;&#227;o de Rastreamento</h1>
  </div>
  <p style="font-size:16px;color:#333">Ol&#225; <strong>{cliente}</strong>,</p>
  <p style="font-size:16px;color:#555;margin:15px 0">Seu pedido have uma atualiza&#231;&#227;o importante:</p>
  <div style="background:#4CAF50;padding:25px;border-radius:6px;margin:20px 0;color:white;text-align:center;font-size:20px;font-weight:bold;line-height:1.6">
    &#9989; {status.upper()}
  </div>
  <div style="background:#f9f9f9;padding:20px;border-radius:6px;margin:20px 0;border-left:4px solid #0066cc">
    <p style="margin:10px 0"><strong>&#128456; Pedido:</strong> {numero}</p>
    <p style="margin:10px 0"><strong>&#128226; Rastreamento:</strong> {ultima_alt}</p>
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
        msg['Subject'] = f'Pedido {numero} - {status}'
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
        return True, 'OK'
    except Exception as e:
        return False, str(e)


# --------------------------------------------------------------------------
# ENVIAR NOTIFICAÃ‡ÃƒO WHATSAPP
# --------------------------------------------------------------------------
def enviar_whatsapp_notificacao(numero, cliente, numero_telefone, status, ultima_alt):
    """Envia notificação pelo WhatsApp com formato profissional"""
    if not WHATSAPP_DISPONIVEL or not numero_telefone or numero_telefone == 'N/A':
        return False, 'WhatsApp indisponível ou sem telefone'
    
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
🔹 Atualizado em: {data_fmt}

🔗 Acompanhe: https://www.correios.com.br

_Allcanci Tecnologia_
        """.strip()
        
        # Enviar via WhatsApp Service (respeita anti-spam automaticamente)
        sucesso, msg = enviar_whatsapp(numero_telefone, mensagem)
        
        if sucesso:
            return True, 'OK'
        else:
            # Se falhar, adiciona à fila (a fila processará respeitando limites)
            logger.info(f'   WhatsApp adicionado à fila: {msg}')
            return True, 'Enfieirado'  # Retorna True porque foi adicionado à fila
            
    except Exception as e:
        logger.warning(f'   Erro ao enviar WhatsApp: {e}')
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
def monitorar(contatos, EMAIL_USUARIO, EMAIL_SENHA, EMAIL_SMTP, EMAIL_PORTA):
    emails_ciclo = []
    sem_email_atualizados = []
    entregues_ciclo = []

    for c in contatos:
        numero = c['numero']
        cliente = c['cliente']
        email = c.get('email', '')
        etiqueta = c.get('etiqueta', '')
        volume_id = c.get('volume_id')
        ultima_situacao = c.get('ultima_situacao', '')

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
        tem_email = bool(email)
        tem_telefone = bool(telefone) and telefone != 'N/A'

        if not (tem_email or tem_telefone):
            logger.info(f'   SEM EMAIL E SEM TELEFONE - nao notificado')
            sem_email_atualizados.append({'numero': numero, 'cliente': cliente, 'situacao': situacao})
            continue

        # Enviar Email
        if tem_email:
            logger.info(f'   📧 Enviando email para: {email}')
            sucesso_email, erro_email = enviar_email(
                numero, cliente, email, situacao, ultima_alt,
                EMAIL_USUARIO, EMAIL_SENHA, EMAIL_SMTP, EMAIL_PORTA
            )
            if sucesso_email:
                agora = datetime.now().strftime('%d/%m/%Y %H:%M')
                c['emails_enviados'].append({'situacao': situacao, 'data': agora})
                emails_ciclo.append({'numero': numero, 'cliente': cliente, 'email': email, 'situacao': situacao})
                logger.info(f'   ✅ Email enviado com sucesso!')
            else:
                logger.error(f'   ❌ ERRO ao enviar email: {erro_email}')
        else:
            logger.info(f'   ⏭️ Sem email cadastrado')

        # Enviar WhatsApp
        if tem_telefone:
            logger.info(f'   📱 Enviando WhatsApp para: {telefone}')
            sucesso_wa, erro_wa = enviar_whatsapp_notificacao(
                numero, cliente, telefone, situacao, ultima_alt
            )
            if sucesso_wa:
                logger.info(f'   ✅ WhatsApp enviado/enfieirado com sucesso!')
            else:
                logger.error(f'   ❌ ERRO ao enviar WhatsApp: {erro_wa}')
        else:
            logger.info(f'   ⏭️ Sem telefone cadastrado')

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
    logger.info('Monitorando todos os clientes a cada 5 minutos')
    logger.info('Pressione Ctrl+C para parar')
    logger.info('=' * 70)

    ciclo = 1

    while True:
        try:
            timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            logger.info('')
            logger.info('=' * 70)
            logger.info(f'CICLO {ciclo} - {timestamp}')
            logger.info('=' * 70)

            # 1. Sincronizar novos clientes e volume_ids
            contatos = sincronizar_clientes()

            logger.info('')
            logger.info('--- VERIFICANDO RASTREAMENTOS ---')

            # 2. Monitorar todos
            emails_ciclo, sem_email_atualizados, entregues_ciclo = monitorar(
                contatos, EMAIL_USUARIO, EMAIL_SENHA, EMAIL_SMTP, EMAIL_PORTA
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

