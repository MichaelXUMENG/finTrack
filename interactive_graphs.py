import json

import pandas as pd
import plotly
import plotly.graph_objs as go
from sqlalchemy import create_engine

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def interactive_annual_report(year):
    engine = create_engine("sqlite:///instance/finTrack.sqlite")
    con = engine.connect()
    monthly = con.execute('SELECT SUM(amount) as summary, mon' +
                          ' FROM spending' +
                          ' WHERE yr=? and category!=?' +
                          ' GROUP BY mon ORDER BY mon',
                          (year, 16,)
                          )
    df_monthly = pd.DataFrame(monthly.fetchall())
    df_monthly.columns = monthly.keys()
    count = len(df_monthly['summary'])
    month_spendings = [0] * 12
    for month_index in range(count):
        month_spendings[df_monthly['mon'][month_index] - 1] = df_monthly['summary'][month_index]
    con.close()

    xScale = months
    yScale = month_spendings

    trace = go.Scatter(x=xScale, y=yScale)
    data = [trace]

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def interactive_annual_report_as_div(year):
    engine = create_engine("sqlite:///instance/finTrack.sqlite")
    con = engine.connect()
    monthly = con.execute('SELECT SUM(amount) as summary, mon' +
                          ' FROM spending' +
                          ' WHERE yr=? and category!=?' +
                          ' GROUP BY mon ORDER BY mon',
                          (year, 16,)
                          )
    df_monthly = pd.DataFrame(monthly.fetchall())
    df_monthly.columns = monthly.keys()
    count = len(df_monthly['summary'])
    month_spendings = [0] * 12
    for month_index in range(count):
        month_spendings[df_monthly['mon'][month_index] - 1] = df_monthly['summary'][month_index]
    con.close()

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
