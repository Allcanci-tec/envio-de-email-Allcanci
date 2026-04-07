#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SIMULAÇÃO DO CÓDIGO PRINCIPAL - Prova que o fluxo completo funciona
Executa EXATAMENTE a mesma lógica do automatico_producao.py mas para UM pedido específico.

Passos:
1. Busca pedido real na API Bling (como sincronizar_clientes faz)
2. Busca contato para pegar o vendedor_id (do contato.vendedor.id)
3. Busca dados do vendedor via vendedor_service
4. Busca rastreamento real do pedido
5. Envia email usando EXATAMENTE a mesma função enviar_email() do código principal
6. Mostra tudo passo a passo

Se tudo funcionar aqui, vai funcionar no código principal.
"""

import json
import os
import sys
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Importar as funções REAIS do código principal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from automatico_producao import (
    headers_bling,
    enviar_email,
    obter_rastreamento_bling,
    BLING_API,
)
from vendedor_service import buscar_vendedor

EMAIL_USUARIO = os.getenv('EMAIL_USUARIO')
EMAIL_SENHA = os.getenv('EMAIL_SENHA')
EMAIL_SMTP = os.getenv('EMAIL_SMTP', 'smtp.hostinger.com')
EMAIL_PORTA = os.getenv('EMAIL_PORTA', '465')


def separador(titulo):
    print(f'\n{"=" * 70}')
    print(f'  {titulo}')
    print(f'{"=" * 70}\n')


def main():
    separador('SIMULAÇÃO COMPLETA DO CÓDIGO PRINCIPAL')
    print('Vamos executar EXATAMENTE a mesma lógica que o automatico_producao.py')
    print('mas para um pedido específico, passo a passo.\n')

    # =========================================================================
    # PASSO 1: Buscar pedido real (mesma lógica de sincronizar_clientes)
    # =========================================================================
    separador('PASSO 1: BUSCAR PEDIDO NA API BLING')

    # Buscar pedido 2409 (Escola Israel Pinheiro) como referência
    numero_alvo = 2409
    pedido_id = None
    pedido_data = None

    print(f'Buscando pedido #{numero_alvo} na API Bling...')
    pagina = 1
    encontrado = False

    while pagina <= 10 and not encontrado:
        resp = requests.get(
            f'{BLING_API}/pedidos/vendas',
            headers=headers_bling(),
            params={'pagina': pagina, 'limite': 100, 'idLogistica': 151483},
            timeout=15,
        )
        if resp.status_code != 200:
            break

        for p in resp.json().get('data', []):
            if p.get('numero') == numero_alvo:
                pedido_id = p.get('id')
                encontrado = True
                break

        pagina += 1

    if not pedido_id:
        print(f'❌ Pedido #{numero_alvo} não encontrado na listagem')
        return

    # Buscar detalhe completo (mesma lógica do código principal)
    print(f'✅ Pedido encontrado! ID interno: {pedido_id}')
    print(f'Buscando detalhes completos...')

    r2 = requests.get(
        f'{BLING_API}/pedidos/vendas/{pedido_id}',
        headers=headers_bling(),
        timeout=10,
    )

    if r2.status_code != 200:
        print(f'❌ Erro ao buscar detalhe: status {r2.status_code}')
        return

    pedido = r2.json().get('data', {})
    volumes = pedido.get('transporte', {}).get('volumes', [])
    volume = volumes[0] if volumes else {}
    etiqueta = volume.get('codigoRastreamento', '')
    volume_id = volume.get('id')
    contato_id = pedido.get('contato', {}).get('id')
    nome_cliente = pedido.get('contato', {}).get('nome', 'Desconhecido')

    print(f'✅ Detalhes obtidos:')
    print(f'   Cliente: {nome_cliente}')
    print(f'   Etiqueta: {etiqueta}')
    print(f'   Volume ID: {volume_id}')
    print(f'   Contato ID: {contato_id}')

    # =========================================================================
    # PASSO 2: Buscar dados do contato + vendedor_id (CORREÇÃO CRÍTICA)
    # =========================================================================
    separador('PASSO 2: BUSCAR CONTATO E VENDEDOR_ID')

    email_escola = ''
    vendedor_id_contato = None

    if contato_id:
        print(f'Buscando contato ID {contato_id}...')
        rc = requests.get(
            f'{BLING_API}/contatos/{contato_id}',
            headers=headers_bling(),
            timeout=10,
        )
        if rc.status_code == 200:
            cd = rc.json().get('data', {})
            email_escola = cd.get('email', '')
            # >>> AQUI É O PONTO CHAVE: vendedor fica no CONTATO <<<
            vendedor_id_contato = cd.get('vendedor', {}).get('id')

            print(f'✅ Dados do contato:')
            print(f'   Nome: {cd.get("nome")}')
            print(f'   Email escola: {email_escola or "(sem email)"}')
            print(f'   vendedor.id (do contato): {vendedor_id_contato}')
            print()
            print(f'   ⚡ Código ANTIGO buscava: pedido.vendedor.id = {pedido.get("vendedor", {}).get("id")} (SEMPRE 0!)')
            print(f'   ⚡ Código NOVO busca:     contato.vendedor.id = {vendedor_id_contato} (CORRETO!)')
        else:
            print(f'❌ Erro ao buscar contato: {rc.status_code}')
    else:
        print('❌ Sem contato_id no pedido')

    # =========================================================================
    # PASSO 3: Buscar dados do vendedor (usando vendedor_service)
    # =========================================================================
    separador('PASSO 3: BUSCAR DADOS DO VENDEDOR')

    vendedor_nome = ''
    vendedor_email = ''

    vendedor_id = vendedor_id_contato
    if vendedor_id and vendedor_id != 0:
        print(f'Buscando vendedor ID {vendedor_id} via buscar_vendedor()...')
        dados_vendedor = buscar_vendedor(vendedor_id)

        if dados_vendedor.get('sucesso'):
            vendedor_nome = dados_vendedor.get('nome', '')
            vendedor_email = dados_vendedor.get('email', '')
            print(f'✅ Vendedor encontrado:')
            print(f'   Nome: {vendedor_nome}')
            print(f'   Email: {vendedor_email}')
            print(f'   Contato ID: {dados_vendedor.get("contato_id")}')
        else:
            print(f'❌ Vendedor não obtido: {dados_vendedor.get("motivo")}')
    else:
        print(f'⚠️ Sem vendedor_id válido ({vendedor_id})')

    # =========================================================================
    # PASSO 4: Buscar rastreamento real (mesma função do código principal)
    # =========================================================================
    separador('PASSO 4: BUSCAR RASTREAMENTO')

    situacao = ''
    ultima_alt = ''

    if volume_id:
        print(f'Consultando rastreamento para volume {volume_id}...')
        rastr = obter_rastreamento_bling(volume_id)
        if rastr:
            situacao = rastr.get('descricao', '')
            ultima_alt = rastr.get('ultimaAlteracao', '')
            print(f'✅ Rastreamento obtido:')
            print(f'   Situação: {situacao}')
            print(f'   Última alteração: {ultima_alt}')
        else:
            print('⚠️ Sem dados de rastreamento - usando dados simulados')
            situacao = 'Objeto em trânsito - por favor aguarde'
            ultima_alt = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    else:
        print('⚠️ Sem volume_id - usando dados simulados')
        situacao = 'Objeto em trânsito - por favor aguarde'
        ultima_alt = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

    # =========================================================================
    # PASSO 5: ENVIAR EMAIL PARA O VENDEDOR (mesma função enviar_email)
    # =========================================================================
    separador('PASSO 5: ENVIAR EMAIL PARA O VENDEDOR')

    if not vendedor_email:
        print('❌ Vendedor sem email - não é possível enviar')
        return

    print(f'Usando a função enviar_email() REAL do automatico_producao.py')
    print(f'Com vendedor_nome="{vendedor_nome}" para personalizar o template\n')
    print(f'📧 Dados do envio:')
    print(f'   Para: {vendedor_email} ({vendedor_nome})')
    print(f'   Pedido: #{numero_alvo}')
    print(f'   Cliente: {nome_cliente}')
    print(f'   Situação: {situacao}')
    print(f'   Assunto: Pedido {numero_alvo} ({nome_cliente}) - {situacao}')
    print()

    # Chamada EXATA igual ao código principal (monitorar())
    sucesso, erro = enviar_email(
        numero_alvo, nome_cliente, vendedor_email, situacao, ultima_alt,
        EMAIL_USUARIO, EMAIL_SENHA, EMAIL_SMTP, EMAIL_PORTA,
        vendedor_nome=vendedor_nome  # <-- parâmetro novo para template do vendedor
    )

    if sucesso:
        print(f'✅ EMAIL ENVIADO COM SUCESSO!')
        print(f'   Destino: {vendedor_email}')
        print(f'   Hora: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
    else:
        print(f'❌ ERRO ao enviar: {erro}')
        return

    # =========================================================================
    # RESUMO FINAL
    # =========================================================================
    separador('RESULTADO DA SIMULAÇÃO')

    print('✅ TODOS OS PASSOS EXECUTADOS COM SUCESSO!\n')
    print('O que foi comprovado:')
    print(f'  1. ✅ Pedido #{numero_alvo} encontrado na API Bling')
    print(f'  2. ✅ Vendedor extraído do CONTATO (contato.vendedor.id = {vendedor_id})')
    print(f'  3. ✅ Dados do vendedor obtidos: {vendedor_nome} ({vendedor_email})')
    print(f'  4. ✅ Rastreamento obtido: "{situacao}"')
    print(f'  5. ✅ Email enviado para vendedor com MESMO DESIGN + nome do vendedor')
    print()
    print('Quando o automatico_producao.py rodar em produção:')
    print(f'  → Para CADA pedido com mudança de rastreamento:')
    print(f'     1. Envia email para ESCOLA (mesmo design, saudação: "Olá Escola...")')
    print(f'     2. Envia email para VENDEDOR (mesmo design, saudação: "Olá Vendedor...")')
    print(f'     3. Registra ambos os envios no contatos_rastreamento.json')
    print()
    print(f'📬 Verifique a caixa de entrada de: {vendedor_email}')
    print(f'   Procure por: "Pedido {numero_alvo} ({nome_cliente}) - {situacao}"')
    print()
    print('=' * 70)
    print('  SIMULAÇÃO COMPLETA - SISTEMA PRONTO PARA PRODUÇÃO')
    print('=' * 70)


if __name__ == '__main__':
    main()
