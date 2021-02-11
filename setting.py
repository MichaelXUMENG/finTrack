from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)

from finTrack.db import rollback_database, commit_database
from .db_utils import Category, SubCategory, Card, Degree

bp = Blueprint('setting', __name__, url_prefix='/setting')


@bp.route('/')
def catalog():
    try:
        categories = Category().fetch_all_in_order()
        sub_categories = SubCategory().fetch_all_in_order()
        cards = Card().fetch_all_in_order(order='bank, name')
        degrees = Degree().fetch_all_in_order(order='id')

        settings = {'cat': categories, 'sub': sub_categories, 'card': cards, 'degree': degrees}

        commit_database()
        return render_template('setting/catalog.html', settings=settings)
    except Exception as e:
        flash(e, 'error')

        rollback_database()
        return redirect(url_for('index.index'))


@bp.route('/category/add', methods=('GET', 'POST'))
def category_add():
    if request.method == 'GET':
        return render_template('setting/add_category.html')

    cat_name = request.form.get('name', '')
    if not cat_name.strip():
        flash('No Category name!', 'error')
        return redirect(url_for('setting.catalog'))

    category_object = Category()
    category_object.name = cat_name
    try:
        category_object.add_a_category()
        flash('Category added!', 'success')

        commit_database()

    except Exception as e:
        flash(e, 'error')

        rollback_database()

    return redirect(url_for('setting.catalog'))


@bp.route('/category/<int:cid>/view')
def category_view(cid):
    try:
        category = Category().fetch_one_by_id(cid)

        commit_database()
        return render_template('setting/view/view_category.html', category=category)
    except Exception as e:
        flash(e, 'error')

        rollback_database()
        return redirect(url_for('setting.catalog'))


@bp.route('/category/<int:cid>/edit', methods=('GET', 'POST'))
def category_edit(cid):
    category_object = Category()

    if request.method == 'GET':
        try:
            category = category_object.fetch_one_by_id(cid)

            commit_database()
            return render_template('setting/edit/edit_category.html', category=category)
        except Exception as e:
            flash(e, 'error')

            rollback_database()
            return redirect(url_for('setting.category_view', cid=cid))

    cat_name = request.form.get('name', '')
    if not cat_name.strip():
        flash('No Category name!', 'error')
        return redirect(url_for('setting.category_view', cid=cid))

    category_object.name = cat_name
    category_object.id = cid
    try:
        category_object.update_category()
        flash('Category updated!', 'success')

        commit_database()
    except Exception as e:
        flash(e, 'error')

        rollback_database()

    return redirect(url_for('setting.category_view', cid=cid))


@bp.route('/<int:cid>/sub-category/add', methods=('GET', 'POST'))
def sub_category_add(cid):
    if request.method == 'GET':
        try:
            category = Category().fetch_one_by_id(cid)
            cards = Card().fetch_all_in_order(order='bank, name')
            degrees = Degree().fetch_all_in_order(order='id')

            commit_database()
            return render_template('setting/add_subcategory.html', category=category, cards=cards, degrees=degrees)
        except Exception as e:
            flash(e, 'error')

            rollback_database()
            return redirect(url_for('setting.catalog'))

    sub_category_object = SubCategory()

    try:
        sub_category_object.load_a_sub_category(request.form)
        sub_category_object.add_a_sub_category()

        flash('Sub-category added!', 'success')
        commit_database()
    except Exception as e:
        flash(e, 'error')
        rollback_database()

    return redirect(url_for('setting.catalog'))


@bp.route('/sub-category/<int:sid>/view')
def sub_category_view(sid):
    try:
        sub_category = SubCategory().fetch_one_by_id(sid)
        sub_cat_dict = dict(sub_category)
        sub_cat_dict['c_name'] = Category().fetch_one_by_id(sub_category['c_id'])['name']
        sub_cat_dict['default_card'] = Card().get_a_card_name(sub_category['default_card'])
        sub_cat_dict['default_degree'] = Degree().get_a_degree_name(sub_category['default_degree'])

        commit_database()
        return render_template('setting/view/view_subcategory.html', sub_category=sub_cat_dict)
    except Exception as e:
        flash(e, 'error')

        rollback_database()
        return redirect(url_for('setting.catalog'))


@bp.route('/sub-category/<int:sid>/edit', methods=('GET', 'POST'))
def sub_category_edit(sid):
    sub_category_object = SubCategory()

    if request.method == 'GET':
        try:
            sub_category = sub_category_object.fetch_one_by_id(sid)
            categories = Category().fetch_all_in_order()
            cards = Card().fetch_all_in_order(order='bank, name')
            degrees = Degree().fetch_all_in_order(order='id')

            commit_database()
            return render_template('setting/edit/edit_subcategory.html',
                                   sub_category=sub_category, category=categories, cards=cards, degrees=degrees)
        except Exception as e:
            flash(e, 'error')

            rollback_database()
            return redirect(url_for('setting.sub_category_view', sid=sid))

    try:
        sub_category_object.load_a_sub_category(request.form)
        sub_category_object.id = sid
        sub_category_object.update_sub_category()

        flash('Sub-category updated!', 'success')

        commit_database()
    except Exception as e:
        flash(e, 'error')
        rollback_database()

    return redirect(url_for('setting.sub_category_view', sid=sid))


@bp.route('/card/add', methods=('GET', 'POST'))
def card_add():
    if request.method == 'GET':
        return render_template('setting/add_card.html')

    card_object = Card()
    try:
        card_object.load_a_card(request.form)
        card_object.add_a_new_card()
        flash('A new card added!', 'success')

        commit_database()
    except Exception as e:
        flash(e, 'error')

        rollback_database()

    return redirect(url_for('setting.catalog'))


@bp.route('/card/<int:card_id>/view')
def card_view(card_id):
    try:
        card = Card().fetch_one_by_id(card_id)

        commit_database()
        return render_template('setting/view/view_card.html', card=card)
    except Exception as e:
        flash(e, 'error')

        rollback_database()
        return redirect(url_for('setting.catalog'))


@bp.route('/card/<int:card_id>/edit', methods=('GET', 'POST'))
def card_edit(card_id):
    card_object = Card()
    card_object.id = card_id
    if request.method == 'GET':
        try:
            card = card_object.fetch_one_by_id(card_id)

            commit_database()
            return render_template('setting/edit/edit_card.html', card=card)
        except Exception as e:
            flash(e, 'error')

            rollback_database()
            return redirect(url_for('setting.card_view', card_id=card_id))

    try:
        card_object.load_a_card(request.form)
        card_object.update_card_information()
        flash('Card information updated!', 'success')

        commit_database()

    except Exception as e:
        flash(e, 'error')
        rollback_database()

    return redirect(url_for('setting.card_view', card_id=card_id))


@bp.route('/degree/add', methods=('GET', 'POST'))
def degree_add():
    if request.method == 'GET':
        return render_template('setting/add_degree.html')

    degree_object = Degree()
    degree_object.name = request.form.get('name', '')
    if not degree_object.name.strip():
        flash('No Degree name!', 'error')
        return redirect(url_for('setting.catalog'))

    try:
        degree_object.add_a_degree()
        flash('A new degree added!', 'success')

        commit_database()
    except Exception as e:
        flash(e, 'error')

        rollback_database()

    return redirect(url_for('setting.catalog'))


@bp.route('/degree/<int:degree_id>/view')
def degree_view(degree_id):
    try:
        degree = Degree().fetch_one_by_id(degree_id)

        commit_database()
        return render_template('setting/view/view_degree.html', degree=degree)
    except Exception as e:
        flash(e, 'error')

        rollback_database()
        return redirect(url_for('setting.catalog'))


@bp.route('/degree/<int:degree_id>/edit', methods=('GET', 'POST'))
def degree_edit(degree_id):
    degree_object = Degree()
    degree_object.id = degree_id

    if request.method == 'GET':
        try:
            degree = degree_object.fetch_one_by_id(degree_id)

            commit_database()
            return render_template('setting/edit/edit_degree.html', degree=degree)
        except Exception as e:
            flash(e, 'error')

            rollback_database()
            return redirect(url_for('setting.degree_view', degree_id=degree_id))

    try:
        degree_object.name = request.form.get('name', '')
        degree_object.update_degree()
        flash('Degree got updated!', 'success')

        commit_database()
    except Exception as e:
        flash(e, 'error')

        rollback_database()

    return redirect(url_for('setting.degree_view', degree_id=degree_id))
