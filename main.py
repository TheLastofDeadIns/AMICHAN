from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from sqlalchemy import create_engine

app = Flask(__name__)

engine = create_engine('sqlite:///project.db')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
app.config['JWT_SECRET_TOKEN'] = 'secretniy kod'

db = SQLAlchemy(app)
jwt = JWTManager(app)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5000)