from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note
from . import db
import  json

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note =  request.form.get('note')

        if len(note) < 1:
            flash('Заметка слишком короткая!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            #flash('Заметка добавлена!', category='success')   
            return redirect(url_for('views.home')+ '#notes-section') 
    return render_template("home.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():
    data = json.loads(request.data)
    noteId = data['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
    return redirect(url_for('views.home') + '#notes-section')

@views.route('/quiz')
def quiz():
    return render_template('quiz.html', user=current_user)

# ==================== ЛЕКЦИИ ====================

lessons_data = [
    {
        "id": 1,
        "title": "Урок 1. Основы кибербезопасности",
        "description": "Что такое кибербезопасность и почему это важно",
        "video": "/static/video/lesson1.mp4",   # только видео
        "audio": None,
        "image": None,
        "text": """
Это текст первой лекции.
Здесь объясняется, почему важно защищать свои данные.
Пароли, фишинг, вирусы — всё по порядку.
        """
    },
    {
        "id": 2,
        "title": "Урок 2. Надёжные пароли",
        "description": "Как создавать и хранить сильные пароли",
        "video": None,
        "audio": "/static/audio/lesson2.mp3",   # только аудио
        "image": None,
        "text": """
Текст второй лекции.
Менеджеры паролей, генерация случайных строк, 2FA.
Примеры хороших и плохих паролей.
        """
    },
    {
        "id": 3,
        "title": "Урок 3. Распознавание фишинга",
        "description": "Как не попасться на мошеннические письма",
        "video": None,
        "audio": None,
        "image": "/static/images/lesson3.jpg",   # только картинка (можно несколько)
        "text": """
Текст третьей лекции.
Скриншоты типичных фишинговых писем.
Что проверять в письме перед кликом по ссылке.
        """
    }
    # Добавляй новые уроки сюда
]

@views.route('/lessons')
@login_required
def lessons():
    return render_template('lessons.html', lessons=lessons_data, user=current_user)

@views.route('/lesson/<int:lesson_id>')
@login_required
def lesson(lesson_id):
    lesson = next((l for l in lessons_data if l["id"] == lesson_id), None)
    if not lesson:
        flash('Урок не найден', category='error')
        return redirect(url_for('views.lessons'))
    return render_template('lesson.html', lesson=lesson, user=current_user)