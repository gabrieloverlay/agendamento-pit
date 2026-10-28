# Dicionário de dados

## clientes
| Campo | Tipo | Nulo | Chave | Descrição / regra |
|---|---|---|---|---|
| id | inteiro | Não | PK | Identificador gerado automaticamente |
| nome | VARCHAR(100) | Não | | Nome completo do cliente |
| telefone | VARCHAR(20) | Não | Única | Telefone com DDD, no mínimo 10 dígitos (RN01) |
| email | VARCHAR(120) | Sim | | E-mail opcional, validado pelo formato |

## servicos
| Campo | Tipo | Nulo | Chave | Descrição / regra |
|---|---|---|---|---|
| id | inteiro | Não | PK | Identificador |
| nome | VARCHAR(100) | Não | | Nome do serviço |
| descricao | VARCHAR(200) | Sim | | Descrição breve |
| duracao | inteiro | Não | | Minutos, mínimo 5 (RN02, validado na aplicação) |

## profissionais
| Campo | Tipo | Nulo | Chave | Descrição / regra |
|---|---|---|---|---|
| id | inteiro | Não | PK | Identificador |
| nome | VARCHAR(100) | Não | | Nome do profissional |
| contato | VARCHAR(120) | Sim | | Telefone ou e-mail |

## agendamentos
| Campo | Tipo | Nulo | Chave | Descrição / regra |
|---|---|---|---|---|
| id | inteiro | Não | PK | Identificador |
| cliente_id | inteiro | Não | FK clientes | Cliente atendido |
| servico_id | inteiro | Não | FK servicos | Serviço contratado |
| profissional_id | inteiro | Não | FK profissionais | Quem atende |
| data | DATE | Não | | Não pode ser anterior a hoje |
| hora | VARCHAR(5) | Não | | Um dos horários da grade (RN03), formato HH:MM |

**Restrição:** (profissional_id, data, hora) é única, então o mesmo profissional não tem dois agendamentos no mesmo horário.
