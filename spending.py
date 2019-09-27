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


def get_subCategory(sub_id=0, fet_all=True):
    if fet_all:
        subCat = get_db().execute(
            'SELECT id, name, c_id, default_card, default_degree'
            ' FROM sub_categories'
            ' ORDER BY name'
        ).fetchall()
    else:
        subCat = get_db().execute(
            'SELECT id, name, c_id, default_card, default_degree'
            ' FROM sub_categories'
            ' WHERE id = ?',
            (sub_id,)
        ).fetchone()

    if subCat is None:
        abort(404, "Sub-Category id {0} doesn't exist.".format(sub_id))

    return subCat


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


@bp.route('/add', methods=('GET', 'POST'))
def spending_add():
    if request.method == 'POST':
        name = request.form['name']
        amount = request.form['amount']
        sub_id = request.form['sub_category']
        cat_id = get_subCategory(sub_id, False)['c_id']
        date = request.form['date']
        card_id = request.form['card']
        degree_id = request.form['degree']
        comments = request.form['comments']
        mode = request.form['mode']

        year = int(date[-4:])
        month = int(date[:2])
        day = int(date[3:5])
        flash("This will be executed")
        error = None

        if not name:
            error = "The spending name is required!!!"
        if not cat_id:
            error = "The Category is required!!!"
        if not sub_id:
            error = "The Sub Category is required!!!"
        if not date:
            error = "The Date is required!!!"
        if not card_id:
            error = "The Card is required!!!"
        if not degree_id:
            error = "The Degree is required!!!"

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO spending (name, amount, category, sub_category, yr, mon, daynum, card, degree, comments)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (name, amount, cat_id, sub_id, year, month, day, card_id, degree_id, comments)
            )
            db.commit()
            if mode == 'com': # Add and Complete
                return redirect(url_for('index.index'))
            elif mode == 'aaa': # Add and Another
                return redirect(url_for('spending.spending_add'))
    else:
        cats = get_category()
        subCats = get_subCategory()
        cards = get_card()
        degrees = get_degree()
        settings = {'cats': cats, 'subCats': subCats, 'cards': cards, 'degrees': degrees}
        return render_template('spending/add_spending.html', settings=settings)


