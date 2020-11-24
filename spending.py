import functools
import os
import re
import csv
from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app, after_this_request
)
from .db_utils import (
    get_all_category, get_all_subCategory, get_one_subCategory, get_all_cards, get_one_card,
    get_all_degrees, get_one_spending, get_card_by_name
)
from finTrack.db import get_db
from .read_in_pdf_statement import read_pdf_statement_chase_credit, read_pdf_statement_chase_checking
from werkzeug.utils import secure_filename
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


@bp.route('/add/statement', methods=['POST'])
def spending_add_from_statement():
    if 'statement_pdf' not in request.files:
        flash('No file part')
        return redirect(url_for('index.index'))
    card = request.form['card']
    file = request.files['statement_pdf']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index.index'))

    filename = secure_filename(file.filename)
    path_to_statement = os.path.join(current_app.config['UPLOAD_STATEMENT_FOLDER'], filename)
    file.save(path_to_statement)

    transaction_preset = os.path.join(current_app.config['UPLOAD_STATEMENT_FOLDER'],
                                      current_app.config['PRESET_FILE_NAME'])

    with open(transaction_preset, 'r') as csv_file:
        preset = {row['name']: {k: v for k, v in row.items()}
                  for row in csv.DictReader(csv_file, skipinitialspace=True)}

    inputs = []
    if card in ('Freedom - Chase', 'Unlimited - Chase', 'Sapphire - Chase'):
        inputs = read_pdf_statement_chase_credit(path_to_statement)
    elif card == 'Checking - Chase':
        inputs = read_pdf_statement_chase_checking(path_to_statement)
    # def generate():
    #     with open(path) as f:
    #         yield from f
    #
    #     os.remove(path)

    os.remove(path_to_statement)

    cats = get_all_category()
    subCats = get_all_subCategory()
    degrees = get_all_degrees()
    settings = {'cats': cats, 'subCats': subCats, 'degrees': degrees}

    return render_template('spending/add_spending_from_statement.html',
                           card=card, inputs=inputs, settings=settings, preset=preset)


@bp.route('/save_statement', methods=['POST'])
def save_statement_data():
    transaction_counts, valid_transactions = int(request.form.get('count', 0)), 0
    card_name = request.form.get('card', '')
    card = get_card_by_name(card_name)
    preset = request.form.get('card', '')

    db = get_db()
    try:
        for index in range(transaction_counts):
            single_trans = {
                'exclude': request.form.get(f'exclude{index+1}', 'False'),
                'name': request.form.get(f'name{index+1}', 'N/A'),
                'category': request.form.get(f'category{index+1}', -1),
                'amount': request.form.get(f'amount{index+1}', 0),
                'date': request.form.get(f'date{index+1}', '01/01/0101'),
                'degree': request.form.get(f'degree{index+1}', -1),
                'note': request.form.get(f'note{index+1}', ''),
            }
            if single_trans['exclude'] == 'False':
                sub_category = get_one_subCategory(single_trans['category'])
                date_match = re.fullmatch(r"([0-9]{2})/([0-9]{2})/([0-9]{4})", single_trans['date'])

                db.execute(
                    'INSERT INTO spending (name, amount, category, sub_category, yr, mon, daynum, card, degree, comments)'
                    ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (single_trans['name'], single_trans['amount'], sub_category['c_id'], single_trans['category'],
                     date_match.group(3), date_match.group(1), date_match.group(2), card['id'], single_trans['degree'],
                     single_trans['note'])
                )
                valid_transactions += 1
                if single_trans['name'] not in preset:
                    preset[single_trans['name']] = {'name': single_trans['name'],
                                                    'category': single_trans['category'],
                                                    'degree': single_trans['degree']}
        db.commit()

        # save the preset back to the preset file.
        if preset:
            transaction_preset = os.path.join(current_app.config['UPLOAD_STATEMENT_FOLDER'],
                                              current_app.config['PRESET_FILE_NAME'])
            sample_entrys = list(preset.keys())
            dict_list = []
            for entry in sample_entrys:
                dict_list.append(preset[entry])
            keys = preset[sample_entrys[0]].keys()

            with open(transaction_preset, 'w', newline='') as output_file:
                dict_writer = csv.DictWriter(output_file, keys)
                dict_writer.writeheader()
                dict_writer.writerows(dict_list)

        flash(f'{valid_transactions} spendings are added!', 'success')
        return redirect(url_for('report.add_spending_card', card=card['id']))
    except TypeError as e:
        flash(e, 'error')
        db.rollback()
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
