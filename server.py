from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
import os

# Инициализация приложения Flask
app = Flask(__name__)

# Конфигурация базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///forum.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'secretniykod'
app.config['JWT_VERIFY_SUB'] = False
# app.config['JWT_TOKEN_LOCATION'] = ['headers']

# Инициализация библиотек
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Модели базы данных
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user')
    registration_date = db.Column(db.DateTime, default=db.func.now())
    status = db.Column(db.String(20), default='active')

class Thread(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    comment_count = db.Column(db.Integer, default=0)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    thread_id = db.Column(db.Integer, db.ForeignKey('thread.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

class Blacklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reason = db.Column(db.String(255))
    ban_duration = db.Column(db.Interval, nullable=True)

# Регистрация нового пользователя
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email:
        return jsonify({'error': 'Email is required.'}), 400
    
    if not password:
        return jsonify({'error': 'Password cannot be empty.'}), 400

    if not email.endswith('@edu.hse.ru'):
        return jsonify({'error': 'Only @edu.hse.ru emails are allowed.'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists.'}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully.'}), 201

# Аутентификация пользователя
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid credentials.'}), 401

    access_token = create_access_token(identity={'id': user.id, 'role': user.role}, expires_delta=timedelta(hours=1))
    return jsonify({'access_token': access_token}), 200

# Создание нового треда
@app.route('/threads', methods=['POST'])
@jwt_required()
def create_thread():
    current_user = get_jwt_identity()
    data = request.get_json()
    title = data.get('title')

    if not title:
        return jsonify({'error': 'Title is required.'}), 400

    new_thread = Thread(title=title, author_id=current_user['id'])
    db.session.add(new_thread)
    db.session.commit()

    return jsonify({'message': 'Thread created successfully.'}), 201

# Получение списка тредов
@app.route('/threads', methods=['GET'])
@jwt_required()
def get_threads():
    threads = Thread.query.all()
    result = [
        {
            'id': thread.id,
            'title': thread.title,
            'author_id': thread.author_id,
            'created_at': thread.created_at,
            'comment_count': thread.comment_count
        } for thread in threads
    ]
    return jsonify(result), 200

# Добавление комментария к треду
@app.route('/threads/<int:thread_id>/comments', methods=['POST'])
@jwt_required()
def add_comment(thread_id):
    current_user = get_jwt_identity()
    data = request.get_json()
    text = data.get('text')

    if not text:
        return jsonify({'error': 'Text is required.'}), 400

    thread = Thread.query.get_or_404(thread_id)
    new_comment = Comment(text=text, author_id=current_user['id'], thread_id=thread.id)
    thread.comment_count += 1
    db.session.add(new_comment)
    db.session.commit()

    return jsonify({'message': 'Comment added successfully.'}), 201

@app.route('/threads/<int:thread_id>/comments', methods=['GET'])
@jwt_required()
def get_comments(thread_id):
    comments = Comment.query.filter_by(thread_id=thread_id)
    result = [
        {
            'id': comment.id,
            'text': comment.text,
            'author_id': comment.author_id,
            'thread_id': comment.thread_id,
            'created_at': comment.created_at
        } for comment in comments
    ]
    return jsonify(result), 200

# Запуск приложения
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
