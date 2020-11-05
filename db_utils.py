from finTrack.db import get_db
from werkzeug.exceptions import abort

"""
Get the setting from database
"""


def get_all_category(order='name'):
    cats = get_db().execute(
        'SELECT id, name'
        ' FROM categories'
        ' ORDER BY ?',
        (order,)
    ).fetchall()
    return cats


def get_one_category(id):
    cat = get_db().execute(
        'SELECT id, name'
        ' FROM categories'
        ' WHERE id = ?',
        (id,)
    ).fetchone()
    return cat


def get_subcats_from_a_cat(id):
    subCat = get_db().execute(
        'SELECT id, name'
        ' FROM sub_categories'
        ' WHERE c_id=?'
        ' ORDER BY id',
        (id, )
    ).fetchall()
    return subCat


def get_all_subCategory(order='name'):
    subCat = get_db().execute(
        'SELECT id, name, c_id, default_card, default_degree'
        ' FROM sub_categories'
        ' ORDER BY ?',
        (order,)
    ).fetchall()
    return subCat


def get_one_subCategory(sub_id):
    subCat = get_db().execute(
        'SELECT id, name, c_id, default_card, default_degree'
        ' FROM sub_categories'
        ' WHERE id = ?',
        (sub_id,)
    ).fetchone()

    if subCat is None:
        abort(404, f"Sub-Category id {sub_id} doesn't exist.")

    return subCat


def get_all_cards(order='bank, name'):
    card = get_db().execute(
        'SELECT id, name, bank, cur_balance, pay_date'
        ' FROM cards'
        ' ORDER BY ?',
        (order,)
    ).fetchall()
    return card


def get_one_card(card_id=0):
    card = get_db().execute(
        'SELECT id, name, bank, cur_balance, pay_date'
        ' FROM cards'
        ' WHERE id = ?',
        (card_id,)
    ).fetchone()

    if card is None:
        abort(404, f"Card id {card_id} doesn't exist.")

    return card


def get_card_by_name(card_name):
    card_info = card_name.split(' - ')
    card = get_db().execute(
        'SELECT id, name, bank, cur_balance, pay_date'
        ' FROM cards'
        ' WHERE name = ? and bank = ?',
        (card_info[0], card_info[1])
    ).fetchone()
    return card


def get_all_degrees(order='name'):
    degrees = get_db().execute(
        'SELECT id, name'
        ' FROM degrees'
        ' ORDER BY ?',
        (order,)
    ).fetchall()
    return degrees


def get_one_degree(id):
    degree = get_db().execute(
        'SELECT id, name'
        ' FROM degrees'
        ' WHERE id = ?',
        (id,)
    ).fetchone()
    return degree


def get_spending_years():
    years = get_db().execute(
        'SELECT DISTINCT yr'
        ' FROM spending'
        ' ORDER BY yr DESC'
    ).fetchall()
    return years


"""
The Report Part (actual number)
"""


# exclude the doctor category
def get_all_spendings():
    spendings = get_db().execute(
        'SELECT id, name, amount, category, sub_category, yr, mon, daynum, card, degree, comments'
        ' FROM spending'
        ' WHERE category!=?'
        ' ORDER BY yr DESC, mon DESC, daynum DESC, card',
        (16,)
    ).fetchall()
    return spendings


def get_doctor_spendings():
    doc_spendings = get_db().execute(
        'SELECT id, name, amount, sub_category, yr, mon, daynum, card, degree, comments'
        ' FROM spending'
        ' WHERE category=?'
        ' ORDER BY yr DESC, mon DESC, daynum DESC, card',
        (16,)
    ).fetchall()
    return doc_spendings


def get_one_spending(id):
    spending = get_db().execute(
        'SELECT id, name, amount, category, sub_category, yr, mon, daynum, card, degree, comments'
        ' FROM spending'
        ' WHERE id = ?',
        (id,)
    ).fetchone()
    return spending


def get_spendings_card(card):
    spendings = get_db().execute(
        'SELECT id, name, amount, category, sub_category, yr, mon, daynum, card, degree, comments'
        ' FROM spending'
        ' WHERE card = ? and category!=?'
        ' ORDER BY yr DESC, mon DESC, daynum DESC, card',
        (card, 16)
    ).fetchall()
    return spendings


def get_all_spendings_card(card):
    spendings = get_db().execute(
        'SELECT id, name, amount, category, sub_category, yr, mon, daynum, card, degree, comments'
        ' FROM spending'
        ' WHERE card = ?'
        ' ORDER BY yr DESC, mon DESC, daynum DESC, card',
        (card,)
    ).fetchall()
    return spendings


def get_spendings_month_cat(year, month, cat):
    spendings = get_db().execute(
        'SELECT id, name, amount, sub_category, yr, mon, daynum, card, degree, comments'
        ' FROM spending'
        ' WHERE yr = ? and mon=? and category=?'
        ' ORDER BY daynum DESC',
        (year, month, cat)
    ).fetchall()
    return spendings


"""
The Summary Part (the summary numbers)
"""


def get_total_spending_month_cat(year, month, category) -> int:
    summary = get_db().execute(
        'SELECT ROUND(SUM(amount), 2) as sum'
        ' FROM spending'
        ' WHERE yr=? and mon=? and category=?',
        (year, month, category)
    ).fetchone()
    return summary['sum']


def get_total_spending_month(year, month):
    summary = get_db().execute(
        'SELECT ROUND(SUM(amount), 2) as sum'
        ' FROM spending'
        ' WHERE yr=? and mon=? and category!=?',
        (year, month, 16)
    ).fetchone()
    return summary


def get_category_total_spending_month(year, month):
    summary = get_db().execute(
        'SELECT category, ROUND(SUM(amount), 2) as sum'
        ' FROM spending'
        ' WHERE yr=? and mon=? and category!=?'
        ' GROUP BY category'
        ' ORDER BY SUM(amount) DESC',
        (year, month, 16)
    ).fetchall()
    return summary


def get_month_total_spending_year(year):
    summary = get_db().execute(
        'SELECT ROUND(SUM(amount), 2) as sum, mon'
        ' FROM spending'
        ' WHERE yr=? and category!=?'
        ' GROUP BY mon'
        ' ORDER BY mon',
        (year, 16,)
    ).fetchall()
    return summary


def get_total_spending_year(year):
    summary = get_db().execute(
        'SELECT ROUND(SUM(amount), 2) as sum'
        ' FROM spending'
        ' WHERE yr=? and category!=?',
        (year, 16)
    ).fetchone()
    return summary


def get_mon_total_spending_doc():
    doc_summary = get_db().execute(
        'SELECT ROUND(SUM(amount), 2) as sum, yr, mon'
        ' FROM spending'
        ' WHERE category=?'
        ' GROUP BY yr, mon'
        ' ORDER BY yr, mon',
        (16,)
    ).fetchall()
    return doc_summary


def get_total_spending_doc():
    doc_summary = get_db().execute(
        'SELECT ROUND(SUM(amount), 2) as sum'
        ' FROM spending'
        ' WHERE category=?',
        (16,)
    ).fetchone()
    return doc_summary