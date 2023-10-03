import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
import numpy as np
from fastapi import FastAPI
app = FastAPI()



df2 = pd.read_csv('df2.csv')

df5 = pd.read_csv('df5.csv')







# Tu código para cargar datos y definir la función get_recommendations aquí


generos = ['adventure', 'software training', 'photo editing', 'indie', 'education', 'action', 'animation &amp; modeling', 'early access', 'free to play', 'audio production', 'massively multiplayer', 'design &amp; illustration', 'utilities', 'sports', 'racing', 'rpg', 'accounting', 'simulation', 'casual', 'strategy', 'video production']
annios= ['2008','2014','2016','2010','2013','2006','2013','2016','2006','2014','2005','2015','2015','2015','2016','2008','0','2008','2009','2017','2014']


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


@app.get("/playtime/{genero}")
def PlayTimeGenre(genero: str):
    if genero not in generos:
        return {"message": f"No se encontraron registros para el género {genero}"}
    
    # Filtrar la lista para obtener los años correspondientes al género dado
    anos_filtrados = [ano for i, ano in enumerate(annios) if generos[i] == genero]
    
    if not anos_filtrados:
        return {"message": f"No se encontraron registros para el género {genero}"}
    
    # Encontrar el año con más horas jugadas para ese género
    ano_mas_horas = max(anos_filtrados, key=anos_filtrados.count)
    
    return {"Año de lanzamiento con más horas jugadas para Género": genero, "Año": int(ano_mas_horas)}




def UserForGenre(df, genero):
    genero = genero.lower()
    df_genero = df[df['genero'].str.lower() == genero]

    if df_genero.empty:
        return {"error": f"No data found for genre {genero}"}

    usuario_mas_horas = df_genero.groupby('user_id')['playtime_forever'].sum().idxmax()
    df_usuario_mas_horas = df_genero[df_genero['user_id'] == usuario_mas_horas]

    df_year_grouped = df_usuario_mas_horas.groupby(df_usuario_mas_horas['release_date'].dt.year)['playtime_forever'].sum().reset_index()

    resultado = {
        f"Usuario con más horas jugadas para Género {genero}": usuario_mas_horas,
        "Horas jugadas": df_year_grouped.rename(columns={'release_date': 'Año', 'playtime_forever': 'Horas'}).to_dict(orient='records')
    }

    return resultado

@app.get("/usuario_mas_horas/{genero}")
async def usuario_mas_horas(genero: str):
    try:
        resultado = UserForGenre(df2, genero)
        return resultado
    except Exception as e:
        print("Error:", str(e))
        return {"error": "Internal Server Error"}





if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
