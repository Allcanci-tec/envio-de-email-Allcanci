import json
d = json.load(open('contatos_rastreamento.json','r',encoding='utf-8'))
for c in d[:15]:
    print(f"#{c['numero']} | vendedor_id={c.get('vendedor_id')} | vendedor_nome={c.get('vendedor_nome','')} | vendedor_email={c.get('vendedor_email','')}")
print(f"\nTotal contatos: {len(d)}")
