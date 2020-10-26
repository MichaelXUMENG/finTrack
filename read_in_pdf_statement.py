from bs4 import BeautifulSoup
import re
import ast
from pdf_reader import extract_pdf_pdfminer_format_without_output


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


def read_pdf_statement_chase(pdf_path: str) -> list:
    """
    this function accepts the path of pdf statement as input; then read and parse the pdf file.
    Get the date, name and amount of all transactions in the statement
    :param pdf_path: The path to the pdf file
    :return: a list containing a list of a single transaction composed as [date, name, amount]
    """
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
            if div.contents[0].contents[0].strip() == 'ACCOUNT ACTIVITY':
                start_index = index
                break
        # when IndexError or TypeError exceptions are raised, we just continue searching the next tag
        # IndexError exception may be raised when there is no item from the '.contents' method of a tag
        # for example, <div style="left:0px; top:50px;"><span style="position:absolute;"></span></div>, this tag's
        # second '.contents' will return nothing

        # TypeError exception may be raised when NoneType is returned by calling '.contents' method of a tag.
        # for example, <div style="left: 1px><div style="left: 10px><div style="left: 20px></div></div></div>, this
        # tag's second '.contents[0]' will return a NoneType object. Cannot compare to a String.
        except (IndexError, TypeError):
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
        except (IndexError, TypeError):
            # if exceptions are raised, assign empty string to the content
            content = ''
        # if we hit the End symbol, just exit the loop
        if content == '2020  Totals Year-to-Date':
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
    for value in result.values():
        # only save the list with 3 elements: [date, name, amount]
        if len(value) == 3:
            final_list.append(value)

    return final_list
