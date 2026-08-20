import re
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User


class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Email is required"),
            Email(message="Invalid email address"),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(message="Password is required")],
    )
    submit = SubmitField("Log In")


class SignupForm(FlaskForm):
    name = StringField(
        "Full Name",
        validators=[
            DataRequired(message="Name is required"),
            Length(
                min=2,
                max=100,
                message="Name must be between 2 and 100 characters",
            ),
        ],
    )
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Email is required"),
            Email(message="Invalid email address"),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Password is required"),
            Length(min=8, message="Password must be at least 8 characters"),
        ],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(message="Please confirm password"),
            EqualTo("password", message="Passwords must match"),
        ],
    )
    submit = SubmitField("Create Account")

    def validate_email(self, email):
        if not email.data:
            return
        user = User.query.filter_by(email=email.data.strip().lower()).first()
        if user:
            raise ValidationError(
                "Email already registered. Please use a different email."
            )

    def validate_password(self, password):
        if not password.data:
            return
        if not re.search(r"[A-Z]", password.data):
            raise ValidationError(
                "Password must contain at least one uppercase letter"
            )
        if not re.search(r"[a-z]", password.data):
            raise ValidationError(
                "Password must contain at least one lowercase letter"
            )
        if not re.search(r"\d", password.data):
            raise ValidationError("Password must contain at least one number")


class URLScanForm(FlaskForm):
    url = StringField(
        "URL",
        validators=[
            DataRequired(message="URL is required"),
            Length(
                min=4,
                max=2048,
                message="URL must be between 4 and 2048 characters",
            ),
        ],
    )
    submit = SubmitField("Analyze Website")

    def validate_url(self, url):
        if not url.data:
            return

        url_pattern = re.compile(
            r"^(?:http|https)://"
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
            r"localhost|"
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
            r"(?::\d+)?"
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )

        test_url = url.data.strip()
        if not test_url.startswith(("http://", "https://")):
            test_url = "https://" + test_url

        if not url_pattern.match(test_url):
            raise ValidationError(
                "Invalid URL format. Please enter a valid URL."
            )


class BatchScanForm(FlaskForm):
    urls = TextAreaField(
        "URLs (one per line)",
        validators=[
            DataRequired(message="Please enter at least one URL"),
            Length(max=10000, message="Too many URLs"),
        ],
    )
    submit = SubmitField("Scan All URLs")

    def validate_urls(self, urls):
        if not urls.data:
            raise ValidationError("Please enter at least one URL")

        url_list = [u.strip() for u in urls.data.splitlines() if u.strip()]
        if len(url_list) == 0:
            raise ValidationError("Please enter at least one URL")
        if len(url_list) > 50:
            raise ValidationError("Maximum 50 URLs allowed per batch")