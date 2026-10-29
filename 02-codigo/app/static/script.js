/* VIEW (front-end): desenha a tela e conversa com a API do Controller */
const $ = (id) => document.getElementById(id);
let dados = { clientes: [], servicos: [], profissionais: [], agendamentos: [] };
let horaEscolhida = null;
let timerAviso;

async function api(url, metodo = "GET", corpo){
  const r = await fetch(url, {
    method: metodo,
    headers: { "Content-Type": "application/json" },
    body: corpo ? JSON.stringify(corpo) : undefined
  });
  const json = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(json.erro || "Erro inesperado. Tente novamente.");
  return json;
}
function aviso(texto, erro){
  const a = $("aviso");
  a.textContent = texto;
  a.className = "aviso mostrar" + (erro ? " erro" : "");
  clearTimeout(timerAviso);
  timerAviso = setTimeout(() => { a.className = "aviso"; }, 4000);
}
const fmt = (iso) => iso.split("-").reverse().join("/");

function preencher(select, itens, vazio){
  const atual = select.value;
  select.innerHTML = "";
  select.disabled = !itens.length;
  if (!itens.length){
    select.appendChild(new Option(vazio, ""));
    return;
  }
  itens.forEach(i => select.appendChild(new Option(i.nome, i.id)));
  if (itens.some(i => String(i.id) === atual)) select.value = atual;
}
async function desenharHorarios(){
  const box = $("slots");
  const dia = $("a-data").value, prof = $("a-prof").value;
  if (!dia || !prof){ box.replaceChildren(); return; }
  try {
    const lista = await api("/api/horarios?data=" + dia + "&profissional_id=" + prof);
    const botoes = [];
    lista.forEach(h => {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "slot";
      b.textContent = h.hora;
      b.disabled = !h.livre;
      b.setAttribute("aria-pressed", String(h.hora === horaEscolhida));
      b.onclick = () => { horaEscolhida = h.hora; desenharHorarios(); };
      botoes.push(b);
    });
    box.replaceChildren(...botoes);
  } catch (e) { aviso(e.message, true); }
}
function desenharLista(){
  const ul = $("lista");
  ul.innerHTML = "";
  if (!dados.agendamentos.length){
    ul.innerHTML = '<li class="vazio">Nenhum agendamento ainda.</li>';
    return;
  }
  [...dados.agendamentos].sort((x, y) => (x.data + x.hora).localeCompare(y.data + y.hora)).forEach(a => {
    const li = document.createElement("li");
    const info = document.createElement("div");
    const q = document.createElement("div");
    q.className = "quando";
    q.textContent = fmt(a.data) + " às " + a.hora;
    const d = document.createElement("div");
    d.className = "det";
    d.textContent = a.cliente + " · " + a.servico + " · com " + a.profissional;
    info.append(q, d);
    const c = document.createElement("button");
    c.className = "cancel";
    c.textContent = "Cancelar";
    c.onclick = async () => {
      if (!confirm("Cancelar este agendamento?")) return;
      try { await api("/api/agendamentos/" + a.id, "DELETE"); await carregar(); aviso("Agendamento cancelado."); }
      catch (e) { aviso(e.message, true); }
    };
    const w = document.createElement("a");
    w.className = "wpp";
    w.textContent = "WhatsApp";
    w.target = "_blank";
    w.rel = "noopener";
    w.href = linkWhatsApp(a);
    const acoes = document.createElement("div");
    acoes.className = "acoes";
    acoes.append(w, c);
    li.append(info, acoes);
    ul.appendChild(li);
  });
}
function linkWhatsApp(a){
  const numero = "55" + String(a.cliente_telefone || "").replace(/\D/g, "");
  const msg = "Olá, " + a.cliente + "! Seu agendamento de " + a.servico + " com " + a.profissional +
    " está marcado para " + fmt(a.data) + " às " + a.hora + ".";
  return "https://wa.me/" + numero + "?text=" + encodeURIComponent(msg);
}
async function desenharAgenda(){
  const dia = $("g-data").value;
  const box = $("grade");
  if (!dia){ box.replaceChildren(); return; }
  try {
    const ag = await api("/api/agenda?data=" + dia);
    if (!ag.profissionais.length){ box.textContent = "Cadastre um profissional para ver a agenda."; return; }
    const tabela = document.createElement("table");
    tabela.className = "grade";
    const cab = tabela.createTHead().insertRow();
    cab.appendChild(document.createElement("th")).textContent = "Horário";
    ag.profissionais.forEach(p => { cab.appendChild(document.createElement("th")).textContent = p.nome; });
    const corpo = tabela.createTBody();
    ag.horarios.forEach(h => {
      const linha = corpo.insertRow();
      linha.insertCell().textContent = h;
      ag.profissionais.forEach(p => {
        const cel = linha.insertCell();
        const item = ag.agendamentos.find(x => x.profissional_id === p.id && x.hora === h);
        cel.className = item ? "ocupado" : "livre";
        cel.textContent = item ? item.cliente + " · " + item.servico : "livre";
      });
    });
    box.replaceChildren(tabela);
  } catch (e) { aviso(e.message, true); }
}
async function carregar(){
  const rotas = ["clientes", "servicos", "profissionais", "agendamentos"];
  const [clientes, servicos, profissionais, agendamentos] = await Promise.all(rotas.map(r => api("/api/" + r)));
  dados = { clientes, servicos, profissionais, agendamentos };
  $("n-clientes").textContent = clientes.length;
  $("n-servicos").textContent = servicos.length;
  $("n-profs").textContent = profissionais.length;
  $("n-agend").textContent = agendamentos.length;
  preencher($("a-cliente"), clientes, "Cadastre um cliente primeiro");
  preencher($("a-servico"), servicos, "Cadastre um serviço primeiro");
  preencher($("a-prof"), profissionais, "Cadastre um profissional primeiro");
  desenharLista();
  await desenharHorarios();
  await desenharAgenda();
}

function enviar(idForm, url, montar, ok, limpar = true){
  $(idForm).addEventListener("submit", async (e) => {
    e.preventDefault();
    try {
      await api(url, "POST", montar());
      if (limpar) e.target.reset(); else horaEscolhida = null;
      await carregar();
      aviso(ok);
    } catch (err) { aviso(err.message, true); }
  });
}
enviar("f-cliente", "/api/clientes", () => ({ nome: $("c-nome").value, telefone: $("c-tel").value, email: $("c-email").value }), "Cliente salvo.");
enviar("f-servico", "/api/servicos", () => ({ nome: $("s-nome").value, descricao: $("s-desc").value, duracao: $("s-dur").value }), "Serviço salvo.");
enviar("f-prof", "/api/profissionais", () => ({ nome: $("p-nome").value, contato: $("p-contato").value }), "Profissional salvo.");
enviar("f-agend", "/api/agendamentos", () => {
  if (!horaEscolhida) throw new Error("Escolha um horário livre.");
  return { cliente_id: $("a-cliente").value, servico_id: $("a-servico").value, profissional_id: $("a-prof").value, data: $("a-data").value, hora: horaEscolhida };
}, "Agendamento confirmado.", false);

$("c-tel").addEventListener("input", (e) => {
  let d = e.target.value.replace(/\D/g, "").slice(0, 11);
  const corte = d.length > 10 ? 7 : 6;
  if (d.length > 6) d = "(" + d.slice(0, 2) + ") " + d.slice(2, corte) + "-" + d.slice(corte);
  else if (d.length > 2) d = "(" + d.slice(0, 2) + ") " + d.slice(2);
  e.target.value = d;
});
["a-data", "a-prof"].forEach(id => $(id).addEventListener("change", () => { horaEscolhida = null; desenharHorarios(); }));

const hoje = new Date();
hoje.setMinutes(hoje.getMinutes() - hoje.getTimezoneOffset());
$("a-data").min = hoje.toISOString().slice(0, 10);
$("a-data").value = $("a-data").min;
$("g-data").value = $("a-data").min;
$("g-data").addEventListener("change", desenharAgenda);

const SECOES = ["cadastros", "agendar", "agenda"];
function mostrarSecao(nome){
  if (!SECOES.includes(nome)) nome = "cadastros";
  SECOES.forEach(s => {
    $("sec-" + s).hidden = s !== nome;
    $("nav-" + s).setAttribute("aria-current", s === nome ? "page" : "false");
  });
  if (location.hash !== "#" + nome) history.replaceState(null, "", "#" + nome);
}
SECOES.forEach(s => $("nav-" + s).addEventListener("click", () => mostrarSecao(s)));
window.addEventListener("hashchange", () => mostrarSecao(location.hash.slice(1)));
mostrarSecao(location.hash.slice(1));
carregar().catch(e => aviso(e.message, true));
