import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import math


def calc_overview_score(movie_1: int, movie_2: int, dataframe: pd.DataFrame):
    """Calcula el score de overview entre dos peliculas, movie_1 y movie_2
    con el algoritmo de cosine similarity. Los parámetros de entrada son los IDs."""
    movie_1_data = dataframe.loc[movie_1]
    movie_2_data = dataframe.loc[movie_2]

    pca_columns = [f"Overview_pca_{x}" for x in range(1,11)]

    movie_1_pca = movie_1_data[pca_columns].values.reshape(1,-1)
    movie_2_pca = movie_2_data[pca_columns].values.reshape(1,-1)

    overview_similarity = cosine_similarity(movie_1_pca, movie_2_pca)[0][0]

    return overview_similarity + 1
     
def genre_score(movie_1: int, movie_2: int, dataframe: pd.DataFrame):
    "Calcula la semejanza entre los generos de 2 peliculas en base a la similaridad de coseno"
    movie_1_genres = list(eval(dataframe.loc[movie_1]["genres"]))
    movie_2_genres = list(eval(dataframe.loc[movie_2]["genres"]))

    unique_genres = list(set(movie_1_genres + movie_2_genres))

    vectors_movie_1 = [1 if genre in movie_1_genres else 0 for genre in unique_genres]
    vectors_movie_2 = [1 if genre in movie_2_genres else 0 for genre in unique_genres]

    vector_1 = np.array(vectors_movie_1).reshape(1, -1)
    vector_2 = np.array(vectors_movie_2).reshape(1, -1)

    similarity = cosine_similarity(vector_1, vector_2)[0][0]

    return similarity + 1

def year_score(movie_1: int, movie_2: int, dataframe: pd.DataFrame):
    year_diff = abs(dataframe.loc[movie_1]["release_year"]-dataframe.loc[movie_2]["release_year"])
    score = math.exp(-1*(year_diff/10))
    return score


def vote_score(movie_1: int, movie_2: int, dataframe: pd.DataFrame):
    year_diff = abs(dataframe.loc[movie_1]["vote_info"]-dataframe.loc[movie_2]["vote_info"])
    score = math.exp(-1*(year_diff/20))
    return score

def title_score(movie_1: int, movie_2: int, dataframe: pd.DataFrame):
    "Calcula la semejanza entre los generos de 2 peliculas en base a la similaridad de coseno"
    movie_1_genres = list(eval(dataframe.loc[movie_1]["title_collection"]))
    movie_2_genres = list(eval(dataframe.loc[movie_2]["title_collection"]))

    unique_genres = list(set(movie_1_genres + movie_2_genres))

    vectors_movie_1 = [1 if genre in movie_1_genres else 0 for genre in unique_genres]
    vectors_movie_2 = [1 if genre in movie_2_genres else 0 for genre in unique_genres]

    vector_1 = np.array(vectors_movie_1).reshape(1, -1)
    vector_2 = np.array(vectors_movie_2).reshape(1, -1)

    similarity = cosine_similarity(vector_1, vector_2)[0][0]

    return similarity + 1

def popularity_score(movie_1:int, movie_2: int, dataframe: pd.DataFrame):
    score_diff = abs(dataframe.loc[movie_1]["popularity_log"]-dataframe.loc[movie_2]["popularity_log"])
    score = math.exp(-1*(score_diff/3))
    return score


def language_score(movie_1: int, movie_2: int, dataframe: pd.DataFrame):
    movie_1_language = list(eval(dataframe.loc[movie_1]["concat_country_language"]))
    movie_2_language = list(eval(dataframe.loc[movie_2]["concat_country_language"]))

    unique_languages = list(set(movie_1_language + movie_2_language))

    vectors_movie_1 = [1 if genre in movie_1_language else 0 for genre in unique_languages]
    vectors_movie_2 = [1 if genre in movie_2_language else 0 for genre in unique_languages]

    vector_1 = np.array(vectors_movie_1).reshape(1, -1)
    vector_2 = np.array(vectors_movie_2).reshape(1, -1)

    similarity = cosine_similarity(vector_1, vector_2)[0][0]

    return similarity + 1

def production_scores(movie_1: int, movie_2: int, dataframe: pd.DataFrame):
    movie_1_production = list(eval(dataframe.loc[movie_1]["production_companies"]))
    movie_2_production = list(eval(dataframe.loc[movie_2]["production_companies"]))

    unique_languages = list(set(movie_1_production + movie_2_production))

    vectors_movie_1 = [1 if genre in movie_1_production else 0 for genre in unique_languages]
    vectors_movie_2 = [1 if genre in movie_2_production else 0 for genre in unique_languages]

    vector_1 = np.array(vectors_movie_1).reshape(1, -1)
    vector_2 = np.array(vectors_movie_2).reshape(1, -1)

    similarity = cosine_similarity(vector_1, vector_2)[0][0]

    return similarity + 1

def similarity_score(movie_1:int, movie_2:int, dataframe: pd.DataFrame):
    overview = calc_overview_score(movie_1, movie_2, dataframe)
    genre = genre_score(movie_1,movie_2, dataframe)
    year = year_score(movie_1, movie_2, dataframe)
    vote_average = vote_score(movie_1, movie_2, dataframe)
    title = title_score(movie_1, movie_2, dataframe)
    popularity = popularity_score(movie_1, movie_2, dataframe)
    language = language_score(movie_1, movie_2, dataframe)
    production = production_scores(movie_1, movie_2, dataframe)
    
    return overview*genre*year*vote_average*title*popularity*language*production



def find_top_5(movie_1: int, dataframe: pd.DataFrame):
    index = dataframe.index
    score_list = [similarity_score(movie_1, i, dataframe) for i in index]
    top_5 = pd.DataFrame(score_list, index=index, columns=["score"]).sort_values(by="score", ascending=False).head(6)
    return list(top_5.index)[1:]