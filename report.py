from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)
from finTrack.db import get_db

bp = Blueprint('report', __name__, url_prefix='/report')


def get_spendings():
    spendings = get_db().execute(
        'SELECT id, name, amount, category, sub_category, yr, mon, daynum, card, degree, comments'
        ' FROM spending'
        ' WHERE category!=?'
        ' ORDER BY yr DESC, mon DESC, daynum DESC, card',
        (16,)
    ).fetchall()
    return spendings


def get_doc_spending():
    doc_spendings = get_db().execute(
        'SELECT id, name, amount, sub_category, yr, mon, daynum, card, degree, comments'
        ' FROM spending'
        ' WHERE category=?'
        ' ORDER BY yr DESC, mon DESC, daynum DESC, card',
        (16,)
    ).fetchall()
    return doc_spendings


def get_spendings_card(card):
    spendings = get_db().execute(
        'SELECT id, name, amount, category, sub_category, yr, mon, daynum, card, degree, comments'
        ' FROM spending'
        ' WHERE card = ? and category!=?'
        ' ORDER BY yr DESC, mon DESC, daynum DESC, card',
        (card, 16)
    ).fetchall()
    return spendings


def get_month_cat_spendings(year, month, cat):
    spendings = get_db().execute(
        'SELECT id, name, amount, sub_category, yr, mon, daynum, card, degree, comments'
        ' FROM spending'
        ' WHERE yr = ? and mon=? and category=?'
        ' ORDER BY daynum DESC',
        (year, month, cat)
    ).fetchall()
    return spendings


def get_sum_month(year, month):
    summary = get_db().execute(
        'SELECT ROUND(SUM(amount), 2) as sum'
        ' FROM spending'
        ' WHERE yr=? and mon=? and category!=?',
        (year, month, 16)
    ).fetchone()
    return summary


def get_category_month(year, month):
    summary = get_db().execute(
        'SELECT category, ROUND(SUM(amount), 2) as sum'
        ' FROM spending'
        ' WHERE yr=? and mon=? and category!=?'
        ' GROUP BY category'
        ' ORDER BY SUM(amount) DESC',
        (year, month, 16)
    ).fetchall()
    return summary


def get_annual_sum(year):
    summary = get_db().execute(
        'SELECT ROUND(SUM(amount), 2) as sum, mon'
        ' FROM spending'
        ' WHERE yr=? and category!=?'
        ' GROUP BY mon'
        ' ORDER BY mon',
        (year, 16,)
    ).fetchall()
    return summary

def get_all_spending(year):
    summary = get_db().execute(
        'SELECT ROUND(SUM(amount), 2) as sum'
        ' FROM spending'
        ' WHERE yr=? and category!=?',
        (year, 16)
    ).fetchone()
    return summary


def get_mon_doc_sum():
    doc_summary = get_db().execute(
        'SELECT ROUND(SUM(amount), 2) as sum, yr, mon'
        ' FROM spending'
        ' WHERE category=?'
        ' GROUP BY yr, mon'
        ' ORDER BY yr, mon',
        (16,)
    ).fetchall()
    return doc_summary


def get_doc_sum():
    doc_summary = get_db().execute(
        'SELECT ROUND(SUM(amount), 2) as sum'
        ' FROM spending'
        ' WHERE category=?',
        (16,)
    ).fetchone()
    return doc_summary


def get_years():
    years = get_db().execute(
        'SELECT DISTINCT yr'
        ' FROM spending'
        ' ORDER BY yr DESC'
    ).fetchall()
    return years


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
    years = get_years()
    cards = get_card()
    return render_template('report/catalog.html', years=years, cards=cards)


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


@bp.route('/<int:year>/<int:month>')
def view_monthly_summary(year, month):
    sum = get_sum_month(year, month)
    cat_sum = get_category_month(year, month)
    cats = {}
    for pair in get_category():
        cats[pair['id']] = pair['name']
    return render_template("report/monthsummary.html", sum=sum, cat_sum=cat_sum, cats=cats, month=month, year=year)


@bp.route('/<int:year>')
def view_annual_summary(year):
    sum = get_annual_sum(year)
    allAmount = get_all_spending(year)
    return render_template("report/annualReport.html", year=year, sum=sum, amount=allAmount)


@bp.route('/docSpending')
def view_doc_summary():
    doc_spending = get_doc_spending()
    doc_annual_sum = get_doc_sum()
    doc_mon_sum = get_mon_doc_sum()
    return render_template("report/docReport.html", doc_spending=doc_spending, doc_annual_sum=doc_annual_sum,
                           doc_mon_sum=doc_mon_sum)


@bp.route('/<int:year>/<int:month>/<int:category>')
def monthlyCatTransaction(year, month, category):
    transactions = get_month_cat_spendings(year, month, category)
    totalSpending = get_db().execute(
        'SELECT ROUND(SUM(amount), 2) as sum'
        ' FROM spending'
        ' WHERE yr=? and mon=? and category=?',
        (year, month, category)
    ).fetchone()['sum']
    catNm = get_db().execute(
        'SELECT name'
        ' FROM categories'
        ' WHERE id=?',
        (category,)
    ).fetchone()['name']
    subCat = get_db().execute(
        'SELECT id, name'
        ' FROM sub_categories'
        ' WHERE c_id=?'
        ' ORDER BY id',
        (category, )
    ).fetchall()
    subs = {}
    cards = {}
    degrees = {}
    for pair in subCat:
        subs[pair['id']] = pair['name']
    for pair in get_card():
        cards[pair['id']] = pair['name']
    for pair in get_degree():
        degrees[pair['id']] = pair['name']
    return render_template("report/monthCatTransaction.html", transactions=transactions, catNm=catNm, subs=subs,
                           cards=cards, degrees=degrees, year=year, month=month, totalSpending=totalSpending)


@bp.route('/doctor')
def doctorSummary():
    transactions = get_doc_spending()
    monthSummary = get_mon_doc_sum()
    totalSpending = get_db().execute(
        'SELECT ROUND(SUM(amount), 2) as sum'
        ' FROM spending'
        ' WHERE category=?',
        (16,)
    ).fetchone()['sum']
    subCat = get_db().execute(
        'SELECT id, name'
        ' FROM sub_categories'
        ' WHERE c_id=?'
        ' ORDER BY id',
        (16,)
    ).fetchall()
    subs = {}
    cards = {}
    degrees = {}
    for pair in subCat:
        subs[pair['id']] = pair['name']
    for pair in get_card():
        cards[pair['id']] = pair['name']
    for pair in get_degree():
        degrees[pair['id']] = pair['name']
    return render_template("report/doctorSummary.html", transactions=transactions, monthSummary=monthSummary,
                           totalSpending=totalSpending, subs=subs, cards=cards, degrees=degrees)
