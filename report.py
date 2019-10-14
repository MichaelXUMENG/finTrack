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
        ' ORDER BY yr DESC, mon DESC, daynum DESC, card'
    ).fetchall()
    return spendings


def get_spendings_card(card):
    spendings = get_db().execute(
        'SELECT id, name, amount, category, sub_category, yr, mon, daynum, card, degree, comments'
        ' FROM spending'
        ' WHERE card = ?'
        ' ORDER BY yr DESC, mon DESC, daynum DESC, card',
        (card,)
    ).fetchall()
    return spendings


def get_sum_month(month):
    summary = get_db().execute(
        'SELECT ROUND(SUM(amount), 2) as sum'
        ' FROM spending'
        ' WHERE mon = ?',
        (month,)
    ).fetchone()
    return summary


def get_category_month(month):
    summary = get_db().execute(
        'SELECT category, ROUND(SUM(amount), 2) as sum'
        ' FROM spending'
        ' WHERE mon = ?'
        ' GROUP BY category'
        ' ORDER BY SUM(amount) DESC',
        (month,)
    ).fetchall()
    return summary


def get_months():
    months = get_db().execute(
        'SELECT DISTINCT mon'
        ' FROM spending'
        ' ORDER BY mon DESC'
    ).fetchall()
    return months


def get_category():
    categorys = get_db().execute(
        'SELECT id, name'
        ' FROM categories'
        ' ORDER BY id'
    ).fetchall()
    return categorys


def get_subcat():
    sub_cats = get_db().execute(
        'SELECT id, name'
        ' FROM sub_categories'
        ' ORDER BY id'
    ).fetchall()
    return sub_cats


def get_card():
    cards = get_db().execute(
        'SELECT id, name'
        ' FROM cards'
        ' ORDER BY id'
    ).fetchall()
    return cards


def get_degree():
    degrees = get_db().execute(
        'SELECT id, name'
        ' FROM degrees'
        ' ORDER BY id'
    ).fetchall()
    return degrees


@bp.route('/')
def catalog():
    months = get_months()
    return render_template('report/catalog.html', months=months)


@bp.route('/viewall')
def view_all_spending():
    spendings = get_spendings()
    cats = {}
    subs = {}
    cards = {}
    degrees = {}
    for pair in get_category():
        cats[pair['id']] = pair['name']
    for pair in get_subcat():
        subs[pair['id']] = pair['name']
    for pair in get_card():
        cards[pair['id']] = pair['name']
    for pair in get_degree():
        degrees[pair['id']] = pair['name']
    return render_template("report/allspending.html", spendings=spendings, cats=cats, subs=subs, cards=cards, degrees=degrees)


@bp.route('/<int:card>/viewall')
def view_all_spending_card(card):
    spendings = get_spendings_card(card)
    cats = {}
    subs = {}
    cards = {}
    degrees = {}
    for pair in get_category():
        cats[pair['id']] = pair['name']
    for pair in get_subcat():
        subs[pair['id']] = pair['name']
    for pair in get_card():
        cards[pair['id']] = pair['name']
    for pair in get_degree():
        degrees[pair['id']] = pair['name']
    return render_template("report/cardspending.html", spendings=spendings, cats=cats, subs=subs, cards=cards,
                           card_id=card, degrees=degrees)


@bp.route('/month/<int:month>')
def view_monthly_summary(month):
    sum = get_sum_month(month)
    cat_sum = get_category_month(month)
    cats = {}
    for pair in get_category():
        cats[pair['id']] = pair['name']
    return render_template("report/monthsummary.html", sum=sum, cat_sum=cat_sum, cats=cats)

