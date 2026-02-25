import requests
import pandas as pd
from transformers import pipeline
import time

"POR BOLSA DE VALORES: url = f'https://api.marketaux.com/v1/news/all?exchanges=NYSE,NASDAQ&filter_entities=true&limit=3&api_token={API_TOKEN}'"

"POR SECTOR/INDUSTRIA]: url = f'https://api.marketaux.com/v1/news/all?industries=Technology,Financial&filter_entities=true&limit=3&api_token={API_TOKEN}'"

"POR TICKER: url = f'https://api.marketaux.com/v1/news/all?symbols=AAPL,MSFT&filter_entities=true&limit=3&api_token={API_TOKEN}'"


# 1. Cargar el motor de inteligencia artificial FinBERT
print("Cargando el motor de inteligencia artificial FinBERT...")
sentiment_analyzer = pipeline("sentiment-analysis", model="ProsusAI/finbert")

API_TOKEN = 'b5ZqDYDztLAnBcfhqJ6jmWiHSwaLN3GIgdTURIRJ' 
datos_exportar = []

print("Conectando con Marketaux y procesando múltiples páginas...\n")
print("=" * 60)

# El plan gratuito entrega 3 noticias por página. 
# Consultaremos 5 páginas automáticas para obtener 15 noticias en total.
# Puedes aumentar este número para obtener más resultados (ej. 10 páginas = 30 noticias)
paginas_a_consultar = 5 

for pagina in range(1, paginas_a_consultar + 1):
    print(f"Consultando página {pagina}...")
    
    # Agregamos el parámetro &page={pagina} a la URL para avanzar en los resultados
    url = f'https://api.marketaux.com/v1/news/all?industries=Technology&filter_entities=true&page={pagina}&api_token={API_TOKEN}'
    
    response = requests.get(url)
    
    if response.status_code == 200:
        news_data = response.json()
        
        for article in news_data.get('data', []):
            title = article['title']
            source = article['source']
            print(f"📰 Procesando: {title[:50]}...")
            
            
          # 3. Extraer el Score de Marketaux
            entities = article.get('entities', [])
            if entities:
                symbol = entities[0].get('symbol', 'N/A')
                marketaux_raw = entities[0].get('sentiment_score')
                
                # Nueva validación: Solo multiplicamos si el valor NO es nulo
                if marketaux_raw is not None:
                    marketaux_score = round(marketaux_raw * 100, 2)
                else:
                    marketaux_score = None
            else:
                symbol = 'N/A'
                marketaux_score = None

            # Calcular el Score con FinBERT
            finbert_result = sentiment_analyzer(title)[0]
            label = finbert_result['label']
            probability = finbert_result['score']
            
            if label == 'positive':
                finbert_score = round(probability * 100, 2)
            elif label == 'negative':
                finbert_score = round(probability * -100, 2)
            else:
                finbert_score = 0
                
            # Calcular la Diferencia
            diferencia = None
            if marketaux_score is not None:
                diferencia = round(abs(marketaux_score - finbert_score), 2)
                
            # Guardar los resultados
            datos_exportar.append({
                "Titular": title,
                "Fuente": source,
                "Empresa (Ticker)": symbol,
                "Score Marketaux": marketaux_score,
                "Score FinBERT": finbert_score,
                "Etiqueta FinBERT": label.upper(),
                "Diferencia": diferencia
            })
    else:
        print(f"Error en la página {pagina}. Código: {response.status_code}")
        break # Detiene el ciclo si se presenta una eventualidad con la conexión
        
    # Pausa de 1 segundo para mantener un flujo estable con la API
    time.sleep(1)

# 2. Crear el archivo Excel final
if datos_exportar:
    df = pd.DataFrame(datos_exportar)
    nombre_archivo = 'Resultados_Sensibilidad_Ampliado.xlsx'
    
    df.to_excel(nombre_archivo, index=False)
    print("=" * 60)
    print(f"✅ ¡Éxito! Se guardaron {len(datos_exportar)} noticias en el archivo: {nombre_archivo}")
    print("=" * 60)
else:
    print("No se encontraron datos para exportar.")