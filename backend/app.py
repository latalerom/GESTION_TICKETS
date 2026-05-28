from flask import Flask, render_template, request, redirect, session
from models import db, Usuario, Ticket
from config import Config

app = Flask(__name__, template_folder="templates")
app.config.from_object(Config)
app.secret_key = "secret123"

db.init_app(app)

# 🔥 AGREGA ESTO (CLAVE)
with app.app_context():
    db.create_all()

# 🏠 HOME
@app.route("/")
def home():
    return render_template("index.html")


#  LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = Usuario.query.filter_by(email=email, password=password).first()

        if user:
            session["user_id"] = user.id
            session["rol"] = user.rol
            return redirect("/dashboard")

    return render_template("login.html")


#  DASHBOARD
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    tickets = Ticket.query.all()
    return render_template("dashboard.html", tickets=tickets)


# CREAR TICKET
@app.route("/crear_ticket", methods=["POST"])
def crear_ticket():
    titulo = request.form["titulo"]
    descripcion = request.form["descripcion"]

    nuevo = Ticket(
        titulo=titulo,
        descripcion=descripcion,
        usuario_id=1  # 🔥 temporal
    )

    db.session.add(nuevo)
    db.session.commit()

    return redirect("/dashboard")


# 🗑 ELIMINAR TICKET
@app.route("/eliminar_ticket/<int:id>")
def eliminar_ticket(id):
    ticket = Ticket.query.get(id)

    if ticket:
        db.session.delete(ticket)
        db.session.commit()

    return redirect("/dashboard?msg=eliminado")

#  CAMBIAR ESTADO
@app.route("/cambiar_estado/<int:id>/<estado>")
def cambiar_estado(id, estado):
    ticket = Ticket.query.get(id)

    if ticket:
        ticket.estado = estado
        db.session.commit()

    return redirect("/dashboard")

#  EDITAR TICKET
@app.route("/editar_ticket/<int:id>", methods=["GET", "POST"])
def editar_ticket(id):
    ticket = Ticket.query.get(id)

    if request.method == "POST":
        ticket.titulo = request.form["titulo"]
        ticket.descripcion = request.form["descripcion"]

        db.session.commit()
        return redirect("/dashboard?msg=editado")

    return render_template("editar.html", ticket=ticket)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)