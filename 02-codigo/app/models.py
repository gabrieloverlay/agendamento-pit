"""MODEL: entidades, regras de validação e acesso ao banco."""
import re
from datetime import date
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
HORARIOS = ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00"]


def _texto(dados, campo, rotulo, obrigatorio=True, maximo=100):
    valor = str(dados.get(campo) or "").strip()
    if obrigatorio and not valor:
        raise ValueError(f"Informe {rotulo}.")
    if len(valor) > maximo:
        raise ValueError(f"{rotulo.capitalize()} excede {maximo} caracteres.")
    return valor


def _buscar(modelo, valor, rotulo):
    try:
        obj = db.session.get(modelo, int(valor))
    except (TypeError, ValueError):
        obj = None
    if obj is None:
        raise ValueError(f"Selecione {rotulo} válido.")
    return obj


class Cliente(db.Model):
    __tablename__ = "clientes"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(120))

    @classmethod
    def criar(cls, dados):
        nome = _texto(dados, "nome", "o nome do cliente")
        telefone = _texto(dados, "telefone", "o telefone", maximo=20)
        if len(re.sub(r"\D", "", telefone)) < 10:
            raise ValueError("Informe um telefone com DDD.")
        email = _texto(dados, "email", "o e-mail", obrigatorio=False, maximo=120)
        if email and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            raise ValueError("E-mail inválido.")
        if cls.query.filter_by(telefone=telefone).first():
            raise ValueError("Já existe um cliente com esse telefone.")
        return cls(nome=nome, telefone=telefone, email=email)

    def to_dict(self):
        return {"id": self.id, "nome": self.nome, "telefone": self.telefone, "email": self.email}


class Servico(db.Model):
    __tablename__ = "servicos"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(200))
    duracao = db.Column(db.Integer, nullable=False)

    @classmethod
    def criar(cls, dados):
        nome = _texto(dados, "nome", "o nome do serviço")
        try:
            duracao = int(dados.get("duracao"))
        except (TypeError, ValueError):
            raise ValueError("Informe uma duração válida.")
        if duracao < 5:
            raise ValueError("A duração mínima é 5 minutos.")
        descricao = _texto(dados, "descricao", "a descrição", obrigatorio=False, maximo=200)
        return cls(nome=nome, descricao=descricao, duracao=duracao)

    def to_dict(self):
        return {"id": self.id, "nome": self.nome, "descricao": self.descricao, "duracao": self.duracao}


class Profissional(db.Model):
    __tablename__ = "profissionais"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    contato = db.Column(db.String(120))

    @classmethod
    def criar(cls, dados):
        nome = _texto(dados, "nome", "o nome do profissional")
        contato = _texto(dados, "contato", "o contato", obrigatorio=False, maximo=120)
        return cls(nome=nome, contato=contato)

    def to_dict(self):
        return {"id": self.id, "nome": self.nome, "contato": self.contato}


class Agendamento(db.Model):
    __tablename__ = "agendamentos"
    # Regra no banco: um profissional não pode ter dois agendamentos no mesmo dia e hora.
    __table_args__ = (db.UniqueConstraint("profissional_id", "data", "hora", name="uq_horario_profissional"),)
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=False)
    servico_id = db.Column(db.Integer, db.ForeignKey("servicos.id"), nullable=False)
    profissional_id = db.Column(db.Integer, db.ForeignKey("profissionais.id"), nullable=False)
    data = db.Column(db.Date, nullable=False)
    hora = db.Column(db.String(5), nullable=False)
    cliente = db.relationship("Cliente")
    servico = db.relationship("Servico")
    profissional = db.relationship("Profissional")

    @classmethod
    def criar(cls, dados):
        cliente = _buscar(Cliente, dados.get("cliente_id"), "um cliente")
        servico = _buscar(Servico, dados.get("servico_id"), "um serviço")
        prof = _buscar(Profissional, dados.get("profissional_id"), "um profissional")
        try:
            dia = date.fromisoformat(str(dados.get("data")))
        except ValueError:
            raise ValueError("Escolha uma data válida.")
        if dia < date.today():
            raise ValueError("Não é possível agendar em uma data que já passou.")
        hora = str(dados.get("hora"))
        if hora not in HORARIOS:
            raise ValueError("Escolha um horário válido.")
        if cls.query.filter_by(profissional_id=prof.id, data=dia, hora=hora).first():
            raise ValueError("Esse horário já está ocupado para o profissional.")
        return cls(cliente=cliente, servico=servico, profissional=prof, data=dia, hora=hora)

    def to_dict(self):
        return {
            "id": self.id, "data": self.data.isoformat(), "hora": self.hora,
            "cliente_id": self.cliente_id, "servico_id": self.servico_id,
            "profissional_id": self.profissional_id,
            "cliente": self.cliente.nome, "cliente_telefone": self.cliente.telefone,
            "servico": self.servico.nome,
            "profissional": self.profissional.nome,
        }
