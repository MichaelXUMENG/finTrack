import functools
from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort
from finTrack.db import get_db

bp = Blueprint('setting', __name__, url_prefix='/setting')


def get_category(cat_id=0, fet_all=True):
    if fet_all:
        cat = get_db().execute(
            'SELECT id, name'
            ' FROM categories'
            ' ORDER BY name'
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


def get_card(card_id=0, fet_all=True):
    if fet_all:
        card = get_db().execute(
            'SELECT id, name, bank, cur_balance, pay_date'
            ' FROM cards'
            ' ORDER BY bank, name'
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


def get_degree(card_id=0, fet_all=True):
    if fet_all:
        degree = get_db().execute(
            'SELECT id, name'
            ' FROM degrees'
            ' ORDER BY name'
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
    categories = get_category()
    sub_categories = get_subCategory()
    cards = get_card()
    degrees = get_degree()

    settings = {'cat': categories, 'sub': sub_categories, 'card': cards, 'degree': degrees}
    return render_template('setting/catalog.html', settings=settings)


@bp.route('/category/add', methods=('GET', 'POST'))
def category_add():
    if request.method == 'POST':
        cat_name = request.form['name']

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
    cat = get_category(cid, False)
    return render_template('setting/view/view_category.html', category=cat)


@bp.route('/category/<int:cid>/edit', methods=('GET', 'POST'))
def category_edit(cid):
    cat = get_category(cid, False)
    if request.method == 'POST':
        cat_name = request.form['name']

        db = get_db()
        db.execute(
            'UPDATE categories SET name = ?'
            ' WHERE id = ?',
            (cat_name, cid)
        )
        db.commit()
        return redirect(url_for('setting.category_view', cid=cid))
    else:
        return render_template('setting/edit/edit_category.html', category=cat)


@bp.route('/<int:cid>/sub-category/add', methods=('GET', 'POST'))
def sub_category_add(cid):
    if request.method == 'POST':
        sub_name = request.form['name']
        cat_id = request.form['c_id']
        card = request.form['default_card']
        degree = request.form['default_degree']

        db = get_db()
        db.execute(
            'INSERT INTO sub_categories (name, c_id, default_card, default_degree)'
            ' VALUES (?, ?, ?, ?)',
            (sub_name, cat_id, card, degree)
        )
        db.commit()
        return redirect(url_for('setting.catalog'))
    else:
        cat = get_category(cid, False)
        cards = get_card()
        degrees = get_degree()
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
    subCat = dict(sub)
    if subCat['default_card']:
        card = get_card(subCat['default_card'], False)
        subCat['default_card'] = card['name'] + ' - ' + card['bank']
    if subCat['default_degree']:
        degree = get_degree(subCat['default_degree'], False)
        subCat['default_degree'] = degree['name']
    return render_template('setting/view/view_subcategory.html', sub_category=subCat)


@bp.route('/sub-category/<int:sid>/edit', methods=('GET', 'POST'))
def sub_category_edit(sid):
    if request.method == 'POST':
        sub_name = request.form['name']
        cat_id = request.form['c_id']
        card = request.form['default_card']
        degree = request.form['default_degree']

        db = get_db()
        db.execute(
            'UPDATE sub_categories SET name = ?, c_id=?, default_card=?, default_degree=?'
            ' WHERE id = ?',
            (sub_name, cat_id, card, degree, sid)
        )
        db.commit()
        return redirect(url_for('setting.sub_category_view', sid=sid))
    else:
        subCat = get_subCategory(sid, False)
        cat = get_category()
        cards = get_card()
        degrees = get_degree()
        return render_template('setting/edit/edit_subcategory.html',
                               sub_category=subCat, category=cat, cards=cards, degrees=degrees)


@bp.route('/card/add', methods=('GET', 'POST'))
def card_add():
    if request.method == 'POST':
        card_name = request.form['name']
        bank_name = request.form['bank']
        pay_date = int(request.form['pay_day'])
        balance = int(request.form['balance'])

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
    card = get_card(id, False)
    return render_template('setting/view/view_card.html', card=card)


@bp.route('/card/<int:id>/edit', methods=('GET', 'POST'))
def card_edit(id):
    card = get_card(id, False)
    if request.method == 'POST':
        card_name = request.form['name']
        bank_name = request.form['bank']
        pay_date = int(request.form['pay_day'])
        balance = int(request.form['balance'])

        db = get_db()
        db.execute(
            'UPDATE cards SET name = ?, bank=?, cur_balance=?, pay_date=?'
            ' WHERE id = ?',
            (card_name, bank_name, pay_date, balance, id)
        )
        db.commit()
        return redirect(url_for('setting.card_view', id=id))
    else:
        return render_template('setting/edit/edit_card.html', card=card)


@bp.route('/degree/add', methods=('GET', 'POST'))
def degree_add():
    if request.method == 'POST':
        degree_name = request.form['name']

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
    degree = get_degree(id, False)
    return render_template('setting/view/view_degree.html', degree=degree)


@bp.route('/degree/<int:id>/edit', methods=('GET', 'POST'))
def degree_edit(id):
    degree = get_degree(id, False)
    if request.method == 'POST':
        degree_name = request.form['name']

        db = get_db()
        db.execute(
            'UPDATE degrees SET name = ?'
            ' WHERE id = ?',
            (degree_name, id)
        )
        db.commit()
        return redirect(url_for('setting.degree_view', id=id))
    else:
        return render_template('setting/edit/edit_degree.html', degree=degree)
