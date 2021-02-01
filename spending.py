import ast
import csv
import json
import os
import re

from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, current_app
)
from werkzeug.utils import secure_filename

from finTrack.db import get_db
from .db_utils import Category, SubCategory, Card, Degree, Spending
from .read_in_pdf_statement import read_pdf_statement_chase, read_apple_csv_transactions, read_pdf_statement_citi

bp = Blueprint('spending', __name__, url_prefix='/spending')


@bp.route('/add', methods=('GET', 'POST'))
def spending_add():
    category = Category()
    sub_category = SubCategory()
    card_object = Card()
    degree_object = Degree()

    if request.method == 'POST':
        name = request.form['name']
        amount = float(request.form['amount'])
        sub_id = request.form['sub_category']
        cat_id = sub_category.fetch_one_by_id(sub_id)['c_id']
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
            balance = card_object.fetch_one_by_id(card_id)['cur_balance']
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
            cats = category.fetch_all_in_order()
            subCats = sub_category.fetch_all_in_order()
            cards = card_object.fetch_all_in_order(order='bank, name')
            degrees = degree_object.fetch_all_in_order()
            settings = {'cats': cats, 'subCats': subCats, 'cards': cards, 'degrees': degrees}
            return render_template('spending/add_spending.html', settings=settings)
        except Exception as e:
            flash(e, 'error')
            return redirect(url_for('index.index'))


@bp.route('/<int:card>/add', methods=('GET', 'POST'))
def spending_add_from_card(card):
    category = Category()
    sub_category = SubCategory()
    card_object = Card()
    degree_object = Degree()

    if request.method == 'POST':
        name = request.form['name']
        amount = float(request.form['amount'])
        sub_id = request.form['sub_category']
        cat_id = sub_category.fetch_one_by_id(sub_id)['c_id']
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
            balance = card_object.fetch_one_by_id(card)['cur_balance']
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
            cats = category.fetch_all_in_order()
            subCats = sub_category.fetch_all_in_order()
            degrees = degree_object.fetch_all_in_order()
            card_info = card_object.fetch_one_by_id(card)
            settings = {'cats': cats, 'subCats': subCats, 'cards': card_info, 'degrees': degrees}
            return render_template('spending/add_card_spending.html', settings=settings)
        except Exception as e:
            flash(e, 'error')
            return redirect(url_for('index.index'))


@bp.route('/add/statement', methods=['POST'])
def spending_add_from_statement():
    # Check if there is file received from the form
    # If there is not, then return to the index page; otherwise, continue
    if 'statement_pdf' not in request.files:
        flash('No file part')
        return redirect(url_for('index.index'))
    # Get the card information from the form
    card = request.form['card']
    # get the actual file object from the form
    file = request.files['statement_pdf']
    # If there is no filename, then return to the index page
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index.index'))

    # get the filename from the file object
    filename = secure_filename(file.filename)
    # compose the /path_to_statement/filename by adding the CONSTANTS from the application
    path_to_statement = os.path.join(current_app.config['UPLOAD_STATEMENT_FOLDER'], filename)
    # save the file to the temporary directory, which will be deleted later
    file.save(path_to_statement)

    # create an empty list for the content of pdf files
    inputs = []
    # extract information from the statements of different cards,
    # and generate the path to the preset according to differnet card
    if card in ('Freedom - Chase', 'Unlimited - Chase', 'Sapphire - Chase'):
        inputs = read_pdf_statement_chase(path_to_statement, 'chase_credit')

        transaction_preset = os.path.join(current_app.config['PRELOAD_FOLDER'],
                                          'chase_credit_' + current_app.config['PRESET_FILE_NAME'])
    elif card == 'Checking - Chase':
        inputs = read_pdf_statement_chase(path_to_statement, 'chase_checking')

        transaction_preset = os.path.join(current_app.config['PRELOAD_FOLDER'],
                                          'chase_checking_' + current_app.config['PRESET_FILE_NAME'])
    elif card == 'Apple - Goldman Sachs':
        inputs = read_apple_csv_transactions(path_to_statement)

        transaction_preset = os.path.join(current_app.config['PRELOAD_FOLDER'],
                                          'apple_' + current_app.config['PRESET_FILE_NAME'])
    elif card in ('AA - Citi', 'Costco - Citi', 'Double Cash Back - Citi'):
        inputs = read_pdf_statement_citi(path_to_statement, 'citi')

        transaction_preset = os.path.join(current_app.config['PRELOAD_FOLDER'],
                                          'citi_' + current_app.config['PRESET_FILE_NAME'])
    else:
        transaction_preset = os.path.join(current_app.config['PRELOAD_FOLDER'],
                                          current_app.config['PRESET_FILE_NAME'])

    # open the 'preset' csv file, and read the contents into a dictionary,
    # whose key is name of each transaction, and value would be another dictionary,
    # whose keys are name, category and degree, whose value are the value from each transaction
    try:
        with open(transaction_preset, 'r') as csv_file:
            preset = {row['name']: {k: v for k, v in row.items()}
                      for row in csv.DictReader(csv_file, skipinitialspace=True)}
    except FileNotFoundError:
        with open('temp/preload/transaction_preset.csv', 'r') as csv_file:
            preset = {row['name']: {k: v for k, v in row.items()}
                      for row in csv.DictReader(csv_file, skipinitialspace=True)}

    # def generate():
    #     with open(path) as f:
    #         yield from f
    #
    #     os.remove(path)

    # After reading and extracting the context from the pdf statements,
    # delete the pdf files saved in the temporary directory
    os.remove(path_to_statement)

    # getting those basic information from the database
    category = Category()
    sub_category = SubCategory()
    degree_object = Degree()

    cats = category.fetch_all_in_order()
    subCats = sub_category.fetch_all_in_order()
    degrees = degree_object.fetch_all_in_order()
    settings = {'cats': cats, 'subCats': subCats, 'degrees': degrees}
    subcat_degree_map = {sub_category['id']: sub_category['default_degree'] for sub_category in subCats}

    # Then pass the pdf contents, preset configuration and basic information into the template
    return render_template('spending/add_spending_from_statement.html',
                           card=card, inputs=inputs, settings=settings, preset=preset, filename=filename,
                           subcat_degree_map=json.dumps(subcat_degree_map))


@bp.route('/save_statement', methods=['POST'])
def save_statement_data():
    sub_category_object = SubCategory()
    card_object = Card()

    # initiate the transaction counts and valid transactions with the count of transactions and 0
    transaction_counts, valid_transactions = int(request.form.get('count', 0)), 0
    # get the card name from the form
    card_name = request.form.get('card', '')
    statement_name = request.form.get('filename', '')
    # then get the card database entry by the card name
    card = card_object.fetch_one_card_by_name(card_name)
    total_amount = card['cur_balance']
    # get the preset from form, which is in json format, and converted into dictionary using ast.literal_eval()
    preset = ast.literal_eval(request.form.get('preset', ''))

    # Get a hold of a database entry
    db = get_db()

    try:
        # loop through all the transactions
        for index in range(transaction_counts):
            # if this transaction is not excluded, then save the transaction into database
            if request.form.get(f'exclude{index + 1}', 'False') == 'False':
                # Compose each single transaction's detail by getting those information by the index
                single_trans = {
                    'name': request.form.get(f'name{index + 1}', 'N/A'),
                    'category': request.form.get(f'category{index + 1}', -1),
                    'amount': request.form.get(f'amount{index + 1}', 0),
                    'date': request.form.get(f'date{index + 1}', '01/01/0101'),
                    'degree': request.form.get(f'degree{index + 1}', -1),
                    'note': request.form.get(f'note{index + 1}', ''),
                }
                # get the sub_category object from database using the sub_category_id
                sub_category = sub_category_object.fetch_one_by_id(single_trans['category'])
                # match the date information from transaction using regular expression
                # by doing so, I can get the year, month and day using the position of the date_match
                date_match = re.fullmatch(r"([0-9]{2})/([0-9]{2})/([0-9]{4})", single_trans['date'])

                # insert the single transaction into the database
                db.execute(
                    'INSERT INTO spending (name, amount, category, sub_category, yr, mon, daynum, card, degree, comments)'
                    ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (single_trans['name'], single_trans['amount'], sub_category['c_id'], single_trans['category'],
                     date_match.group(3), date_match.group(1), date_match.group(2), card['id'], single_trans['degree'],
                     single_trans['note'])
                )
                # increase the valid transaction number
                valid_transactions += 1
                total_amount += float(single_trans['amount'])
                # if the transaction is not already in the preset,
                # then save the transaction into the preset dictionary.
                if single_trans['name'] not in preset:
                    preset[single_trans['name']] = {'name': single_trans['name'],
                                                    'category': single_trans['category'],
                                                    'degree': single_trans['degree']}

        # Update card information
        db.execute(
            'UPDATE cards SET last_statement = ?, cur_balance = ?'
            ' WHERE id = ?',
            (statement_name, total_amount, card['id'])
        )
        # Then commit the database after all transactions are saved
        db.commit()

        # save the preset back to the preset file, if the preset is not empty
        if preset:
            if card_name in ('Freedom - Chase', 'Unlimited - Chase', 'Sapphire - Chase'):
                transaction_preset = os.path.join(current_app.config['PRELOAD_FOLDER'],
                                                  'chase_credit_' + current_app.config['PRESET_FILE_NAME'])
            elif card == 'Checking - Chase':
                transaction_preset = os.path.join(current_app.config['PRELOAD_FOLDER'],
                                                  'chase_checking_' + current_app.config['PRESET_FILE_NAME'])
            elif card == 'Apple - Goldman Sachs':
                transaction_preset = os.path.join(current_app.config['PRELOAD_FOLDER'],
                                                  'apple_' + current_app.config['PRESET_FILE_NAME'])
            elif card in ('AA - Citi', 'Costco - Citi', 'Double Cash Back - Citi'):
                transaction_preset = os.path.join(current_app.config['PRELOAD_FOLDER'],
                                                  'citi_' + current_app.config['PRESET_FILE_NAME'])
            else:
                transaction_preset = os.path.join(current_app.config['PRELOAD_FOLDER'],
                                                  current_app.config['PRESET_FILE_NAME'])

            # get a list of the keys of preset dictionary, which are the saved transaction name
            sample_entrys = list(preset.keys())
            # create an empty list to hold all the transactions in dictionary format
            # and save each transaction into the list
            dict_list = []
            for entry in sample_entrys:
                dict_list.append(preset[entry])
            # Then get the keys from a single transaction, which will be the header of the preset csv file
            keys = preset[sample_entrys[0]].keys()

            # Open the preset csv files in the writing mode, and save the list of dictionary into the csv,
            # with the keys as header
            with open(transaction_preset, 'w+', newline='') as output_file:
                dict_writer = csv.DictWriter(output_file, keys)
                dict_writer.writeheader()
                dict_writer.writerows(dict_list)

        # Flash the successful message to the screen
        flash(f'{valid_transactions} spendings are added!', 'success')
        # and return to the report page of that card
        return redirect(url_for('report.add_spending_card', card=card['id']))
    # If any exception raised, flash the error message and rollback the database and return to the index page.
    except TypeError as e:
        flash(e, 'error')
        db.rollback()
        return redirect(url_for('index.index'))


@bp.route('/<int:id>/eidt/', methods=('GET', 'POST'))
def spending_edit(id):
    category = Category()
    sub_category = SubCategory()
    card_object = Card()
    degree_object = Degree()
    spending_object = Spending()

    if request.method == 'POST':
        name = request.form['name']
        amount = float(request.form['amount'])
        sub_id = request.form['sub_category']
        cat_id = sub_category.fetch_one_by_id(sub_id)['c_id']
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
            balance = card_object.fetch_one_by_id(card_id)['cur_balance']
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
            cats = category.fetch_all_in_order()
            subCats = sub_category.fetch_all_in_order()
            cards = card_object.fetch_all_in_order(order='bank, name')
            degrees = degree_object.fetch_all_in_order()
            spending = spending_object.fetch_one_by_id(id)
            date = str(spending['mon'])+'/'+str(spending['daynum'])+'/'+str(spending['yr'])
            settings = {'cats': cats, 'subCats': subCats, 'cards': cards, 'degrees': degrees}
            return render_template('spending/edit_spending.html', settings=settings, spending=spending, date=date)
        except Exception as e:
            flash(e, 'error')
            return redirect(url_for('report.view_all_spending'))
