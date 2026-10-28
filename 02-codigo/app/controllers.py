"""CONTROLLER: recebe as requisições, chama o Model e devolve JSON para a View."""
from datetime import date
from flask import Blueprint, jsonify, render_template, request
from sqlalchemy.exc import IntegrityError
from .models import db, Cliente, Servico, Profissional, Agendamento, HORARIOS

bp = Blueprint("main", __name__)


@bp.get("/")
def index():
    return render_template("index.html")


def _listar(modelo):
    return jsonify([x.to_dict() for x in modelo.query.order_by(modelo.id)])


def _criar(modelo):
    obj = modelo.criar(request.get_json(silent=True) or {})
    db.session.add(obj)
    db.session.commit()
    return jsonify(obj.to_dict()), 201


for rota, modelo in (("clientes", Cliente), ("servicos", Servico),
                     ("profissionais", Profissional), ("agendamentos", Agendamento)):
    bp.add_url_rule(f"/api/{rota}", f"listar_{rota}", lambda m=modelo: _listar(m), methods=["GET"])
    bp.add_url_rule(f"/api/{rota}", f"criar_{rota}", lambda m=modelo: _criar(m), methods=["POST"])


@bp.delete("/api/agendamentos/<int:id>")
def cancelar(id):
    ag = db.session.get(Agendamento, id)
    if ag is None:
        return jsonify({"erro": "Agendamento não encontrado."}), 404
    db.session.delete(ag)
    db.session.commit()
    return jsonify({"ok": True})


@bp.get("/api/horarios")
def horarios():
    try:
        dia = date.fromisoformat(request.args.get("data", ""))
    except ValueError:
        return jsonify({"erro": "Data inválida."}), 400
    prof = request.args.get("profissional_id", type=int)
    ocupados = {a.hora for a in Agendamento.query.filter_by(data=dia, profissional_id=prof)}
    return jsonify([{"hora": h, "livre": h not in ocupados} for h in HORARIOS])


@bp.app_errorhandler(ValueError)
def erro_validacao(e):
    return jsonify({"erro": str(e)}), 400


@bp.app_errorhandler(IntegrityError)
def erro_integridade(e):
    db.session.rollback()
    return jsonify({"erro": "Não foi possível salvar: registro duplicado ou inválido."}), 400
