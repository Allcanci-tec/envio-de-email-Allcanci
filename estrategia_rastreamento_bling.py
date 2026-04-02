import json
import os
from dotenv import load_dotenv
import requests
from datetime import datetime

load_dotenv()

# Carregar tokens
with open('tokens.json', 'r') as f:
    tokens = json.load(f)
    
ACCESS_TOKEN = tokens['access_token']
headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

def monitorar_rastreamento():
    """
    Estratégia Vencedora:
    1. Carrega contatos_rastreamento.json com lista de pedidos
    2. Para cada pedido, busca dados de rastreamento no Bling
    3. Extrai: codigo, descricao, situacao, origin, destino, ultimaAlteracao
    4. Compara ultimaAlteracao com última consulta salva
    5. Se for mais recente → envia email com dados atualizados
    """
    
    print("🚀 MONITORANDO RASTREAMENTO - ESTRATÉGIA VENCEDORA\n")
    
    # Carregar contatos
    with open('contatos_rastreamento.json', 'r', encoding='utf-8') as f:
        contatos = json.load(f)
    
    # Carregar histórico de última sincronização (se existir)
    historico_file = 'historico_rastreamento.json'
    if os.path.exists(historico_file):
        with open(historico_file, 'r', encoding='utf-8') as f:
            historico = json.load(f)
    else:
        historico = {}
    
    resultados = []
    
    for contato in contatos[:3]:  # Primeiros 3 para teste
        numero = contato['numero']
        cliente = contato['cliente']
        email = contato['email']
        etiqueta = contato['etiqueta']
        
        print(f"\n📦 Pedido {numero} - {cliente}")
        print(f"   Etiqueta: {etiqueta}")
        
        # Buscar dados do pedido no Bling
        response = requests.get(
            f"https://api.bling.com.br/v3/pedidos/vendas?numero={numero}",
            headers=headers
        )
        
        if response.status_code == 200:
            dados = response.json()
            
            if 'data' in dados and len(dados['data']) > 0:
                pedido = dados['data'][0]
                
                # ✅ AQUI PROCURA O CAMPO RASTREAMENTO
                if 'rastreamento' in pedido:
                    rastreamento = pedido['rastreamento']
                    
                    codigo = rastreamento.get('codigo', etiqueta)
                    descricao = rastreamento.get('descricao', 'N/A')
                    situacao = rastreamento.get('situacao', 0)
                    origem = rastreamento.get('origem', 'N/A')
                    destino = rastreamento.get('destino', 'N/A')
                    ultima_alteracao = rastreamento.get('ultimaAlteracao', '')
                    url = rastreamento.get('url', '')
                    
                    print(f"   ✅ RASTREAMENTO ENCONTRADO!")
                    print(f"   Status: {descricao}")
                    print(f"   Última alteração: {ultima_alteracao}")
                    print(f"   Origem: {origem}")
                    print(f"   Destino: {destino}")
                    
                    # Verificar se é atualização nova
                    chave_historico = f"pedido_{numero}"
                    ultima_consulta = historico.get(chave_historico, {}).get('ultima_alteracao', '')
                    
                    if ultima_alteracao != ultima_consulta:
                        print(f"   🔔 NOVA ATUALIZAÇÃO DETECTADA!")
                        print(f"      Anterior: {ultima_consulta}")
                        print(f"      Atual: {ultima_alteracao}")
                        
                        # Preparar dados para envio de email
                        resultados.append({
                            'numero': numero,
                            'cliente': cliente,
                            'email': email,
                            'etiqueta': etiqueta,
                            'rastreamento': {
                                'codigo': codigo,
                                'descricao': descricao,
                                'situacao': situacao,
                                'origem': origem,
                                'destino': destino,
                                'ultimaAlteracao': ultima_alteracao,
                                'url': url
                            },
                            'deve_enviar_email': True if email else False
                        })
                        
                        # Atualizar histórico
                        historico[chave_historico] = {
                            'ultima_alteracao': ultima_alteracao,
                            'timestamp_consulta': datetime.now().isoformat(),
                            'ultimo_status': descricao
                        }
                    else:
                        print(f"   ℹ️  Sem mudanças desde última consulta")
                else:
                    print(f"   ⚠️  Campo 'rastreamento' não encontrado no pedido")
                    print(f"   Chaves disponíveis: {list(pedido.keys())}")
            else:
                print(f"   ❌ Pedido não encontrado no Bling")
        else:
            print(f"   ❌ Erro ao buscar: {response.status_code}")
    
    # Salvar histórico atualizado
    with open(historico_file, 'w', encoding='utf-8') as f:
        json.dump(historico, f, indent=2, ensure_ascii=False)
    
    # Salvar pedidos com atualizações
    if resultados:
        with open('rastreamentos_com_atualizacoes.json', 'w', encoding='utf-8') as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False)
        
        print(f"\n\n✅ {len(resultados)} RASTREAMENTO(S) COM ATUALIZAÇÃO!")
        print("Dados salvos em: rastreamentos_com_atualizacoes.json")
    else:
        print(f"\n\n✅ Monitoramento concluído - Nenhuma atualização nova")

if __name__ == "__main__":
    monitorar_rastreamento()
