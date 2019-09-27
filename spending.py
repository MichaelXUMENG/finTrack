import functools
from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort
from finTrack.db import get_db

bp = Blueprint('spending', __name__, url_prefix='/spending')


def get_category():
    cats = get_db().execute(
        'SELECT id, name'
        ' FROM categories'
        ' ORDER BY name'
    ).fetchall()
    return cats


def get_subCategory():
    subCats = get_db().execute(
        'SELECT id, name, c_id, default_card, default_degree'
        ' FROM sub_categories'
        ' ORDER BY name'
    ).fetchall()
    return subCats


def get_card():
    cards = get_db().execute(
        'SELECT id, name, bank, cur_balance, pay_date'
        ' FROM cards'
        ' ORDER BY bank, name'
    ).fetchall()
    return cards


def get_degree():
    degrees = get_db().execute(
        'SELECT id, name'
        ' FROM degrees'
        ' ORDER BY name'
    ).fetchall()
    return degrees


@bp.route('add', methods=('GET', 'POST'))
def spending_add():
    if request.method == 'POST':
        name = request.form['name']
        cat_id = request.form['category']
        sub_id = request.form['sub_category']
        date = request.form['date']
        card_id = request.form['card']
        degree_id = request.form['degree']
