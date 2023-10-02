import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
import numpy as np
from fastapi import FastAPI
app = FastAPI()


df1 = pd.read_csv('df1.csv')
df2 = pd.read_csv('df2.csv')
df3 = pd.read_csv('df3.csv')
df4 = pd.read_csv('df4.csv')
df5 = pd.read_csv('df5.csv')







# Tu código para cargar datos y definir la función get_recommendations aquí





categories = df5[['adventure',
 'software training',
 'photo editing',
 'indie',
 'education',
 'action',
 'animation &amp; modeling',
 'early access',
 'free to play',
 'audio production',
 'massively multiplayer',
 'design &amp; illustration',
 'utilities',
 'sports',
 'racing',
 'rpg',
 'accounting',
 'simulation',
 'casual',
 'strategy',
 'video production']]

def get_recommendations(game_name):
    game_index = df5[df5['game'] == game_name].index
    if len(game_index) == 0:
        return []

    game_index = game_index[0]
    game_similarity = cosine_similarity(categories.iloc[[game_index]], categories)[0]
    game_indices = np.argsort(game_similarity)[::-1][:5]  # Siempre 5 recomendaciones
    recommendations = [df5.loc[index, 'game'] for index in game_indices]

    return recommendations

# Ruta para obtener recomendaciones
@app.get("/recomendacion_juego/{nombre_producto}")
async def recomendacion_juego(nombre_producto: str):
    recommendations = get_recommendations(nombre_producto)
    return {"Recomendaciones": recommendations}



def PlayTimeGenre(df, genero):
    # Convertir el género ingresado a minúsculas
    genero = genero.lower()

    # Filtrar el DataFrame para el género especificado
    df_genero = df[df[genero] == 1]

    # Agrupar por año y calcular las horas totales jugadas
    df_grouped = df_genero.groupby(df_genero['release_date'].dt.year)['playtime_forever'].sum()

    # Encontrar el año con más horas jugadas
    año_mas_horas = df_grouped.idxmax()

    # Crear el resultado como un diccionario
    resultado = {f"Año de lanzamiento con más horas jugadas para {genero}": año_mas_horas}

    return resultado

# Ejemplo de uso:
@app.get("/anio_mas_horas/{genero}")
async def anio_mas_horas(genero: str):
    resultado = PlayTimeGenre(df1, genero)
    return resultado




def UserForGenre(df, genero):
    # Convertir el género ingresado a minúsculas
    genero = genero.lower()

    # Filtrar el DataFrame para el género especificado
    df_genero = df[df[genero] == 1]

    if df_genero.empty:
        return {}  # No se encontraron datos para el género dado

    # Encontrar el usuario con más horas jugadas para el género
    usuario_mas_horas = df_genero.groupby('user_id')['playtime_forever'].sum().idxmax()

    # Filtrar el DataFrame para el usuario con más horas jugadas
    df_usuario_mas_horas = df_genero[df_genero['user_id'] == usuario_mas_horas]

    # Agrupar por año y calcular las horas totales jugadas por año
    df_year_grouped = df_usuario_mas_horas.groupby(df_usuario_mas_horas['release_date'].dt.year)['playtime_forever'].sum().reset_index()

    # Crear el resultado como un diccionario en el formato deseado
    resultado = {
        f"Usuario con más horas jugadas para Género {genero}": usuario_mas_horas,
        "Horas jugadas": df_year_grouped.rename(columns={'release_date': 'Año', 'playtime_forever': 'Horas'}).to_dict(orient='records')
    }

    return resultado

# Ejemplo de uso:
@app.get("/usuario_mas_horas/{genero}")
async def usuario_mas_horas(genero: str):
    resultado = UserForGenre(df2, genero)
    return resultado


def UsersRecommend(año: int):
    # Filtra las revisiones para el año dado y comentarios positivos/neutrales, luego ordena por puntaje
    top_3_juegos = df3[(df3['release_date'].dt.year == año) & (df3['puntaje'] >= 0)]\
        .sort_values(by='puntaje', ascending=False).head(3)

    # Crea una lista de diccionarios en el formato deseado
    resultados = [{"Puesto {}: {}".format(i+1, juego['game']): juego['puntaje']} for i, (_, juego) in enumerate(top_3_juegos.iterrows())]

    return resultados

@app.get("/mejores_recomendaciones/{año}")
async def mejores_recomendaciones(año: int):
    resultado = UsersRecommend(año)
    return resultado

def UsersNotRecommend(año: int):
    # Filtra las revisiones para el año dado, comentarios negativos y no recomendados, luego ordena por puntaje
    top_3_juegos = df3[(df3['release_date'].dt.year == año) & (df3['puntaje'] < 0)]\
        .sort_values(by='puntaje', ascending=True).head(3)

    # Crea una lista de diccionarios en el formato deseado
    resultados = [{"Puesto {}: {}".format(i+1, juego['game']): juego['puntaje']} for i, (_, juego) in enumerate(top_3_juegos.iterrows())]

    return resultados

# Ejemplo de uso:
@app.get("/peores_recomendaciones/{año}")
async def peores_recomendaciones(año: int):
    resultado = UsersNotRecommend(año)
    return resultado 

def sentiment_analysis(año: int):
    # Filtra las reseñas para el año dado
    reseñas_por_año = df4[df4['release_date'].dt.year == año]

    # Calcula la cantidad de registros para cada categoría de sentimiento
    cantidad_negativos = (reseñas_por_año['sentiment_neg'] == 1).sum()
    cantidad_neutrales = (reseñas_por_año['sentiment_neu'] == 1).sum()
    cantidad_positivos = (reseñas_por_año['sentiment_pos'] == 1).sum()

    # Crea un diccionario con los resultados
    resultados = {
        'Negative': cantidad_negativos,
        'Neutral': cantidad_neutrales,
        'Positive': cantidad_positivos
    }

    return resultados

# Ejemplo de uso:
@app.get("/analisis_sentimiento/{año}")
async def analisis_sentimiento(año: int):
    resultado = sentiment_analysis(año)
    return resultado


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)