#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço de busca de dados de vendedor
Busca pelo ID na API Bling e retorna nome, email, etc.
"""

import requests
import json
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger('rastreamento')

BLING_API = 'https://api.bling.com.br/v3'


def carregar_token():
    """Carrega token do Bling de tokens.json com validação"""
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


def buscar_vendedor(vendedor_id):
    """
    Busca dados de um vendedor pelo ID no Bling
    
    Retorna:
    {
        'id': vendedor_id,
        'nome': nome do vendedor,
        'email': email do vendedor,
        'telefone': telefone do vendedor,
        'sucesso': True/False
    }
    """
    
    if not vendedor_id or vendedor_id == 0 or vendedor_id == '0':
        return {
            'id': vendedor_id,
            'nome': 'N/A',
            'email': '',
            'telefone': '',
            'sucesso': False,
            'motivo': 'ID de vendedor inválido (0 ou nulo)'
        }
    
    try:
        # Buscar dados do vendedor diretamente
        resp = requests.get(
            f'{BLING_API}/vendedores/{vendedor_id}',
            headers=headers_bling(),
            timeout=10,
        )
        
        if resp.status_code == 200:
            dados = resp.json().get('data', {})
            contato_info = dados.get('contato', {})
            nome_vendedor = contato_info.get('nome', 'Desconhecido')
            contato_id = contato_info.get('id')
            
            email = ''
            telefone = ''
            
            # Se temos o ID do contato, buscar email
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
                            telefone = tel.get('numero', '')
                except Exception as e:
                    logger.warning(f'   Erro ao buscar email do contato {contato_id}: {e}')
            
            return {
                'id': vendedor_id,
                'nome': nome_vendedor,
                'email': email,
                'telefone': telefone,
                'contato_id': contato_id,
                'sucesso': True,
                'motivo': 'OK'
            }
        elif resp.status_code == 404:
            return {
                'id': vendedor_id,
                'nome': 'N/A',
                'email': '',
                'telefone': '',
                'sucesso': False,
                'motivo': f'Vendedor {vendedor_id} não encontrado no Bling (404)'
            }
        else:
            logger.warning(f'   Bling retornou status {resp.status_code} ao buscar vendedor {vendedor_id}')
            return {
                'id': vendedor_id,
                'nome': 'N/A',
                'email': '',
                'telefone': '',
                'sucesso': False,
                'motivo': f'Bling retornou status {resp.status_code}'
            }
            
    except requests.Timeout:
        logger.error(f'   TIMEOUT ao buscar vendedor {vendedor_id}')
        return {
            'id': vendedor_id,
            'nome': 'N/A',
            'email': '',
            'telefone': '',
            'sucesso': False,
            'motivo': 'TIMEOUT ao consultar Bling'
        }
    except requests.ConnectionError:
        logger.error(f'   ERRO DE CONEXÃO ao buscar vendedor {vendedor_id}')
        return {
            'id': vendedor_id,
            'nome': 'N/A',
            'email': '',
            'telefone': '',
            'sucesso': False,
            'motivo': 'Erro de conexão com Bling'
        }
    except Exception as e:
        logger.error(f'   Erro ao buscar vendedor {vendedor_id}: {type(e).__name__}: {e}')
        return {
            'id': vendedor_id,
            'nome': 'N/A',
            'email': '',
            'telefone': '',
            'sucesso': False,
            'motivo': str(e)
        }


def buscar_vendedor_por_nome(nome_vendedor):
    """
    Busca um vendedor pelo nome usando listagem de vendedores
    
    Retorna mesmo formato que buscar_vendedor()
    """
    
    if not nome_vendedor or not isinstance(nome_vendedor, str):
        return {
            'nome': nome_vendedor or 'N/A',
            'email': '',
            'sucesso': False,
            'motivo': 'Nome do vendedor inválido'
        }
    
    try:
        logger.info(f'   Procurando vendedor por nome: {nome_vendedor}')
        
        # Listar vendedores (com paginação se necessário)
        resp = requests.get(
            f'{BLING_API}/vendedores',
            headers=headers_bling(),
            params={'limite': 100},
            timeout=10,
        )
        
        if resp.status_code == 200:
            vendedores = resp.json().get('data', [])
            
            # Procurar por nome (case-insensitive)
            nome_lower = nome_vendedor.lower().strip()
            
            for vendedor in vendedores:
                nome_v = vendedor.get('nome', '').lower().strip()
                if nome_v == nome_lower or nome_lower in nome_v:
                    return {
                        'id': vendedor.get('id'),
                        'nome': vendedor.get('nome', 'Desconhecido'),
                        'email': vendedor.get('email', ''),
                        'telefone': vendedor.get('telefone', '') or vendedor.get('celular', ''),
                        'sucesso': True,
                        'motivo': f'Vendedor encontrado por nome: {vendedor.get("nome")}'
                    }
            
            # Se não encontrou por nome exato, procurar parcial
            for vendedor in vendedores:
                nome_v = vendedor.get('nome', '').lower().strip()
                if nome_lower in nome_v:
                    return {
                        'id': vendedor.get('id'),
                        'nome': vendedor.get('nome', 'Desconhecido'),
                        'email': vendedor.get('email', ''),
                        'telefone': vendedor.get('telefone', '') or vendedor.get('celular', ''),
                        'sucesso': True,
                        'motivo': f'Vendedor encontrado por busca parcial: {vendedor.get("nome")}'
                    }
            
            return {
                'nome': nome_vendedor,
                'email': '',
                'sucesso': False,
                'motivo': f'Nenhum vendedor encontrado com o nome: {nome_vendedor}'
            }
        else:
            logger.warning(f'   Bling retornou status {resp.status_code} ao listar vendedores')
            return {
                'nome': nome_vendedor,
                'email': '',
                'sucesso': False,
                'motivo': f'Bling retornou status {resp.status_code}'
            }
            
    except requests.Timeout:
        logger.error(f'   TIMEOUT ao buscar vendedor por nome')
        return {
            'nome': nome_vendedor,
            'email': '',
            'sucesso': False,
            'motivo': 'TIMEOUT ao consultar Bling'
        }
    except requests.ConnectionError:
        logger.error(f'   ERRO DE CONEXÃO ao buscar vendedor')
        return {
            'nome': nome_vendedor,
            'email': '',
            'sucesso': False,
            'motivo': 'Erro de conexão com Bling'
        }
    except Exception as e:
        logger.error(f'   Erro ao buscar vendedor por nome: {type(e).__name__}: {e}')
        return {
            'nome': nome_vendedor,
            'email': '',
            'sucesso': False,
            'motivo': str(e)
        }


if __name__ == '__main__':
    # Teste simples
    print("\n" + "=" * 70)
    print("TESTE DO VENDEDOR SERVICE")
    print("=" * 70 + "\n")
    
    # Teste 1: Buscar vendedor por ID
    print("Teste 1: Buscar vendedor por ID (15596468785)")
    resultado = buscar_vendedor(15596468785)
    print(f"Resultado: {json.dumps(resultado, indent=2, ensure_ascii=False)}")
    
    # Teste 2: Buscar vendedor por nome
    print("\n\nTeste 2: Buscar todos os vendedores")
    try:
        token = carregar_token()
        headers = {'Authorization': f'Bearer {token}'}
        resp = requests.get(
            f'{BLING_API}/vendedores',
            headers=headers,
            params={'limite': 50},
            timeout=10,
        )
        if resp.status_code == 200:
            vendedores = resp.json().get('data', [])
            print(f"\nTotal de vendedores encontrados: {len(vendedores)}\n")
            for v in vendedores[:10]:
                print(f"  ID: {v.get('id')}")
                print(f"  Nome: {v.get('nome')}")
                print(f"  Email: {v.get('email')}")
                print(f"  ---")
    except Exception as e:
        print(f"Erro: {e}")
