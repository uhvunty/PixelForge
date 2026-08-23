from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_user,
    logout_user,
    current_user
)

from extensions import db
from models import User


auth_bp = Blueprint(
    "auth",
    __name__
)


# =========================
# LOGIN
# =========================

@auth_bp.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if current_user.is_authenticated:
        return redirect(
            url_for("main.dashboard")
        )

    if request.method == "POST":

        identifier = request.form.get(
            "identifier",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        # Check that both fields are filled
        if not identifier or not password:

            flash(
                "Please enter your username/email and password.",
                "error"
            )

            return render_template(
                "login.html"
            )

        # Find user by username OR email
        user = User.query.filter(
            db.or_(
                User.username.ilike(identifier),
                User.email.ilike(identifier)
            )
        ).first()

        # Check password
        if (
            user is None
            or not user.check_password(password)
        ):

            flash(
                "Invalid username/email or password.",
                "error"
            )

            return render_template(
                "login.html"
            )

        # Log the user in
        login_user(
            user,
            remember=True
        )

        flash(
            "Login successful.",
            "success"
        )

        # Handle redirect after login
        next_page = request.args.get(
            "next"
        )

        if (
            next_page
            and next_page.startswith("/")
        ):

            return redirect(
                next_page
            )

        return redirect(
            url_for("main.dashboard")
        )

    return render_template(
        "login.html"
    )


# =========================
# REGISTER
# =========================

@auth_bp.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if current_user.is_authenticated:
        return redirect(
            url_for("main.dashboard")
        )

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        # Check required fields
        if not username or not email or not password:

            flash(
                "All fields are required.",
                "error"
            )

            return render_template(
                "register.html"
            )

        # Check username length
        if len(username) < 3:

            flash(
                "Username must contain at least 3 characters.",
                "error"
            )

            return render_template(
                "register.html"
            )

        # Check password length
        if len(password) < 8:

            flash(
                "Password must contain at least 8 characters.",
                "error"
            )

            return render_template(
                "register.html"
            )

        # Check if username already exists
        existing_username = User.query.filter(
            db.func.lower(User.username)
            == username.lower()
        ).first()

        if existing_username:

            flash(
                "That username is already taken.",
                "error"
            )

            return render_template(
                "register.html"
            )

        # Check if email already exists
        existing_email = User.query.filter(
            db.func.lower(User.email)
            == email.lower()
        ).first()

        if existing_email:

            flash(
                "An account with that email already exists.",
                "error"
            )

            return render_template(
                "register.html"
            )

        # Create user
        user = User(
            username=username,
            email=email
        )

        # Hash and store the password
        user.set_password(
            password
        )

        # Save user to database
        db.session.add(
            user
        )

        db.session.commit()

        # Log user in automatically
        login_user(
            user
        )

        flash(
            "Account created successfully.",
            "success"
        )

        return redirect(
            url_for("main.dashboard")
        )

    return render_template(
        "register.html"
    )


# =========================
# LOGOUT
# =========================

@auth_bp.route(
    "/logout"
)
def logout():

    logout_user()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("main.index")
    )