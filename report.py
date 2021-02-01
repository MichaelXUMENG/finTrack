from flask import (
    Blueprint, flash, render_template
)

from .db_utils import Category, SubCategory, Card, Degree, Spending, DoctorSpending
from .interactive_graphs import interactive_annual_report, interactive_annual_report_as_div

bp = Blueprint('report', __name__, url_prefix='/report')


@bp.route('/')
def catalog():
    spending_object = Spending()

    card_object = Card()
    years, cards = {}, {}
    try:
        years = spending_object.get_years()
        cards = card_object.fetch_all_in_order(order='id')
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
    card_object = Card()
    degree_object = Degree()
    spending_object = Spending()

    try:
        spendings = spending_object.fetch_all_category_spending(include_doctor=False)
        for pair in category.fetch_all_in_order(order='id'):
            cats[pair['id']] = pair['name']
        for pair in sub_category.fetch_all_in_order(order='id'):
            subs[pair['id']] = pair['name']
        for pair in card_object.fetch_all_in_order(order='id'):
            cards[pair['id']] = pair['name']
        for pair in degree_object.fetch_all_in_order(order='id'):
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
    card_object = Card()
    degree_object = Degree()
    spending_object = Spending()

    try:
        spendings = spending_object.fetch_all_spendings_from_a_card(card, include_doctor=False)
        for pair in category.fetch_all_in_order(order='id'):
            cats[pair['id']] = pair['name']
        for pair in sub_category.fetch_all_in_order(order='id'):
            subs[pair['id']] = pair['name']
        for pair in card_object.fetch_all_in_order(order='id'):
            cards[pair['id']] = pair['name']
        for pair in degree_object.fetch_all_in_order(order='id'):
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
    card_object = Card()
    degree_object = Degree()
    spending_object = Spending()

    try:
        spendings = spending_object.fetch_all_spendings_from_a_card(card)
        for pair in category.fetch_all_in_order(order='id'):
            cats[pair['id']] = pair['name']
        for pair in sub_category.fetch_all_in_order(order='id'):
            subs[pair['id']] = pair['name']
        for pair in card_object.fetch_all_in_order(order='id'):
            cards[pair['id']] = pair['name']
        for pair in degree_object.fetch_all_in_order(order='id'):
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
    spending_object = Spending()
    try:
        sum = spending_object.get_total_spending_amount_of_month(year, month)
        cat_sum = spending_object.get_each_category_total_spending_amount_of_month(year, month, include_doctor=False)
        for pair in category.fetch_all_in_order(order='id'):
            cats[pair['id']] = pair['name']
    except Exception as e:
        flash(e, 'error')
    return render_template("report/monthsummary.html", sum=sum, cat_sum=cat_sum, cats=cats, month=month, year=year)


@bp.route('/<int:year>')
def view_annual_summary(year):
    sum = {}
    allAmount = 0
    spending_object = Spending()
    try:
        sum = spending_object.get_total_spending_amount_of_each_month(year, include_doctor=False)
        allAmount = spending_object.get_total_spending_of_a_year(year, include_doctor=False)
        graphJSON = interactive_annual_report(year)
        div_graph = interactive_annual_report_as_div(year)
    except Exception as e:
        flash(e, 'error')
    return render_template("report/annualReport.html", year=year, sum=sum, amount=allAmount, graphJSON=graphJSON, div_graph=div_graph)


@bp.route('/docSpending')
def view_doc_summary():
    doctor_spending_object = DoctorSpending()
    doc_annual_sum, doc_mon_sum = 0, 0
    doc_spending = {}
    try:
        doc_spending = doctor_spending_object.fetch_doctor_spending()
        doc_annual_sum = doctor_spending_object.get_total_amount_of_doctor_spending()
        doc_mon_sum = doctor_spending_object.get_doctor_spending_of_each_month()
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
    card_object = Card()
    degree_object = Degree()
    spending_object = Spending()

    try:
        transactions = spending_object.fetch_all_spending_of_category_in_month(year, month, category)
        totalSpending = spending_object.get_total_spending_amount_of_month(year, month, category)
        catNm = category_object.fetch_one_by_id(category)['name']
        subCat = sub_category.fetch_all_subcategories_in_category(category)
        for pair in subCat:
            subs[pair['id']] = pair['name']
        for pair in card_object.fetch_all_in_order(order='id'):
            cards[pair['id']] = pair['name']
        for pair in degree_object.fetch_all_in_order(order='id'):
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
    card_object = Card()
    degree_object = Degree()
    doctor_spending_object = DoctorSpending()

    try:
        transactions = doctor_spending_object.fetch_doctor_spending()
        monthSummary = doctor_spending_object.get_doctor_spending_of_each_month()
        totalSpending = doctor_spending_object.get_total_amount_of_doctor_spending()
        subCat = sub_category.fetch_all_subcategories_in_category(16)
        for pair in subCat:
            subs[pair['id']] = pair['name']
        for pair in card_object.fetch_all_in_order(order='id'):
            cards[pair['id']] = pair['name']
        for pair in degree_object.fetch_all_in_order(order='id'):
            degrees[pair['id']] = pair['name']
    except Exception as e:
        flash(e, 'error')
    return render_template("report/doctorSummary.html", transactions=transactions, monthSummary=monthSummary,
                           totalSpending=totalSpending, subs=subs, cards=cards, degrees=degrees)
