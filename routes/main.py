from flask import (
    Blueprint,
    render_template
)

from flask_login import (
    login_required,
    current_user
)

from models import Artwork


main_bp = Blueprint(
    "main",
    __name__
)


@main_bp.route("/")
def index():

    return render_template(
        "index.html"
    )



@main_bp.route("/dashboard")
@login_required
def dashboard():

    artworks = Artwork.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Artwork.created_at.desc()
    ).all()


    return render_template(
        "dashboard.html",
        artworks=artworks
    )



@main_bp.route("/profile")
@login_required
def profile():

    artwork_count = Artwork.query.filter_by(
        user_id=current_user.id
    ).count()


    return render_template(
        "profile.html",
        artwork_count=artwork_count
    )