import functools
from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from .db_utils import (
    get_all_category, get_all_subCategory, get_one_subCategory, get_all_cards, get_one_card,
    get_all_degrees, get_one_spending
)
from finTrack.db import get_db

bp = Blueprint('spending', __name__, url_prefix='/spending')


@bp.route('/add', methods=('GET', 'POST'))
def spending_add():
    if request.method == 'POST':
        name = request.form['name']
        amount = float(request.form['amount'])
        sub_id = request.form['sub_category']
        cat_id = get_one_subCategory(sub_id)['c_id']
        date = request.form['date']
        card_id = request.form['card']
        degree_id = request.form['degree']
        comments = request.form['comments']
        mode = request.form['mode']

        year = int(date[-4:])
        if '/' in date:
            mbar = date.index('/')
            month = int(date[:mbar])
            dbar = date[mbar+1:].index('/')
            day = int(date[mbar+1:mbar+dbar+1])
        else:
            mbar = date.index('-')
            month = int(date[:mbar])
            dbar = date[mbar + 1:].index('-')
            day = int(date[mbar + 1:mbar + dbar + 1])

        try:
            balance = get_one_card(card_id)['cur_balance']
            balance += amount

            db = get_db()
            db.execute(
                'INSERT INTO spending (name, amount, category, sub_category, yr, mon, daynum, card, degree, comments)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (name, amount, cat_id, sub_id, year, month, day, card_id, degree_id, comments)
            )
            db.execute(
                'UPDATE cards SET cur_balance = ?'
                ' WHERE id = ?',
                (balance, card_id)
            )
            db.commit()
            flash('A spending is added!', 'success')
        except Exception as e:
            flash(e, 'error')
        finally:
            if mode == 'com': # Add and Complete
                return redirect(url_for('index.index'))
            elif mode == 'aaa': # Add and Another
                return redirect(url_for('spending.spending_add'))
    else:
        try:
            cats = get_all_category()
            subCats = get_all_subCategory()
            cards = get_all_cards()
            degrees = get_all_degrees()
            settings = {'cats': cats, 'subCats': subCats, 'cards': cards, 'degrees': degrees}
            return render_template('spending/add_spending.html', settings=settings)
        except Exception as e:
            flash(e, 'error')
            return redirect(url_for('index.index'))


@bp.route('/<int:card>/add', methods=('GET', 'POST'))
def spending_add_from_card(card):
    if request.method == 'POST':
        name = request.form['name']
        amount = float(request.form['amount'])
        sub_id = request.form['sub_category']
        cat_id = get_one_subCategory(sub_id)['c_id']
        date = request.form['date']
        degree_id = request.form['degree']
        comments = request.form['comments']
        mode = request.form['mode']

        year = int(date[-4:])
        if '/' in date:
            mbar = date.index('/')
            month = int(date[:mbar])
            dbar = date[mbar + 1:].index('/')
            day = int(date[mbar + 1:mbar + dbar + 1])
        else:
            mbar = date.index('-')
            month = int(date[:mbar])
            dbar = date[mbar + 1:].index('-')
            day = int(date[mbar + 1:mbar + dbar + 1])

        try:
            balance = get_one_card(card)['cur_balance']
            balance += amount

            db = get_db()
            db.execute(
                'INSERT INTO spending (name, amount, category, sub_category, yr, mon, daynum, card, degree, comments)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (name, amount, cat_id, sub_id, year, month, day, card, degree_id, comments)
            )
            db.execute(
                'UPDATE cards SET cur_balance = ?'
                ' WHERE id = ?',
                (balance, card)
            )
            db.commit()
            flash('A spending has been added!', 'success')
        except Exception as e:
            flash(e, 'error')
        finally:
            if mode == 'com':  # Add and Complete
                return redirect(url_for('index.index'))
            elif mode == 'aaa':  # Add and Another
                return redirect(url_for('spending.spending_add_from_card', card=card))
    else:
        try:
            cats = get_all_category()
            subCats = get_all_subCategory()
            degrees = get_all_degrees()
            card_info = get_one_card(card)
            settings = {'cats': cats, 'subCats': subCats, 'cards': card_info, 'degrees': degrees}
            return render_template('spending/add_card_spending.html', settings=settings)
        except Exception as e:
            flash(e, 'error')
            return redirect(url_for('index.index'))


@bp.route('/<int:id>/eidt/', methods=('GET', 'POST'))
def spending_edit(id):
    if request.method == 'POST':
        name = request.form['name']
        amount = float(request.form['amount'])
        sub_id = request.form['sub_category']
        cat_id = get_one_subCategory(sub_id)['c_id']
        date = request.form['date']
        card_id = request.form['card']
        degree_id = request.form['degree']
        comments = request.form['comments']

        year = int(date[-4:])
        if '/' in date:
            mbar = date.index('/')
            month = int(date[:mbar])
            dbar = date[mbar + 1:].index('/')
            day = int(date[mbar + 1:mbar + dbar + 1])
        else:
            mbar = date.index('-')
            month = int(date[:mbar])
            dbar = date[mbar + 1:].index('-')
            day = int(date[mbar + 1:mbar + dbar + 1])

        try:
            balance = get_one_card(card_id)['cur_balance']
            balance += amount

            db = get_db()
            db.execute(
                'UPDATE spending SET name=?, amount=?, category=?, sub_category=?, yr=?, mon=?, daynum=?, card=?, degree=?, comments=?'
                ' WHERE id=?',
                (name, amount, cat_id, sub_id, year, month, day, card_id, degree_id, comments, id)
            )
            db.execute(
                'UPDATE cards SET cur_balance = ?'
                ' WHERE id = ?',
                (balance, card_id)
            )
            db.commit()
            flash('Spending has been updated!', 'success')
        except Exception as e:
            flash(e, 'error')
        finally:
            return redirect(url_for('report.view_all_spending'))
    else:
        try:
            cats = get_all_category()
            subCats = get_all_subCategory()
            cards = get_all_cards()
            degrees = get_all_degrees()
            spending = get_one_spending(id)
            date = str(spending['mon'])+'/'+str(spending['daynum'])+'/'+str(spending['yr'])
            settings = {'cats': cats, 'subCats': subCats, 'cards': cards, 'degrees': degrees}
            return render_template('spending/edit_spending.html', settings=settings, spending=spending, date=date)
        except Exception as e:
            flash(e, 'error')
            return redirect(url_for('report.view_all_spending'))
