import json
import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Carregar tokens
with open('tokens.json', 'r') as f:
    tokens = json.load(f)
    
ACCESS_TOKEN = tokens['access_token']
headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

def obter_rastreamento_bling(volume_id):
    """
    Busca dados de rastreamento sincronizados do Bling
    usando o endpoint: GET /logisticas/objetos/{idObjeto}
    """
    response = requests.get(
        f"https://api.bling.com.br/v3/logisticas/objetos/{volume_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json().get('data', {})
    else:
        return None

def extrair_dados_rastreamento(dados_objeto):
    """
    Extrai campos importantes do objeto de logística
    """
    rastreamento = dados_objeto.get('rastreamento', {})
    
    return {
        'codigo': rastreamento.get('codigo', 'N/A'),
        'descricao': rastreamento.get('descricao', 'N/A'),
        'situacao': rastreamento.get('situacao', 0),
        'origem': rastreamento.get('origem', 'N/A'),
        'destino': rastreamento.get('destino', 'N/A'),
        'ultimaAlteracao': rastreamento.get('ultimaAlteracao', ''),
        'url': rastreamento.get('url', ''),
        'peso': dados_objeto.get('dimensao', {}).get('peso', 'N/A'),
        'dataSaida': dados_objeto.get('dataSaida', ''),
        'prazoEntregaPrevisto': dados_objeto.get('prazoEntregaPrevisto', 0)
    }

def monitorar_rastreamento_bling():
    """
    Estratégia Vencedora:
    1. Carrega contatos_rastreamento.json
    2. Para cada pedido, obtém o idObjeto (volume_id)
    3. Chama GET /logisticas/objetos/{idObjeto}
    4. Extrai dados de rastreamento com ultimaAlteracao
    5. Compara com histórico e envia email se houver atualização
    """
    
    print("🚀 MONITORANDO RASTREAMENTO VIA BLING - ESTRATÉGIA VENCEDORA\n")
    
    # Carregar contatos
    with open('contatos_rastreamento.json', 'r', encoding='utf-8') as f:
        contatos = json.load(f)
    
    # Carregar histórico de última sincronização
    historico_file = 'historico_rastreamento.json'
    if os.path.exists(historico_file):
        with open(historico_file, 'r', encoding='utf-8') as f:
            historico = json.load(f)
    else:
        historico = {}
    
    resultados = []
    
    # Neste exemplo, usamos o volume_id fixo, mas em produção
    # você buscaria de cada pedido
    volume_ids = {
        2363: 16014294940,  # AD287897978BR - CAIXA ESCOLAR PADRE AFONSO DE LEMOS
        2372: 16015289930,  # AD292045598BR - CAIXA ESCOLAR JULIÃO FELIPE SIMÃO
    }
    
    for numero, volume_id in list(volume_ids.items())[:2]:  # Primeiros 2 para teste
        
        # Encontrar contato correspondente
        contato = next((c for c in contatos if c['numero'] == numero), None)
        if not contato:
            print(f"⚠️  Pedido {numero} não encontrado em contatos_rastreamento.json")
            continue
        
        cliente = contato['cliente']
        email = contato['email']
        etiqueta = contato['etiqueta']
        
        print(f"\n📦 Pedido {numero} - {cliente}")
        print(f"   Etiqueta: {etiqueta}")
        print(f"   Volume ID: {volume_id}")
        
        # 🎯 CHAMADA AO ENDPOINT CORRETO
        dados_objeto = obter_rastreamento_bling(volume_id)
        
        if dados_objeto:
            rastreamento = extrair_dados_rastreamento(dados_objeto)
            
            print(f"   ✅ RASTREAMENTO SINCRONIZADO DO BLING!")
            print(f"      Código: {rastreamento['codigo']}")
            print(f"      Status: {rastreamento['descricao']}")
            print(f"      Situação: {rastreamento['situacao']}")
            print(f"      Origem: {rastreamento['origem']}")
            print(f"      Destino: {rastreamento['destino']}")
            print(f"      Última Alteração: {rastreamento['ultimaAlteracao']}")
            print(f"      Prazo Entrega: {rastreamento['prazoEntregaPrevisto']} dias")
            print(f"      Data Saída: {rastreamento['dataSaida']}")
            
            # Verificar se é atualização nova
            chave_historico = f"pedido_{numero}"
            ultima_consulta = historico.get(chave_historico, {}).get('ultima_alteracao', '')
            
            if rastreamento['ultimaAlteracao'] != ultima_consulta:
                print(f"\n   🔔 NOVA ATUALIZAÇÃO DETECTADA!")
                print(f"      Anterior: {ultima_consulta}")
                print(f"      Atual: {rastreamento['ultimaAlteracao']}")
                
                # Preparar dados para envio de email
                resultados.append({
                    'numero': numero,
                    'cliente': cliente,
                    'email': email,
                    'etiqueta': etiqueta,
                    'rastreamento': rastreamento,
                    'volume_id': volume_id,
                    'deve_enviar_email': bool(email),
                    'data_processamento': datetime.now().isoformat()
                })
                
                # Atualizar histórico
                historico[chave_historico] = {
                    'ultima_alteracao': rastreamento['ultimaAlteracao'],
                    'timestamp_consulta': datetime.now().isoformat(),
                    'ultimo_status': rastreamento['descricao']
                }
            else:
                print(f"\n   ℹ️  Sem mudanças desde última consulta")
        else:
            print(f"   ❌ Erro ao obter rastreamento do Bling")
    
    # Salvar histórico atualizado
    with open(historico_file, 'w', encoding='utf-8') as f:
        json.dump(historico, f, indent=2, ensure_ascii=False)
    
    # Salvar pedidos com atualizações
    if resultados:
        with open('rastreamentos_atualizados_bling.json', 'w', encoding='utf-8') as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False)
        
        print(f"\n\n✅ {len(resultados)} RASTREAMENTO(S) COM ATUALIZAÇÃO!")
        print("Dados salvos em: rastreamentos_atualizados_bling.json")
        print("\n📧 Próximo passo: Esses dados estão prontos para enviar emails!")
        return resultados
    else:
        print(f"\n\n✅ Monitoramento concluído - Nenhuma atualização nova")
        return []

if __name__ == "__main__":
    resultados = monitorar_rastreamento_bling()
    
    if resultados:
        print("\n\n" + "="*70)
        print("DADOS PRONTOS PARA ENVIAR EMAIL:")
        print("="*70)
        for r in resultados:
            print(f"\nPedido: {r['numero']}")
            print(f"Cliente: {r['cliente']}")
            print(f"Email: {r['email']}")
            print(f"Status: {r['rastreamento']['descricao']}")
            print(f"Última Alteração: {r['rastreamento']['ultimaAlteracao']}")
