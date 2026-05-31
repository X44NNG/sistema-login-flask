# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, session
from flask_mail import Mail, Message
import requests
import random
import re

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True

app.config['MAIL_USERNAME'] = 'pythonflask4@gmail.com'
app.config['MAIL_PASSWORD'] = 'ahrl ivki rmtc kfqa'

mail = Mail(app)

app.secret_key = "clave_super_secreta"

SITE_KEY = "6LfkFu8sAAAAABjCVJG9kLychDY4wAqCYlLqdXDV"
SECRET_KEY = "6LfkFu8sAAAAABHKNwkj3_x-sHTTO8EODhgF6eEu"

# Usuarios guardados en memoria
users = {
    "admin": {
        "password": "12345",
        "question": "Color favorito",
        "answer": "azul"
    }
}

# LOGIN
@app.route("/", methods=["GET", "POST"])
def login():


    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        # Google reCAPTCHA
        captcha_response = request.form.get("g-recaptcha-response")

        verify = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={
                "secret": SECRET_KEY,
                "response": captcha_response
            }
        )

        result = verify.json()

        if not result["success"]:

            return render_template(
                "login.html",
                error="Confirma que no eres un robot",
                site_key=SITE_KEY
            )
        
        # Validar usuario
        if username in users and users[username]["password"] == password:

            session["user"] = username
            return redirect("/dashboard")

        else:

            return render_template(
                "login.html",
                error="Usuario o contrasena incorrectos",
                site_key=SITE_KEY
            )

    return render_template(
        "login.html", 
        site_key=SITE_KEY
        )

# REGISTRO
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        question = request.form["question"]
        answer = request.form["answer"]
        

                # Usuario mínimo 4 caracteres
        if len(username) < 4:

            return render_template(
                "register.html",
                error="El usuario debe tener mínimo 4 caracteres"
            )
        

        # Usuario sin espacios
        if " " in username:

            return render_template(
                "register.html",
                error="El usuario no puede tener espacios"
            )

        # Confirmar contraseña
        if password != confirm_password:

            return render_template(
                "register.html",
                error="Las contrasenas no coinciden"
            )

        # Validar contraseña segura
        pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$'

        if not re.match(pattern, password):

            return render_template(
                "register.html",
                error="La contrasena debe tener mínimo 8 caracteres, una mayúscula, un número y un símbolo"
            )

        if username in users:

            return render_template(
                "register.html",
                error="El usuario ya existe"
            )

        users[username] = {
            "email": email,
            "password": password,
            "question": question,
            "answer": answer.lower()
        }

        

        return redirect("/")

    return render_template("register.html")

# RECUPERAR CONTRASEÑA
@app.route("/recover", methods=["GET", "POST"])
def recover():

    if request.method == "POST":

        username = request.form["username"]

        if username in users:

            question = users[username]["question"]

            return render_template(
                "recover_answer.html",
                username=username,
                question=question
            )

        else:

            return render_template(
                "recover.html",
                error="Usuario no encontrado"
            )

    return render_template("recover.html")

# VALIDAR RESPUESTA
@app.route("/recover_answer", methods=["POST"])
def recover_answer():

    username = request.form["username"]
    answer = request.form["answer"].lower()

    if users[username]["answer"] == answer:

        email = users[username]["email"]

        msg = Message(
            'Codigo de recuperacion',
            sender=app.config['MAIL_USERNAME'],
            recipients=[email]
        )

        code = random.randint(100000, 999999)

        session["code"] = code
        session["recover_user"] = username

        msg.body = str("Tu codigo es : " + str(code))

        msg.charset = "utf-8"
        mail.send(msg)

        return redirect("/verify_code")
    
    else:

        return render_template(
            "recover_answer.html",
            error="Respuesta incorrecta",
            username=username,
            question=users[username]["question"]
        )

# VERIFICAR CODIGO
@app.route("/verify_code", methods=["GET", "POST"])
def verify_code():

    if request.method == "POST":

        code = request.form["code"]

        if code == str(session["code"]):

            return redirect("/reset_password")
        
        else:

            return render_template(
                "verify_code.html",
                error="Codigo incorrecto"
            )

    return render_template("verify_code.html")

# RESTABLECER CONTRASEÑA
@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():

    if request.method == "POST":

        password = request.form["password"]

        confirm_password = request.form["confirm_password"]

        if password != confirm_password:

            return render_template(
                "reset_password.html",
                error="Las contrasenas no coinciden"
            )

        users[session["recover_user"]]["password"] = password

        return render_template(
            "reset_password.html",
            success="Contrasena actualizada correctamente"
        )

    return render_template("reset_password.html")

# DASHBOARD
@app.route("/dashboard")
def dashboard():

    if "user" in session:

        return render_template(
            "dashboard.html",
            user=session["user"]
        )

    return redirect("/")

# LOGOUT
@app.route("/logout")
def logout():

    session.pop("user", None)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)