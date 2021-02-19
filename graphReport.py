import io

import pandas as pd
from flask import Blueprint, Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from .db_utils import Spending, Category

bp = Blueprint('graph', __name__, url_prefix='/graph')
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


@bp.route('/<int:year>/annualReport.png')
def annualReport(year):
    df_monthly = pd.DataFrame(Spending().get_total_spending_amount_of_each_month(year=year, include_doctor=False))
    df_monthly.columns = ['sum', 'mon']
    month_spendings = [0]*12
    for month_index in range(len(df_monthly['sum'])):
        month_spendings[df_monthly['mon'][month_index]-1] = df_monthly['sum'][month_index]

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


@bp.route('/<int:year>/<int:month>/monthReport.png')
def monthReport(year, month):
    month_translate = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April',
        5: 'May', 6: 'June', 7: 'July', 8: 'August',
        9: 'September', 10: 'October', 11: 'November', 12: 'December',
    }
    monthly_summary = Spending().get_each_category_total_spending_amount_of_month(year, month, include_doctor=False,
                                                                                  category_name=True)
    df_monthly_summary = pd.DataFrame(monthly_summary)
    df_monthly_summary.columns = ['sum', 'name']

    title = f'{year} {month_translate[month]} Monthly Summary'
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
    explode = [0.1] * len(df_monthly_summary.index)
    axis.pie(df_monthly_summary['sum'], colors=colors, labels=df_monthly_summary['name'],
             autopct='%1.1f%%', startangle=180, explode=explode, radius=1)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@bp.route('/<int:year>/utilityReport.png')
def utilityReport(year):
    utility_category_id = Category().get_category_id_by_name('Utility')
    # Select each utility category's total amount of each month
    df_utility_for_bar = pd.DataFrame(
        Spending().get_sub_category_monthly_spending_of_a_category(year, [utility_category_id])
    )
    df_utility_for_bar.columns = ['sum', 'name', 'mon']

    # Select the total amount of utility of each month
    df_utility_for_line = pd.DataFrame(
        Spending().get_specific_category_monthly_spending(year, [utility_category_id])
    )
    df_utility_for_line.columns = ['sum', 'mon']

    total_utility = [0] * 12
    for index in range(len(df_utility_for_line)):
        total_utility[df_utility_for_line['mon'][index]-1] = df_utility_for_line['sum'][index]

    # save the each utility category into its own variable
    df_water = df_utility_for_bar[df_utility_for_bar['name'] == 'Water and Waste']
    df_electricity = df_utility_for_bar[df_utility_for_bar['name'] == 'Electricity']
    df_internet = df_utility_for_bar[df_utility_for_bar['name'] == 'Internet']
    df_gas = df_utility_for_bar[df_utility_for_bar['name'] == 'Nature Gas']
    df_mobile = df_utility_for_bar[df_utility_for_bar['name'] == 'Mobile Bill']

    # Save the previous amount of each utility category; will be used in the stack column
    water_bar = [0] * 12
    electrisity_bar = [0] * 12
    internet_bar = [0] * 12
    gas_bar = [0] * 12
    mobile_bar = [0] * 12

    for index in range(len(df_water)):
        water_bar[df_water['mon'].tolist()[index]-1] = df_water['sum'].tolist()[index]
    electrisity_base = water_bar[:]
    internet_base = electrisity_base[:]
    for index in range(len(df_electricity)):
        electrisity_bar[df_electricity['mon'].tolist()[index]-1] = df_electricity['sum'].tolist()[index]
        internet_base[df_electricity['mon'].tolist()[index] - 1] += df_electricity['sum'].tolist()[index]
    gas_base = internet_base[:]
    for index in range(len(df_internet)):
        internet_bar[df_internet['mon'].tolist()[index]-1] = df_internet['sum'].tolist()[index]
        gas_base[df_internet['mon'].tolist()[index] - 1] += df_internet['sum'].tolist()[index]
    mobile_base = gas_base[:]
    for index in range(len(df_gas)):
        gas_bar[df_gas['mon'].tolist()[index]-1] += df_gas['sum'].tolist()[index]
        mobile_base[df_gas['mon'].tolist()[index] - 1] += df_gas['sum'].tolist()[index]
    for index in range(len(df_mobile)):
        mobile_bar[df_mobile['mon'].tolist()[index]-1] += df_mobile['sum'].tolist()[index]

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
    category_list = [Category().get_category_id_by_name('Food'), Category().get_category_id_by_name('Grocery')]
    # Select Food and Grocery total amount of each month
    df_food_for_bar = pd.DataFrame(
        Spending().get_categories_monthly_spending_with_category_name(year, category_list)
    )
    df_food_for_bar.columns = ['sum', 'name', 'mon']

    # Select the total amount of both Food and Grocery of each month
    df_food_for_line = pd.DataFrame(
        Spending().get_specific_category_monthly_spending(year, category_list)
    )
    df_food_for_line.columns = ['sum', 'mon']

    total_food = [0] * 12
    for index in range(len(df_food_for_line)):
        total_food[df_food_for_line['mon'][index]-1] = df_food_for_line['sum'][index]

    # save the Food and Grocery into its own variable
    df_grocery = df_food_for_bar[df_food_for_bar['name'] == 'Grocery']
    df_food_for_bar = df_food_for_bar[df_food_for_bar['name'] == 'Food']

    food_bar = [0] * 12
    grocery_bar = [0] * 12
    for index in range(len(df_grocery)):
        grocery_bar[df_grocery['mon'].tolist()[index]-1] = df_grocery['sum'].tolist()[index]
    for index in range(len(df_food_for_bar)):
        food_bar[df_food_for_bar['mon'].tolist()[index]-1] = df_food_for_bar['sum'].tolist()[index]

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
    grocery_category_id = Category().get_category_id_by_name('Grocery')
    # Select Grocery total amount of each month
    df_grocery = pd.DataFrame(
        Spending().get_specific_category_monthly_spending(year, [grocery_category_id])
    )
    df_grocery.columns = ['sum', 'mon']

    # save the Food and Grocery into its own variable
    grocery_bar = [0] * 12
    for index in range(len(df_grocery)):
        grocery_bar[df_grocery['mon'].tolist()[index] - 1] = df_grocery['sum'].tolist()[index]

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
    food_category_id = Category().get_category_id_by_name('Food')
    # Select Food total amount of each month
    df_food = pd.DataFrame(
        Spending().get_specific_category_monthly_spending(year, [food_category_id])
    )
    df_food.columns = ['sum', 'mon']

    # save the Food and Grocery into its own variable
    food_bar = [0] * 12
    for index in range(len(df_food)):
        food_bar[df_food['mon'].tolist()[index]-1] = df_food['sum'].tolist()[index]

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
