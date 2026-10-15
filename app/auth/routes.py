from urllib.parse import urlsplit

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.auth import bp
from app.auth.forms import (
    LoginForm,
    ProfileForm,
    RegistrationForm,
    ResetPasswordForm,
    ResetRequestForm,
)
from app.extensions import limiter
from app.services import auth as auth_service


def _safe_next_url() -> str:
    """Only follow relative ?next= URLs, so login can't redirect to another site."""
    target = request.args.get("next", "")
    parts = urlsplit(target)
    if target.startswith("/") and not target.startswith("//") and not parts.netloc:
        return target
    return url_for("main.index")


@bp.route("/auth/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = auth_service.register_user(form.name.data, form.email.data, form.password.data)
        except auth_service.EmailTakenError:
            form.email.errors.append("Этот email уже зарегистрирован.")
        else:
            login_user(user)
            flash("Добро пожаловать в RentAll! Регистрация прошла успешно.", "success")
            return redirect(url_for("main.index"))
    return render_template("auth/register.html", form=form)


@bp.route("/auth/login", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = auth_service.authenticate(form.email.data, form.password.data)
        if user is None:
            flash("Неверный email или пароль.", "danger")
        else:
            login_user(user, remember=form.remember.data)
            flash(f"С возвращением, {user.name}!", "success")
            return redirect(_safe_next_url())
    return render_template("auth/login.html", form=form)


@bp.post("/auth/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта.", "info")
    return redirect(url_for("main.index"))


@bp.route("/auth/reset-password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = ResetRequestForm()
    if form.validate_on_submit():
        auth_service.send_password_reset(form.email.data)
        # Same message whether or not the account exists.
        flash("Если такой аккаунт существует, мы отправили ссылку для сброса пароля.", "info")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_request.html", form=form)


@bp.route("/auth/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token: str):
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    user = auth_service.verify_reset_token(token)
    if user is None:
        flash("Ссылка для сброса пароля недействительна или устарела. Запросите новую.", "danger")
        return redirect(url_for("auth.reset_request"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        auth_service.reset_password(user, form.password.data)
        flash("Пароль изменён. Теперь вы можете войти.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html", form=form)


@bp.get("/me")
@login_required
def me():
    return redirect(url_for("auth.profile"))


@bp.route("/me/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        auth_service.update_profile(current_user, form.name.data, form.phone.data)
        flash("Профиль сохранён.", "success")
        return redirect(url_for("auth.profile"))
    return render_template("auth/profile.html", form=form)


@bp.post("/me/become-owner")
@login_required
def become_owner():
    if current_user.is_owner:
        flash("Вы уже арендодатель.", "info")
    else:
        auth_service.become_owner(current_user)
        flash("Готово! Теперь вы арендодатель и можете размещать объявления.", "success")
    return redirect(url_for("auth.profile"))
