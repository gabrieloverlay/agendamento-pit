from datetime import date, timedelta
import pytest
from app import create_app

FUTURO = (date.today() + timedelta(days=7)).isoformat()


@pytest.fixture
def c():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", "SEED": False})
    with app.test_client() as cliente:
        yield cliente


def base(c):
    cli = c.post("/api/clientes", json={"nome": "Maria", "telefone": "(11) 91234-5678"}).get_json()
    ser = c.post("/api/servicos", json={"nome": "Consulta", "duracao": 30}).get_json()
    pro = c.post("/api/profissionais", json={"nome": "Ana"}).get_json()
    return {"cliente_id": cli["id"], "servico_id": ser["id"], "profissional_id": pro["id"], "data": FUTURO, "hora": "09:00"}


def test_cria_cliente(c):
    r = c.post("/api/clientes", json={"nome": "Maria", "telefone": "(11) 91234-5678"})
    assert r.status_code == 201 and r.get_json()["nome"] == "Maria"


def test_rejeita_telefone_curto(c):
    r = c.post("/api/clientes", json={"nome": "Maria", "telefone": "123"})
    assert r.status_code == 400 and "telefone" in r.get_json()["erro"].lower()


def test_rejeita_telefone_duplicado(c):
    c.post("/api/clientes", json={"nome": "Maria", "telefone": "(11) 91234-5678"})
    r = c.post("/api/clientes", json={"nome": "Outra", "telefone": "(11) 91234-5678"})
    assert r.status_code == 400


def test_rejeita_duracao_invalida(c):
    r = c.post("/api/servicos", json={"nome": "X", "duracao": 2})
    assert r.status_code == 400


def test_agenda_e_bloqueia_conflito(c):
    ag = base(c)
    assert c.post("/api/agendamentos", json=ag).status_code == 201
    r = c.post("/api/agendamentos", json=ag)
    assert r.status_code == 400 and "ocupado" in r.get_json()["erro"]


def test_rejeita_data_passada(c):
    ag = base(c)
    ag["data"] = (date.today() - timedelta(days=1)).isoformat()
    assert c.post("/api/agendamentos", json=ag).status_code == 400


def test_rejeita_hora_fora_da_grade(c):
    ag = base(c)
    ag["hora"] = "03:00"
    assert c.post("/api/agendamentos", json=ag).status_code == 400


def test_horarios_marcam_ocupado_e_cancelar_libera(c):
    ag = base(c)
    id_ag = c.post("/api/agendamentos", json=ag).get_json()["id"]
    url = f"/api/horarios?data={FUTURO}&profissional_id={ag['profissional_id']}"
    nove = [h for h in c.get(url).get_json() if h["hora"] == "09:00"][0]
    assert nove["livre"] is False
    assert c.delete(f"/api/agendamentos/{id_ag}").status_code == 200
    nove = [h for h in c.get(url).get_json() if h["hora"] == "09:00"][0]
    assert nove["livre"] is True


def test_cancelar_inexistente_retorna_404(c):
    assert c.delete("/api/agendamentos/999").status_code == 404


def test_agenda_do_dia_lista_agendamentos(c):
    c.post("/api/agendamentos", json=base(c))
    r = c.get(f"/api/agenda?data={FUTURO}")
    dados = r.get_json()
    assert r.status_code == 200
    assert dados["horarios"][0] == "09:00"
    assert len(dados["profissionais"]) == 1
    assert dados["agendamentos"][0]["cliente"] == "Maria"


def test_agenda_do_dia_sem_agendamentos(c):
    base(c)
    assert c.get(f"/api/agenda?data={FUTURO}").get_json()["agendamentos"] == []


def test_agenda_rejeita_data_invalida(c):
    assert c.get("/api/agenda?data=abc").status_code == 400


def test_agendamento_traz_telefone_para_whatsapp(c):
    r = c.post("/api/agendamentos", json=base(c))
    assert r.get_json()["cliente_telefone"] == "(11) 91234-5678"
