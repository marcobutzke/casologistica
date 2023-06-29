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
    st.dataframe(altovale)
    st.dataframe(matriz_tempo)
    st.dataframe(matriz_distancia)