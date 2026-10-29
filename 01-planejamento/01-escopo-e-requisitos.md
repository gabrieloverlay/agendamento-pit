# Escopo e requisitos

## Escopo
Sistema web de agendamento para pequenos negócios e consultórios. Permite cadastrar clientes, serviços e
profissionais e marcar horários sem conflito para cada profissional.

**Fora do escopo desta versão:** login de usuários, envio de notificações, pagamento e uso da duração do
serviço para bloquear horários consecutivos.

## Requisitos funcionais
| Código | Requisito |
|---|---|
| RF01 | Cadastrar cliente (nome, telefone com DDD, e-mail opcional) |
| RF02 | Cadastrar serviço (nome, descrição opcional, duração em minutos) |
| RF03 | Cadastrar profissional (nome, contato opcional) |
| RF04 | Consultar os horários livres de um profissional em um dia |
| RF05 | Agendar cliente, serviço, profissional, dia e horário |
| RF06 | Cancelar agendamento, com confirmação |
| RF07 | Exibir resumo com a quantidade de clientes, serviços, profissionais e agendamentos |
| RF08 | Exibir a agenda do dia em grade, com horários nas linhas e profissionais nas colunas |
| RF09 | Abrir o WhatsApp do cliente com a mensagem de confirmação do agendamento pronta |

## Requisitos não funcionais
| Código | Requisito |
|---|---|
| RNF01 | Um profissional não pode ter dois agendamentos no mesmo dia e horário (regra na aplicação e no banco) |
| RNF02 | Não permitir agendamento em data passada nem telefone duplicado |
| RNF03 | Mensagem clara de sucesso ou erro após cada ação |
| RNF04 | Interface responsiva, com tema claro e escuro |
| RNF05 | Dados em banco relacional (PostgreSQL em produção) |
| RNF06 | Back-end em Python no padrão MVC, com testes automatizados |

## Regras de negócio
- RN01: telefone com pelo menos 10 dígitos (DDD + número) e único por cliente.
- RN02: duração mínima do serviço de 5 minutos.
- RN03: horários disponíveis: 09:00, 10:00, 11:00, 13:00, 14:00, 15:00, 16:00 e 17:00.
