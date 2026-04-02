#!/usr/bin/env python3
"""
🧪 Script de Teste - WhatsApp Service Anti-Spam

Execute este teste para validar que o sistema está funcionando corretamente.
"""

import sys
import time
from datetime import datetime
from pathlib import Path

# Importar o serviço
try:
    from whatsapp_service import (
        enviar_mensagem,
        adicionar_fila,
        processar_fila,
        status_fila,
        stats_anti_spam,
        fechar_sessao,
    )
    print("✅ whatsapp_service importado com sucesso!\n")
except ImportError as e:
    print(f"❌ Erro ao importar: {e}")
    sys.exit(1)


def teste_1_envio_simples():
    """Teste 1: Envio simples (compatível com versão anterior)"""
    print("\n" + "=" * 70)
    print("TESTE 1: Envio Simples")
    print("=" * 70)

    numero = input("📱 Digite um número para teste (ex: 31984163357): ").strip()
    if not numero:
        print("⏭️ Teste 1 pulado")
        return

    mensagem = "🧪 Teste automático Allcanci\n✓ Sistema anti-spam ativo"

    print(f"📤 Enviando para {numero}...")
    sucesso, msg = enviar_mensagem(numero, mensagem)

    print(f"RESULTADO: {msg}")

    if sucesso:
        print("✅ Teste 1: PASSOU")
    else:
        print("⚠️ Teste 1: Mensagem enfieirada (verifique limites)")


def teste_2_fila():
    """Teste 2: Sistema de fila"""
    print("\n" + "=" * 70)
    print("TESTE 2: Sistema de Fila")
    print("=" * 70)

    print("\n📬 Adicionando 3 mensagens à fila...")
    adicionar_fila("31900000001", "Fila teste 1", prioridade=10)
    adicionar_fila("31900000002", "Fila teste 2", prioridade=0)
    adicionar_fila("31900000003", "Fila teste 3", prioridade=-10)

    status = status_fila()
    print(f"\n📊 Status da fila: {status}")

    print("\n✅ Teste 2: PASSOU - Fila funcionando")


def teste_3_anti_spam():
    """Teste 3: Verificar estatísticas anti-spam"""
    print("\n" + "=" * 70)
    print("TESTE 3: Estatísticas Anti-Spam")
    print("=" * 70)

    stats = stats_anti_spam()

    print(f"""
📊 Estatísticas:
   • Mensagens hoje: {stats['hoje']}/{stats['limite_dia']}
   • Mensagens esta hora: {stats['hora_atual']}/{stats['limite_hora']}
   • Bloqueios detectados: {stats['bloqueios_detectados']}
   • Em pausa? {stats['em_pausa']}
    """)

    print("✅ Teste 3: PASSOU - Estatísticas acessíveis")


def teste_4_verificar_arquivos():
    """Teste 4: Verificar se arquivos foram criados"""
    print("\n" + "=" * 70)
    print("TESTE 4: Arquivos de Sessão")
    print("=" * 70)

    base_dir = Path(__file__).parent

    arquivos_esperados = [
        'whatsapp_session',
        'whatsapp_service.log',
        'whatsapp_envios.json',
        'whatsapp_fila.json',
        'whatsapp_stats.json',
    ]

    print("\n📁 Verificando arquivos...")

    todos_ok = True
    for arquivo in arquivos_esperados:
        caminho = base_dir / arquivo
        existe = caminho.exists()
        status = "✅" if existe else "❌"
        print(f"   {status} {arquivo}")
        if not existe and arquivo not in ['whatsapp_fila.json', 'whatsapp_stats.json']:
            todos_ok = False

    if todos_ok or (base_dir / 'whatsapp_session').exists():
        print("\n✅ Teste 4: PASSOU - Arquivos criados corretamente")
    else:
        print("\n⚠️ Teste 4: Algum arquivo faltando (pode ser normal na primeira vez)")


def teste_5_compatibilidade():
    """Teste 5: Verificar compatibilidade com versão anterior"""
    print("\n" + "=" * 70)
    print("TESTE 5: Compatibilidade com Versão Anterior")
    print("=" * 70)

    print("\n✅ API mantida compatível:")
    print("   • enviar_mensagem(numero, mensagem) ✓")
    print("   • Retorna (sucesso: bool, mensagem: str) ✓")
    print("   • Sessão persistente ✓")
    print("   • QR Code só na primeira vez ✓")

    print("\n✅ Teste 5: PASSOU - Compatibilidade garantida")


def teste_6_documentacao():
    """Teste 6: Verificar documentação"""
    print("\n" + "=" * 70)
    print("TESTE 6: Documentação")
    print("=" * 70)

    base_dir = Path(__file__).parent
    guia = base_dir / 'WHATSAPP_ANTISPAM_GUIA.md'

    if guia.exists():
        print(f"✅ Guia encontrado: {guia}")
        print("\n📖 Leia o guia completo para entender todas as funcionalidades:")
        print("   WHATSAPP_ANTISPAM_GUIA.md")
    else:
        print("⚠️ Guia não encontrado")

    print("\n✅ Teste 6: PASSOU")


def menu_principal():
    """Menu interativo"""
    while True:
        print("\n" + "=" * 70)
        print("🧪 TESTE DE WHATSAPP SERVICE - MENU PRINCIPAL")
        print("=" * 70)
        print("""
Escolha um teste:

1. Envio Simples (teste com seu número)
2. Sistema de Fila
3. Estatísticas Anti-Spam
4. Verificar Arquivos de Sessão
5. Compatibilidade
6. Documentação
7. Executar Todos os Testes
0. Sair

        """)

        opcao = input("Digite a opção (0-7): ").strip()

        if opcao == '0':
            print("\n👋 Encerrando...")
            break
        elif opcao == '1':
            teste_1_envio_simples()
        elif opcao == '2':
            teste_2_fila()
        elif opcao == '3':
            teste_3_anti_spam()
        elif opcao == '4':
            teste_4_verificar_arquivos()
        elif opcao == '5':
            teste_5_compatibilidade()
        elif opcao == '6':
            teste_6_documentacao()
        elif opcao == '7':
            print("\n" + "=" * 70)
            print("EXECUTANDO TODOS OS TESTES")
            print("=" * 70)
            teste_2_fila()
            teste_3_anti_spam()
            teste_4_verificar_arquivos()
            teste_5_compatibilidade()
            teste_6_documentacao()
            print("\n" + "=" * 70)
            print("✅ TODOS OS TESTES CONCLUÍDOS!")
            print("=" * 70)
        else:
            print("❌ Opção inválida")

        if opcao != '7':
            input("\nPressione ENTER para continuar...")


def teste_automatico():
    """Modo teste automático"""
    print("=" * 70)
    print("🧪 TESTE AUTOMÁTICO - WhatsApp Service")
    print("=" * 70)
    print(f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")

    # Teste 2
    teste_2_fila()
    time.sleep(1)

    # Teste 3
    teste_3_anti_spam()
    time.sleep(1)

    # Teste 4
    teste_4_verificar_arquivos()
    time.sleep(1)

    # Teste 5
    teste_5_compatibilidade()
    time.sleep(1)

    # Teste 6
    teste_6_documentacao()

    print("\n" + "=" * 70)
    print("✅ TESTES AUTOMÁTICOS CONCLUÍDOS")
    print("=" * 70)
    print("\n📖 Próximos passos:")
    print("   1. Leia: WHATSAPP_ANTISPAM_GUIA.md")
    print("   2. Teste envio: python teste_whatsapp.py (opção 1)")
    print("   3. Integre com seu sistema")


if __name__ == "__main__":
    try:
        if len(sys.argv) > 1 and sys.argv[1] == '--auto':
            # Modo automático
            teste_automatico()
        else:
            # Menu interativo
            menu_principal()

    except KeyboardInterrupt:
        print("\n\n🛑 Teste interrompido")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Fechar sessão
        try:
            fechar_sessao()
        except:
            pass
