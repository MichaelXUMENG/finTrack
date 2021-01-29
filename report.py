from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)
from .db_utils import (
    get_all_spendings, get_doctor_spendings, get_spendings_card, get_spendings_month_cat,
    get_total_spending_month, get_category_total_spending_month, get_month_total_spending_year,
    get_total_spending_year, get_mon_total_spending_doc, get_total_spending_doc, get_spending_years,
    get_all_cards, get_all_degrees, get_all_spendings_card,
    get_total_spending_month_cat
)
from .db_utils import Category, SubCategory
from .interactive_graphs import interactive_annual_report, interactive_annual_report_as_div

bp = Blueprint('report', __name__, url_prefix='/report')


@bp.route('/')
def catalog():
    years, cards = {}, {}
    try:
        years = get_spending_years()
        cards = get_all_cards(order='id')
    except Exception as e:
        flash(e, 'error')
    return render_template('report/catalog.html', years=years, cards=cards)


@bp.route('/viewall')
def view_all_spending():
    spendings = {}
    cats = {}
    subs = {}
    cards = {}
    degrees = {}
    category = Category()
    sub_category = SubCategory()
    try:
        spendings = get_all_spendings()
        for pair in category.get_all_in_order(order='id'):
            cats[pair['id']] = pair['name']
        for pair in sub_category.get_all_in_order(order='id'):
            subs[pair['id']] = pair['name']
        for pair in get_all_cards(order='id'):
            cards[pair['id']] = pair['name']
        for pair in get_all_degrees(order='id'):
            degrees[pair['id']] = pair['name']
    except Exception as e:
        flash(e, 'error')
    return render_template("report/allspending.html", spendings=spendings, cats=cats, subs=subs, cards=cards, degrees=degrees)


@bp.route('/<int:card>/viewall')
def view_all_spending_card(card):
    spendings = {}
    cats = {}
    subs = {}
    cards = {}
    degrees = {}
    category = Category()
    sub_category = SubCategory()
    try:
        spendings = get_spendings_card(card)
        for pair in category.get_all_in_order(order='id'):
            cats[pair['id']] = pair['name']
        for pair in sub_category.get_all_in_order(order='id'):
            subs[pair['id']] = pair['name']
        for pair in get_all_cards(order='id'):
            cards[pair['id']] = pair['name']
        for pair in get_all_degrees(order='id'):
            degrees[pair['id']] = pair['name']
    except Exception as e:
        flash(e, 'error')
    return render_template("report/cardspending.html", spendings=spendings, cats=cats, subs=subs, cards=cards,
                           card_id=card, degrees=degrees)


@bp.route('/<int:card>/addcardspending')
def add_spending_card(card):
    cats = {}
    subs = {}
    cards = {}
    degrees = {}
    spendings = {}
    category = Category()
    sub_category = SubCategory()
    try:
        spendings = get_all_spendings_card(card)
        for pair in category.get_all_in_order(order='id'):
            cats[pair['id']] = pair['name']
        for pair in sub_category.get_all_in_order(order='id'):
            subs[pair['id']] = pair['name']
        for pair in get_all_cards(order='id'):
            cards[pair['id']] = pair['name']
        for pair in get_all_degrees(order='id'):
            degrees[pair['id']] = pair['name']
    except Exception as e:
        flash(e, 'error')
    return render_template("report/cardspending.html", spendings=spendings, cats=cats, subs=subs, cards=cards,
                           card_id=card, degrees=degrees)


@bp.route('/<int:year>/<int:month>')
def view_monthly_summary(year, month):
    cats = {}
    sum = {}
    cat_sum = {}
    category = Category()
    try:
        sum = get_total_spending_month(year, month)
        cat_sum = get_category_total_spending_month(year, month)
        for pair in category.get_all_in_order(order='id'):
            cats[pair['id']] = pair['name']
    except Exception as e:
        flash(e, 'error')
    return render_template("report/monthsummary.html", sum=sum, cat_sum=cat_sum, cats=cats, month=month, year=year)


@bp.route('/<int:year>')
def view_annual_summary(year):
    sum = {}
    allAmount = 0
    try:
        sum = get_month_total_spending_year(year)
        allAmount = get_total_spending_year(year)
        graphJSON = interactive_annual_report(year)
        div_graph = interactive_annual_report_as_div(year)
    except Exception as e:
        flash(e, 'error')
    return render_template("report/annualReport.html", year=year, sum=sum, amount=allAmount, graphJSON=graphJSON, div_graph=div_graph)


@bp.route('/docSpending')
def view_doc_summary():
    doc_annual_sum, doc_mon_sum = 0, 0
    doc_spending = {}
    try:
        doc_spending = get_doctor_spendings()
        doc_annual_sum = get_total_spending_doc()
        doc_mon_sum = get_mon_total_spending_doc()
    except Exception as e:
        flash(e, 'error')
    return render_template("report/docReport.html", doc_spending=doc_spending, doc_annual_sum=doc_annual_sum,
                           doc_mon_sum=doc_mon_sum)


@bp.route('/<int:year>/<int:month>/<int:category>')
def monthlyCatTransaction(year, month, category):
    subs = {}
    cards = {}
    degrees = {}
    transactions = {}
    catNm = {}
    totalSpending = 0
    category_object = Category()
    sub_category = SubCategory()
    try:
        transactions = get_spendings_month_cat(year, month, category)
        totalSpending = get_total_spending_month_cat(year, month, category)
        catNm = category_object.get_one_item_by_id(category)['name']
        subCat = sub_category.get_all_subcategories_in_category(category)
        for pair in subCat:
            subs[pair['id']] = pair['name']
        for pair in get_all_cards(order='id'):
            cards[pair['id']] = pair['name']
        for pair in get_all_degrees(order='id'):
            degrees[pair['id']] = pair['name']
    except Exception as e:
        flash(e, 'error')
    return render_template("report/monthCatTransaction.html", transactions=transactions, catNm=catNm, subs=subs,
                           cards=cards, degrees=degrees, year=year, month=month, totalSpending=totalSpending)


@bp.route('/doctor')
def doctorSummary():
    subs = {}
    cards = {}
    degrees = {}
    transactions = {}
    monthSummary, totalSpending = 0, 0
    sub_category = SubCategory()
    try:
        transactions = get_doctor_spendings()
        monthSummary = get_mon_total_spending_doc()
        totalSpending = get_total_spending_doc()['sum']
        subCat = sub_category.get_all_subcategories_in_category(16)
        for pair in subCat:
            subs[pair['id']] = pair['name']
        for pair in get_all_cards(order='id'):
            cards[pair['id']] = pair['name']
        for pair in get_all_degrees(order='id'):
            degrees[pair['id']] = pair['name']
    except Exception as e:
        flash(e, 'error')
    return render_template("report/doctorSummary.html", transactions=transactions, monthSummary=monthSummary,
                           totalSpending=totalSpending, subs=subs, cards=cards, degrees=degrees)
