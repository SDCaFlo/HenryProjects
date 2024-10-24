from fastapi import FastAPI
import pandas as pd

app = FastAPI()

#Load data from CSV
movies_df = pd.read_csv("transformed/movies_df.csv", parse_dates=["release_date"])

#Diccionario GLOBAL para consultas mensuales:
MONTH_DICT = {
    "enero" : 1,
    "febrero" : 2,
    "marzo" : 3,
    "abril" : 4,
    "mayo" :5,
    "junio" : 6,
    "julio" : 7,
    "agosto" : 8,
    "septiembre" : 9,
    "setiembre" : 9,
    "octubre" : 10,
    "noviembre" : 11,
    "diciembre" : 12
}


#def cantidad_filmaciones_mes( Mes ): Se ingresa un mes en idioma Español. Debe devolver la cantidad de películas que fueron estrenadas en el mes consultado en la totalidad del dataset.
@app.get("/filmaciones_por_mes/{mes}")
async def cantidad_filmaciones_mes(mes: str):
    mes = MONTH_DICT[mes.lower()]
    #following process can be optimized by filtering title from the start.
    mask = movies_df["release_date"].dt.month==mes
    count = movies_df["title"][mask].drop_duplicates().shape[0]
    return {"Movie month:": mes,
            "N° of movies": count}

#def cantidad_filmaciones_dia( Dia ): Se ingresa un día en idioma Español. Debe devolver la cantidad de películas que fueron estrenadas en día consultado en la totalidad del dataset.
@app.get("/cantidad_filmaciones_dia/{dia}")
async def cantidad_filmaciones_dia(dia: str):
    dia = dia.capitalize()
    check_df = movies_df[["title","release_date"]].drop_duplicates()
    mask = check_df["release_date"].dt.day_name(locale="es_ES")==dia
    count = check_df[mask].shape[0]
    return {"Día": dia,
            "Cantidad de peliculas": count}

#def score_titulo( titulo_de_la_filmación ): Se ingresa el título de una filmación esperando como respuesta el título, el año de estreno y el score.
@app.get("/film/{film_name}")
async def titulo_de_la_filmacion(film_name: str):
    item = movies_df[["title","release_date", "vote_average"]].drop_duplicates().set_index("title").filter(regex="^"+film_name+"$", axis=0)
    title = item.iloc[0].name
    date = str(item.iloc[0].release_date.date())
    score = item.iloc[0].vote_average
    return {
        "Título": title,
        "Fecha de estreno" : date,
        "Puntuación" : score
    }





