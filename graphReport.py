import io
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from flask import Blueprint, Response

bp = Blueprint('graph', __name__, url_prefix='/graph')


@bp.route('/annualReport.png')
def annualReport():
    engine = create_engine("sqlite:///instance/finTrack.sqlite")
    con = engine.connect()
    monthly = con.execute('SELECT SUM(amount) as summary, mon' +
                          ' FROM spending' +
                          ' GROUP BY mon ORDER BY mon')
    df_monthly = pd.DataFrame(monthly.fetchall())
    df_monthly.columns = monthly.keys()
    con.close()

    title = "Totle Spending of each Month in 2019"
    ylabel = "Dolors"
    xlabel = "Month"
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1, title=title, xlabel=xlabel, ylabel=ylabel, ylim=(0, 10000))
    axis.plot(df_monthly['mon'], df_monthly['summary'])
    axis.scatter(df_monthly['mon'], df_monthly['summary'])
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@bp.route('/<int:month>/monthReport.png')
def monthReport(month):
    engine = create_engine("sqlite:///instance/finTrack.sqlite")
    con = engine.connect()
    summary = con.execute('SELECT SUM(amount) as summary, c.name' +
                          ' FROM spending LEFT JOIN categories AS c on category = c.id' +
                          ' WHERE mon=? GROUP BY category ORDER BY SUM(amount) DESC',
                          (month,)
                          )
    df_summary = pd.DataFrame(summary.fetchall())
    df_summary.columns = summary.keys()
    con.close()

    title = str(month)+" Monthly Summary"
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ffc4d8', '#9bf6ff', '#ffe39e', '#ffd3b8', '#e9fba6',
              '#adebad', '#99ffeb']
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1, title=title)
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
    explode = [0.2] * len(df_summary.index)
    axis.pie(df_summary['summary'], colors=colors, labels=df_summary['name'],
            autopct='%1.1f%%', startangle=90, explode=explode, radius=1)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@bp.route('/utilityReport.png')
def utilityReport():
    engine = create_engine("sqlite:///instance/finTrack.sqlite")
    con = engine.connect()
    # Select each utility category's total amount of each month
    utility = con.execute('SELECT SUM(amount) as summary, s.name, mon' +
                          ' FROM spending LEFT JOIN sub_categories AS s on sub_category=s.id' +
                          ' WHERE category=3'
                          ' GROUP BY sub_category, mon ORDER BY mon')
    df_utility = pd.DataFrame(utility.fetchall())
    df_utility.columns = utility.keys()

    # Select the total amount of utility of each month
    utility_total = con.execute('SELECT SUM(amount) as summary, mon' +
                                ' FROM spending' +
                                ' WHERE category=3'
                                ' GROUP BY mon ORDER BY mon')
    df_utility_total = pd.DataFrame(utility_total.fetchall())
    df_utility_total.columns = utility_total.keys()
    con.close()

    # save the each utility category into its own variable
    df_water = df_utility[df_utility['name'] == 'Water and Waste']
    df_electricity = df_utility[df_utility['name'] == 'Electricity']
    df_internet = df_utility[df_utility['name'] == 'Internet']
    df_gas = df_utility[df_utility['name'] == 'Nature Gas']
    df_mobile = df_utility[df_utility['name'] == 'Mobile Bill']

    # Save the previous amount of each utility category; will be used in the stack column
    for_electrisity = df_water['summary'].tolist()
    for_internet = (for_electrisity + df_electricity['summary']).tolist()
    for_gas = (for_internet + df_internet['summary']).tolist()
    for_mobile = (for_gas + df_gas['summary']).tolist()
    # Since there is no data for mobile bill in March, so remove the first entry from the other utility categories
    for_mobile = for_mobile[1:]
    # and add the last 0 entry if there is no data
    if len(for_mobile) != len(df_mobile.index):
        for_mobile += [0]

    # set the month from water entry as the default month
    month = df_water['mon'].tolist()

    title="The report of Utility"
    # Add y axis lable and the title
    ylabel="Dolors"
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1, title=title, ylabel=ylabel)
    # stack each utility category onto the previous one
    pw = axis.bar(month, df_water['summary'], width=0.35, color='#66b3ff')
    pe = axis.bar(month, df_electricity['summary'], width=0.35, bottom=for_electrisity, color='#ff9999')
    pi = axis.bar(month, df_internet['summary'], width=0.35, bottom=for_internet, color='#99ff99')
    pg = axis.bar(month, df_gas['summary'], width=0.35, bottom=for_gas, color='#ffcc99')
    pm = axis.bar(df_mobile['mon'].tolist(), df_mobile['summary'], width=0.35, bottom=for_mobile, color='#9bf6ff')

    # Then add the line and point onto the plot
    axis.plot(df_utility_total['mon'], df_utility_total['summary'])
    axis.scatter(df_utility_total['mon'], df_utility_total['summary'])

    # add the color mapping
    axis.legend((pw[0], pe[0], pi[0], pg[0], pm[0]),
               ('Water and Waste', 'Electricity', 'Internet', 'Natral Gas', 'Mobile Bill'))

    # show the plot
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@bp.route('/eatingReport.png')
def eatingReport():
    engine = create_engine("sqlite:///instance/finTrack.sqlite")
    con = engine.connect()
    # Select Food and Grocery total amount of each month
    food = con.execute('SELECT SUM(amount) as summary, c.name, mon' +
                       ' FROM spending LEFT JOIN categories AS c on category=c.id' +
                       ' WHERE category=2 or category=6'
                       ' GROUP BY category, mon ORDER BY mon')
    df_food = pd.DataFrame(food.fetchall())
    df_food.columns = food.keys()

    # Select the total amount of both Food and Grocery of each month
    food_total = con.execute('SELECT SUM(amount) as summary, mon' +
                             ' FROM spending' +
                             ' WHERE category=2 or category=6'
                             ' GROUP BY mon ORDER BY mon')
    df_food_total = pd.DataFrame(food_total.fetchall())
    df_food_total.columns = food_total.keys()
    con.close()

    # save the Food and Grocery into its own variable
    df_grocery = df_food[df_food['name'] == 'Grocery']
    df_food = df_food[df_food['name'] == 'Food']

    # Save the Grocery spending into numpy array; will be used in the stack column
    for_food = df_grocery['summary'].tolist()

    month = df_grocery['mon'].tolist()
    title = "Total Spending of Food and Grocery in 2019"
    ylabel = "Dolors"
    xlabel = "Month"

    # Then add the line and point onto the plot
    fig = Figure()
    axisB = fig.add_subplot(1, 1, 1, title=title, xlabel=xlabel, ylabel=ylabel, ylim=(0, 1500))
    pg = axisB.bar(month, df_grocery['summary'], 0.35, color='#66b3ff')
    pf = axisB.bar(month, df_food['summary'], 0.35, bottom=for_food, color='#ff9999')
    axisB.plot(df_food_total['mon'], df_food_total['summary'])
    axisB.scatter(df_food_total['mon'], df_food_total['summary'])

    # add the color mapping
    axisB.legend((pg[0], pf[0]), ('Grocery', 'Food'))

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@bp.route('/groceryReport.png')
def groceryReport():
    engine = create_engine("sqlite:///instance/finTrack.sqlite")
    con = engine.connect()
    # Select Food and Grocery total amount of each month
    food = con.execute('SELECT SUM(amount) as summary, c.name, mon' +
                       ' FROM spending LEFT JOIN categories AS c on category=c.id' +
                       ' WHERE category=2 or category=6'
                       ' GROUP BY category, mon ORDER BY mon')
    df_food = pd.DataFrame(food.fetchall())
    df_food.columns = food.keys()
    con.close()

    # save the Food and Grocery into its own variable
    df_grocery = df_food[df_food['name'] == 'Grocery']

    month = df_grocery['mon'].tolist()

    # Plot for Grocery Only
    fig = Figure()
    title = "Total Spending of Grocery in 2019"
    ylabel = "Dolors"
    xlabel = "Month"
    axisG = fig.add_subplot(1, 1, 1, title=title, xlabel=xlabel, ylabel=ylabel, ylim=(0, 1000))
    axisG.bar(month, df_grocery['summary'], 0.35, color='#66b3ff')
    axisG.plot(df_grocery['mon'], df_grocery['summary'])
    axisG.scatter(df_grocery['mon'], df_grocery['summary'])

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@bp.route('/foodReport.png')
def foodReport():
    engine = create_engine("sqlite:///instance/finTrack.sqlite")
    con = engine.connect()
    # Select Food and Grocery total amount of each month
    food = con.execute('SELECT SUM(amount) as summary, c.name, mon' +
                       ' FROM spending LEFT JOIN categories AS c on category=c.id' +
                       ' WHERE category=2 or category=6'
                       ' GROUP BY category, mon ORDER BY mon')
    df_food = pd.DataFrame(food.fetchall())
    df_food.columns = food.keys()
    con.close()

    # save the Food and Grocery into its own variable
    df_food = df_food[df_food['name'] == 'Food']

    month = df_food['mon'].tolist()

    # Plot for Grocery Only
    fig = Figure()
    title = "Total Spending of Restaurant in 2019"
    ylabel = "Dolors"
    xlabel = "Month"
    # Plot for Food Only
    axisF = fig.add_subplot(1, 1, 1, title=title, xlabel=xlabel, ylabel=ylabel, ylim=(0, 1000))
    axisF.bar(month, df_food['summary'], 0.35, color='#ff9999')
    axisF.plot(df_food['mon'], df_food['summary'])
    axisF.scatter(df_food['mon'], df_food['summary'])

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')