import streamlit  as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon="🏠",
    layout="wide"
)

#image_path = r'C:\Users\renan\OneDrive\DS\python\images\logofenix.jpg'
image = Image.open('logofenix.jpg')
st.sidebar.image(image, width=120)
st.sidebar.markdown('### Phoenix Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.write(" ## Phoenix Company Growth Dashboard ")
st.markdown(
    """
    Este dashboard foi construído para acompanhar métricas de crescimento dos Entregadores e Restaurantes da Phoenix Company.
    
    ### 🎯 Principais Recursos do Dashboard:
    
    #### 🏢 Visão Empresa:
    - **Visão Geral**: Acesso aos dados brutos e métricas gerais
    - **Visão Gerencial**: 
        * Pedidos por dia
        * Distribuição de pedidos por tipo de tráfego
        * Comparação de pedidos por cidade
    - **Visão Tática**: 
        * Pedidos por semana
        * Análise de crescimento semanal
    - **Visão Geográfica**: 
        * Mapa de distribuição de pedidos
        * Concentração de entregas por região
    
    #### 🍽️ Visão Restaurantes:
    - Tempo médio de entrega por cidade
    - Distribuição de distância das entregas
    - Tempo médio de entrega por tipo de pedido
    - Análise de desempenho por condições de tráfego
    
    #### 🚚 Visão Entregadores:
    - Avaliações dos entregadores
    - Métricas de velocidade de entrega
    - Rankings de performance
    - Análise por condições climáticas
    
    ### 📊 Utilize os filtros laterais para personalizar sua análise:
    - Período de tempo
    - Condições de tráfego
    - Condições climáticas
    """
)