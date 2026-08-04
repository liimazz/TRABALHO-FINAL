from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from functools import wraps
import json
import os

app = Flask(__name__)
app.secret_key = "muraltech2026"

ARQUIVO_JSON = "dados/avisos.json"

# Categorias padronizadas
CATEGORIAS = ["Evento", "Prova", "Reunião", "Curso", "Esporte", "Informativo", "Outro"]

# Credenciais do administrador (simples para o projeto)
USUARIO_ADMIN = "admin"
SENHA_ADMIN = "admin123"


# ==========================
# Decorador de Login
# ==========================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario" not in session:
            flash("Você precisa estar logado para acessar esta página.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


# ==========================
# Funções auxiliares
# ==========================

def carregar_avisos():
    if not os.path.exists(ARQUIVO_JSON):
        return []

    with open(ARQUIVO_JSON, "r", encoding="utf-8") as arquivo:
        try:
            return json.load(arquivo)
        except json.JSONDecodeError:
            return []


def salvar_avisos(lista):
    os.makedirs(os.path.dirname(ARQUIVO_JSON), exist_ok=True)
    with open(ARQUIVO_JSON, "w", encoding="utf-8") as arquivo:
        json.dump(lista, arquivo, indent=4, ensure_ascii=False)


def ordenar_avisos(lista):
    """Ordena: fixados primeiro, depois mais recentes"""
    return sorted(lista, key=lambda x: (not x.get("fixado", False), -x.get("id", 0)))


# ==========================
# Login / Logout
# ==========================

@app.route("/login", methods=["GET", "POST"])
def login():
    if "usuario" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        senha = request.form.get("senha", "").strip()

        if usuario == USUARIO_ADMIN and senha == SENHA_ADMIN:
            session["usuario"] = usuario
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("index"))
        else:
            flash("Usuário ou senha incorretos.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("usuario", None)
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("index"))


# ==========================
# Página inicial
# ==========================

@app.route("/")
def index():
    avisos = carregar_avisos()
    categorias = len(set(a["categoria"] for a in avisos)) if avisos else 0

    return render_template(
        "index.html",
        total=len(avisos),
        categorias=categorias
    )


# ==========================
# Lista de avisos
# ==========================

@app.route("/avisos")
def avisos():
    lista = carregar_avisos()
    pesquisa = request.args.get("pesquisa", "").lower().strip()
    categoria_filtro = request.args.get("categoria", "").strip()

    if pesquisa:
        lista = [
            aviso for aviso in lista
            if pesquisa in aviso["titulo"].lower()
            or pesquisa in aviso["categoria"].lower()
            or pesquisa in aviso["descricao"].lower()
        ]

    if categoria_filtro:
        lista = [a for a in lista if a["categoria"].lower() == categoria_filtro.lower()]

    lista = ordenar_avisos(lista)

    return render_template(
        "avisos.html",
        avisos=lista,
        pesquisa=pesquisa,
        categoria_filtro=categoria_filtro,
        categorias=CATEGORIAS
    )


# ==========================
# Novo aviso (protegido)
# ==========================

@app.route("/novo", methods=["GET", "POST"])
@login_required
def novo():
    if request.method == "POST":
        avisos = carregar_avisos()

        novo_id = 1
        if avisos:
            novo_id = max(a["id"] for a in avisos) + 1

        aviso = {
            "id": novo_id,
            "titulo": request.form["titulo"].strip(),
            "categoria": request.form["categoria"],
            "descricao": request.form["descricao"].strip(),
            "data": datetime.now().strftime("%d/%m/%Y às %H:%M"),
            "fixado": "fixado" in request.form
        }

        avisos.append(aviso)
        salvar_avisos(avisos)

        flash("Aviso cadastrado com sucesso!", "success")
        return redirect(url_for("avisos"))

    return render_template("novo.html", categorias=CATEGORIAS)


# ==========================
# Editar aviso (protegido)
# ==========================

@app.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar(id):
    avisos = carregar_avisos()
    aviso = next((a for a in avisos if a["id"] == id), None)

    if not aviso:
        flash("Aviso não encontrado.", "danger")
        return redirect(url_for("avisos"))

    if request.method == "POST":
        aviso["titulo"] = request.form["titulo"].strip()
        aviso["categoria"] = request.form["categoria"]
        aviso["descricao"] = request.form["descricao"].strip()
        aviso["data"] = datetime.now().strftime("%d/%m/%Y às %H:%M") + " (Editado)"
        aviso["fixado"] = "fixado" in request.form

        salvar_avisos(avisos)
        flash("Aviso atualizado com sucesso!", "success")
        return redirect(url_for("avisos"))

    return render_template("editar.html", aviso=aviso, categorias=CATEGORIAS)


# ==========================
# Excluir aviso (protegido)
# ==========================

@app.route("/excluir/<int:id>")
@login_required
def excluir(id):
    avisos = carregar_avisos()
    avisos = [a for a in avisos if a["id"] != id]
    salvar_avisos(avisos)

    flash("Aviso removido com sucesso!", "warning")
    return redirect(url_for("avisos"))


# ==========================
# Sobre
# ==========================

@app.route("/sobre")
def sobre():
    return render_template("sobre.html")


# ==========================
# Inicialização
# ==========================

if __name__ == "__main__":
    app.run(debug=True)