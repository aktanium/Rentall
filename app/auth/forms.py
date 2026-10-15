from flask_wtf import FlaskForm
from wtforms import BooleanField, EmailField, PasswordField, StringField, SubmitField, TelField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, Regexp

MIN_PASSWORD_LENGTH = 8


def _strip(value):
    return value.strip() if isinstance(value, str) else value


_email_validators = [
    DataRequired(message="Введите email."),
    Email(message="Введите корректный email.", check_deliverability=False),
    Length(max=255, message="Email слишком длинный."),
]


def _new_password_fields():
    password = PasswordField(
        "Пароль",
        validators=[
            DataRequired(message="Введите пароль."),
            Length(
                min=MIN_PASSWORD_LENGTH,
                max=128,
                message=f"Пароль должен быть не короче {MIN_PASSWORD_LENGTH} символов.",
            ),
        ],
    )
    confirm = PasswordField(
        "Повторите пароль",
        validators=[
            DataRequired(message="Повторите пароль."),
            EqualTo("password", message="Пароли не совпадают."),
        ],
    )
    return password, confirm


class RegistrationForm(FlaskForm):
    name = StringField(
        "Имя",
        validators=[
            DataRequired(message="Введите имя."),
            Length(max=100, message="Имя слишком длинное."),
        ],
    )
    email = EmailField("Email", validators=_email_validators, filters=[_strip])
    password, confirm = _new_password_fields()
    submit = SubmitField("Зарегистрироваться")


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=_email_validators, filters=[_strip])
    password = PasswordField("Пароль", validators=[DataRequired(message="Введите пароль.")])
    remember = BooleanField("Запомнить меня")
    submit = SubmitField("Войти")


class ProfileForm(FlaskForm):
    name = StringField(
        "Имя",
        validators=[
            DataRequired(message="Введите имя."),
            Length(max=100, message="Имя слишком длинное."),
        ],
    )
    phone = TelField(
        "Телефон",
        validators=[
            Optional(),
            Regexp(
                r"^\+?[\d\s\-()]{7,20}$",
                message="Введите номер в формате +996 555 123 456.",
            ),
        ],
    )
    submit = SubmitField("Сохранить")


class ResetRequestForm(FlaskForm):
    email = EmailField("Email", validators=_email_validators, filters=[_strip])
    submit = SubmitField("Отправить ссылку")


class ResetPasswordForm(FlaskForm):
    password, confirm = _new_password_fields()
    submit = SubmitField("Сменить пароль")
