import pandas as pd
import numpy as np
import streamlit as st
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config(
    page_title="Visão de Entregadores",
    page_icon="🚚",
    layout="wide"
)

# Importando o dataset
df = pd.read_csv('C:/Users/renan/OneDrive/DS/python/dataset/train.csv')

df1 = df.copy()

# Remover espaços em branco antes e depois dos valores nas colunas importantes
df1['Delivery_person_Age'] = df1['Delivery_person_Age'].str.strip()
df1['Road_traffic_density'] = df1['Road_traffic_density'].str.strip()
df1['City'] = df1['City'].str.strip()
df1['Festival'] = df1['Festival'].str.strip()

# Substituir strings vazias e valores inválidos por NaN
df1.replace(['', ' ', 'NaN'], np.nan, inplace=True)

# Remover valores NaN das colunas especificadas
df1.dropna(subset=['Delivery_person_Age', 'Road_traffic_density', 'City', 'Festival'], inplace=True)

# Convertendo 'Delivery_person_Ratings' para numérico, substituindo valores inválidos por NaN
df1['Delivery_person_Ratings'] = pd.to_numeric(df1['Delivery_person_Ratings'], errors='coerce')

# Converter 'Delivery_person_Age' para numérico e remover quaisquer valores não numéricos resultantes
df1['Delivery_person_Age'] = pd.to_numeric(df1['Delivery_person_Age'], errors='coerce')
df1.dropna(subset=['Delivery_person_Age'], inplace=True)

# Redefinir os índices para organizar o DataFrame após a limpeza
df1.reset_index(drop=True, inplace=True)

# Convertendo múltiplas entregas para número
df1['multiple_deliveries'] = pd.to_numeric(df1['multiple_deliveries'], errors='coerce')
df1 = df1[df1['multiple_deliveries'].notna()].copy()

# Ajustando Time_taken(min) para extrair o número
df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(str)  # Garantindo que todos sejam strings
df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.replace('(min)', '').strip() if '(min)' in x else x)

# Convertendo para numérico, tratando erros
df1['Time_taken(min)'] = pd.to_numeric(df1['Time_taken(min)'], errors='coerce')

# Removendo linhas com NaN após a conversão
df1 = df1[df1['Time_taken(min)'].notna()].copy()

# Convertendo para int
df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

# Converter a coluna Order_Date para datetime
df1['Order_Date'] = pd.to_datetime(df1['Order_Date'])

# Colunas para agrupar
cols = ['ID', 'Order_Date']

# Seleção de linhas e contagem por data
df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()

#==================================
# Barra Lateral Streamlit
#==================================
st.header('MarketPlace - Visão de Entregadores')

image_path = r'C:\Users\renan\OneDrive\DS\python\images\logofenix.jpg'
image = Image.open(image_path)
st.sidebar.image(image, width=120)
st.sidebar.markdown('### Phoenix Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime(2022, 4, 13),
    min_value=datetime(2022, 2, 11),
    max_value=datetime(2022, 4, 6),
    format='DD-MM-YYYY'
)



traffic_options=st.sidebar.multiselect(
    'Quais as condições do trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam']
)

st.sidebar.markdown("""---""")


# Filtrando o DataFrame 'df1' com base no valor do 'date_slider'
df1 = df1.loc[df1['Order_Date'] <= date_slider, :]


# Filtrar por condições de trânsito selecionadas no multiselect
linhas = df1['Road_traffic_density'].isin(traffic_options)
# Filtrar por condição de clima
clima_conditions=st.sidebar.multiselect(
    'Quais as condições do clima?',
    ['conditions Sunny', 'conditions Cloudy', 'conditions Sandstorms', 'conditions Fog'],
    default=['conditions Sunny', 'conditions Cloudy', 'conditions Sandstorms', 'conditions Fog']
)
df1 = df1.loc[df1['Weatherconditions'].isin(clima_conditions), :]
# Aplicar o filtro com base em 'linhas'
df1 = df1.loc[linhas, :]
st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Renan Lima')

#==================================
# Layout Streamlit
#==================================
tab1,= st.tabs(['Visão Gerencial'])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        
        col1, col2, col3, col4 = st.columns(4, gap='large')
        
        with col1:
            
            # A Maior idade dos entregadores
            maior_idade = (df1.loc[:, 'Delivery_person_Age'].max())
            col1.metric( 'Maiorde de idade',maior_idade)
        with col2:
            
            # A Menor idade dos entregadores
            menor_idade = (df1.loc[:, 'Delivery_person_Age'].min())
            col2.metric( 'Menor de de idade',menor_idade)
            
            
        with col3:
            
            # A melhor condição de veículo dos entregadores
            melhor_condicao = (df1.loc[:, 'Vehicle_condition'].max())
            col3.metric( 'Melhor condições',melhor_condicao)
            
            
        with col4:
            
            # Veiculos em más condições
            pior_condicao = (df1.loc[:, 'Vehicle_condition'].min())
            col4.metric(' Pior condição', pior_condicao)
            
with st.container():
    st.markdown("""---""")
    st.title('Avaliações')
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('##### Avalição Média por Entregador')
        # Avaliação média por entregador
        media_entregador = (df1.loc[:, ['Delivery_person_Ratings','Delivery_person_ID']]
                            .groupby('Delivery_person_ID')
                            .mean()
                            .reset_index())
        st.dataframe(media_entregador)
    
    with col2:
        st.markdown('##### Avaliação por trânsito')
        # Avaliação por transito
        media_transito = (df1.loc[:, ['Delivery_person_Ratings','Road_traffic_density']]
                          .groupby('Road_traffic_density')
                          .agg({'Delivery_person_Ratings': ['mean', 'std']}))
        
        media_transito.columns = ['delivery_mean', 'delivery_std']
        media_transito = media_transito.reset_index()
        st.dataframe(media_transito)
        
        
        st.markdown('##### Avaliação por clima')
        # Avaliação por clima
        media_clima = (df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                       .groupby('Weatherconditions')
                       .agg({'Delivery_person_Ratings': ['mean', 'std']}))
        
        media_clima.columns = ['delivery_mean', 'delivery_std']
        media_clima = media_clima.reset_index()
        st.dataframe(media_clima)
        
with st.container():
    st.markdown("""---""")
    st.title('Velocidade de Entrega')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('##### Top Entregadores mais rápidos')
        df2= (df1.loc[:, ['Delivery_person_ID', 'City','Time_taken(min)']].groupby(['City','Delivery_person_ID']
                    ).mean().sort_values(['City','Time_taken(min)'],ascending=True).reset_index())
        df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
        df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
        df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
        df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
        st.dataframe(df3)
        
        
    with col2:
        st.markdown('##### Top Entregadores mais lentos')
        df2 = (df1.loc[:, ['Delivery_person_ID', 'City','Time_taken(min)']].groupby(['City','Delivery_person_ID']
                    ).mean().sort_values(['City','Time_taken(min)'],ascending=False).reset_index())
        df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
        df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
        df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
        df4 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
        st.dataframe(df4)