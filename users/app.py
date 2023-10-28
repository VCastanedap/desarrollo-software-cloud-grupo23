from flask import Flask, request, session
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
import psycopg2


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


# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), nullable=False)
#     email = db.Column(db.String(120), unique=True)
#     password = db.Column(db.String(120), nullable=False)


# class UsuarioSchema(SQLAlchemyAutoSchema):
#     class Meta:
#         model = User
#         include_relationships = True
#         load_instance = True
        
#     id = fields.String()


# db.create_all()


conn = psycopg2.connect(
    host="postgres",
    port=5432,
    user="flask_celery",
    password="flask_celery",
    database="flask_celery"
)
    
cursor = conn.cursor()


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
            conn = psycopg2.connect(
                dbname="tu_basededatos",
                user="tu_usuario",
                password="tu_contraseña",
                host="tu_host",
                port="tu_puerto"
            )
            cursor = conn.cursor()

            sql_query = """
            INSERT INTO "user" (username, email, password) 
            VALUES (%s, %s, %s) RETURNING id
            """
            values = (user_name, email, password)

            cursor.execute(sql_query, values)
            user_id = cursor.fetchone()[0]
            conn.commit()

            access_token = create_access_token(identity=user_name)

            cursor.close()
            conn.close()

            return {
                "message": "User created!",
                "access_token": access_token
            }
        except Exception as e:
            return {
                "message": "Bad request"
            }
    else:
        return {
            "message": "User with this email already exists"
        }

@app.route("/api/auth/login", methods=["POST"])
def login():
    email = request.json["email"]
    password = request.json["password"]

    try:
        sql_query = "SELECT * FROM usuario WHERE email = %s"
        values = (email,)

        cursor.execute(sql_query, values)
        user = cursor.fetchone()

        if user and user[2] == password:  # La columna 2 debe ser la columna de contraseña en la tabla
            # Autenticación exitosa, generar un token JWT
            access_token = create_access_token(identity=user[1])  # El nombre de usuario está en la columna 1
            cursor.close()
            conn.close()
            return {
                "message": "Success login",
                "access_token": access_token
            }
        else:
            # Autenticación fallida
            cursor.close()
            conn.close()
            return {
                "message": "Invalid email or password"
            }
    except Exception as e:
        return {
            "message": "Error during authentication"
        }


@app.route("/api/auth//logout")
def logout():
    session.pop("username", None)
    return {
        "message": "Finished session"
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
