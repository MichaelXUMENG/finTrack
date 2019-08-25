import functools
from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort
from finTrack.db import get_db

bp = Blueprint('setting', __name__, url_prefix='/setting')


@bp.route('/')
def catalog():
    db = get_db()
    categories = db.execute(
        'SELECT id, name'
        ' FROM categories'
        ' ORDER BY name'
    ).fetchall()
    sub_categories = db.execute(
        'SELECT id, name, c_id'
        ' FROM sub_categories'
        ' ORDER BY name'
    ).fetchall()
    cards = db.execute(
        'SELECT id, name, cur_balance, pay_date'
        ' FROM cards'
        ' ORDER BY name'
    ).fetchall()
    degrees = db.execute(
        'SELECT id, name'
        ' FROM degrees'
        ' ORDER BY name'
    ).fetchall()
    settings = {'cat':categories, 'sub':sub_categories, 'card':cards, 'degree':degrees}
    return render_template('setting/catalog.html', settings=settings)


@bp.route('/category/add', methods=('GET', 'POST'))
def category_add():
    if request.method == 'POST':
        cat_name = request.form['name']
        flash(cat_name)
        error = None

        if not cat_name:
            error = "Name is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO categories (name)'
                ' VALUES (?)',
                (cat_name,)
            )
            db.commit()
            return redirect(url_for('setting.catalog'))
    return render_template('setting/add_category.html')


@bp.route('/<int:cid>/sub-category/add', methods=('GET', 'POST'))
def sub_category_add(cid):
    if request.method == 'POST':
        sub_name = request.form['name']
        cat_id = request.form['c_id']
        error = None

        if not sub_name:
            error = "Name is required."
        if not cat_id:
            error = "Must link to a Category"

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO sub_categories (name, c_id)'
                ' VALUES (?, ?)',
                (sub_name, cat_id)
            )
            db.commit()
            return redirect(url_for('setting.catalog'))
    else:
        db = get_db()
        cat = db.execute(
            'SELECT id, name'
            ' FROM categories'
            ' WHERE id = ?',
            (cid,)
        ).fetchone()
    return render_template('setting/add_subcategory.html', category=cat)
