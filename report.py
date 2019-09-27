import functools
from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort
from finTrack.db import get_db

bp = Blueprint('report', __name__, url_prefix='/report')

def get_spendings():
    spendings = get_db().execute(
        'SELECT id, name, amount, category, sub_category, yr, mon, daynum, card, degree, comments'
        ' FROM spending'
        ' ORDER BY id'
    ).fetchall()
    return spendings


@bp.route('/viewall')
def view_all_spending():
    spendings = get_spendings()
    return render_template("report/allspending.html", spendings=spendings)