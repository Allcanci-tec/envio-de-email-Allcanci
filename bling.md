regras de limitação de taxa
As regras de limitação de taxa permitem definir limites de taxa para solicitações que correspondam a uma expressão, bem como a ação a ser executada quando esses limites forem atingidos. Use regras de limitação de taxa para evitar o uso indevido de seus sites e APIs — por exemplo, para proteger um endpoint de login contra ataques de força bruta ou para limitar quantas chamadas de API um único cliente pode fazer em um determinado período.

No novo painel de segurança , as regras de limitação de taxa são um dos tipos de regras de segurança disponíveis . As regras de segurança executam ações relacionadas à segurança em solicitações recebidas que correspondem a filtros especificados.

Alguns clientes corporativos podem criar conjuntos de regras de limitação de taxa no nível da conta, que podem ser implementados em várias zonas corporativas.

Parâmetros da regra
Assim como outras regras avaliadas pelo mecanismo de regras da Cloudflare , as regras de limitação de taxa têm os seguintes parâmetros básicos:

Uma expressão que especifica os critérios que você está usando para corresponder o tráfego na linguagem de Regras .
Uma ação que especifica o que fazer quando a regra é correspondida e quaisquer condições adicionais são atendidas. No caso de regras de limitação de taxa, a ação ocorre quando a taxa atinge o limite especificado.
Além desses dois parâmetros, as regras de limitação de taxa exigem os seguintes parâmetros adicionais:

Características : O conjunto de parâmetros que define como o Cloudflare rastreia a taxa para esta regra.
Período : O período de tempo (em segundos) a ser considerado ao avaliar a taxa.
Requisições por período : O número de requisições durante o período de tempo que acionará a regra de limitação de taxa.
Duração (ou tempo limite de mitigação): Assim que a taxa for atingida, a regra de limitação de taxa bloqueará novas solicitações pelo período de tempo definido neste campo.
Comportamento da ação : Por padrão, o Cloudflare aplicará a ação da regra pela duração configurada (ou tempo limite de mitigação), independentemente da taxa de solicitações durante esse período. Alguns clientes Enterprise podem configurar a regra para limitar as solicitações acima da taxa máxima, permitindo solicitações de entrada quando a taxa for inferior ao limite configurado.
Consulte a seção Parâmetros de limitação de taxa para obter mais informações sobre parâmetros obrigatórios e opcionais.

Consulte a seção Como a Cloudflare determina a taxa de solicitações para saber como a Cloudflare usa os parâmetros acima ao determinar a taxa de solicitações recebidas.

Interação com outros recursos de segurança do aplicativo
Se você utiliza diversos recursos de segurança de aplicativos, como regras personalizadas, regras gerenciadas e o Modo de Combate a Super Bots, é importante entender como esses recursos interagem e a ordem em que são executados. Consulte a seção Interoperabilidade de recursos de segurança para obter mais informações.

Observações importantes
As regras de limitação de taxa são avaliadas em ordem, e algumas ações, como Bloquear , interrompem a avaliação de outras regras. Para obter mais detalhes sobre as ações e seu comportamento, consulte Ações .

As regras de limitação de taxa não são projetadas para permitir que um número preciso de solicitações chegue ao seu servidor de origem. Pode haver um atraso de até alguns segundos entre a detecção de uma solicitação e a atualização dos contadores de taxa. Devido a esse atraso, solicitações em excesso ainda podem chegar à origem antes que a Cloudflare aplique uma ação de mitigação, como bloqueio ou contestação. Para obter mais informações sobre como os contadores funcionam, incluindo seu escopo por data center, consulte Cálculo da taxa de solicitações .

Aplicar regras de limitação de taxa a bots verificados pode afetar a otimização para mecanismos de busca (SEO). Para mais informações, consulte Melhorar o SEO .

Disponibilidade
Recurso	Livre	Pró	Negócios	Empresa com segurança de aplicativos	Empresa com Limitação de Taxa Avançada
Campos disponíveis
na expressão da regra	Caminho, Bot Verificado	Host, URI, Caminho, URI completo, Consulta, Bot verificado	Host, URI, Caminho, URI completo, Consulta, Método, IP de origem, Agente do usuário, Bot verificado	Campos gerais de solicitação, campos de cabeçalho de solicitação, Bot verificado, campos de gerenciamento de bot 1	Campos gerais da solicitação, campos do cabeçalho da solicitação, Bot verificado, campos de gerenciamento de bot 1 , campos do corpo da solicitação 2
Exclusão de cache	Não	Não	Sim	Sim	Sim
Características de contagem	IP	IP	IP, IP com suporte a NAT	IP, IP com suporte a NAT	IP, IP com suporte a NAT, Consulta, Host, Cabeçalhos, Cookie, ASN, País, Caminho, Impressão digital JA3/JA4 1 , Valor do campo JSON 2 , Corpo 2 , Valor de entrada do formulário 2 , Personalizado
Expressão de contagem personalizada	Não	Não	Sim	Sim	Sim
Campos disponíveis
na expressão de contagem	N / D	N / D	Todos os campos de expressão de regra, código de resposta, cabeçalhos de resposta	Todos os campos de expressão de regra, código de resposta, cabeçalhos de resposta	Todos os campos de expressão de regra, código de resposta, cabeçalhos de resposta
Modelo de contagem	Número de solicitações	Número de solicitações	Número de solicitações	Número de solicitações	Número de solicitações, pontuação de complexidade

comportamento de ação limitante de taxa	Executar ações durante o período de mitigação.	Executar ações durante o período de mitigação.	Executar ações durante o período de mitigação.	Executar ação durante o período de mitigação, limitar solicitações acima da taxa com ação de bloqueio.	Executar ação durante o período de mitigação, limitar solicitações acima da taxa com ação de bloqueio.
Contagem de períodos	10 segundos	Todos os valores suportados até 1 min 3	Todos os valores suportados até 10 min 3	Todos os valores suportados até 65.535 s 3	Todos os valores suportados até 65.535 s 3
Períodos de tempo limite de mitigação	10 segundos	Todos os valores suportados até 1 h 3	Todos os valores suportados até 1 dia 3	Todos os valores suportados até 1 dia 3  4	Todos os valores suportados até 1 dia 3  4
Número de regras	1	2	5	100 5	100
Notas de rodapé
1: Disponível apenas para clientes Enterprise que adquiriram o Gerenciamento de Bots .

2: A disponibilidade depende do seu plano WAF.

3: Lista de valores suportados para o período de contagem/mitigação em segundos:
10, 15, 20, 30, 40, 45, 60 (1 min), 90, 120 (2 min), 180 (3 min), 240 (4 min), 300 (5 min), 480, 600 (10 min), 900, 1200 (20 min), 1800, 2400, 3600 (1 h), 65535, 86400 (1 dia).
Nem todos os valores estão disponíveis em todos os planos.

4: Clientes corporativos podem especificar um período de tempo limite de mitigação personalizado por meio da API.

5: Clientes corporativos devem ter segurança de aplicativos em seu contrato para obter acesso às regras de limitação de taxa. O número de regras depende dos termos específicos do contrato.

Observação

Clientes corporativos podem experimentar este produto como um serviço sem contrato , que oferece acesso completo, sem taxas de uso por consumo, limites ou outras restrições.

Próximos passos
Consulte os seguintes recursos:

Crie uma regra de limitação de taxa no painel de controle para uma zona.
Crie uma regra de limitação de taxa via API para uma zona.
Para exemplos de Terraform, consulte Configuração de regras de limitação de taxa usando Terraform .

Recursos relacionados
Centro de Aprendizagem: O que é fator limitante de taxa? ↗

Limitação de taxa do Cloudflare (versão anterior, não disponível) : Documentação da versão anterior das regras de limitação de taxa (cobrança baseada no uso).1. Acesse: https://myaccount.google.com/apppasswords
2. Selecione: Mail + Windows
3. Copie a senha gerada (16 caracteres)
4. No arquivo .env, substitua:
   EMAIL_REMETENTE=professorrennifer10@gmail.com
   EMAIL_USUARIO=professorrennifer10@gmail.com
   EMAIL_SENHA=(cole a senha de 16 caracteres aqui)
   EMAIL_SMTP=smtp.gmail.com
   EMAIL_PORTA=465