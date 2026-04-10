#!/usr/bin/env python3
"""Detecta nome correto da pasta Enviados na conta logisticaallcanci@allcanci.com.br"""
import imaplib
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_USUARIO = os.getenv('EMAIL_USUARIO')
EMAIL_SENHA = os.getenv('EMAIL_SENHA')
EMAIL_IMAP = os.getenv('EMAIL_IMAP', 'imap.hostinger.com')
EMAIL_IMAP_PORTA = int(os.getenv('EMAIL_IMAP_PORTA', 993))

print(f'Conectando: {EMAIL_USUARIO} @ {EMAIL_IMAP}:{EMAIL_IMAP_PORTA}')

imap = imaplib.IMAP4_SSL(EMAIL_IMAP, EMAIL_IMAP_PORTA)
imap.login(EMAIL_USUARIO, EMAIL_SENHA)

print('\nPastas disponíveis:')
_, folders = imap.list()
for f in folders:
    print(f'  {f.decode("utf-8", errors="ignore")}')

imap.logout()
