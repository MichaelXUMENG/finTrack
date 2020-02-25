import io
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from flask import Blueprint, Response

bp = Blueprint('graph', __name__, url_prefix='/graph')
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


@bp.route('/<int:year>/annualReport.png')
def annualReport(year):
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
    month_spendings = [0]*12
    for month_index in range(count):
        month_spendings[df_monthly['mon'][month_index]-1] = df_monthly['summary'][month_index]
    con.close()

    title = f'Totle Spending of each Month in {year}'
    ylabel = "Dolors"
    xlabel = "Month"
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1, title=title, xlabel=xlabel, ylabel=ylabel, ylim=(0, 10000))
    axis.plot(months, month_spendings)
    axis.scatter(months, month_spendings)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@bp.route('/<int:month>/monthReport.png')
def monthReport(month):
    engine = create_engine("sqlite:///instance/finTrack.sqlite")
    con = engine.connect()
    summary = con.execute('SELECT SUM(amount) as summary, c.name' +
                          ' FROM spending LEFT JOIN categories AS c on category = c.id' +
                          ' WHERE mon=? and category!=?' +
                          ' GROUP BY category ORDER BY SUM(amount) DESC',
                          (month, 16,)
                          )
    df_summary = pd.DataFrame(summary.fetchall())
    df_summary.columns = summary.keys()
    con.close()

    title = str(month)+" Monthly Summary"
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ffc4d8', '#9bf6ff', '#ffe39e', '#ffd3b8', '#e9fba6',
              '#adebad', '#99ffeb']
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    fig.suptitle(title, fontsize=16)
    # start drawing the pie chart
    """
    fig1, ax1 = plt.subplots()
    ax1.pie(df_summary['summary'], colors=colors, labels=df_summary['name'], autopct='%1.1f%%', startangle=90,
            pctdistance=0.85)
    # draw circle
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    # Equal aspect ratio ensures that pie is drawn as a circle
    ax1.axis('equal')
    plt.tight_layout()
    plt.show()
    """
    explode = [0.1] * len(df_summary.index)
    axis.pie(df_summary['summary'], colors=colors, labels=df_summary['name'],
            autopct='%1.1f%%', startangle=180, explode=explode, radius=1)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@bp.route('/<int:year>/utilityReport.png')
def utilityReport(year):
    engine = create_engine("sqlite:///instance/finTrack.sqlite")
    con = engine.connect()
    # Select each utility category's total amount of each month
    utility = con.execute('SELECT SUM(amount) as summary, s.name, mon' +
                          ' FROM spending LEFT JOIN sub_categories AS s on sub_category=s.id' +
                          ' WHERE yr=? and category=3'
                          ' GROUP BY sub_category, mon ORDER BY mon',
                          (year,)
                          )
    df_utility = pd.DataFrame(utility.fetchall())
    df_utility.columns = utility.keys()

    # Select the total amount of utility of each month
    utility_total = con.execute('SELECT SUM(amount) as summary, mon' +
                                ' FROM spending' +
                                ' WHERE yr=? and category=3'
                                ' GROUP BY mon ORDER BY mon',
                                (year,)
                                )
    df_utility_total = pd.DataFrame(utility_total.fetchall())
    df_utility_total.columns = utility_total.keys()
    con.close()

    total_utility = [0] * 12
    for index in range(len(df_utility_total)):
        total_utility[df_utility_total['mon'][index]-1] = df_utility_total['summary'][index]

    # save the each utility category into its own variable
    df_water = df_utility[df_utility['name'] == 'Water and Waste']
    df_electricity = df_utility[df_utility['name'] == 'Electricity']
    df_internet = df_utility[df_utility['name'] == 'Internet']
    df_gas = df_utility[df_utility['name'] == 'Nature Gas']
    df_mobile = df_utility[df_utility['name'] == 'Mobile Bill']

    # Save the previous amount of each utility category; will be used in the stack column
    water_bar = [0] * 12
    electrisity_bar = [0] * 12
    internet_bar = [0] * 12
    gas_bar = [0] * 12
    mobile_bar = [0] * 12

    for index in range(len(df_water)):
        water_bar[df_water['mon'].tolist()[index]-1] = df_water['summary'].tolist()[index]
    electrisity_base = water_bar[:]
    internet_base = electrisity_base[:]
    for index in range(len(df_electricity)):
        electrisity_bar[df_electricity['mon'].tolist()[index]-1] = df_electricity['summary'].tolist()[index]
        internet_base[df_electricity['mon'].tolist()[index] - 1] += df_electricity['summary'].tolist()[index]
    gas_base = internet_base[:]
    for index in range(len(df_internet)):
        internet_bar[df_internet['mon'].tolist()[index]-1] = df_internet['summary'].tolist()[index]
        gas_base[df_internet['mon'].tolist()[index] - 1] += df_internet['summary'].tolist()[index]
    mobile_base = gas_base[:]
    for index in range(len(df_gas)):
        gas_bar[df_gas['mon'].tolist()[index]-1] += df_gas['summary'].tolist()[index]
        mobile_base[df_gas['mon'].tolist()[index] - 1] += df_gas['summary'].tolist()[index]
    for index in range(len(df_mobile)):
        mobile_bar[df_mobile['mon'].tolist()[index]-1] += df_mobile['summary'].tolist()[index]

    title="The report of Utility"
    # Add y axis lable and the title
    ylabel="Dolors"
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1, title=title, ylabel=ylabel)
    # stack each utility category onto the previous one
    pw = axis.bar(months, water_bar, width=0.35, color='#66b3ff')
    pe = axis.bar(months, electrisity_bar, width=0.35, bottom=electrisity_base, color='#ff9999')
    pi = axis.bar(months, internet_bar, width=0.35, bottom=internet_base, color='#99ff99')
    pg = axis.bar(months, gas_bar, width=0.35, bottom=gas_base, color='#ffcc99')
    pm = axis.bar(months, mobile_bar, width=0.35, bottom=mobile_base, color='#9bf6ff')

    # Then add the line and point onto the plot
    axis.plot(months, total_utility)
    axis.scatter(months, total_utility)

    # add the color mapping
    axis.legend((pw[0], pe[0], pi[0], pg[0], pm[0]),
               ('Water and Waste', 'Electricity', 'Internet', 'Natral Gas', 'Mobile Bill'))

    # show the plot
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@bp.route('/<int:year>/eatingReport.png')
def eatingReport(year):
    engine = create_engine("sqlite:///instance/finTrack.sqlite")
    con = engine.connect()
    # Select Food and Grocery total amount of each month
    food = con.execute('SELECT SUM(amount) as summary, c.name, mon' +
                       ' FROM spending LEFT JOIN categories AS c on category=c.id' +
                       ' WHERE yr=? and (category=2 or category=6)'
                       ' GROUP BY category, mon ORDER BY mon',
                       (year,)
                       )
    df_food = pd.DataFrame(food.fetchall())
    df_food.columns = food.keys()

    # Select the total amount of both Food and Grocery of each month
    food_total = con.execute('SELECT SUM(amount) as summary, mon' +
                             ' FROM spending' +
                             ' WHERE yr=? and (category=2 or category=6)'
                             ' GROUP BY mon ORDER BY mon',
                             (year,)
                             )
    df_food_total = pd.DataFrame(food_total.fetchall())
    df_food_total.columns = food_total.keys()
    con.close()

    total_food = [0] * 12
    for index in range(len(df_food_total)):
        total_food[df_food_total['mon'][index]-1] = df_food_total['summary'][index]

    # save the Food and Grocery into its own variable
    df_grocery = df_food[df_food['name'] == 'Grocery']
    df_food = df_food[df_food['name'] == 'Food']

    food_bar = [0] * 12
    grocery_bar = [0] * 12
    for index in range(len(df_grocery)):
        grocery_bar[df_grocery['mon'].tolist()[index]-1] = df_grocery['summary'].tolist()[index]
    for index in range(len(df_food)):
        food_bar[df_food['mon'].tolist()[index]-1] = df_food['summary'].tolist()[index]

    title = f'Total Spending of Food and Grocery in {year}'
    ylabel = "Dolors"
    xlabel = "Month"

    # Then add the line and point onto the plot
    fig = Figure()
    axisB = fig.add_subplot(1, 1, 1, title=title, xlabel=xlabel, ylabel=ylabel, ylim=(0, 1500))
    pg = axisB.bar(months, grocery_bar, 0.35, color='#66b3ff')
    pf = axisB.bar(months, food_bar, 0.35, bottom=grocery_bar, color='#ff9999')
    axisB.plot(months, total_food)
    axisB.scatter(months, total_food)

    # add the color mapping
    axisB.legend((pg[0], pf[0]), ('Grocery', 'Food'))

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@bp.route('/<int:year>/groceryReport.png')
def groceryReport(year):
    engine = create_engine("sqlite:///instance/finTrack.sqlite")
    con = engine.connect()
    # Select Food and Grocery total amount of each month
    food = con.execute('SELECT SUM(amount) as summary, c.name, mon' +
                       ' FROM spending LEFT JOIN categories AS c on category=c.id' +
                       ' WHERE yr=? and (category=2 or category=6)'
                       ' GROUP BY category, mon ORDER BY mon',
                       (year,)
                       )
    df_food = pd.DataFrame(food.fetchall())
    df_food.columns = food.keys()
    con.close()

    # save the Food and Grocery into its own variable
    df_grocery = df_food[df_food['name'] == 'Grocery']
    grocery_bar = [0] * 12
    for index in range(len(df_grocery)):
        grocery_bar[df_grocery['mon'].tolist()[index] - 1] = df_grocery['summary'].tolist()[index]

    # Plot for Grocery Only
    fig = Figure()
    title = f'Total Spending of Grocery in {year}'
    ylabel = "Dolors"
    xlabel = "Month"
    axisG = fig.add_subplot(1, 1, 1, title=title, xlabel=xlabel, ylabel=ylabel, ylim=(0, 1000))
    axisG.bar(months, grocery_bar, 0.35, color='#66b3ff')
    axisG.plot(months, grocery_bar)
    axisG.scatter(months, grocery_bar)

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@bp.route('/<int:year>/foodReport.png')
def foodReport(year):
    engine = create_engine("sqlite:///instance/finTrack.sqlite")
    con = engine.connect()
    # Select Food and Grocery total amount of each month
    food = con.execute('SELECT SUM(amount) as summary, c.name, mon' +
                       ' FROM spending LEFT JOIN categories AS c on category=c.id' +
                       ' WHERE yr=? and (category=2 or category=6)'
                       ' GROUP BY category, mon ORDER BY mon',
                       (year,)
                       )
    df_food = pd.DataFrame(food.fetchall())
    df_food.columns = food.keys()
    con.close()

    # save the Food and Grocery into its own variable
    df_food = df_food[df_food['name'] == 'Food']
    food_bar = [0] * 12
    for index in range(len(df_food)):
        food_bar[df_food['mon'].tolist()[index]-1] = df_food['summary'].tolist()[index]

    # Plot for Grocery Only
    fig = Figure()
    title = f'Total Spending of Restaurant in {year}'
    ylabel = "Dolors"
    xlabel = "Month"
    # Plot for Food Only
    axisF = fig.add_subplot(1, 1, 1, title=title, xlabel=xlabel, ylabel=ylabel, ylim=(0, 1000))
    axisF.bar(months, food_bar, 0.35, color='#ff9999')
    axisF.plot(months, food_bar)
    axisF.scatter(months, food_bar)

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')
