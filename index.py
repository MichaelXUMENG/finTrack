from flask import(
    Blueprint, render_template, flash
)
from finTrack.db import commit_database
from .db_utils import Card

bp = Blueprint('index', __name__)


@bp.route('/')
def index():
    card_object = Card()
    try:
        cards = card_object.fetch_all_in_order(order='bank, name')
    except Exception as e:
        flash(e, 'error')
        cards = []
    
    commit_database()
    return render_template('index.html', cards=cards)
