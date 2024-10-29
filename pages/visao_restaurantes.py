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
    page_title="Visão de Restaurantes",
    page_icon="🍽️",
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
st.header('MarketPlace - Visão de Restaurantes')

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
tab1, = st.tabs(['Visão Gerencial'])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        
        
        col1, col2, col3, col4, col5, col6 = st.columns([2.0, 2.2, 2.5, 2.3, 2.3, 3.0])

        with col1:
            delivery_unique = len(df1['Delivery_person_ID'].unique())
            col1.metric('Entregadores', delivery_unique)
            
        with col2:
            cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 
                    'Restaurant_latitude', 'Restaurant_longitude']
            df1['distance'] = df1[cols].apply(
                lambda x: haversine(
                    (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                    (x['Delivery_location_latitude'], x['Delivery_location_longitude'])
                ), axis=1
            )
            distancia_media = np.round(df1['distance'].mean(), 2)
            col2.metric('Distância média', distancia_media)
            
        with col3:
            df_aux = (df1[['Time_taken(min)', 'Festival']]
                      .groupby('Festival')
                      .agg({'Time_taken(min)': ['mean', 'std']}))
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()

            # Média de tempo no festival (Festival = "Yes")
            df_aux_avg = np.round(df_aux.loc[df_aux['Festival'] == 'Yes', 'avg_time'].values[0], 2)
            col3.metric('Tempo de entrega', df_aux_avg)

        with col4:
            # Desvio padrão no festival (Festival = "Yes")
            df_aux_std = np.round(df_aux.loc[df_aux['Festival'] == 'Yes', 'std_time'].values[0], 2)
            col4.metric('STD no Festival', df_aux_std)

        with col5:
            # Média de tempo fora do festival (Festival = "No")
            df_aux_avg_no = np.round(df_aux.loc[df_aux['Festival'] == 'No', 'avg_time'].values[0], 2)
            col5.metric('Média de Tempo', df_aux_avg_no)

        with col6:
            # Desvio padrão fora do festival (Festival = "No")
            df_aux_std_no = np.round(df_aux.loc[df_aux['Festival'] == 'No', 'std_time'].values[0], 2)
            col6.metric('STD fora do Festival', df_aux_std_no)

    with st.container():
        st.markdown("""---""")
        col1, col2 = st.columns(2)

        with col1:
            st.title('Tempo médio de entrega por cidade')
        
            df_aux = (df1[['City', 'Time_taken(min)']]
                      .groupby('City')
                      .agg({'Time_taken(min)': ['mean', 'std']}))
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()

            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='Control',
                x=df_aux['City'],
                y=df_aux['avg_time'],
                error_y=dict(type='data', array=df_aux['std_time'])
            ))
            fig.update_layout(barmode='group')
            st.plotly_chart(fig)
        
        with col2:
            st.title('Distribuição da Distância')
            df_aux = df1[['City', 'Time_taken(min)', 'Type_of_order']].groupby(['City', 'Type_of_order']).agg(
                {'Time_taken(min)': ['mean', 'std']}
            )
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            st.dataframe(df_aux)
        
    with st.container():
        st.markdown("""---""")
        st.title('Distribuição do Tempo')
        col1, col2 = st.columns(2)

        with col1:
            # Distância média das entregas por cidade
            distancia_media = df1[['City', 'distance']].groupby('City').mean().reset_index()
            fig = go.Figure(data=[go.Pie(labels=distancia_media['City'], values=distancia_media['distance'], pull=[0, 0.1, 0])])
            st.plotly_chart(fig)
        
        with col2:
            # Tempo médio de entrega por cidade e densidade de tráfego
            cols = ['City', 'Time_taken(min)', 'Road_traffic_density']
            df_aux = (df1[cols]
                      .groupby(['City', 'Road_traffic_density'])
                      .agg({'Time_taken(min)': ['mean', 'std']}))
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()

            fig = px.sunburst(
                df_aux, 
                path=['City', 'Road_traffic_density'], 
                values='avg_time',
                color='std_time', 
                color_continuous_scale='RdBu',
                color_continuous_midpoint=np.average(df_aux['std_time'])
            )
            st.plotly_chart(fig)
