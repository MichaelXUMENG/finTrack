from flask import(
    Blueprint, redirect, url_for, flash
)
import pandas as pd
from .db_utils import Category, SubCategory, Card, Degree, Spending
from sqlalchemy import create_engine
engine = create_engine("sqlite:///instance/finTrack.sqlite")

bp = Blueprint('backup', __name__, url_prefix='/backup')


def pull_write_data():
    df_card = pd.DataFrame(Card().fetch_all())
    df_card.columns = ['id', 'bank', 'name', 'cur_balance', 'pay_date', 'last_statement']
    df_category = pd.DataFrame(Category().fetch_all())
    df_category.columns = ['id', 'name']
    df_subcategory = pd.DataFrame(SubCategory().fetch_all())
    df_subcategory.columns = ['id', 'name', 'c_id', 'default_card', 'default_degree']
    df_degree = pd.DataFrame(Degree().fetch_all())
    df_degree.columns = ['id', 'name']
    df_spending = pd.DataFrame(Spending().fetch_all())
    df_spending.columns = ['id', 'name', 'amount', 'category', 'sub_category', 'yr', 'mon', 'daynum', 'card', 'degree',
                           'comments']

    with pd.ExcelWriter('setting_backup.xlsx') as writer:
        df_card.to_excel(writer, sheet_name='card', index=None, header=True)
        df_category.to_excel(writer, sheet_name='category', index=None, header=True)
        df_subcategory.to_excel(writer, sheet_name='sub', index=None, header=True)
        df_degree.to_excel(writer, sheet_name='degree', index=None, header=True)
    with pd.ExcelWriter('spending_backup.xlsx') as writer:
        df_spending.to_excel(writer, sheet_name='spending', index=None, header=True)


def restore_backup():
    file = 'setting_backup.xlsx'
    data = pd.ExcelFile(file)

    excel_card = data.parse('card')
    excel_category = data.parse('category')
    excel_sub = data.parse('sub')
    excel_degree = data.parse('degree')

    # start writing to sql database
    excel_card.to_sql('cards', con=engine, if_exists='append', index=False)
    excel_category.to_sql('categories', con=engine, if_exists='append', index=False)
    excel_sub.to_sql('sub_categories', con=engine, if_exists='append', index=False)
    excel_degree.to_sql('degrees', con=engine, if_exists='append', index=False)

    spending_file = 'spending_backup.xlsx'
    data = pd.ExcelFile(spending_file)
    excel_spending = data.parse('spending')
    # start writing to sql database
    excel_spending.to_sql('spending', con=engine, if_exists='append', index=False)


@bp.route('/data')
def data_backup():
    try:
        pull_write_data()
        flash('All Spending and Setting data have been backed up!', 'success')
    except Exception as e:
        flash(e, 'error')
    finally:
        return redirect(url_for('index.index'))


@bp.route('/restore')
def data_restore():
    try:
        restore_backup()
        flash('Data has been restored!', 'success')
    except Exception as e:
        flash(e, 'error')
    finally:
        return redirect(url_for('index.index'))
