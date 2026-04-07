import json
with open('contatos_rastreamento.json','r',encoding='utf-8') as f:
    d = json.load(f)
com_data = [c for c in d if c.get('data_inclusao')]
sem_data = [c for c in d if not c.get('data_inclusao')]
print(f'Total: {len(d)}')
print(f'Com data_inclusao: {len(com_data)}')
print(f'Sem data_inclusao: {len(sem_data)}')
if com_data:
    datas = set(c['data_inclusao'] for c in com_data)
    print(f'Datas: {datas}')
    for dt in sorted(datas):
        qtd = len([c for c in com_data if c['data_inclusao'] == dt])
        print(f'  {dt}: {qtd} pedidos')
