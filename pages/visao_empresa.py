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
    page_title="Visão Empresa",
    page_icon="🏢",
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
st.header('MarketPlace - Visão de Cliente')

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

# Aplicar o filtro com base em 'linhas'
df1 = df1.loc[linhas, :]
clima_conditions=st.sidebar.multiselect(
    'Quais as condições do clima?',
    ['conditions Sunny', 'conditions Cloudy', 'conditions Sandstorms', 'conditions Fog'],
    default=['conditions Sunny', 'conditions Cloudy', 'conditions Sandstorms', 'conditions Fog']
)
df1 = df1.loc[df1['Weatherconditions'].isin(clima_conditions), :]
# Aplicar o filtro com base em 'linhas'
st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Renan Lima')



#==================================
# Layout Streamlit
#==================================
tab1, tab2, tab3, tab4= st.tabs(['Visão Geral','Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])
with tab1:
    st.dataframe(df1)

with tab2:
    with st.container():
        # Order Metric
        st.markdown('# Orders by Day')
        cols = ['ID', 'Order_Date']
        
        # Seleção de linhas
        df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()
        
        # Plotagem
        fig = px.bar(df_aux, x='Order_Date', y='ID')
        
        # Exibição do gráfico
        st.plotly_chart(fig, use_container_width=True)
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.header('Traffic Order Share')
            df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
            df_aux = df_aux.loc[df_aux['Road_traffic_density'] != "Nan", :]
            df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()
            
            fig = px.pie(df_aux, values='entregas_perc', names='Road_traffic_density')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.header('Traffic Order City')
            df_aux = df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
            df_aux = df_aux.loc[df_aux['City'] != "Nan", :]
            df_aux = df_aux.loc[df_aux['Road_traffic_density'] != "Nan", :]
            
            fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
            st.plotly_chart(fig, use_container_width=True)

with tab3:
    with st.container():
        st.markdown('# Order by Week')
    
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%Y-%U')
    df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    fig = px.line(df_aux, x='week_of_year', y='ID')
    
    st.plotly_chart(fig, use_container_width=True)
    
    with st.container():
        st.markdown('# Order Share by Week')
        df_aux01 = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
        df_aux02 = df1.loc[:, [ 'Delivery_person_ID','week_of_year']].groupby(['week_of_year']).nunique().reset_index()
        
        df_aux = pd.merge(df_aux01, df_aux02, how='inner', on ='week_of_year')
        df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
        
        fig = px.line(df_aux, x='week_of_year', y='order_by_delivery')
        st.plotly_chart(fig, use_container_width=True)
        
    

with tab4:
    with st.container():
        st.markdown('# Country Maps')

        # Agrupamento e filtragem de dados
        df_aux = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()
        df_aux = df_aux.loc[df_aux['City'] != "Nan", :]
        df_aux = df_aux.loc[df_aux['Road_traffic_density'] != "Nan", :]
        
        # Criação do mapa
        map = folium.Map()
        
        # Loop para adicionar marcadores ao mapa
        for index, location_info in df_aux.iterrows():
            folium.Marker([location_info['Delivery_location_latitude'],
                           location_info['Delivery_location_longitude']],
                          popup=f"{location_info['City']}, {location_info['Road_traffic_density']}").add_to(map)
        
        # Exibição do mapa fora do loop
        folium_static(map, width=1024, height=600)

