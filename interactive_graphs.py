import json

import pandas as pd
import plotly
import plotly.graph_objs as go

from .db_utils import Spending, Category, SubCategory
from pandas import DataFrame

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def month_translation(input_df: DataFrame) -> list:
    """
    Replace the month in integer with String code
    :param input_df: DataFrame of result
    :return:
    """
    month_list = []
    for index, row in input_df.iterrows():
        month_list.append(months[row['mon'] - 1])
    return month_list


############################################################
# 2 different ways to create interactive graphs
############################################################
def interactive_annual_report(year):
    monthly_amount = Spending().get_monthly_total_spending_of_a_year(year=year, include_doctor=False)
    df_monthly = pd.DataFrame(monthly_amount)
    df_monthly.columns = ['sum', 'mon']
    count = len(df_monthly['sum'])
    month_spendings = [0] * 12
    for month_index in range(count):
        month_spendings[df_monthly['mon'][month_index] - 1] = df_monthly['sum'][month_index]

    xScale = months
    yScale = month_spendings

    trace = go.Scatter(x=xScale, y=yScale)
    data = [trace]

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def interactive_annual_report_as_div(year):
    monthly_amount = Spending().get_monthly_total_spending_of_a_year(year=year, include_doctor=False)
    df_monthly = pd.DataFrame(monthly_amount)
    df_monthly.columns = ['sum', 'mon']
    count = len(df_monthly['sum'])
    month_spendings = [0] * 12
    for month_index in range(count):
        month_spendings[df_monthly['mon'][month_index] - 1] = df_monthly['sum'][month_index]

    fig = {'data': [{'x': months,
                     'y': month_spendings,
                     'type': 'bar'}],
           'layout': {'width': 800,
                      'height': 550}}

    aPlot = plotly.offline.plot(fig,
                                config={"displayModeBar": False},
                                show_link=False,
                                include_plotlyjs=False,
                                output_type='div')

    return aPlot


############################################################
# Generating interactive reports
############################################################
def interactive_accumulate_yearly_bar_report():
    yearly_amount = Spending().get_total_spending_amount_of_month()
    df_yearly_amount_bar = pd.DataFrame(yearly_amount)
    df_yearly_amount_bar.columns = ['sum', 'yr']

    fig = {
        'data': [{
            'x': df_yearly_amount_bar['yr'],
            'y': df_yearly_amount_bar['sum'],
            'type': 'bar'
        }],
        'layout': {
            'width': 200*len(df_yearly_amount_bar['yr']),
            'height': 550
        }
    }

    aPlot = plotly.offline.plot(
        fig,
        config={"displayModeBar": False},
        show_link=False,
        include_plotlyjs=False,
        output_type='div'
    )

    return aPlot


def interactive_annual_monthly_amount_line_report():
    years_from_db = Spending().get_years()
    years = [year['yr'] for year in years_from_db]

    df_year_monthly_amount = []
    for year in years:
        monthly_amount = Spending().get_monthly_total_spending_of_a_year(year, include_doctor=False)
        df_monthly_amount = pd.DataFrame(monthly_amount)
        df_monthly_amount.columns = ['sum', 'mon']
        df_year_monthly_amount.append(df_monthly_amount)

    fig = {
        'data': [
            {'x': df_monthly_amount['mon'],
             'y': df_monthly_amount['sum'],
             'name': f'{years[index]}',
             'type': 'scatter'} for index, df_monthly_amount in enumerate(df_year_monthly_amount)
        ],
        'layout': {
            'width': 960,
            'height': 550
        }
    }

    aPlot = plotly.offline.plot(
        fig,
        config={"displayModeBar": False},
        show_link=False,
        include_plotlyjs=False,
        output_type='div'
    )

    return aPlot


def interactive_annual_monthly_bar_report_with_buttons(year: int):
    """
    this function will create a ployly graph with buttons, to show the average monthly spending and last years'
    :param year: the current year to show
    :return:
    """
    condition_dict = {'key': 'category', 'operation': '!=', 'value': 16}
    average_monthly_amount = Spending().get_average_monthly_spending_amount(condition_dict=condition_dict)
    current_annual_monthly_amount = Spending().get_monthly_total_spending_of_a_year(year, include_doctor=False)

    df_average_monthly = pd.DataFrame(average_monthly_amount, columns=['avg', 'mon'])
    df_current_annual_monthly = pd.DataFrame(current_annual_monthly_amount, columns=['sum', 'mon'])

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df_current_annual_monthly['mon'],
            y=df_current_annual_monthly['sum'],
            name=f'{year} monthly spending'
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df_average_monthly['mon'],
            y=df_average_monthly['avg'],
            name='Average Monthly Spending',
            visible=True,
            line=dict(color="#33CFA5", dash="dash")
        )
    )

    fig.update_layout(
        updatemenus=[
            dict(
                type='buttons',
                direction='right',
                active=1,
                x=0.57,
                y=1.2,
                buttons=list([
                    dict(
                        label='Current Year',
                        method='update',
                        args=[
                            {'visible': [True, False]},
                            {'title': f'{year} monthly spending', "annotations": []}
                        ]
                    ),
                    dict(
                        label='Average',
                        method='update',
                        args=[
                            {'visible': [True, True]},
                            {'title': 'Compare with Average monthly', "annotations": []}
                        ]
                    ),
                ]),
            )
        ]
    )

    fig.update_layout(
        {
            'width': 960,
            'height': 550
        },
        overwrite=True
    )

    aPlot = plotly.offline.plot(fig,
                                config={"displayModeBar": False},
                                show_link=False,
                                include_plotlyjs=False,
                                output_type='div')

    return aPlot


def interactive_utility_report_with_buttons(year: int):
    """
    This function will create a interactive graph of monthly utility amount
    The total spending will be displayed as bar chart, and each category of utility will be displayed as scatter
    :param year: year in int
    :return:
    """
    utility_category_id = Category().get_category_id_by_name('Utility')
    monthly_utility_total = Spending().get_specific_category_monthly_spending(year, [utility_category_id])
    monthly_utility_details = Spending().get_sub_category_monthly_spending_of_a_category(year, [utility_category_id])

    df_monthly_total = pd.DataFrame(monthly_utility_total, columns=['sum', 'mon'])
    df_monthly_details = pd.DataFrame(monthly_utility_details, columns=['sum', 'name', 'mon'])

    df_water = df_monthly_details[df_monthly_details['name'] == 'Water and Waste']
    df_electricity = df_monthly_details[df_monthly_details['name'] == 'Electricity']
    df_internet = df_monthly_details[df_monthly_details['name'] == 'Internet']
    df_gas = df_monthly_details[df_monthly_details['name'] == 'Nature Gas']
    df_mobile = df_monthly_details[df_monthly_details['name'] == 'Mobile Bill']

    fig = go.Figure()
    # Add the total amount into figure as bar chart
    fig.add_trace(
        go.Bar(
            x=df_monthly_total['mon'],
            y=df_monthly_total['sum'],
            name=f"{year} utility"
        )
    )
    # Add water
    fig.add_trace(
        go.Scatter(x=df_water['mon'], y=df_water['sum'], name='Water',
                   visible=False, line=dict(color="#5DADE2"))
    )
    # Add Electricity
    fig.add_trace(
        go.Scatter(x=df_electricity['mon'], y=df_electricity['sum'], name='Electricity',
                   visible=False, line=dict(color="#F7DC6F"))
    )
    # Add Internet
    fig.add_trace(
        go.Scatter(x=df_internet['mon'], y=df_internet['sum'], name='Internet',
                   visible=False, line=dict(color="#82E0AA"))
    )
    # Add Gas
    fig.add_trace(
        go.Scatter(x=df_gas['mon'], y=df_gas['sum'], name='Gas',
                   visible=False, line=dict(color="#E74C3C"))
    )
    # Add Mobile
    fig.add_trace(
        go.Scatter(x=df_mobile['mon'], y=df_mobile['sum'], name='Mobile',
                   visible=False, line=dict(color="#BB8FCE"))
    )

    fig.update_layout(
        updatemenus=[
            dict(
                type='buttons',
                direction='right',
                active=0,
                x=0.57,
                y=1.2,
                buttons=list([
                    dict(
                        label='Total Utility Spending',
                        method='update',
                        args=[
                            {'visible': [True, False, False, False, False, False]},
                            {'title': 'Total Utility Spending', "annotations": []}
                        ]
                    ),
                    dict(
                        label='Water',
                        method='update',
                        args=[
                            {'visible': [True, True, False, False, False, False]},
                            {'title': 'Total vs Water', "annotations": []}
                        ]
                    ),
                    dict(
                        label='Electricity',
                        method='update',
                        args=[
                            {'visible': [True, False, True, False, False, False]},
                            {'title': 'Total vs Electricity', "annotations": []}
                        ]
                    ),
                    dict(
                        label='Internet',
                        method='update',
                        args=[
                            {'visible': [True, False, False, True, False, False]},
                            {'title': 'Total vs Internet', "annotations": []}
                        ]
                    ),
                    dict(
                        label='Gas',
                        method='update',
                        args=[
                            {'visible': [True, False, False, False, True, False]},
                            {'title': 'Total vs Gas', "annotations": []}
                        ]
                    ),
                    dict(
                        label='Mobile',
                        method='update',
                        args=[
                            {'visible': [True, False, False, False, False, True]},
                            {'title': 'Total vs Mobile', "annotations": []}
                        ]
                    ),
                ])
            )
        ]
    )

    fig.update_layout(
        {
            'width': 1200,
            'height': 550
        },
        overwrite=True
    )

    aPlot = plotly.offline.plot(fig,
                                config={"displayModeBar": False},
                                show_link=False,
                                include_plotlyjs=False,
                                output_type='div')

    return aPlot


def interactive_eating_reports_with_button(year: int):
    """
    this function will generate the bar charts of grocery and food.
    :param year: the year of summary
    :return:
    """
    # Get the ids
    food_category_id = Category().get_category_id_by_name('Food')
    grocery_category_id = Category().get_category_id_by_name('Grocery')
    category_list = [food_category_id, grocery_category_id]
    food_condition = {'key': 'category', 'operation': '=', 'value': food_category_id}
    grocery_condition = {'key': 'category', 'operation': '=', 'value': grocery_category_id}

    # Get the total monthly amount of sum of food and grocery
    monthly_eating_total = Spending().get_specific_category_monthly_spending(year, category_list)
    monthly_eating_details = Spending().get_categories_monthly_spending_with_category_name(year, category_list)

    # Get the total monthly average amount of food and grocery category
    average_food = Spending().get_average_amount_of_all_spending(food_condition)
    average_grocery = Spending().get_average_amount_of_all_spending(grocery_condition)

    # Get the average amount of each month of food and grocery category
    average_food_monthly = Spending().get_average_monthly_spending_amount(food_condition)
    average_grocery_monthly = Spending().get_average_monthly_spending_amount(grocery_condition)

    df_monthly_total = pd.DataFrame(monthly_eating_total, columns=['sum', 'mon'])
    df_monthly_details = pd.DataFrame(monthly_eating_details, columns=['sum', 'name', 'mon'])

    df_grocery = df_monthly_details[df_monthly_details['name'] == 'Grocery']
    df_food = df_monthly_details[df_monthly_details['name'] == 'Food']

    df_food_average = pd.DataFrame(average_food_monthly, columns=['avg', 'mon'])
    df_grocery_average = pd.DataFrame(average_grocery_monthly, columns=['avg', 'mon'])

    fig = go.Figure()
    # Add the total amount into figure as both bar and scatter
    fig.add_trace(
        go.Scatter(
            x=df_monthly_total['mon'], y=df_monthly_total['sum'], name='Total Cost',
            visible=True, line=dict(color="#5DADE2")
        )
    )
    fig.add_trace(
        go.Bar(
            x=df_monthly_total['mon'], y=df_monthly_total['sum'], name='Total Cost',
            visible=False
        )
    )
    # Add Grocery bar and scatter
    fig.add_trace(
        go.Bar(
            x=df_grocery['mon'], y=df_grocery['sum'], name='Grocery',
            visible=True
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_grocery_average['mon'], y=df_grocery_average['avg'], name='Grocery monthly Average',
            visible=False, line=dict(color="#82E0AA")
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_grocery_average['mon'], y=[average_grocery]*12, name='Grocery Average',
            visible=False, line=dict(color="#82E0AA", dash="dash")
        )
    )
    # Add Food bar
    fig.add_trace(
        go.Bar(
            x=df_food['mon'], y=df_food['sum'], name='Food',
            visible=True
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_food_average['mon'], y=df_food_average['avg'], name='Food monthly Average',
            visible=False, line=dict(color="#E74C3C")
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_food_average['mon'], y=[average_food] * 12, name='Grocery Average',
            visible=False, line=dict(color="#E74C3C", dash="dash")
        )
    )

    fig.update_layout(
        updatemenus=[
            dict(
                type='buttons',
                direction='right',
                active=0,
                x=0.57,
                y=1.2,
                buttons=list([
                    dict(
                        label='Overview',
                        method='update',
                        args=[
                            {'visible': [True, False, True, False, False, True, False, False]},
                            {'title': f'{year} monthly spending', "annotations": []}
                        ]
                    ),
                    dict(
                        label='Total Eating',
                        method='update',
                        args=[
                            {'visible': [False, True, False, False, False, False, False, False]},
                            {'title': 'Total Monthly Spending', "annotations": []}
                        ]
                    ),
                    dict(
                        label='Grocery Only',
                        method='update',
                        args=[
                            {'visible': [False, False, True, True, True, False, False, False]},
                            {'title': 'Grocery Monthly Spending', "annotations": []}
                        ]
                    ),
                    dict(
                        label='Food Only',
                        method='update',
                        args=[
                            {'visible': [False, False, False, False, False, True, True, True]},
                            {'title': 'Food Monthly Spending', "annotations": []}
                        ]
                    ),
                ]),
            )
        ]
    )

    fig.update_layout(
        {
            'width': 960,
            'height': 550
        },
        overwrite=True
    )

    aPlot = plotly.offline.plot(fig,
                                config={"displayModeBar": False},
                                show_link=False,
                                include_plotlyjs=False,
                                output_type='div')

    return aPlot
