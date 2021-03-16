import re
import csv
from datetime import datetime

from bs4 import BeautifulSoup

from .pdf_reader import extract_pdf_pdfminer_format_without_output


def parse_style(style_string: str) -> dict:
    """
    This function will read the style string as input,
    and save each style as a key and its value of value of a dictionary
    :param style_string: The string type of style. For example "top: 1234px; left: 123px;"
    :return: the dictionary with style name as key and its value as value
    """
    styles = style_string.strip().split(';')
    style_dic = {}
    for style in styles:
        if style:
            items = style.split(':')
            style_dic[items[0].strip()] = items[1].strip()
    return style_dic


# def read_pdf_statement_chase_credit(pdf_path: str) -> list:
#     """
#     this function accepts the path of pdf statement as input; then read and parse the pdf file.
#     Get the date, name and amount of all transactions in the statement
#     :param pdf_path: The path to the pdf file
#     :return: a list containing a list of a single transaction composed as [date, name, amount]
#     """
#     # read the pdf file, and export its content as html
#     context = extract_pdf_pdfminer_format_without_output(pdf_path)
#
#     # Create a BeautifulSoup object to parse the html
#     soup = BeautifulSoup(context, 'html.parser')
#
#     # get all tags with '<div>' from the html
#     all_divs = soup.find_all('div')
#
#     # Define the variables which hold the result of html parsing
#     result = {}
#     final_list = []
#     start_index = 0
#
#     # loop through all the <div> tags to find the symbol of the starting of all transactions.
#     # For statements of Chase credit cards, the symbol is 'ACCOUNT ACTIVITY'
#     for index, div in enumerate(all_divs):
#         try:
#             # found the symbol, then return the starting index
#             if div.contents[0].contents[0].strip() == 'ACCOUNT ACTIVITY':
#                 start_index = index
#                 break
#         # when IndexError or TypeError exceptions are raised, we just continue searching the next tag
#         # IndexError exception may be raised when there is no item from the '.contents' method of a tag
#         # for example, <div style="left:0px; top:50px;"><span style="position:absolute;"></span></div>, this tag's
#         # second '.contents' will return nothing
#
#         # TypeError exception may be raised when NoneType is returned by calling '.contents' method of a tag.
#         # for example, <div style="left: 1px><div style="left: 10px><div style="left: 20px></div></div></div>, this
#         # tag's second '.contents[0]' will return a NoneType object. Cannot compare to a String.
#         except (IndexError, TypeError, AttributeError):
#             continue
#
#     # Start from the symbol tag by assigning the current_tag to the starting point
#     current_tag = all_divs[start_index]
#     # Get the style information dictionary from the tag. We will need the top(y axis) value
#     position_info = parse_style(current_tag.attrs['style'])
#     # then we save the top value (y axis) as key in the result dictionary, and the content of the tag will be save
#     # into a list, which will be the value of the top value key in the result dictionary
#     result[position_info['top']] = [current_tag.contents[0].contents[0].strip()]
#     # move the current_tag to the next div tag
#     current_tag = current_tag.find_next_sibling('div')
#
#     # Loop through the rest of tags starting from the starting symbol.
#     # Also we have the End symbol, which is '2020  Totals Year-to-Date' for now
#     while True:
#         try:
#             # get the content of the current tag
#             content = current_tag.contents[0].contents[0].strip()
#         except (IndexError, TypeError, AttributeError):
#             # if exceptions are raised, assign empty string to the content
#             content = ''
#         # if we hit the End symbol, just exit the loop
#         if content == 'INTEREST CHARGES':
#             break
#         # otherwise, if the content is not empty, we will save the content into the result dictionary
#         elif content:
#             # first, we will get the top value (y axis), and save it into 'top_position'
#             position_info = parse_style(current_tag.attrs['style'])
#             top_position = position_info['top']
#             # if the top value already exists, we then append the tag's content to the list as the key's value
#             # otherwise, we save the tag's content in a list as the value of key of top value
#             if top_position in result:
#                 result[top_position].append(content)
#             else:
#                 result[top_position] = [content]
#         # then move the current_tag to the next <div> tag
#         current_tag = current_tag.find_next_sibling('div')
#
#     # after getting all the transaction information, we then need to clean up the result
#     # and save the results into the list
#     date_pattern = re.compile("[0-9]{2}/[0-9]{2}")
#     for value in result.values():
#         # only save the list with 3 elements: [date, name, amount]
#         if len(value) == 3:
#
#             final_list.append(value)
#
#     return final_list


def read_pdf_statement_chase(pdf_path: str, card_type) -> list:
    """
    this function accepts the path of pdf statement as input; then read and parse the pdf file.
    Get the date, name and amount of all transactions in the statement
    :param pdf_path: The path to the pdf file
    :param card_type: determine the card type of chase bank, either chase_credit or chase_checking
    :return: a list containing a list of a single transaction composed as [date, name, amount]
    """
    card_key_points = {
        'chase_credit': {
            'starting_index': 'ACCOUNT ACTIVITY',
            'ending_index': 'INTEREST CHARGES',
            'contained_elements': 3
        },
        'chase_checking': {
            'starting_index': 'CHECKING SUMMARY',
            'ending_index': 'SAVINGS SUMMARY',
            'contained_elements': 4
        }
    }
    # read the pdf file, and export its content as html
    context = extract_pdf_pdfminer_format_without_output(pdf_path)

    # Create a BeautifulSoup object to parse the html
    soup = BeautifulSoup(context, 'html.parser')

    # get all tags with '<div>' from the html
    all_divs = soup.find_all('div')

    # Define the variables which hold the result of html parsing
    result = {}
    final_list = []
    start_index = 0

    # # loop through all the <div> tags to find the symbol of the starting of all transactions.
    # # For statements of Chase credit cards, the symbol is 'ACCOUNT ACTIVITY'
    # for index, div in enumerate(all_divs):
    #     try:
    #         # found the symbol, then return the starting index
    #         if div.contents[0].contents[0].strip() == card_key_points[card_type]['starting_index']:
    #             start_index = index
    #             break
    #     # when IndexError or TypeError exceptions are raised, we just continue searching the next tag
    #     # IndexError exception may be raised when there is no item from the '.contents' method of a tag
    #     # for example, <div style="left:0px; top:50px;"><span style="position:absolute;"></span></div>, this tag's
    #     # second '.contents' will return nothing
    #
    #     # TypeError exception may be raised when NoneType is returned by calling '.contents' method of a tag.
    #     # for example, <div style="left: 1px><div style="left: 10px><div style="left: 20px></div></div></div>, this
    #     # tag's second '.contents[0]' will return a NoneType object. Cannot compare to a String.
    #     except (IndexError, TypeError, AttributeError):
    #         continue

    # Start from the symbol tag by assigning the current_tag to the starting point
    current_tag = all_divs[start_index]
    # Get the style information dictionary from the tag. We will need the top(y axis) value
    position_info = parse_style(current_tag.attrs['style'])
    # then we save the top value (y axis) as key in the result dictionary, and the content of the tag will be save into
    # a list, which will be the value of the top value key in the result dictionary
    result[position_info['top']] = [current_tag.contents[0].contents[0].strip()]
    # move the current_tag to the next div tag
    current_tag = current_tag.find_next_sibling('div')

    # Loop through the rest of tags starting from the starting symbol.
    # Also we have the End symbol, which is '2020  Totals Year-to-Date' for now
    while True:
        try:
            # get the content of the current tag
            content = current_tag.contents[0].contents[0].strip()
        except (IndexError, TypeError, AttributeError):
            # if exceptions are raised, assign empty string to the content
            content = ''
        # if we hit the End symbol, just exit the loop
        if content == card_key_points[card_type]['ending_index']:
            break
        # otherwise, if the content is not empty, we will save the content into the result dictionary
        elif content:
            # first, we will get the top value (y axis), and save it into 'top_position'
            position_info = parse_style(current_tag.attrs['style'])
            top_position = position_info['top']
            # if the top value already exists, we then append the tag's content to the list as the key's value
            # otherwise, we save the tag's content in a list as the value of key of top value
            if top_position in result:
                result[top_position].append(content)
            else:
                result[top_position] = [content]
        # then move the current_tag to the next <div> tag
        current_tag = current_tag.find_next_sibling('div')

    # after getting all the transaction information, we then need to clean up the result
    # and save the results into the list
    date_pattern = re.compile("[0-9]{2}/[0-9]{2}")
    amount_pattern = re.compile("-?[0-9,]*\.[0-9]{2}")
    # loop through all the items in the result list
    for value in result.values():
        # only save the list with 3 or 4 elements: [date, name, amount] depending on the card type
        if len(value) == card_key_points[card_type]['contained_elements']:
            # create an empty dictionary to host each transaction
            spending = {}
            # check each item in the value list, match the pattern with either date or amount, and save the item into
            # the matched key
            for item in value:
                if date_pattern.fullmatch(item) is not None:
                    spending['date'] = item + f'/{datetime.today().year}'
                elif amount_pattern.fullmatch(item) is not None:
                    if 'amount' not in spending or spending['amount'] > float(item.replace(',', '')):
                        spending['amount'] = float(item.replace(',', ''))
                else:
                    item = re.sub(' +', ' ', item)
                    spending['name'] = item.replace(',', '')
            # if the card type is checking, then alter the amount of transaction by adding the '-' of the amount
            if card_type == 'chase_checking':
                spending['amount'] = -spending.get('amount', 0)
            final_list.append(spending)

    # return sorted(final_list, key=lambda i: i['date'], reverse=True)
    return final_list


def read_pdf_statement_citi(pdf_path: str, card_type) -> list:
    """
    this function accepts the path of pdf statement as input; then read and parse the pdf file.
    Get the date, name and amount of all transactions in the statement
    :param pdf_path: The path to the pdf file
    :param card_type: determine the card type of chase bank, either chase_credit or chase_checking
    :return: a list containing a list of a single transaction composed as [date, name, amount]
    """
    card_key_points = {
        'citi': {
            'starting_index': 'Account Summary',
            'ending_index': 'Account messages',
            'contained_elements': (3, 4)
        }
    }
    # read the pdf file, and export its content as html
    context = extract_pdf_pdfminer_format_without_output(pdf_path)

    # Create a BeautifulSoup object to parse the html
    soup = BeautifulSoup(context, 'html.parser')

    # get all tags with '<div>' from the html
    all_divs = soup.find_all('div')

    # Define the variables which hold the result of html parsing
    result = {}
    final_list = []
    start_index = 0

    # loop through all the <div> tags to find the symbol of the starting of all transactions.
    # For statements of Chase credit cards, the symbol is 'ACCOUNT ACTIVITY'
    for index, div in enumerate(all_divs):
        try:
            # found the symbol, then return the starting index
            if div.contents[0].contents[0].strip() == card_key_points[card_type]['starting_index']:
                start_index = index
                break
        # when IndexError or TypeError exceptions are raised, we just continue searching the next tag
        # IndexError exception may be raised when there is no item from the '.contents' method of a tag
        # for example, <div style="left:0px; top:50px;"><span style="position:absolute;"></span></div>, this tag's
        # second '.contents' will return nothing

        # TypeError exception may be raised when NoneType is returned by calling '.contents' method of a tag.
        # for example, <div style="left: 1px><div style="left: 10px><div style="left: 20px></div></div></div>, this
        # tag's second '.contents[0]' will return a NoneType object. Cannot compare to a String.
        except (IndexError, TypeError, AttributeError):
            continue

    # Start from the symbol tag by assigning the current_tag to the starting point
    current_tag = all_divs[start_index]
    # Get the style information dictionary from the tag. We will need the top(y axis) value
    position_info = parse_style(current_tag.attrs['style'])
    # then we save the top value (y axis) as key in the result dictionary, and the content of the tag will be save into
    # a list, which will be the value of the top value key in the result dictionary
    result[position_info['top']] = [current_tag.contents[0].contents[0].strip()]
    # move the current_tag to the next div tag
    current_tag = current_tag.find_next_sibling('div')

    # Loop through the rest of tags starting from the starting symbol.
    # Also we have the End symbol, which is '2020  Totals Year-to-Date' for now
    while True:
        try:
            # get the content of the current tag
            content = current_tag.contents[0].contents[0].strip()
        except (IndexError, TypeError, AttributeError):
            # if exceptions are raised, assign empty string to the content
            content = ''
        # if we hit the End symbol, just exit the loop
        if content == card_key_points[card_type]['ending_index']:
            break
        # otherwise, if the content is not empty, we will save the content into the result dictionary
        elif content:
            # first, we will get the top value (y axis), and save it into 'top_position'
            position_info = parse_style(current_tag.attrs['style'])
            top_position = position_info['top']
            # if the top value already exists, we then append the tag's content to the list as the key's value
            # otherwise, we save the tag's content in a list as the value of key of top value
            if top_position in result:
                if content not in result[top_position]:
                    result[top_position].append(content)
            else:
                result[top_position] = [content]
        # then move the current_tag to the next <div> tag
        current_tag = current_tag.find_next_sibling('div')

    # after getting all the transaction information, we then need to clean up the result
    # and save the results into the list
    date_pattern = re.compile("[0-9]{2}/[0-9]{2}")
    date_alternative_pattern = re.compile("[0-9]{2}/[0-9]{2} [0-9]{2}/[0-9]{2}")
    amount_pattern = re.compile("-?\$[0-9,]*\.[0-9]{2}")
    # loop through all the items in the result list
    for value in result.values():
        # create an empty dictionary to host each transaction
        spending = {}
        # check each item in the value list, match the pattern with either date or amount, and save the item into
        # the matched key
        for item in value:
            if date_pattern.fullmatch(item.strip()) is not None:
                spending['date'] = item + f'/{datetime.today().year}'
            elif date_alternative_pattern.fullmatch(item.strip()) is not None:
                spending['date'] = item.split(' ')[0] + f'/{datetime.today().year}'
            elif amount_pattern.fullmatch(item.strip()) is not None:
                if 'amount' not in spending or spending['amount'] > float(item.replace(',', '')):
                    spending['amount'] = float(item.replace('$', '').replace(',', ''))
            else:
                item = re.sub(' +', ' ', item)
                spending['name'] = item.replace(',', '')
        if len(spending) >= 2:
            final_list.append(spending)

    return final_list


def read_apple_csv_transactions(path_to_file):
    """
    this function will open the apple transction file in .csv format, and get the date, name and amount of each
    transaction.
    :param path_to_file: The path to the csv file
    :return: a list of dictionary which contains name, date and amount
    """
    with open(path_to_file, 'r') as transaction_csv:
        transactions = [{k: v for k, v in row.items()}
                        for row in csv.DictReader(transaction_csv, skipinitialspace=True)]
    inputs = []
    for transaction in transactions:
        input = {'date': transaction['Transaction Date'],
                 'name': transaction['Merchant'],
                 'amount': transaction['Amount (USD)']}
        inputs.append(input)
    return inputs
