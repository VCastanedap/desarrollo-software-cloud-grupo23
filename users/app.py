from flask import Flask, request, render_template, redirect, url_for, session
from flask_jwt_extended import JWTManager, jwt_required, create_access_token

from flask import jsonify

from .models import User
from .models import db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://flask_celery:flask_celery@db:5432/flask_celery'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'frase-secreta'
app.config['PROPAGATE_EXCEPTIONS'] = True

jwt = JWTManager(app)


def __validate_user(email:str) -> bool:
    if User.query.filter(email==email).first():
        return True
    else:
        return False


@app.route("/api/users/signup", methods=['POST'])
def signup():
    user_name = request.json['username']
    email = request.json['email']
    password = request.json['password']
    
    if not __validate_user(email=email): 
        try:
            new_user = User(
                username = user_name,
                email=email, 
                password = password
            )
        except Exception:
            return {
                "message": "Bad request"
            }
        else:
            access_token = create_access_token(identity=user_name)
            db.session.add(new_user)
            db.session.commit()
            return {
                "message": "User created!", 
                "access_token": access_token
            }


@app.route("/api/auth/login", methods=["POST"])
def login():
    username = request.json["username"]
    email = request.json['email']
    
    if __validate_user(email=email):
        access_token = create_access_token(identity=username)
        return {
                "message": "Success login", 
                "access_token": access_token
            }
    else:
        return {
            "message": "Invalid username or password"
        }


@app.route("/logout")
def logout():
    session.pop("username", None)
    return {
        "message": "Finished session"
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
