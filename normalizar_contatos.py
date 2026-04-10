#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Normaliza números telefônicos em contatos_rastreamento.json

Converte todos os números para formato padrão internacional:
    "31984163357" → "5531984163357"
    "(31) 98416-3357" → "5531984163357"
    etc.
"""

import json
import shutil
from pathlib import Path
from whatsapp_service import formatar_numero_telefone


def normalizar_contatos_arquivo(caminho_arquivo='contatos_rastreamento.json'):
    """
    Normaliza números telefônicos em arquivo de contatos.
    
    Args:
        caminho_arquivo: Caminho para contatos_rastreamento.json
    """
    
    arquivo = Path(caminho_arquivo)
    
    if not arquivo.exists():
        print(f"❌ Arquivo não encontrado: {arquivo}")
        return False
    
    print(f"📂 Carregando: {arquivo}")
    print()
    
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            contatos = json.load(f)
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")
        return False
    
    if not isinstance(contatos, list):
        print(f"❌ Formato inválido: esperado lista de contatos")
        return False
    
    # Backup
    backup = arquivo.with_suffix('.json.backup')
    shutil.copy(arquivo, backup)
    print(f"✅ Backup criado: {backup}")
    print()
    
    # Processar
    alterados = 0
    invalidos = 0
    
    print("NORMALIZANDO NÚMEROS:")
    print("=" * 80)
    
    for i, contato in enumerate(contatos):
        numero_original = contato.get('telefone_celular', '')
        
        if not numero_original or numero_original == 'N/A':
            continue
        
        numero_formatado = formatar_numero_telefone(numero_original)
        
        if not numero_formatado:
            print(f"❌ INVÁLIDO | {contato.get('cliente', 'DESCONHECIDO')}")
            print(f"   Número: {numero_original}")
            invalidos += 1
            print()
            continue
        
        if numero_original != numero_formatado:
            print(f"✅ NORMALIZADO | {contato.get('cliente', 'DESCONHECIDO')}")
            print(f"   Original:   {numero_original}")
            print(f"   Formatado:  {numero_formatado}")
            contato['telefone_celular'] = numero_formatado
            alterados += 1
            print()
    
    # Salvar
    print("=" * 80)
    print()
    
    if alterados == 0 and invalidos == 0:
        print("✅ Nenhuma alteração necessária - todos os números já estão normalizados!")
        return True
    
    try:
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(contatos, f, ensure_ascii=False, indent=2)
        print(f"✅ Arquivo salvo: {arquivo}")
        print(f"   • {alterados} número(s) normalizado(s)")
        print(f"   • {invalidos} número(s) inválido(s)")
        print()
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar: {e}")
        print(f"   Restaurando backup...")
        shutil.copy(backup, arquivo)
        return False


def mostrar_resumo(caminho_arquivo='contatos_rastreamento.json'):
    """Mostra resumo dos números no arquivo."""
    
    arquivo = Path(caminho_arquivo)
    
    if not arquivo.exists():
        return
    
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            contatos = json.load(f)
    except:
        return
    
    print("\n" + "=" * 80)
    print("RESUMO DOS CONTATOS")
    print("=" * 80)
    
    com_telefone = 0
    com_telefone_valido = 0
    
    for contato in contatos:
        telefone = contato.get('telefone_celular', '')
        
        if telefone and telefone != 'N/A':
            com_telefone += 1
            if formatar_numero_telefone(telefone):
                com_telefone_valido += 1
    
    total = len(contatos)
    
    print(f"Total de contatos: {total}")
    print(f"Com telefone cadastrado: {com_telefone}")
    print(f"Com telefone válido: {com_telefone_valido}")
    print()
    
    if com_telefone > 0:
        taxa_validade = (com_telefone_valido / com_telefone) * 100
        print(f"Taxa de validação: {taxa_validade:.1f}%")
    
    print()


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("NORMALIZAÇÃO DE NÚMEROS TELEFÔNICOS")
    print("=" * 80)
    print()
    
    resultado = normalizar_contatos_arquivo()
    
    if resultado:
        print("✅ Normalização concluída com sucesso!")
        mostrar_resumo()
    else:
        print("❌ Falha na normalização")
    
    print()
