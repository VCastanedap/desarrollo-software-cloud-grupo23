from flask import Flask, request, render_template, redirect, url_for, session
from flask_jwt_extended import JWTManager, jwt_required, create_access_token

from flask import jsonify

from .models import User
from .models import db

app = Flask(__name__)


@app.route("/create_user")
def create_user():
    user = User(username="example_user", password="example_password")
    db.session.add(user)
    db.session.commit()
    return "User created!"


@app.route("/api/auth/signup", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in users:
            return "Username already exists. Please choose a different username."
        users[username] = password
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return 'Registration successful. <a href="/api/auth/login">Login</a>'
    return render_template("register.html")


@app.route("/api/auth/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in users and users[username] == password:
            chef = User.query.filter(
                User.username == username,
                User.password == password,
            ).first()

            session["id_user"] = chef.id

            session["username"] = username
            token_de_acceso = create_access_token(
                identity=username,
                expires_delta=False,
                additional_claims={"username": username},
            )
            session["token"] = token_de_acceso

            return redirect(url_for("home"))
        return "Invalid username or password"
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
