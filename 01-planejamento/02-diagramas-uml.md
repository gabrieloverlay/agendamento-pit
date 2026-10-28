# Diagramas UML

Os diagramas usam Mermaid e aparecem desenhados direto no GitHub.

## Diagrama de classes
```mermaid
classDiagram
    class Cliente {
        +int id
        +string nome
        +string telefone
        +string email
        +criar(dados)
    }
    class Servico {
        +int id
        +string nome
        +string descricao
        +int duracao
        +criar(dados)
    }
    class Profissional {
        +int id
        +string nome
        +string contato
        +criar(dados)
    }
    class Agendamento {
        +int id
        +date data
        +string hora
        +criar(dados)
    }
    Cliente "1" --> "0..*" Agendamento : realiza
    Servico "1" --> "0..*" Agendamento : é contratado em
    Profissional "1" --> "0..*" Agendamento : atende
```

## Casos de uso
O Mermaid não tem diagrama de casos de uso nativo, então foi desenhado como fluxo com o ator à esquerda.
```mermaid
flowchart LR
    A([Atendente])
    A --> UC1(Cadastrar cliente)
    A --> UC2(Cadastrar serviço)
    A --> UC3(Cadastrar profissional)
    A --> UC4(Agendar horário)
    A --> UC5(Cancelar agendamento)
    A --> UC6(Ver resumo e lista de agendamentos)
    UC4 -. inclui .-> UC7(Consultar horários livres)
```

## Diagrama de sequência: agendar horário
```mermaid
sequenceDiagram
    actor U as Atendente
    participant V as View (HTML e JS)
    participant C as Controller (Flask)
    participant M as Model (SQLAlchemy)
    participant B as Banco de dados
    U->>V: escolhe cliente, serviço, profissional e dia
    V->>C: GET /api/horarios
    C->>M: busca agendamentos do dia
    M->>B: SELECT
    B-->>M: horários ocupados
    C-->>V: lista de horários livres
    U->>V: escolhe horário e confirma
    V->>C: POST /api/agendamentos
    C->>M: Agendamento.criar(dados)
    M->>M: valida dados e conflito
    M->>B: INSERT
    B-->>C: confirmação
    C-->>V: 201 Created
    V-->>U: "Agendamento confirmado."
```

## Diagrama de atividades: agendar horário
```mermaid
flowchart TD
    I([Início]) --> A[Escolher cliente, serviço, profissional e dia]
    A --> B[Sistema mostra horários livres]
    B --> C[Escolher um horário]
    C --> D{Todos os campos preenchidos?}
    D -- Não --> E[Exibir erro e voltar] --> A
    D -- Sim --> F{Data não passou e horário livre?}
    F -- Não --> G[Exibir erro e voltar] --> A
    F -- Sim --> H[Salvar no banco]
    H --> J[Exibir Agendamento confirmado]
    J --> Z([Fim])
```
