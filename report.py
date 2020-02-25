from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)
from finTrack.db import get_db
from .db_utils import (
    get_all_spendings, get_doctor_spendings, get_spendings_card, get_spendings_month_cat,
    get_total_spending_month, get_category_total_spending_month, get_month_total_spending_year,
    get_total_spending_year, get_mon_total_spending_doc, get_total_spending_doc, get_spending_years,
    get_all_category_id, get_all_subcat_id, get_all_cards_id, get_all_degrees_id
)

bp = Blueprint('report', __name__, url_prefix='/report')


@bp.route('/')
def catalog():
    years = get_spending_years()
    cards = get_all_cards_id()
    return render_template('report/catalog.html', years=years, cards=cards)


@bp.route('/viewall')
def view_all_spending():
    spendings = get_all_spendings()
    cats = {}
    subs = {}
    cards = {}
    degrees = {}
    for pair in get_all_category_id():
        cats[pair['id']] = pair['name']
    for pair in get_all_subcat_id():
        subs[pair['id']] = pair['name']
    for pair in get_all_cards_id():
        cards[pair['id']] = pair['name']
    for pair in get_all_degrees_id():
        degrees[pair['id']] = pair['name']
    return render_template("report/allspending.html", spendings=spendings, cats=cats, subs=subs, cards=cards, degrees=degrees)


@bp.route('/<int:card>/viewall')
def view_all_spending_card(card):
    spendings = get_spendings_card(card)
    cats = {}
    subs = {}
    cards = {}
    degrees = {}
    for pair in get_all_category_id():
        cats[pair['id']] = pair['name']
    for pair in get_all_subcat_id():
        subs[pair['id']] = pair['name']
    for pair in get_all_cards_id():
        cards[pair['id']] = pair['name']
    for pair in get_all_degrees_id():
        degrees[pair['id']] = pair['name']
    return render_template("report/cardspending.html", spendings=spendings, cats=cats, subs=subs, cards=cards,
                           card_id=card, degrees=degrees)


@bp.route('/<int:card>/addcardspending')
def add_spending_card(card):
    spendings = get_db().execute(
        'SELECT id, name, amount, category, sub_category, yr, mon, daynum, card, degree, comments'
        ' FROM spending'
        ' WHERE card = ?'
        ' ORDER BY yr DESC, mon DESC, daynum DESC, card',
        (card,)
    ).fetchall()
    cats = {}
    subs = {}
    cards = {}
    degrees = {}
    for pair in get_all_category_id():
        cats[pair['id']] = pair['name']
    for pair in get_all_subcat_id():
        subs[pair['id']] = pair['name']
    for pair in get_all_cards_id():
        cards[pair['id']] = pair['name']
    for pair in get_all_degrees_id():
        degrees[pair['id']] = pair['name']
    return render_template("report/cardspending.html", spendings=spendings, cats=cats, subs=subs, cards=cards,
                           card_id=card, degrees=degrees)


@bp.route('/<int:year>/<int:month>')
def view_monthly_summary(year, month):
    sum = get_total_spending_month(year, month)
    cat_sum = get_category_total_spending_month(year, month)
    cats = {}
    for pair in get_all_category_id():
        cats[pair['id']] = pair['name']
    return render_template("report/monthsummary.html", sum=sum, cat_sum=cat_sum, cats=cats, month=month, year=year)


@bp.route('/<int:year>')
def view_annual_summary(year):
    sum = get_month_total_spending_year(year)
    allAmount = get_total_spending_year(year)
    return render_template("report/annualReport.html", year=year, sum=sum, amount=allAmount)


@bp.route('/docSpending')
def view_doc_summary():
    doc_spending = get_doctor_spendings()
    doc_annual_sum = get_total_spending_doc()
    doc_mon_sum = get_mon_total_spending_doc()
    return render_template("report/docReport.html", doc_spending=doc_spending, doc_annual_sum=doc_annual_sum,
                           doc_mon_sum=doc_mon_sum)


@bp.route('/<int:year>/<int:month>/<int:category>')
def monthlyCatTransaction(year, month, category):
    transactions = get_spendings_month_cat(year, month, category)
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
    for pair in get_all_cards_id():
        cards[pair['id']] = pair['name']
    for pair in get_all_degrees_id():
        degrees[pair['id']] = pair['name']
    return render_template("report/monthCatTransaction.html", transactions=transactions, catNm=catNm, subs=subs,
                           cards=cards, degrees=degrees, year=year, month=month, totalSpending=totalSpending)


@bp.route('/doctor')
def doctorSummary():
    transactions = get_doctor_spendings()
    monthSummary = get_mon_total_spending_doc()
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
    for pair in get_all_cards_id():
        cards[pair['id']] = pair['name']
    for pair in get_all_degrees_id():
        degrees[pair['id']] = pair['name']
    return render_template("report/doctorSummary.html", transactions=transactions, monthSummary=monthSummary,
                           totalSpending=totalSpending, subs=subs, cards=cards, degrees=degrees)
