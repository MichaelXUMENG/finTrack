from finTrack.db import get_db
from werkzeug.exceptions import abort

from sqlalchemy import create_engine


def get_database_connection():
    engine = create_engine("sqlite:///instance/finTrack.sqlite")
    return engine.connect()


class AllSettings(object):
    __name__ = 'AllSettings'

    def get_all(self):
        connection = get_database_connection()
        try:
            all_items = connection.execute(
                'SELECT *'
                f' FROM {self.__name__}'
            ).fetchall()
        finally:
            connection.close()
        return all_items

    def get_all_in_order(self, order: str = 'name'):
        """
        get all items sorted by the item passed in order
        :param order: the column to be sorted
        :return:
        """
        connection = get_database_connection()
        try:
            all_items = connection.execute(
                'SELECT *'
                f' FROM {self.__name__}'
                f' ORDER BY ?',
                (order,)
            ).fetchall()
        finally:
            connection.close()
        return all_items

    def get_one_by_id(self, item_id: int):
        """
        Get one item by its id
        :param item_id: item id
        :return:
        """
        connection = get_database_connection()
        try:
            target_item = connection.execute(
                'SELECT *'
                f' FROM {self.__name__}'
                ' WHERE id = ?',
                (item_id,)
            ).fetchone()
        finally:
            connection.close()
        return target_item


class Category(AllSettings):
    __name__ = 'categories'


class SubCategory(AllSettings):
    __name__ = 'sub_categories'

    def get_all_subcategories_in_category(self, category_id: int):
        """
        This method will get a list of all linked sub-categories from a category
        :param category_id: the id of parent category
        :return:
        """
        connection = get_database_connection()
        try:
            all_sub_categories = connection.execute(
                'SELECT *'
                f' FROM {self.__name__}'
                f' WHERE c_id=?'
                'ORDER BY id',
                (category_id,)
            ).fetchall()
        finally:
            connection.close()
        return all_sub_categories


class Card(AllSettings):
    __name__ = 'cards'

    def get_one_card_by_name(self, card_name: str):
        """
        Get one card by its name in format name - bank
        :param card_name: card name in 'name - bank' format
        :return:
        """
        connection = get_database_connection()
        card_info = card_name.split(' - ')
        try:
            card = connection.execute(
                'SELECT *'
                f' FROM {self.__name__}'
                ' WHERE name = ? and bank = ?',
                (card_info[0], card_info[1])
            ).fetchone()
        finally:
            connection.close()
        return card


class Degree(AllSettings):
    __name__ = 'degrees'


"""
Get the setting from database
"""


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