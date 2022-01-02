import datetime as dt
import io
from math import e
from attr import field

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas.core.reshape.pivot import pivot_table
import plotly
import plotly.express as px
import plotly.figure_factory as ff
import seaborn as sns
import streamlit as st
from matplotlib import colors
from pandas._config.config import options
from pandas.core import groupby
from pandas.core.algorithms import mode
from pandas.core.frame import DataFrame
from PIL import Image
from sklearn import linear_model
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import PolynomialFeatures
from streamlit.elements.arrow import Data

# from covidcases import covidInfectionTendence
# from coviddeaths import covidDeathsByCountry,covidDeathsPredictionByDep


def generatePredictionGraph(y: DataFrame, grade, days, max_val):

    X = []
    Y = y
    print(y)

    size = y.__len__()
    for i in range(0, size):
        X.append(i)

    #st.write('XD')
    #st.write(Y)
    X = np.asarray(X)
    Y = np.asarray(Y)

    X = X[:, np.newaxis]
    Y = Y[:, np.newaxis]

    # GRAPH 1 
    #st.subheader("Plot graph")
    #st.set_option('deprecation.showPyplotGlobalUse', False)
    #plt.scatter(X, Y)
    #plt.show()
    #st.pyplot()

    # st.write(Y)
    # Step 2: Data preparation
    nb_degree = grade

    polynomial_features = PolynomialFeatures(degree=nb_degree)
    X_TRANSF = polynomial_features.fit_transform(X)

    # ## print(Y)
    # Step 3: define and train a model
    model = LinearRegression()
    model.fit(X_TRANSF, Y)

    # Step 4: calculate bias and variance
    Y_NEW = model.predict(X_TRANSF)

    rmse = np.sqrt(mean_squared_error(Y, Y_NEW))
    r2 = r2_score(Y, Y_NEW)

    print('RMSE: ', rmse)
    print('R2: ', r2)

    # Step 5: predicition
    x_new_min = 0.0
    x_new_max = float(days)  ## days to predict

    X_NEW = np.linspace(x_new_min, x_new_max, 50)
    X_NEW = X_NEW[:, np.newaxis]

    X_NEW_TRANSF = polynomial_features.fit_transform(X_NEW)

    Y_NEW = model.predict(X_NEW_TRANSF)
    
    st.subheader("Plot graph")
    plt.scatter(X, Y)
    plt.plot(X_NEW, Y_NEW, color='green', linewidth=3)
    #plt.scatter(X_NEW, Y_NEW, color='blue', linewidth=3)
    plt.grid()
    plt.xlim(x_new_min, x_new_max)  ## X axis

    plt.ylim(0, Y_NEW[int(Y_NEW.size - 1)])
    #title = 'Degree={ }; RMSE={ }; R2={ }'.format(nb_degree, round(rmse, 2), round(r2, 2))
    plt.title('Prediction')
    plt.xlabel('x')
    plt.ylabel('y')

    plt.savefig('pol_reg.jpg', bbox_inches='tight')
    plt.show()
    st.pyplot()
    st.caption('Prediction graph')
    st.write("La predicción será de ", Y_NEW[int(Y_NEW.size - 1)][0])

    #
    #fig = ff.create_distplot(Y_NEW, ['test'], bin_size=[0] )

    pass


def generateTendencyGraph(y, header, maxY):
    x = []
    #y = country_infections[select_col[2]]

    for i in range(0, y.__len__()):
        x.append(i)

    X = np.asarray(x).reshape(-1, 1)
    reg = linear_model.LinearRegression()
    reg.fit(X, y)
    y_pred = reg.predict(X)

    plt.scatter(X, y, color='black')
    plt.plot(X, y_pred, color='blue', linewidth=3)

    #print(reg.predict([[10]]))
    max_val = maxY

    # Header
    st.subheader(header)

    plt.ylim(-10, max_val + 10)
    plt.show()
    st.pyplot()
    st.caption('COVID-19 tendence graph')
    st.info("""Para poder comprender de mejor forma esta grafica,
    es importante tomar en cuenta la pendiente generada, por ejemplo si la pendiente es creciente (positiva)
    la tendencia de contagios en los dias siguientes al analisis será a la alta, pero si de lo contrario
    la pendiente de la grafica es decreciente (negativa), la tendencia numero de contagios es a la baja.
    """)


# ===================== METHODS =====================


# Tendencia de la infección por Covid-19 en un País.
def covidInfectionTendence(data: DataFrame):

    data_options = st.multiselect('Select filter [country]: ', data.columns)
    # st.write(data_options)
    try:

        country_options = st.multiselect(
            'Select country', data[data_options[0]].drop_duplicates())

        country = [country_options[0]]

        flt = data[data[data_options[0]].isin(country)]

        have_date = st.checkbox('This file has "date" field')

        st.write(have_date)

        if have_date:
            variable = st.multiselect(
                'Select variables to analize [date, numeric]: ', data.columns)
            #st.write(flt)
            st.write(variable)
            # data

            flt[variable[0]] = pd.to_datetime(flt[variable[0]])
            flt[variable[0]] = flt[variable[0]]

            flt = flt[[variable[0], variable[1]]].sort_values(by=[variable[0]])

            st.write(flt)
            #sum
            st.write(
                flt.groupby([variable[0], variable[1]]).sum().reset_index())

            # Tendency
            generateTendencyGraph(flt[variable[1]],
                                  "Tendency COVID spread by country",
                                  flt[variable[1]].max())
        else:
            variable = st.selectbox('Select variable to analyze: ',
                                    data.columns)

            st.write(flt[variable])

            generateTendencyGraph(flt[variable],
                                  "Tendency COVID spread by country",
                                  flt[variable].max())

            #generatePredictionGraph(flt[variable], 3, 40, flt[variable].max())

    except Exception as e:
        st.write(e)
        st.warning("Please select a field")


# Predicción de Infectados en un País.
def covidInfectedPredictionByCountry(data: DataFrame):

    have_date = st.checkbox('This file has "date" field')

    try:
        if have_date:
            option = st.multiselect(
                'Select date, country and numeric variable: ', data.columns)

            df = data[[option[0], option[1], option[2]]]
            #st.write(df)
            country = st.selectbox('Select country: ',
                                   df[[option[1]]].drop_duplicates())

            # Filter data by country
            c = [country]

            data[data[option[1]].isin(c)]

            y = data[option[2]]

            days = st.slider('Select a number of days to predict', 5, 1000)

            grade = st.slider('Select a polynomial grade prediction: ', 1, 5)
            # print(y)
            generatePredictionGraph(y, grade, days, y.max())

        else:

            option = st.multiselect(
                'Select a field, and numeric variable to filter [ex. country, infections]: ',
                data.columns)

            country = st.selectbox('Select country',
                                   data[option[0]].drop_duplicates())

            data = data[data[option[0]].isin([country])]

            data[[option[0], option[1]]]

            days = st.slider('Select a number of days to predict', 5, 1000)

            grade = st.slider('Select a polynomial grade prediction: ', 1, 5)

            y = data[option[1]]
            generatePredictionGraph(y, grade, days, y.max())
            #st.write(data)
            pass

    except Exception as e:
        st.write(e)
        st.warning('Please select three fields')

    # infected = st.multiselect('Select numeric variable: ', data.columns)

    pass


# Indice de Progresión de la pandemia.


# Tendencia de la vacunación de en un País.
def vaccinationTendencyByCountry(data: DataFrame):

    data_options = st.multiselect(
        'Select [date, country/region, and numeric variable]: ', data.columns)

    try:

        region = data_options[1]

        country = st.selectbox('Select country: ',
                               data[region].drop_duplicates())

        data = data[data[region].isin([country])]

        st.write(data)

        vac = data[data_options[2]]

        st.write(vac)

        generateTendencyGraph(vac, "Vaccines trend graph", vac.max() + 500)

    except Exception as e:
        st.write(e)
        st.warning(":c")


# Ánalisis Comparativo de Vacunación entre 2 paises.
def vaccinationComparationByCountries(data: DataFrame):

    try:

        option = st.multiselect(
            'Select field and variable of comparation [place, variable, group by] : ',
            data.columns)

        place = option[0]
        variable = option[1]
        col1, col2 = st.columns(2)

        with col1:

            st.subheader('Select Place 1:')
            country1 = st.selectbox('Select country 1: ',
                                    data[place].drop_duplicates())
            p1 = data[data[place].isin([country1])]

            #st.write(p1[variable])
            t1 = p1[variable].sum()
            generateTendencyGraph(p1[variable], 'Country1', p1[variable].max())

        with col2:

            st.subheader('Select Place 2:')
            country2 = st.selectbox('Select country 2: ',
                                    data[place].drop_duplicates())
            p2 = data[data[place].isin([country2])]

            #st.write(p2[variable])
            t2 = p2[variable].sum()
            generateTendencyGraph(p2[variable], 'Country2', p2[variable].max())

        ## graph
        plotdata = pd.DataFrame({str(variable): [t1, t2]},
                                index=[country1, country2])

        st.bar_chart(plotdata)
        st.caption('Vaccination comparative graph')

        ## Interpretación
        if t1 > t2:
            st.info(
                'De acuerdo a la grafica, {} presenta una mejor tasa de vacunacion que {}'
                .format(country1, country2))

        # st.set_option('deprecation.showPyplotGlobalUse', False)
        # plotdata.plot(kind="bar", color="green")
        # plt.title("Comparative")
        # st.pyplot()

    except Exception as e:

        st.write(e)
        st.warning('Error :(')


# Predicción de mortalidad por COVID en un Departamento.
def covidDeathsPredictionByDeparment(data: DataFrame):

    try:
        # date, state, cases
        data_options = st.multiselect(
            'Select fields [date, region, cases, filter]: ', data.columns)

        date_ = data_options[0]
        region = data_options[1]
        cases = data_options[2]
        flter = data_options[3]

        st.write(data_options)

        country_option = st.selectbox('Select country',
                                      data[region].drop_duplicates())

        ## select states
        c = [country_option]
        cs = data[data[region].isin(c)]

        province = st.selectbox('Select state/province/department',
                                cs[flter].drop_duplicates())

        # Filter by deparment/state
        dep = cs[data[flter].isin([province])]

        ## convert dates
        dep[date_] = pd.to_datetime(dep[date_])
        dep = dep.sort_values(by=date_)
        st.write(dep[[date_, cases]])

        y = dep[cases]

        # slider
        n_days = st.slider('Select number of days to predict: ', 5, 100)
        grade = st.slider('Select grade of the regression: ', 1, 3)
        max_val = dep[cases].max()

        generatePredictionGraph(y, grade, n_days, max_val)

    except Exception as e:
        st.write(e)
        st.warning('Select a field')


# Ánalisis Comparativo entres 2 o más paises o continentes.
def covidComparative(data: DataFrame):

    try:

        option = st.multiselect(
            'Select field and variable of comparation [place, variable, group by] : ',
            data.columns)

        place = option[0]
        variable = option[1]

        countries = st.multiselect('Select list of countries: ',
                                   data[place].drop_duplicates())
        st.write(countries)

        elements = []
        #size =
        if countries.__len__() >= 2:

            for i in range(0, countries.__len__()):
                country = countries[i]
                temp = data[data[place].isin([country])]
                val = temp[variable].sum()
                elements.append(val)

            # Graph
            plotdata = pd.DataFrame({
                str(variable): elements,
            },
                                    index=[countries])

            st.set_option('deprecation.showPyplotGlobalUse', False)
            plotdata.plot(kind="bar", color="blue")
            plt.title("Comparative")
            st.pyplot()

        else:
            st.warning('Please, select more countries ')

        # col1, col2 = st.columns(2)

        # with col1:

        #     st.subheader('Select Place 1:')
        #     country1 = st.selectbox('Select country 1: ',
        #                             data[place].drop_duplicates())
        #     p1 = data[data[place].isin([country1])]

        #     st.write(p1[variable].sum())
        #     t1 = p1[variable].sum()

        # with col2:

        #     st.subheader('Select Place 2:')
        #     country2 = st.selectbox('Select country 2: ',
        #                             data[place].drop_duplicates())
        #     p2 = data[data[place].isin([country2])]

        #     st.write(p2[variable].sum())
        #     t2 = p2[variable].sum()

        # ## Graph
        # plotdata = pd.DataFrame({
        #     str(variable): [t1, t2],
        # },
        #                         index=[country1, country2])

        # st.set_option('deprecation.showPyplotGlobalUse', False)
        # plotdata.plot(kind="bar", color="green")
        # plt.title("Comparative")
        # st.pyplot()

    except Exception as e:

        st.write(e)
        st.warning('Error :(')

    # if option == 'Countries':

    # elif option == 'Continents':

    #     col1, col2 = st.columns(2)

    #     with col1:
    #         st.subheader('Select Continent 1:')
    #         continent1 = st.selectbox('Select continent 1: ', data.columns)

    #     with col2:
    #         st.subheader('Select Continent 2:')
    #         continent2 = st.selectbox('Select continent 2: ', data.columns)


# Tendencia del número de infectados por día de un País
def covidInfectedByDay(data: DataFrame):

    select_col = st.multiselect(
        'Select a columns to parameterize (date, country and numeric variable): ',
        data.columns)

    #st.write(select_col)

    try:
        # select_date = st.selectbox('Select a date: ',
        #                            data[select_col[0]].drop_duplicates())

        select_country = st.selectbox('Select a country: ',
                                      data[select_col[1]].drop_duplicates())

        ## Filter data
        country = [select_country]

        country_infections = data[data[select_col[1]].isin(country)]  ##

        ## sort
        country_infections[select_col[0]] = pd.to_datetime(
            country_infections[
                select_col[0]])  #country_infections.sort_values(by='Date')
        st.write(country_infections)

        # group by and sum
        #st.write(country_infections.groupby([select_col[0], select_col[1]]).sum().sort_values(by='date'))

        fig = country_infections.groupby(
            [select_col[0],
             select_col[1]]).sum().sort_values(by=select_col[0]).head()

        st.write(fig)

        # x = []
        y = country_infections[select_col[2]]
        hd = "COVID-19 Spread tendency in " + country[0]
        max_val = country_infections[select_col[2]].max()

        generateTendencyGraph(y, hd, max_val)

    except Exception as e:
        st.write(e)
        st.warning('Select the fields ')

    pass


# Predicción de mortalidad por COVID en un País
def covidDeathPredictionByCountry(data: DataFrame):

    data_options = st.multiselect('Select fields', data.columns)

    try:
        df = data[data_options[0]]
        country_options = st.multiselect('Select country: ', df)
        country = data.loc[data[data_options[0]] == country_options[0]]
        size = country.columns.__len__()

        #
        start = st.slider("Select a start day: ", 0, size)
        end = st.slider("Select an end day: ", 0, size)

        if end > start:
            # x axis
            st.write("Range between ", country.columns[start], " and ",
                     country.columns[end])
            # st.write(country[start])
            x = country.columns[4:size - 1]
            x = pd.to_datetime(x, format='%m/%d/%y')
            # y axis
            deaths = country.loc[:,
                                 country.columns[4]:country.columns[size - 1]]
            data_index = deaths.index[0]

            st.write(deaths.loc[data_index][end])  # No borrar XD
            X = []
            Y = deaths.loc[data_index][start:end]
            # st.write(deaths.loc[data_index][start:end])
            for i in range(start, end):

                X.append(i)

            X = np.asarray(X)
            Y = np.asarray(Y)

            X = X[:, np.newaxis]
            Y = Y[:, np.newaxis]

            plt.scatter(X, Y)
            plt.show()
            st.pyplot()

            # Step 2:
            nb_degree = 3

            polynomial_features = PolynomialFeatures(degree=nb_degree)
            X_TRANSF = polynomial_features.fit_transform(X)

            # Step 3:
            model = LinearRegression()
            model.fit(X_TRANSF, Y)

            # Step 4:
            Y_NEW = model.predict(X_TRANSF)

            rmse = np.sqrt(mean_squared_error(Y, Y_NEW))
            r2 = r2_score(Y, Y_NEW)

            st.write('RMSE: ', rmse)
            st.write('R2', r2)

            # Step 5:
            n_days = st.slider("Days to predict ", 0, 100)
            x_new_min = start
            x_new_max = start + n_days

            X_NEW = np.linspace(x_new_min, x_new_max)
            X_NEW = X_NEW[:, np.newaxis]

            X_NEW_TRANSF = polynomial_features.fit_transform(X_NEW)
            Y_NEW = model.predict(X_NEW_TRANSF)

            plt.plot(X_NEW, Y_NEW, color='coral', linewidth=3)

            plt.grid()
            plt.xlim(x_new_min, x_new_max)
            # st.write(Y[x_new_max])
            plt.ylim(0, deaths.loc[data_index][end] + 50)

            st.write("## Covid deaths prediction for ",
                     country.columns[start + n_days])

            plt.title('Covid prediction')
            plt.xlabel('x')
            plt.ylabel('y')

            plt.show()
            st.pyplot()

            # image = plt.savefig('pol_reg.jpg', bbox_inches='tight')
            # with open(image, "rb") as file:
            #     btn = st.download_button(
            #             label="Download image",
            #             data=file,
            #             file_name="image.png",
            #             mime="image/jpg"
            #         )

        try:
            st.write("")

        except:
            st.warning('The graph could not be generated')

    except:

        st.warning('Please select a field')


# Análisis del número de muertes por coronavirus en un País.
def covidDeathsByCountry(data: DataFrame):

    data_options = st.multiselect(
        'Select field, and variables to analize [ex. country, deaths, date]: ',
        data.columns)

    try:
        # IMPORTANTE REVISAR AQUI XD
        country = st.selectbox('Select country',
                               data[data_options[0]].drop_duplicates())

        data = data[data[data_options[0]].isin([country])]

        data[data_options[2]] = pd.to_datetime(data[data_options[2]])

        st.subheader('Deaths analysis in {}'.format(country))
        st.write(data[[data_options[1], data_options[2]]])


        y = data[data_options[1]]

        generateTendencyGraph(y, 'Deaths in {}'.format(country), y.max())



    except Exception as e:
        st.write(e)
        st.warning("Please select a field")


# Tendencia de casos confirmados de Coronavirus en un departamento de un País
def covidCasesByDep(data: DataFrame):

    try:
        # date, state, cases
        data_options = st.multiselect(
            'Select fields [date, region, cases, filter]: ', data.columns)

        st.write(data_options)

        country_option = st.selectbox('Select country',
                                      data[data_options[1]].drop_duplicates())

        ## select states
        c = [country_option]
        cs = data[data[data_options[1]].isin(c)]

        # Select department
        province = st.selectbox('Select state/province/department',
                                cs[data_options[3]].drop_duplicates())

        #st.write(cs)
        # Filter by deparment/state
        dep = cs[data[data_options[3]].isin([province])]

        #st.write(dep)
        #st.write(dep[[data_options[0], data_options[2]]])

        ## convert dates
        dep[data_options[0]] = pd.to_datetime(dep[data_options[0]])
        dep = dep.sort_values(by=data_options[0])
        st.write(dep[[data_options[0], data_options[2]]])

        y = dep[data_options[2]]
        hd = "COVID-19 Spread tendency in " + province
        max_val = dep[data_options[2]].max()
        #st.write(max_val)
        generateTendencyGraph(y, hd, max_val)

    except Exception as e:
        st.write(e)
        st.warning('Select a field')


# Comparación entre el número de casos detectados y el número de pruebas de un país.
def covidCasesTestComparation(data: DataFrame):

    try:
        options = st.multiselect(
            'Select fields to filter [Country, cases, tests]', data.columns)

        place = options[0]
        var1 = options[1]
        var2 = options[2]

        country = st.selectbox('Select country', data[place].drop_duplicates())

        flt = data[data[place].isin([country])]

        val1 = flt[var1].sum()
        val2 = flt[var2].sum()

        #st.write(val1.sum())
        #st.write(val2.sum())

        plotdata = pd.DataFrame({'Var': [val1, val2]}, index=[var1, var2])

        st.bar_chart(plotdata)
        # fig = px.bar(plotdata, x="X", y="Y", color="smoker", barmode='group')
        # fig.show()

        # st.set_option('deprecation.showPyplotGlobalUse', False)
        # plotdata.plot(kind="bar", color="green")
        # plt.title("Comparative")
        # plt.savefig('hola.pdf')
        # st.pyplot()

        buffer = io.StringIO()

        #text_contents = '''This is some text'''
        #st.download_button('Download some text', text_contents)

    except Exception as e:

        st.write(e)
        st.warning('Error :(')


# Predicción de casos confirmados por día
def covidCasesPredictionByDay(data: DataFrame):

    field = st.multiselect('Select filter, and order by: ', data.columns)

    flter = field[0]
    order_by = field[1]

    st.write('Filtering by: ', field)

    try:
        ## sort

        ##
        data[order_by] = pd.to_datetime(data[order_by])

        st.write(data)

        data = data.groupby(order_by)[flter].sum()

        #y = data[flter]
        st.write(data)

        generatePredictionGraph(data, 7, 10, 20000)

    except Exception as e:

        st.write(e)
        st.warning('Error :(')


# Tasa de comportamiento de casos activos en relación al número de muertes en un continente
def performoranceRateCasesDeaths(data: DataFrame):

    options = st.multiselect('Select filters: [place, date ,cases, deaths]',
                             data.columns)
    st.write(options)

    place = options[0]
    date_ = options[1]
    cases = options[2]
    deaths = options[3]

    try:

        continent = st.selectbox('Select continent: ',
                                 data[place].drop_duplicates())

        flt = data[data[place].isin([continent])]

        flt[date_] = pd.to_datetime(flt[date_])
        #flt[[date_, cases, deaths]]

        st.line_chart(flt[[cases, deaths]])
        st.caption('Cases / Deaths performance during the pandemic. ')
        st.info(
            'Esta grafica muestra el comportamiento de las muertes y los casos confirmados a lo largo de la pandemia en {}'
            .format(place))

        pass
    except Exception as e:

        st.write(e)
        st.warning('Error :(')

    pass


# Porcentaje de muertes frente al total de casos en un país, región o continente
def percentageDeathsCases(data: DataFrame):

    try:

        options = st.multiselect(
            'Select filter [country, region or continent] and [death, cases]',
            data.columns)

        st.write(options)
        reg = options[0]
        var1 = options[1]
        var2 = options[2]

        place = st.selectbox('Select place: ', data[reg].drop_duplicates())

        data = data[data[reg].isin([place])]

        # total deaths
        t1 = data[var1].sum()
        t2 = data[var2].sum()
        st.subheader('total deaths {}'.format(t1))
        st.subheader('total cases {}'.format(t2))
        perc1 = (t1 / t2) * 100
        perc2 = 100 - perc1
        st.subheader('Percentege {}, {}'.format(perc1.__round__(2),
                                                perc2.__round__(2)))

        df = {'Data': [perc1.__round__(2), perc2.__round__(2)]}
        data[[var1, var2]]

        st.subheader('Deaths percentage vs Positive cases')
        fig = px.pie(df, values='Data', names='Data')
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.write(e)
        st.write('Error :C')


# Tasa de mortalidad por coronavirus (COVID-19) en un país.
def deathsRateByCountry(data: DataFrame):

    option = st.selectbox('Select a field to filter [ex: country]',
                          data.columns)

    country = st.selectbox('Select country: ', data[option].drop_duplicates())

    numeric_vars = st.multiselect(
        'Select numeric varabales to analyze [ex: deaths, positives]: ',
        data.columns)

    if numeric_vars.__len__() == 2:

        deaths = numeric_vars[0]
        positives = numeric_vars[1]

        data = data[data[option].isin([country])]

        flt = data[[deaths, positives]]
        st.write(flt)

        deathrate = []

        for i in range(0, flt.__len__()):
            # death_rate = (n1/n2) * 100
            n1 = flt[deaths][i]  # deaths
            n2 = flt[positives][i]  # positives
            
            if n1 == 0 or n2 == 0:
                deathrate.append(0)
            else:
                # st.write('xd')
                death_rate = (n1 / n2) * 100
                deathrate.append(death_rate)

        xd = pd.DataFrame(deathrate)
        generateTendencyGraph(deathrate, "Death rate by country", 20)
        
        # st.write(deathrate)
        st.line_chart(deathrate)
        #de(xd, 3, 20, 1000)

        #st.write(deathrate)

        pass

    pass


# Predicción de casos de un país para un año.
def casesPredictionOneYear(data: DataFrame):

    select_option = st.selectbox('Select a field to filter [country]: ',
                                 data.columns)

    country = st.selectbox('Select a country: ',
                           data[select_option].drop_duplicates())

    data = data[data[select_option].isin([country])]

    var = st.selectbox('Select a variable to predict', data.columns)

    has_date = st.checkbox('This file has "date" field')

    if has_date:

        date_ = st.selectbox('Order by: ', data.columns)

        data[date_] = pd.to_datetime(data[date_])

        flt = data[[date_, var]]
        st.write(flt)
        flt = data.sort_values(by=date_)

        st.write(flt[[date_, var]])

    else:

        y = data[var]

        days = st.slider('Select number of days to predict: ', 10, 1000)
        grade = st.slider('Select polynomial grade: ', 0, 10)

        st.write(y)
        generatePredictionGraph(y, grade, days, y.max())

        pass

    #generatePredictionGraph(data[var],6, 365, 500000)


# ===================== END METHODS =====================

# Sidebar option tuple
sid_opt_tuple = ('COVID Cases', 'COVID Deaths', 'Vaccines')

#  **** OPTION TUPLES ****
# Covid deaths
covid_deaths_tuple = (
    'Análisis del número de muertes por coronavirus en un País.',
    'Predicción de mortalidad por COVID en un Departamento.',
    'Predicción de mortalidad por COVID en un País',
    'Porcentaje de muertes frente al total de casos en un país, región o continente',
    'Tasa de mortalidad por coronavirus (COVID-19) en un país.')
# Covid Cases
covid_cases_tuple = (
    'Tendencia de la infección por Covid-19 en un País.',
    'Predicción de Infectados en un País.',
    'Ánalisis Comparativo entres 2 o más paises o continentes.',
    'Tendencia del número de infectados por día de un País',
    'Tendencia de casos confirmados de Coronavirus en un departamento de un País',
    'Comparación entre el número de casos detectados y el número de pruebas de un país.',
    'Predicción de casos confirmados por día',
    'Tasa de comportamiento de casos activos en relación al número de muertes en un continente',
    'Predicción de casos de un país para un año.')

# Covid Vaccines
covid_vaccines_tuple = ('Tendencia de la vacunación de en un País.',
                        'Ánalisis Comparativo de Vacunación entre 2 paises.')

# Main
st.sidebar.write("""
    # PROYECTO 2
    *Juan Antonio Solares Samayoa* - 201800496
""")

# add sidebar
# insert image
image = st.sidebar.image(
    'https://peterborough.ac.uk/wp-content/uploads/2020/03/NHS-covid-banner-1.png'
)
app_sidebar = st.sidebar.title("MENU")
st.sidebar.header("Load a file: ")

# file uploader
upload_file = st.sidebar.file_uploader("Choose a .csv, .xls or .json file")

# add selectbox to the sidebar
sidebar_selectbox = st.sidebar.selectbox('Select Type...', sid_opt_tuple)

# read csv file

if upload_file is not None:

    data = pd.read_csv(upload_file)

    # Validate area of analysis
    if sidebar_selectbox == 'COVID Cases':
        st.header('COVID Spread/Cases Reports ')

        select_report = st.selectbox('Select report', covid_cases_tuple)

        st.write(data)
        # Validate option
        if select_report == 'Tendencia de la infección por Covid-19 en un País.':
            covidInfectionTendence(data)

        elif select_report == 'Tendencia de casos confirmados de Coronavirus en un departamento de un País':
            covidCasesByDep(data)

        elif select_report == 'Predicción de Infectados en un País.':
            covidInfectedPredictionByCountry(data)

        elif select_report == 'Tendencia del número de infectados por día de un País':
            #select_date = st.selectbox('Select data to parameterize', data.)
            covidInfectedByDay(data)

        elif select_report == 'Ánalisis Comparativo entres 2 o más paises o continentes.':

            covidComparative(data)

        elif select_report == 'Comparación entre el número de casos detectados y el número de pruebas de un país.':

            covidCasesTestComparation(data)

        elif select_report == 'Predicción de casos confirmados por día':

            covidCasesPredictionByDay(data)

        elif select_report == 'Tasa de comportamiento de casos activos en relación al número de muertes en un continente':

            performoranceRateCasesDeaths(data)

        elif select_report == 'Predicción de casos de un país para un año.':

            casesPredictionOneYear(data)

    elif sidebar_selectbox == 'COVID Deaths':

        st.header("COVID deaths Reports")
        select_report = st.selectbox('Select report', covid_deaths_tuple)

        st.write(data)
        if select_report == 'Análisis del número de muertes por coronavirus en un País.':
            covidDeathsByCountry(data)

        elif select_report == 'Predicción de mortalidad por COVID en un Departamento.':
            covidDeathsPredictionByDeparment(data)

        elif select_report == 'Predicción de mortalidad por COVID en un País':
            covidDeathPredictionByCountry(data)

        elif select_report == 'Porcentaje de muertes frente al total de casos en un país, región o continente':
            percentageDeathsCases(data)

        elif select_report == 'Tasa de mortalidad por coronavirus (COVID-19) en un país.':
            deathsRateByCountry(data)

    elif sidebar_selectbox == 'Vaccines':
        st.header('COVID Vaccines Reports')
        select_report = st.selectbox('Select report', covid_vaccines_tuple)

        st.write(data)
        if select_report == 'Tendencia de la vacunación de en un País.':
            vaccinationTendencyByCountry(data)

        elif select_report == 'Ánalisis Comparativo de Vacunación entre 2 paises.':
            vaccinationComparationByCountries(data)

else:

    st.warning("the file is empty or invalid, please upload a valid file")

# ## Validate sidebar option
