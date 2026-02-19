from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, ResetToken
from  werkzeug.security import generate_password_hash, check_password_hash 
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import secrets
from datetime import datetime, timedelta
from flask import current_app  # ← добавила 
from flask_mail import Mail, Message


auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True) 
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 =  request.form.get('password2')

        user = User.query.filter_by(email=email).first()

        if user:
            flash('Email already exists.', category='error')
        elif len(email)  < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Password dont\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1))
            db.session.add(new_user)
            db.session.commit()
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)



#начало добавления
@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if not user:
            flash('Пользователь с таким email не найден.', 'error')
            return redirect(url_for('auth.forgot_password'))

       
        token = secrets.token_urlsafe(32)
        reset = ResetToken(user_id=user.id)
        db.session.add(reset)
        db.session.commit()

       
        reset_url = url_for('auth.reset_password', token=token, _external=True)

        # Отправляем письмо  деду
        msg = Message(
            subject="Сброс пароля на твоём сайте",
            sender= current_app.config['MAIL_USERNAME'],  # МОЯ ПОЧТАААААА 
            recipients=[email]
        )
        msg.body = f"Привет!\n\nПерейди по этой ссылке, чтобы сменить пароль:\n{reset_url}\n\nСсылка работает 1 час.\n\nЕсли ты не запрашивал сброс — просто игнорируй это письмо."
        current_app.extensions['mail'].send(msg)

        flash('Ссылка для сброса пароля отправлена на почту!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('forgot_password.html', user=current_user)


@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    reset = ResetToken.query.filter_by(token=token).first()

    if not reset or reset.expires_at < datetime.utcnow():
        flash('Ссылка недействительна или просрочена. Запроси новую.', 'error')
        return redirect(url_for('auth.forgot_password'))

    user = User.query.get(reset.user_id)

    if request.method == 'POST':
        password = request.form.get('password')
        password2 = request.form.get('password2')

        if password != password2:
            flash('Пароли не совпадают.', 'error')
        elif len(password) < 6:
            flash('Пароль должен быть минимум 6 символов.', 'error')
        else:
            user.password = generate_password_hash(password)
            db.session.delete(reset)  # токен использован
            db.session.commit()
            flash('Пароль успешно изменён! Теперь можешь войти.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('reset_password.html', token=token)

