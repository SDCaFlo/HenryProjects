from fastapi import FastAPI
import pandas as pd
import numpy as np
import ml_functions


app = FastAPI()

#Load data from CSV
#Tabla movies

movies_df = pd.read_csv("transformed_consultas/movies_df_small.csv", parse_dates=["release_date"], usecols=[
    "id","title", "release_date", "vote_average", "vote_count", "budget", "revenue","return"]).drop_duplicates().reset_index(drop=True)
#tabla actores
actor_df = pd.read_csv("transformed/credits_cast_df.csv", usecols=["id", "cast.character", "cast.name"]).drop_duplicates().dropna(subset=["cast.name"]).reset_index(drop=True)
#tabla directores
director_df = pd.read_csv("transformed/credits_crew_df.csv", usecols=["id", "crew.job", "crew.name"])
director_df = director_df[director_df["crew.job"]=="Director"].reset_index(drop=True)

# dataframes para ML
title_id_df = pd.read_csv("transformed_consultas/id_title_db.csv", index_col="title")
ml_matrix_df = pd.read_csv("transformed_consultas/movies_ml_df_v2_1.csv", index_col="id").head(1000)


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

DAY_DICT = {
    "lunes" : 0,
    "martes" : 1,
    "miercoles" : 2,
    "miércoles" : 2,
    "jueves" : 3,
    "viernes" : 4,
    "sábado" : 5,
    "sabado" : 5,
    "domingo" : 6,
}

#welcome page
@app.get("/")
async def hello_world():
    return "Hello Henry. how r you?"

#def cantidad_filmaciones_mes( Mes ): Se ingresa un mes en idioma Español. Debe devolver la cantidad de películas que fueron estrenadas en el mes consultado en la totalidad del dataset.
@app.get("/filmaciones_por_mes/{mes}")
async def cantidad_filmaciones_mes(mes: str):
    mes_str = mes.lower()
    mes = MONTH_DICT[mes_str]
    mask = movies_df["release_date"].dt.month==mes
    count = movies_df["title"][mask].shape[0]
    return {"Movie month:": mes_str,
            "N° of movies": count}

#def cantidad_filmaciones_dia( Dia ): Se ingresa un día en idioma Español. Debe devolver la cantidad de películas que fueron estrenadas en día consultado en la totalidad del dataset.
# @app.get("/cantidad_filmaciones_dia/{dia}")
# async def cantidad_filmaciones_dia(dia: str):
#     dia = dia.capitalize()
#     check_df = movies_df[["title","release_date"]]
#     mask = check_df["release_date"].dt.day_name(locale="es_ES")==dia
#     count = check_df[mask].shape[0]
#     return {"Día": dia,
#             "Cantidad de peliculas": count}

@app.get("/cantidad_filmaciones_dia/{dia}")
async def cantidad_filmaciones_dia(dia: str):
    dia_str = dia.lower()
    dia = DAY_DICT[dia_str]
    check_df = movies_df[["title","release_date"]]
    mask = check_df["release_date"].dt.weekday==dia
    count = check_df[mask].shape[0]
    return {"Día": dia_str,
            "Cantidad de peliculas": count}

#def score_titulo( titulo_de_la_filmación ): Se ingresa el título de una filmación esperando como respuesta el título, el año de estreno y el score.
@app.get("/film/{film_name}")
async def score_titulo(film_name: str):
    item = movies_df[["title","release_date", "vote_average"]].set_index("title").filter(regex="^"+film_name+"$", axis=0)
    title = item.iloc[0].name
    date = str(item.iloc[0].release_date.date())
    score = item.iloc[0].vote_average
    return {
        "Título": title,
        "Fecha de estreno" : date,
        "Puntuación" : score
    }


#def votos_titulo( titulo_de_la_filmación ): Se ingresa el título de una filmación esperando como respuesta el título, la cantidad de votos y 
# el valor promedio de las votaciones. La misma variable deberá de contar con al menos 2000 valoraciones, caso contrario, debemos contar con un mensaje
#  avisando que no cumple esta condición y que por ende, no se devuelve ningun valor.

@app.get("/votos_titulo/{film_name}")
async def votos_titulo(film_name: str):
    item = movies_df[["title", "vote_average", "vote_count"]].set_index("title").filter(regex="^"+film_name+"$", axis=0).iloc[0]
    title = item.name
    vote_count = item.vote_count
    vote_average = item.vote_average
    
    if vote_count >= 2000:
        return {
            "Título" : title,
            "Cantidad de votos" : vote_count,
            "Promedio de votos" : vote_average
        }
    else:
        return f"La película {title} no posee una cantidad suficiente de votos"

#def get_actor( nombre_actor ): Se ingresa el nombre de un actor que se encuentre dentro de un dataset debiendo devolver el éxito del mismo 
# medido a través del retorno. Además, la cantidad de películas que en las que ha participado y el promedio de retorno. 
# La definición no deberá considerar directores.

@app.get("/get_actor/{actor_name}")
async def get_actor(actor_name: str):
    #lista de id de peliculas donde actua
    movie_id_list_df = actor_df[actor_df["cast.name"]==actor_name]["id"].drop_duplicates()
    #cruce con return de cada pelicula
    merge_df = pd.merge(movies_df[["id", "return"]], movie_id_list_df, how="inner", on="id")
    #cantidad de peliculas
    count = merge_df.shape[0]
    #suma return
    total_return = merge_df["return"].sum()
    #return promedio
    avg_return = total_return / count
    return {
        "Nombre" : actor_name,
        "cantidad de películas" : count,
        "total retorno": total_return,
        "retorno promedio": avg_return
    }

#def get_director( nombre_director ): Se ingresa el nombre de un director que se encuentre dentro de un dataset debiendo devolver el éxito del 
# mismo medido a través del retorno. Además, deberá devolver el nombre de cada película con la fecha de lanzamiento, 
# retorno individual, costo y ganancia de la misma.


@app.get("/get_director/{director_name}")
async def get_director(director_name: str):
    #lista de IDs de peliculas que dirige
    film_record = director_df[director_df["crew.name"]==director_name]["id"].drop_duplicates()
    #data of every film
    film_record_data = pd.merge(movies_df, film_record, how='inner', on="id").filter(["title", "budget", "revenue", "return"], axis=1)
    json_film_record = film_record_data.to_dict('records')

    total_return = film_record_data["return"].sum()
    avg_return = film_record_data["return"].mean()
    count = film_record_data["return"].shape[0]

    return {
        "Nombre" : director_name,
        "cantidad de películas" : count,
        "total retorno": total_return,
        "retorno promedio": avg_return,
        "Lista de peliculas": json_film_record 
    }

# Funcion para hacer recomendaciones
@app.get("/get_recomendation/{film_name}")
async def recomendacion(film_name: str):
    # se verifica que la pelicula se encuentre en la lista.
    try:
        movie_id = int(title_id_df.loc[film_name]["id"])
    except:
        return{"result": "movie not in database"}
    
    # las funciones estan definidas en el archivo ML_functions.py y su logica en el archivo ML_algorithm.ipynb.
    top_5_list = ml_functions.find_top_5(movie_id, ml_matrix_df)
    movie_list = []
    for id in top_5_list:
        movie_list.append(title_id_df.index[title_id_df["id"] == id][0])

    return {"top_1": movie_list[0],
            "top_2": movie_list[1],
            "top_3" : movie_list[2],
            "top_4" : movie_list[3],
            "top_5" : movie_list[4]}