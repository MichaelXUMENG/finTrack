from flask import(
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from finTrack.db import get_db

bp = Blueprint('index', __name__)

@bp.route('/')
def index():
    return render_template('index.html')