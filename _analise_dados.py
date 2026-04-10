import json, re, os

with open('contatos_rastreamento.json', 'r', encoding='utf-8') as f:
    contatos = json.load(f)

def val_email(e):
    if not e or not isinstance(e, str): return False
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', e) is not None

def val_tel(t):
    if not t or t == 'N/A': return False
    apenas = re.sub(r'\D', '', str(t))
    return len(apenas) >= 10

total = len(contatos)
com_email = sum(1 for c in contatos if c.get('email'))
emails_validos = sum(1 for c in contatos if val_email(c.get('email', '')))
emails_invalidos = com_email - emails_validos
com_telefone = sum(1 for c in contatos if c.get('telefone_celular') and c['telefone_celular'] != 'N/A')
telefones_validos = sum(1 for c in contatos if val_tel(c.get('telefone_celular', '')))
com_volume = sum(1 for c in contatos if c.get('volume_id'))
com_etiqueta = sum(1 for c in contatos if c.get('etiqueta'))
emails_enviados = sum(1 for c in contatos if c.get('emails_enviados'))
com_vendedor_email = sum(1 for c in contatos if c.get('vendedor_email'))
vendedor_email_valido = sum(1 for c in contatos if val_email(c.get('vendedor_email', '')))
com_situacao = sum(1 for c in contatos if c.get('ultima_situacao'))

from collections import Counter
situacoes = Counter(c.get('ultima_situacao', '(vazio)') for c in contatos)

print('=== ANALISE COMPLETA DOS DADOS ===')
print(f'Total contatos: {total}')
print(f'Com email: {com_email} | Validos: {emails_validos} | Invalidos: {emails_invalidos}')
print(f'Com telefone: {com_telefone} | Validos (10+ dig): {telefones_validos}')
print(f'Com volume_id: {com_volume} | Sem: {total - com_volume}')
print(f'Com etiqueta: {com_etiqueta}')
print(f'Ja receberam email: {emails_enviados}')
print(f'Vendedor com email: {com_vendedor_email} | Validos: {vendedor_email_valido}')
print(f'Com situacao: {com_situacao}')
print()
print('=== SITUACOES ATUAIS ===')
for sit, count in situacoes.most_common():
    print(f'  {count:3d}x  {sit}')

print()
print('=== EMAILS COM FORMATO INVALIDO ===')
invalidos_encontrados = 0
for c in contatos:
    e = c.get('email', '')
    if e and not val_email(e):
        invalidos_encontrados += 1
        print(f'  Pedido {c["numero"]}: "{e}"')
if not invalidos_encontrados:
    print('  Nenhum email invalido encontrado')

print()
print('=== ARQUIVOS ESSENCIAIS ===')
for f in ['tokens.json', '.env', 'contatos_rastreamento.json', 'whatsapp_service.py', 'vendedor_service.py']:
    exists = os.path.exists(f)
    size = os.path.getsize(f) if exists else 0
    print(f'  {"OK" if exists else "FALTA"} {f} ({size} bytes)')

# Verificar se .env tem as credenciais
from dotenv import load_dotenv
load_dotenv()
print()
print('=== CREDENCIAIS .ENV ===')
eu = os.getenv('EMAIL_USUARIO', '')
es = os.getenv('EMAIL_SENHA', '')
smtp = os.getenv('EMAIL_SMTP', '')
porta = os.getenv('EMAIL_PORTA', '')
print(f'  EMAIL_USUARIO: {"OK (" + eu + ")" if eu else "FALTA"}')
print(f'  EMAIL_SENHA: {"OK (****)" if es else "FALTA"}')
print(f'  EMAIL_SMTP: {"OK (" + smtp + ")" if smtp else "FALTA"}')
print(f'  EMAIL_PORTA: {"OK (" + porta + ")" if porta else "FALTA"}')
print(f'  EMAIL_USUARIO valido: {val_email(eu)}')

# Verificar token Bling
print()
print('=== TOKEN BLING ===')
try:
    with open('tokens.json', 'r') as f:
        tk = json.load(f)
    at = tk.get('access_token', '')
    print(f'  access_token: {"OK (" + at[:20] + "...)" if at else "VAZIO"}')
    print(f'  Tamanho token: {len(at)} chars')
except Exception as ex:
    print(f'  ERRO: {ex}')

# BUG: logger usado antes de ser definido
print()
print('=== BUGS DETECTADOS ===')
with open('automatico_producao.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    
# Checar se logger e usado antes da definicao
logger_definido = False
for i, line in enumerate(lines, 1):
    if 'logger = logging.getLogger' in line:
        logger_definido = True
    if not logger_definido and 'logger.' in line and 'import logging' not in line:
        print(f'  BUG LINHA {i}: logger usado ANTES de ser definido: {line.strip()[:80]}')
        break

if logger_definido:
    # Confirmar se nao ha uso antes
    first_use = None
    first_def = None
    for i, line in enumerate(lines, 1):
        if 'logger = logging.getLogger' in line and not first_def:
            first_def = i
        if 'logger.' in line and 'import logging' not in line and not first_use:
            first_use = i
    if first_use and first_def and first_use < first_def:
        print(f'  BUG CRITICO: logger usado na linha {first_use} mas definido na linha {first_def}')
    else:
        print(f'  OK: logger definido (linha {first_def}) antes do primeiro uso (linha {first_use})')
