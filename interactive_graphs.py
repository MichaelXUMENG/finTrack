import json

import pandas as pd
import plotly
import plotly.graph_objs as go

from .db_utils import Spending

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def interactive_annual_report(year):
    monthly_amount = Spending().get_total_spending_amount_of_each_month(year=year, include_doctor=False)
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
    monthly_amount = Spending().get_total_spending_amount_of_each_month(year=year, include_doctor=False)
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
