from flask import (
    Blueprint, flash, render_template, redirect, url_for
)
from .db import commit_database, rollback_database
from .db_utils import Category, SubCategory, Card, Degree, Spending, DoctorSpending
from .interactive_graphs import interactive_annual_report, interactive_annual_report_as_div

bp = Blueprint('report', __name__, url_prefix='/report')


@bp.route('/')
def catalog():
    try:
        years = Spending().get_years()
        cards = Card().fetch_all_in_order(order='id')

        commit_database()

        return render_template('report/catalog.html', years=years, cards=cards)
    except Exception as e:
        flash(e, 'error')

        rollback_database()

        return redirect(url_for('index.index'))


@bp.route('/viewall')
def view_all_spending():
    try:
        spendings = Spending().fetch_all_category_spending(include_doctor=False)
        categories = {pair['id']: pair['name'] for pair in Category().fetch_all_in_order(order='id')}
        sub_categories = {pair['id']: pair['name'] for pair in SubCategory().fetch_all_in_order(order='id')}
        cards = {pair['id']: pair['name'] for pair in Card().fetch_all_in_order(order='id')}
        degrees = {pair['id']: pair['name'] for pair in Degree().fetch_all_in_order(order='id')}

        commit_database()

        return render_template("report/allspending.html", spendings=spendings, cats=categories, subs=sub_categories,
                               cards=cards, degrees=degrees)
    except Exception as e:
        flash(e, 'error')

        rollback_database()

        return redirect(url_for('report.catalog'))


@bp.route('/<int:card_id>/viewall')
def view_all_spending_card(card_id):
    try:
        spendings = Spending().fetch_all_spendings_from_a_card(card_id, include_doctor=False)
        categories = {pair['id']: pair['name'] for pair in Category().fetch_all_in_order(order='id')}
        sub_categories = {pair['id']: pair['name'] for pair in SubCategory().fetch_all_in_order(order='id')}
        cards = {pair['id']: pair['name'] for pair in Card().fetch_all_in_order(order='id')}
        degrees = {pair['id']: pair['name'] for pair in Degree().fetch_all_in_order(order='id')}

        commit_database()

        return render_template("report/cardspending.html", spendings=spendings, cats=categories, subs=sub_categories,
                               cards=cards, card_id=card_id, degrees=degrees)
    except Exception as e:
        flash(e, 'error')

        rollback_database()

        return redirect(url_for('report.catalog'))


@bp.route('/<int:card_id>/addcardspending')
def add_spending_card(card_id):
    try:
        spendings = Spending().fetch_all_spendings_from_a_card(card_id)
        categories = {pair['id']: pair['name'] for pair in Category().fetch_all_in_order(order='id')}
        sub_categories = {pair['id']: pair['name'] for pair in SubCategory().fetch_all_in_order(order='id')}
        cards = {pair['id']: pair['name'] for pair in Card().fetch_all_in_order(order='id')}
        degrees = {pair['id']: pair['name'] for pair in Degree().fetch_all_in_order(order='id')}

        commit_database()

        return render_template("report/cardspending.html", spendings=spendings, cats=categories, subs=sub_categories,
                               cards=cards, card_id=card_id, degrees=degrees)
    except Exception as e:
        flash(e, 'error')

        rollback_database()

        return redirect(url_for('report.catalog'))


@bp.route('/<int:year>/<int:month>')
def view_monthly_summary(year, month):
    try:
        total_amount = Spending().get_total_spending_amount_of_month(year, month)
        total_amount_category = Spending().get_each_category_total_spending_amount_of_month(year, month, include_doctor=False)
        categories = {pair['id']: pair['name'] for pair in Category().fetch_all_in_order(order='id')}

        commit_database()

        return render_template("report/monthsummary.html", sum=total_amount, cat_sum=total_amount_category,
                               cats=categories, month=month, year=year)
    except Exception as e:
        flash(e, 'error')

        rollback_database()

        return redirect(url_for('report.catalog'))


@bp.route('/<int:year>')
def view_annual_summary(year):
    try:
        monthly_amount = Spending().get_total_spending_amount_of_each_month(year, include_doctor=False)
        annual_amount = Spending().get_total_spending_of_a_year(year, include_doctor=False)
        graphJSON = interactive_annual_report(year)
        div_graph = interactive_annual_report_as_div(year)

        commit_database()

        return render_template("report/annualReport.html", year=year, sum=monthly_amount, amount=annual_amount,
                               graphJSON=graphJSON, div_graph=div_graph)
    except Exception as e:
        flash(e, 'error')

        rollback_database()

        return redirect(url_for('report.catalog'))


@bp.route('/docSpending')
def view_doc_summary():
    try:
        doc_spending = DoctorSpending().fetch_doctor_spending()
        doc_annual_sum = DoctorSpending().get_total_amount_of_doctor_spending()
        doc_monthly_sum = DoctorSpending().get_doctor_spending_of_each_month()

        commit_database()

        return render_template("report/docReport.html", doc_spending=doc_spending, doc_annual_sum=doc_annual_sum,
                               doc_mon_sum=doc_monthly_sum)
    except Exception as e:
        flash(e, 'error')

        rollback_database()

        return redirect(url_for('report.catalog'))


@bp.route('/<int:year>/<int:month>/<int:category_id>')
def monthlyCatTransaction(year, month, category_id):
    try:
        transactions = Spending().fetch_all_spending_of_category_in_month(year, month, category_id)
        total_month_amount = Spending().get_total_spending_amount_of_month(year, month, category_id)
        category_name = Category().fetch_one_by_id(category_id)['name']

        sub_categories = {pair['id']: pair['name'] for pair in SubCategory().fetch_all_subcategories_in_category(category_id)}
        cards = {pair['id']: pair['name'] for pair in Card().fetch_all_in_order(order='id')}
        degrees = {pair['id']: pair['name'] for pair in Degree().fetch_all_in_order(order='id')}

        commit_database()

        return render_template("report/monthCatTransaction.html", transactions=transactions, catNm=category_name,
                               subs=sub_categories, cards=cards, degrees=degrees, year=year, month=month,
                               totalSpending=total_month_amount)
    except Exception as e:
        flash(e, 'error')

        rollback_database()

        return redirect(url_for('report.catalog'))


@bp.route('/doctor')
def doctorSummary():
    try:
        transactions = DoctorSpending().fetch_doctor_spending()
        monthly_amount = DoctorSpending().get_doctor_spending_of_each_month()
        total_amount = DoctorSpending().get_total_amount_of_doctor_spending()

        sub_categories = {pair['id']: pair['name'] for pair in SubCategory().fetch_all_subcategories_in_category(16)}
        cards = {pair['id']: pair['name'] for pair in Card().fetch_all_in_order(order='id')}
        degrees = {pair['id']: pair['name'] for pair in Degree().fetch_all_in_order(order='id')}

        commit_database()

        return render_template("report/doctorSummary.html", transactions=transactions, monthSummary=monthly_amount,
                               totalSpending=total_amount, subs=sub_categories, cards=cards, degrees=degrees)
    except Exception as e:
        flash(e, 'error')

        rollback_database()

        return redirect(url_for('report.catalog'))
