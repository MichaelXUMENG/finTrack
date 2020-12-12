from flask import(
    Blueprint, render_template
)
from finTrack.db import get_db

bp = Blueprint('index', __name__)


def get_card():
    card = get_db().execute(
        'SELECT id, name, bank, cur_balance, pay_date, last_statement'
        ' FROM cards'
        ' ORDER BY bank, name'
    ).fetchall()

    return card


@bp.route('/')
def index():
    cards = get_card()
    return render_template('index.html', cards=cards)
