import os
from flask import Flask
from .models import db, Servico, Profissional


def create_app(config=None):
    app = Flask(__name__)
    # Banco: PostgreSQL em produção (DATABASE_URL); SQLite local para desenvolvimento.
    url = os.environ.get("DATABASE_URL", "sqlite:///agendamento.db")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    app.config.update(SQLALCHEMY_DATABASE_URI=url, SEED=True)
    app.config.update(config or {})
    db.init_app(app)

    from .controllers import bp
    app.register_blueprint(bp)

    with app.app_context():
        db.create_all()
        if app.config["SEED"] and not Servico.query.first():
            db.session.add_all([
                Servico(nome="Consulta", descricao="Atendimento padrão", duracao=30),
                Servico(nome="Retorno", descricao="Revisão de atendimento", duracao=20),
                Servico(nome="Avaliação", descricao="Primeira avaliação", duracao=45),
                Profissional(nome="Ana Souza"),
                Profissional(nome="Carlos Lima"),
                Profissional(nome="Marina Alves"),
            ])
            db.session.commit()
    return app
