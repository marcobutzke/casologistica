import pandas as pd 
import numpy as np
import streamlit as st
from streamlit_folium import folium_static

import folium
import plotly.express as px
import pyomo.environ as pyo
from pyomo.opt import SolverFactory

import warnings
warnings.filterwarnings('ignore')

def rota_otimizada(solucao):
    solucao_indice = list(
        np.where(np.array(
            solucao[i]) == 1)[0][0]
            for i in range(len(solucao)
        )
    )
    dicionario = {k:solucao_indice[k] for k, _ in enumerate(solucao_indice)}
    solucao_retorno = '0 -> '
    proximo = dicionario[0]
    solucao_retorno += str(proximo)
    while True:
        proximo = dicionario[proximo]
        solucao_retorno += ' -> '
        solucao_retorno += str(proximo)
        if proximo == 0:
            break
    return solucao_retorno

@st.cache_data
def load_database():
    df = pd.read_excel('avp.xlsx')
    df = df.rename(columns={"index":"id"})
    df = df.drop(columns=['Unnamed: 0'])
    mt = pd.read_excel('matriz_tempo.xlsx')
    mt = mt.reset_index()
    mt = mt.drop(columns=['index', 'Unnamed: 0'])
    mt.columns = list(mt.index)
    md = pd.read_excel('matriz_distancia.xlsx')
    md = md.reset_index()
    md = md.drop(columns=['index', 'Unnamed: 0'])
    md.columns = list(md.index) 
    return df, mt, md

st.set_page_config(layout="wide")
st.title('Caso para Ensino - Logística')

altovale, matriz_tempo, matriz_distancia = load_database()

tabela, caminho, entr_total, producao = st.tabs(['Tabela', 'Cidades', 'Entrega Total', 'Produção'])   

with tabela:
    col1, col2 = st.columns(2)
    col2.table(altovale[['municipio', 'valor', 'demanda', 'receita']])
    altovale["cidade_base"] = altovale["municipio"].apply(lambda x: 1 if x=='Rio do Sul' else 0)
    cidade_base = altovale[altovale["cidade_base"]==1][["latitude","longitude"]].values[0]
    ## Mostrar os dados com métricas
    mapa = folium.Map(location=cidade_base, tiles="cartodbpositron", zoom_start=10)
    cores = ["green","blue"]
    lista_cores = sorted(list(altovale["cidade_base"].unique()))
    altovale["cor"] = altovale["cidade_base"].apply(lambda x: cores[lista_cores.index(x)])
    altovale.apply(
        lambda row: folium.CircleMarker(
            location=[
                row["latitude"],
                row["longitude"]
            ],
            popup=row["municipio"],
            color=row["cor"],
            fill=True,
            radius=5
        ).add_to(mapa),
        axis=1
    )
    col1.metric('Quantidade total de demanda do produto', altovale['demanda'].sum())
    col1.metric('Valor total da Receita', altovale['receita'].sum())
    col1.metric('Valor médio do produto por valor', altovale['valor'].mean())
    col1.metric('Valor médio do produto por receita', round((altovale['receita'].sum() / altovale['demanda'].sum()),2))
    with col1:
        folium_static(mapa)
with caminho:
    rota_cidades = st.multiselect('Escolha a sequência da rota de entrega', altovale['municipio'])
    st.write(rota_cidades)
    rotas = []
    inicio = 0
    primeiro = 0
    for elemento in rota_cidades:
        if primeiro == 0:
            inicio = elemento
            primeiro = 1
            cidade_inicio = elemento
        else:
            rotas.insert(len(rotas), [inicio, elemento])
            inicio = elemento
    rotas.insert(len(rotas), [rota_cidades[-1], cidade_inicio])
    st.write(rotas)

