# Sistema de Agendamento (PIT - Engenharia de Software II)

Back-end em **Python (Flask)** no padrão **MVC**, banco relacional via SQLAlchemy
(PostgreSQL em produção, SQLite no desenvolvimento) e testes com **pytest**.

## Estrutura
- `01-planejamento/`: UML, telas (IHC), modelo de dados e dicionário de dados
- `02-codigo/app/models.py`: **Model** (entidades, validações, banco)
- `02-codigo/app/controllers.py`: **Controller** (rotas e API JSON)
- `02-codigo/app/templates` e `static/`: **View** (HTML, CSS, JavaScript)
- `03-testes/`: testes automatizados e formulários dos colegas
- `04-entrega/`: laudo de qualidade, PDF dos testes e links dos vídeos

## Como rodar
    pip install -r requirements.txt
    cd 02-codigo && python run.py        # abre em http://127.0.0.1:5000

## Como testar
    pytest                                # na raiz do projeto

## Produção (ex.: Render)
Variável `DATABASE_URL` apontando para o PostgreSQL.
Start: `gunicorn --chdir 02-codigo run:app`
