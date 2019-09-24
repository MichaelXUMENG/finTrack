import functools
from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort
from finTrack.db import get_db

bp = Blueprint('setting', __name__, url_prefix='/setting')


def get_category(cat_id=0, fet_all=True, order='name'):
    if fet_all:
        cat = get_db().execute(
            'SELECT id, name'
            ' FROM categories'
            ' ORDER BY ?',
            (order, )
        ).fetchall()
    else:
        cat = get_db().execute(
            'SELECT id, name'
            ' FROM categories'
            ' WHERE id = ?',
            (cat_id,)
        ).fetchone()

    if cat is None:
        abort(404, "Category id {0} doesn't exist.".format(cat_id))

    return cat


def get_subCategory(sub_id=0, fet_all=True, order='name'):
    if fet_all:
        subCat = get_db().execute(
            'SELECT id, name, cid, default_card, default_degree'
            ' FROM sub_categories'
            ' ORDER BY ?',
            (order, )
        ).fetchall()
    else:
        subCat = get_db().execute(
            'SELECT id, name, cid, default_card, default_degree'
            ' FROM sub_categories'
            ' WHERE id = ?',
            (sub_id,)
        ).fetchone()

    if subCat is None:
        abort(404, "Sub-Category id {0} doesn't exist.".format(sub_id))

    return subCat


def get_card(card_id=0, fet_all=True, order='name'):
    if fet_all:
        card = get_db().execute(
            'SELECT id, name, bank, cur_balance, pay_date'
            ' FROM cards'
            ' ORDER BY ?',
            (order, )
        ).fetchall()
    else:
        card = get_db().execute(
            'SELECT id, name, bank, cur_balance, pay_date'
            ' FROM cards'
            ' WHERE id = ?',
            (card_id,)
        ).fetchone()

    if card is None:
        abort(404, "Card id {0} doesn't exist.".format(card_id))

    return card


def get_degree(card_id=0, fet_all=True, order='name'):
    if fet_all:
        degree = get_db().execute(
            'SELECT id, name'
            ' FROM degrees'
            ' ORDER BY ?',
            (order, )
        ).fetchall()
    else:
        degree = get_db().execute(
            'SELECT id, name'
            ' FROM degrees'
            ' WHERE id = ?',
            (card_id,)
        ).fetchone()

    if degree is None:
        abort(404, "Degree id {0} doesn't exist.".format(card_id))

    return degree


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


@bp.route('/category/<int:cid>/view')
def category_view(cid):
    db = get_db()
    cat = db.execute(
        'SELECT id, name'
        ' FROM categories'
        ' WHERE id = ?',
        (cid,)
    ).fetchone()
    return render_template('setting/view/view_category.html', category=cat)


@bp.route('/category/<int:cid>/edit', methods=('GET', 'POST'))
def category_edit(cid):
    if request.method == 'POST':
        cat_id = request.form['id']
        cat_name = request.form['name']
        error = None

        if not cat_name:
            error = 'Category Name is Required!'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE categories SET name = ?'
                ' WHERE id = ?',
                (cat_id, cat_name)
            )
            db.commit()
            return redirect(url_for('setting.catalog'))


@bp.route('/<int:cid>/sub-category/add', methods=('GET', 'POST'))
def sub_category_add(cid):
    if request.method == 'POST':
        sub_name = request.form['name']
        cat_id = request.form['c_id']
        card = request.form['default_card']
        degree = request.form['default_degree']
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
                'INSERT INTO sub_categories (name, c_id, default_card, default_degree)'
                ' VALUES (?, ?, ?, ?)',
                (sub_name, cat_id, card, degree)
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
        cards = db.execute(
            'SELECT id, name'
            ' FROM cards'
            ' ORDER BY bank, name',
        ).fetchall()
        degrees = db.execute(
            'SELECT id, name'
            ' FROM degrees'
            ' ORDER BY name',
        ).fetchall()
        return render_template('setting/add_subcategory.html', category=cat, cards=cards, degrees=degrees)


@bp.route('/sub-category/<int:sid>/view')
def sub_category_view(sid):
    db = get_db()
    sub = db.execute(
        'SELECT s.id, s.name, c.name AS c_name, default_card, default_degree'
        ' FROM sub_categories AS s LEFT JOIN categories AS c on s.c_id=c.id'
        ' WHERE s.id = ?',
        (sid,)
    ).fetchone()
    subCat=dict(sub)
    if subCat['default_card']:
        card = db.execute(
            'SELECT id, name'
            ' FROM cards'
            ' WHERE id = ?',
            (subCat['default_card'],)
        ).fetchone()
        subCat['default_card'] = card['name']
    if subCat['default_degree']:
        degree = db.execute(
            'SELECT id, name'
            ' FROM degrees'
            ' WHERE id = ?',
            (subCat['default_degree'],)
        ).fetchone()
        subCat['default_degree'] = degree['name']
    return render_template('setting/view/view_subcategory.html', sub_category=subCat)


@bp.route('/card/add', methods=('GET', 'POST'))
def card_add():
    if request.method == 'POST':
        card_name = request.form['name']
        bank_name = request.form['bank']
        pay_date = request.form['pay_day']
        balance = request.form['balance']
        error = None

        if not card_name:
            error = 'Card Name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO cards (name, bank, cur_balance, pay_date)'
                ' VALUES (?, ?, ?, ?)',
                (card_name, bank_name, balance, pay_date)
            )
            db.commit()
            return redirect(url_for('setting.catalog'))
    return render_template('setting/add_card.html')


@bp.route('/card/<int:id>/view')
def card_view(id):
    db = get_db()
    card = db.execute(
        'SELECT id, bank, name, cur_balance, pay_date'
        ' FROM cards'
        ' WHERE id = ?',
        (id,)
    ).fetchone()
    return render_template('setting/view/view_card.html', card=card)


@bp.route('/degree/add', methods=('GET', 'POST'))
def degree_add():
    if request.method == 'POST':
        degree_name = request.form['name']
        error = None

        if not degree_name:
            error = 'Degree Name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO degrees (name)'
                ' VALUES (?)',
                (degree_name,)
            )
            db.commit()
            return redirect(url_for('setting.catalog'))
    return render_template('setting/add_degree.html')


@bp.route('/degree/<int:id>/view')
def degree_view(id):
    db = get_db()
    degree = db.execute(
        'SELECT id, name'
        ' FROM degrees'
        ' WHERE id = ?',
        (id,)
    ).fetchone()
    return render_template('setting/view/view_degree.html', degree=degree)
