
# Proyecto2 OLC2 VACDIC2021

## Datos del estudiante

JUAN ANTONIO SOLARES SAMAYOA
<br>
CARNET 201800496

![banner](img/home-banner.jpg)

# MANUAL TÉCNICO



:green_book:[Descripción del problema](#tag1)

:green_book:[Solucion](#tag2)

:green_book:[Flujo de la aplicación](#tag3)

:green_book:[Generar predicciones en Python](#tag4)

:green_book:[Generar tendencias en Python](#tag5)

## :beginner: Descripción del problema<a name="tag1"></a>
La pandemia del COVID-19 sin duda alguna ha causado un cambio significativo en la vida de todas las personas **alrededor** del mundo debido a los cambios drásticos que vinieron junto a está pandemia.

Debido a esto, desde el año 2020, han ocurrido muchos sucesos relacionados a la pandemia que han afectado l

A lo largo del tiempo, gracias a los avances tecnologicos se ha podido recabar una gran cantidad de datos y estadisticas  los cuales son muy necesarios para poder tomar decisiones para poder contener el avance de la pandemia y poder responder de la mejor forma para evitar muchos contagios.


## :beginner: Solucion<a name="tag2"></a>
La solución propuesta es realizar una aplicacíón web en la cual se puedan analizar datos estadisticos de la pandemia a lo largo del tiempo, utilizando Ciencia de Datos. La Ciancia de Datos es una campo interdisciplinario que incolucra metodos cientificos, procesos y sistemas para poder extraer datos y conocimientos para poder tomar decisiones.

![1](./img/holaaaa.jpg)

## Breve descripción de la aplicación
La aplicación consiste en un analizador de archivos .CSV, JSON y XLS los cuales contienen datos recopilados de distintas fuetes, y la aplicación tiene la capacidad (por medio de SciKit learn) de generar graficas de tendencia así como generar predicciones y gráficas de tendencia. 


## Conceptos importantes a tener en cuenta 

### REGRESIÓN LINEAL: 
La regresión lineal es una técnica de modelado estadístico que se emplea para describir una variable de respuesta continua como una función de una o varias variables predictoras. Puede ayudar a comprender y predecir el comportamiento de sistemas complejos o a analizar datos experimentales, financieros y biológicos.

![1](./img/regr.png)

## :beginner: Flujo de la aplicación<a name="tag3"></a>
El flujo de funcionamiento de la aplicación es el siguiente: 

1. Se carga el archivo de entrada en cualquier formato.

![1](./img/flujo1.png)

2. Se muestran los datos del archivo cargados en la interfaz

![1](./img/grafica2.png)

3. Se parametrizan los campos de del dataframe, para que posteriormente pueda realizar el analisis de los datos obtenidos, como predicciones y graficos de tendencia

![1](./img/parametrizacion.png)


4. Luego de haber preparado y filtrado las columnas del datraframe se procede a generar la grafica de acuerdo a los campos y condiciones dadas.

![1](./img/flujo4.png)

5. La aplicación cuenta con una opción para generar la predicción y grafico de tendencia, en formato PDF.

![1](./img/download.png)


6. Una vez descargado el reporte PDF, se procede a visualizarlo en el navegador
   
![1](./img/reporte.png).


## Importar las librerias usadas
```python
import base64
import datetime as dt
import io
import time
from math import e

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas.core.indexes.timedeltas import timedelta_range
import plotly
import plotly.express as px
import plotly.figure_factory as ff
import seaborn as sns
import streamlit as st
from attr import field
from fpdf import FPDF
from matplotlib import colors
from pandas._config.config import options
from pandas.core import groupby
from pandas.core.algorithms import mode
from pandas.core.frame import DataFrame
from pandas.core.reshape.pivot import pivot_table
from PIL import Image
from sklearn import linear_model
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import PolynomialFeatures
from streamlit.elements.arrow import Data
```

## Generar predicciones en Python
## :beginner: Generar predicciones en Python<a name="tag4"></a>
```python

def generatePredictionGraph(y: DataFrame, grade, days, max_val):

    X = []
    Y = y
    print(y)

    size = y.__len__()
    for i in range(0, size):
        X.append(i)

    X = np.asarray(X)
    Y = np.asarray(Y)

    X = X[:, np.newaxis]
    Y = Y[:, np.newaxis]

    #  2:
    nb_degree = grade

    polynomial_features = PolynomialFeatures(degree=nb_degree)
    X_TRANSF = polynomial_features.fit_transform(X)

    # ## print(Y)
    #  3:
    model = LinearRegression()
    model.fit(X_TRANSF, Y)

    #  4
    Y_NEW = model.predict(X_TRANSF)

    rmse = np.sqrt(mean_squared_error(Y, Y_NEW))
    r2 = r2_score(Y, Y_NEW)

    print('RMSE: ', rmse)
    print('R2: ', r2)

    #  5:
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
    title = 'Degree={}; RMSE={}; R2={}'.format(nb_degree, round(rmse, 2),
                                               round(r2, 2))
    plt.title(title)
    plt.xlabel('x')
    plt.ylabel('y')

    plt.savefig('D:\\prediction.png')
    #plt.savefig('pol_reg.jpg', )
    plt.show()
    st.pyplot()
    st.caption('Prediction graph')
    st.write("La predicción será de ", Y_NEW[int(Y_NEW.size - 1)][0])

    #
    #fig = ff.create_distplot(Y_NEW, ['test'], bin_size=[0] )

```

## Generar tendencias en Python
## :beginner: Generar tendencias en Python<a name="tag5"></a>
```python


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
    plt.savefig('D:\\trend.jpg')
    #print(reg.predict([[10]]))
    max_val = maxY

    # Header
    st.subheader(header)
    plt.title(header)
    plt.ylim(-10, max_val + 10)
    plt.show()
    st.pyplot()
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.caption('COVID-19 tendence graph')
```

# Metodos utilizados para realizar los reportes

| Metodo | Metodo Python |
| --- | ----------- |
| 1. Tendencia de la infección por Covid-19 en un País | def covidInfectionTendence(data: DataFrame) |
| 2.  Predicción de Infectados en un País. | def covidInfectedPredictionByCountry(data: DataFrame) |
| 3. Indice de Progresión de la pandemia. | def pandemicProgression(data: DataFrame) |
| 4. Predicción de mortalidad por COVID en un Departamento. | def covidDeathsPredictionByDeparment(data: DataFrame) |
| 5. Predicción de mortalidad por COVID en un País | def covidDeathPredictionByCountry(data: DataFrame) |
| 6. Análisis del número de muertes por coronavirus en un País. | def covidDeathsByCountry(data: DataFrame) |
| 7. Tendencia del número de infectados por día de un País | def covidInfectedByDay(data: DataFrame) |
| 8. Predicción de casos de un país para un año. | def casesPredictionOneYear(data: DataFrame) |
| 9. Tendencia de la vacunación de en un País. | Title |
| 10. Ánalisis Comparativo de Vacunación entre 2 paises | def vaccinationTendencyByCountry(data: DataFrame) |
| 11. Porcentaje de hombres infectados por covid-19 en un País desde el primer caso activo | def menPercentageInfected(data: DataFrame) |
| 12. Ánalisis Comparativo entres 2 o más paises o continentes. | def covidComparative(data: DataFrame) |
| 13. Muertes promedio por casos confirmados y edad de covid 19 en un País. | Title |
| 14. Muertes según regiones de un país - Covid 19. | def deathsByCountryRegions(data: DataFrame): |
| 15. Tendencia de casos confirmados de Coronavirus en un departamento de un País | def covidCasesByDep(data: DataFrame) |
| 16. Porcentaje de muertes frente al total de casos en un país, región o continente | def percentageDeathsCases(data: DataFrame) |
| 17. Tasa de comportamiento de casos activos en relación al número de muertes en un continente| def performoranceRateCasesDeaths(data: DataFrame) |
| 18. Comportamiento y clasificación de personas infectadas por COVID-19 por municipio en un País. | def classificationInfectedPeopleByState(data: DataFrame) |
| # 19. Predicción de muertes en el último día del primer año de infecciones en un país | def deathsPredictionOnFirstYear(data: DataFrame) |
| 20. Tasa de crecimiento de casos de COVID-19 en relación con nuevos casos diarios y tasa de muerte por COVID-19  | def growthRateCasesAndDeathRate(data: DataFrame) |
| 21. Predicciones de casos y muertes en todo el mundo | def deathGlobalPrediction(data: DataFrame) |
| 22. Tasa de mortalidad por coronavirus (COVID-19) en un país. | def deathsRateByCountry(data: DataFrame) |
| 23. Factores de muerte por COVID-19 en un país. | def covidCasesTestComparation(data: DataFrame) |
| 24. Comparación entre el número de casos detectados y el número de pruebas de un país. | Text |
| 25. Predicción de casos confirmados por día | covidCasesPredictionByDay(data: DataFrame) | 



