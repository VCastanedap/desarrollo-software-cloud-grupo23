from flask import Flask, request, session
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://flask_celery:flask_celery@db:5432/flask_celery'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'frase-secreta'
app.config['PROPAGATE_EXCEPTIONS'] = True

jwt = JWTManager(app)

db = SQLAlchemy()

app_context = app.app_context()
app_context.push()

db.init_app(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120), nullable=False)


class UsuarioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        load_instance = True
        
    id = fields.String()


# db.create_all()


def __validate_user(email:str) -> bool:
    if User.query.filter(email==email).first():
        return True
    else:
        return False


@app.route("/")
def hello():
    return "Users"


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


@app.route("/api/auth//logout")
def logout():
    session.pop("username", None)
    return {
        "message": "Finished session"
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
