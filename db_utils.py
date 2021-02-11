from sqlalchemy import create_engine
import re


def get_database_connection():
    engine = create_engine("sqlite:///instance/finTrack.sqlite")
    return engine.connect()


class AllSettings(object):
    __name__ = 'AllSettings'

    id = int()
    name = str()

    @staticmethod
    def _fetch_all_action(sql_command: str):
        """
        This method wil execute the sql_command, and fetch all result and return
        :param sql_command: the sql command to be executed
        :return:
        """
        connection = get_database_connection()
        try:
            all_items = connection.execute(sql_command).fetchall()
        finally:
            connection.close()
        return all_items

    @staticmethod
    def _fetch_one_action(sql_command: str):
        """
        This method wil execute the sql_command, and fetch one result and return
        :param sql_command: the sql command to be executed
        :return:
        """
        connection = get_database_connection()
        try:
            item = connection.execute(sql_command).fetchone()
        finally:
            connection.close()
        return item

    def _update_database(self, field_name_list: list, value_tuple: tuple):
        """
        This method will execute the UPDATE command
        :param field_name_list: list of database fields to be updated
        :param value_tuple: the actual values of the field. Should be the same order of filed name
        :return:
        """
        connection = get_database_connection()
        fields_to_update = ' = ?, '.join(field_name_list) + ' = ?'
        try:
            connection.execute(
                f'UPDATE {self.__name__} SET {fields_to_update} WHERE id = {self.id}',
                value_tuple
            )
        finally:
            connection.close()

    def _insert_into_database(self, field_name: str, value_tuple: tuple):
        """
        This method will insert a row into database
        :param field_name: list of database fields
        :param value_tuple: the actual values of the field. Should be the same order of filed name
        :return:
        """
        connection = get_database_connection()
        try:
            connection.execute(
                f'INSERT INTO {self.__name__} ({field_name})'
                f' VALUES ({",".join(["?" for _ in range(len(value_tuple))])})',
                value_tuple
            )
        finally:
            connection.close()

    def fetch_all(self):
        sql_command = f'SELECT * FROM {self.__name__}'
        return self._fetch_all_action(sql_command)

    def fetch_all_in_order(self, order: str = 'name'):
        """
        get all items sorted by the item passed in order
        :param order: the column to be sorted
        :return:
        """
        all_items_sql = f'SELECT * FROM {self.__name__} ORDER BY {order}'
        return self._fetch_all_action(all_items_sql)

    def fetch_one_by_id(self, item_id: int):
        """
        Get one item by its id
        :param item_id: item id
        :return:
        """
        single_item_sql = f'SELECT * FROM {self.__name__} WHERE id = {item_id}'
        return self._fetch_one_action(single_item_sql)


class Category(AllSettings):
    __name__ = 'categories'

    def add_a_category(self):
        """
        This method inserts a new category into database
        :return:
        """
        field_name = 'name'
        value_tuple = (self.name,)
        self._insert_into_database(field_name, value_tuple)

    def update_category(self):
        """
        This method updates an existing category name
        :return:
        """
        field_name = ['name']
        value_tuple = (self.name,)
        self._update_database(field_name, value_tuple)


class SubCategory(AllSettings):
    __name__ = 'sub_categories'

    c_id = int()
    default_card = int()
    default_degree = int()

    def fetch_all_subcategories_in_category(self, category_id: int):
        """
        This method will get a list of all linked sub-categories from a category
        :param category_id: the id of parent category
        :return:
        """
        all_sub_categories_from_cat_sql = f'SELECT * FROM {self.__name__} WHERE c_id = {category_id} ORDER BY id'
        return self._fetch_all_action(all_sub_categories_from_cat_sql)

    ################################################################################
    # Add sub-category
    ################################################################################

    def load_a_sub_category(self, request_form):
        """
        This method will load the sub-category with data from the form
        :param request_form: the request form from website
        :return:
        """
        self.name = request_form.get('name', '')
        self.c_id = request_form.get('c_id', -1)
        self.default_card = request_form.get('default_card', None)
        self.default_degree = request_form.get('default_degree', None)

    def add_a_sub_category(self):
        """
        This method inserts a new sub-category into database
        :return:
        """
        field_name = "name, c_id, default_card, default_degree"
        value_tuple = (self.name, self.c_id, self.default_card, self.default_degree)
        self._insert_into_database(field_name, value_tuple)

    def update_sub_category(self):
        """
        This method updates a sub-category entry
        :return:
        """
        field_name = ['name', 'c_id', 'default_card', 'default_degree']
        value_tuple = (self.name, self.c_id, self.default_card, self.default_degree)
        self._update_database(field_name, value_tuple)


class Card(AllSettings):
    __name__ = 'cards'

    bank = str()
    cur_balance = float()
    pay_date = int()
    last_statement = str()

    def fetch_one_card_by_name(self, card_name: str):
        """
        Get one card by its name in format name - bank
        :param card_name: card name in 'name - bank' format
        :return:
        """
        card_info = card_name.split(' - ')
        one_card_sql = f'SELECT * FROM {self.__name__} WHERE name = "{card_info[0]}" and bank = "{card_info[1]}"'
        return self._fetch_one_action(one_card_sql)

    def get_a_card_name(self, card_id: int):
        """
        This method will return the card name as 'bank - name' by a given id
        :param card_id: card id
        :return:
        """
        if not card_id:
            return ''
        card = self.fetch_one_by_id(card_id)
        return ' - '.join([card['name'], card['bank']])

    ################################################################################
    # Update Card
    ################################################################################

    def load_a_card(self, request_form):
        """
        This method loads information of a card
        :param request_form: the request form which contains the information
        :return:
        """
        self.name = request_form.get('name', '')
        self.bank = request_form.get('bank', '')
        self.pay_date = int(request_form.get('pay_day', 0))
        self.cur_balance = int(request_form.get('balance', 0))

    def add_a_new_card(self):
        """
        This method will insert a card into database
        :return:
        """
        field_name = "name, bank, cur_balance, pay_date"
        value_tuple = (self.name, self.bank, self.cur_balance, self.pay_date)
        self._insert_into_database(field_name, value_tuple)

    def update_card_information(self):
        """
        This method will update information of a card
        :return:
        """
        field_name = ['name', 'bank', 'cur_balance', 'pay_date']
        value_tuple = (self.name, self.bank, self.cur_balance, self.pay_date)
        self._update_database(field_name, value_tuple)

    def update_card_balance(self):
        """
        This method will update a card current balance
        :return:
        """
        field_name = ['cur_balance']
        value_tuple = (self.cur_balance,)
        self._update_database(field_name, value_tuple)

    def update_card_statement_information(self):
        """
        This method will update a card current balance
        :return:
        """
        field_name = ['last_statement', 'cur_balance']
        value_tuple = (self.last_statement, self.cur_balance)
        self._update_database(field_name, value_tuple)


class Degree(AllSettings):
    __name__ = 'degrees'

    def get_a_degree_name(self, degree_id: int):
        """
        This method will return the degree's name by a given id
        :param degree_id: degree id
        :return:
        """
        if not degree_id:
            return ''
        degree = self.fetch_one_by_id(degree_id)
        return degree['name']

    ################################################################################
    # Update Card
    ################################################################################

    def add_a_degree(self):
        """
        This method inserts a new degree into database
        :return:
        """
        field_name = 'name'
        value_tuple = (self.name,)
        self._insert_into_database(field_name, value_tuple)

    def update_degree(self):
        """
        This method updates information of a degree
        :return:
        """
        field_name = ['name']
        value_tuple = (self.name,)
        self._update_database(field_name, value_tuple)


class Spending(AllSettings):
    __name__ = 'spending'

    amount = float()
    category = int()
    sub_category = int()
    yr = int()
    mon = int()
    daynum = int()
    card = int()
    degree = int()
    comments = str()

    ###############################################################
    # Get all section
    ###############################################################

    def get_years(self):
        """
        This method will return a list of distinct years of all spendings
        :return:
        """
        years_sql = f'SELECT DISTINCT yr FROM {self.__name__} ORDER BY yr DESC'
        return self._fetch_all_action(years_sql)

    def fetch_all_spendings_from_a_card(self, card_id: int, include_doctor: bool = True):
        """
        Get all spendings from a card, fetching from a card id
        :param card_id: id of the card
        :param include_doctor: boolean value, whether to include doctor category (16)
        :return:
        """
        condition = f'card = {card_id}' if include_doctor else f'card = {card_id} and category != 16'
        card_spending_sql = f'SELECT * FROM {self.__name__} WHERE {condition}' \
                            f' ORDER BY yr DESC, mon DESC, daynum DESC, card'
        return self._fetch_all_action(card_spending_sql)

    def fetch_all_spending_of_category_in_month(self, year: int, month: int, category_id: int):
        """
        This method will get all spending of a category within a particular month of a year
        :param year: the year of spending
        :param month: the month of spending
        :param category_id: the id of category to fetch spending
        :return:
        """
        spending_category_month_sql = f'SELECT * FROM {self.__name__}' \
                                      f' WHERE yr = {year} and mon = {month} and category = {category_id}' \
                                      f' ORDER BY daynum DESC'
        return self._fetch_all_action(spending_category_month_sql)

    def fetch_all_category_spending(self, include_doctor: bool = True):
        """
        Get spending from all category
        :param include_doctor: boolean value, whether to include doctor category (16)
        :return:
        """
        condition = '' if include_doctor else f' WHERE category != 16'
        all_spending_sql = f'SELECT * FROM {self.__name__}{condition} ORDER BY yr DESC, mon DESC, daynum DESC, card'
        return self._fetch_all_action(all_spending_sql)

    ###############################################################
    # Summary Section
    ###############################################################

    def get_total_spending_amount_of_month(self, year: int, month: int, category: int = None):
        """
        Get the amount of total spending of a month in a year.
        If the category is provided, then return the total spending of that category in that month
        Otherwise return all category except for doctor category (16)
        :param year: year in int
        :param month: month in int
        :param category: id of a particular category or None
        :return:
        """
        condition = ' and category != 16' if category is None else f' and category = {category}'
        total_spending_amount_sql = f'SELECT ROUND(SUM(amount), 2) as sum FROM {self.__name__}' \
                                    f' WHERE yr = {year} and mon = {month}{condition}'
        total_spending_amount = self._fetch_one_action(total_spending_amount_sql)
        return total_spending_amount['sum']

    def get_each_category_total_spending_amount_of_month(self, year: int, month: int, include_doctor: bool = True):
        """
        This method get total spending of each category of a month, and return them all as a list. If the include_doctor
        indicator set to False, then the list will exclude doctor category (16)
        :param year: year in int
        :param month: month in int
        :param include_doctor: whether to include doctor category. Default set to True
        :return:
        """
        condition = '' if include_doctor else ' and category != 16'
        each_month_spending_amount_sql = f'SELECT category, ROUND(SUM(amount), 2) as sum FROM {self.__name__}' \
                                         f' WHERE yr = {year} and mon = {month}{condition}' \
                                         f' GROUP BY category ORDER BY SUM(amount) DESC'
        return self._fetch_all_action(each_month_spending_amount_sql)

    def get_total_spending_amount_of_each_month(self, year: int, include_doctor: bool = True):
        """
        This method will get each month's total spending of a year.
        Exclude doctor category if include_doctor is set to False
        :param year: year in int
        :param include_doctor: whether to include doctor category. Default set to True
        :return:
        """
        condition = '' if include_doctor else ' and category != 16'
        each_month_total_spending_sql = f'SELECT ROUND(SUM(amount), 2) as sum, mon FROM {self.__name__}' \
                                        f' WHERE yr = {year}{condition} GROUP BY mon ORDER BY mon'
        return self._fetch_all_action(each_month_total_spending_sql)

    def get_total_spending_of_a_year(self, year: int, include_doctor: bool = True):
        """
        This method will return total amount of spending of a given year
        :param year: the year to be summarized
        :param include_doctor: whether to include doctor category. Default set to True
        :return:
        """
        condition = '' if include_doctor else ' and category != 16'
        yearly_total_spending_sql = f'SELECT ROUND(SUM(amount), 2) as sum FROM {self.__name__}' \
                                    f' WHERE yr = {year}{condition}'
        yearly_total_spending_amount = self._fetch_one_action(yearly_total_spending_sql)
        return yearly_total_spending_amount['sum']

    ################################################################################
    # Add Spending
    ################################################################################

    def load_spending_values(self, request_form):
        """
        This method will load the spending object with values
        :param request_form: the request object containing the values
        :return:
        """
        self.name = request_form.form.get('name', 'N/A')
        self.amount = float(request_form.form.get('amount', 0.0))
        self.sub_category = int(request_form.form.get('sub_category', -1))
        self.card = int(request_form.form.get('card', -1))
        self.degree = int(request_form.form.get('degree', -1))
        self.comments = request_form.form.get('comments', '')
        date = request_form.form.get('date', '01/01/1960')

        date_match = re.fullmatch(r"([0-9]{1,2})/([0-9]{1,2})/([0-9]{2,4})", date)
        if date_match is None:
            date_match = re.fullmatch(r"([0-9]{1,2})-([0-9]{1,2})-([0-9]{2,4})", date)
        self.yr, self.mon, self.daynum = int(date_match.group(3)), int(date_match.group(1)), int(date_match.group(2))

    def add_a_spending(self):
        """
        Add the spending object into database
        :return:
        """
        field_name = 'name, amount, category, sub_category, yr, mon, daynum, card, degree, comments'
        value_tuple = (self.name, self.amount, self.category, self.sub_category, self.yr, self.mon, self.daynum,
                       self.card, self.degree, self.comments)
        self._insert_into_database(field_name, value_tuple)

    def update_a_spending(self):
        """
        Update an existing spending object in database
        :return:
        """
        field_name = ['name', 'amount', 'category', 'sub_category', 'yr', 'mon', 'daynum', 'card', 'degree', 'comments']
        value_tuple = (self.name, self.amount, self.category, self.sub_category, self.yr, self.mon, self.daynum,
                       self.card, self.degree, self.comments)
        self._update_database(field_name, value_tuple)


class DoctorSpending(AllSettings):
    __name__ = 'spending'

    def fetch_doctor_spending(self):
        """
        This method will query each transaction of doctor category
        :return:
        """
        doctor_spending_sql = f'SELECT * FROM {self.__name__} WHERE category = 16' \
                              f' ORDER BY yr DESC, mon DESC, daynum DESC, card'
        return self._fetch_all_action(doctor_spending_sql)

    def get_doctor_spending_of_each_month(self):
        """
        This method will get total spending amount of doctor category of each month
        :return:
        """
        monthly_doctor_spending_amount_sql = f'SELECT ROUND(SUM(amount), 2) as sum, yr, mon FROM {self.__name__}' \
                                             f' WHERE category = 16' \
                                             f' GROUP BY yr, mon' \
                                             f' ORDER BY yr, mon'
        return self._fetch_all_action(monthly_doctor_spending_amount_sql)

    def get_total_amount_of_doctor_spending(self):
        """
        This method will get total spending of a given year
        :return:
        """
        total_amount_doctor_spending_sql = f'SELECT ROUND(SUM(amount), 2) as sum' \
                                           f' FROM {self.__name__} WHERE category = 16'
        total_amount_doctor_spending = self._fetch_one_action(total_amount_doctor_spending_sql)
        return total_amount_doctor_spending['sum']
