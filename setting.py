import functools
from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from .db_utils import (
    get_all_category, get_one_category, get_all_subCategory, get_one_subCategory, get_all_cards, get_one_card,
    get_all_degrees, get_one_degree
)
from finTrack.db import get_db

bp = Blueprint('setting', __name__, url_prefix='/setting')


@bp.route('/')
def catalog():
    categories = get_all_category()
    sub_categories = get_all_subCategory()
    cards = get_all_cards()
    degrees = get_all_degrees()

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
    cat = get_one_category(cid)
    return render_template('setting/view/view_category.html', category=cat)


@bp.route('/category/<int:cid>/edit', methods=('GET', 'POST'))
def category_edit(cid):
    cat = get_one_category(cid)
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
        cat = get_one_category(cid)
        cards = get_all_cards()
        degrees = get_all_degrees()
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
        card = get_one_card(subCat['default_card'])
        subCat['default_card'] = card['name'] + ' - ' + card['bank']
    if subCat['default_degree']:
        degree = get_one_degree(subCat['default_degree'])
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
        subCat = get_one_subCategory(sid)
        cat = get_all_category()
        cards = get_all_cards()
        degrees = get_all_degrees()
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
    card = get_one_card(id)
    return render_template('setting/view/view_card.html', card=card)


@bp.route('/card/<int:id>/edit', methods=('GET', 'POST'))
def card_edit(id):
    card = get_one_card(id)
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
    degree = get_one_degree(id)
    return render_template('setting/view/view_degree.html', degree=degree)


@bp.route('/degree/<int:id>/edit', methods=('GET', 'POST'))
def degree_edit(id):
    degree = get_one_degree(id)
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
