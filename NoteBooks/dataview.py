# RF01 -Criação de um Data set de vendas com dados sintéticos / Gerar o dataset no código
import pandas as pd 
import numpy as np 
import random 
import os 
import json 
import matplotlib.pyplot as plt 
import seaborn as sns 
from datetime import datetime, timedelta

# Gera um dataset sintético de vendas com dados propositalmente sujos, incluindo valores nulos, 
# strings sujas, datas inválidas e outliers. 

def gerar_dataset_vendas(n_registros= 500 , seed= 100):
  
  random.seed(seed)
  np.random.seed(seed)
  produtos = [ 'Notebook' , 'Smartphone' , 'Tablet' , 'Monitor' , 'Teclado' , 'Mouse' ]
  precos = { 'Notebook' : 3500 , 'Smartphone' : 2200 , 'Tablet' : 1800 , 'Monitor' : 1200 , 'Teclado' : 250 , 'Mouse' : 120 }
  categorias = { "Notebook" : "Computadores" , "Smartphone" : "Celulares" , "Tablet" : "Celulares" , "Monitor" : "Computadores" , "Teclado" : "Periféricos" , "Mouse" : "Periféricos" }
  regioes = [ "Sudeste" , "Sul" , "Nordeste" , "Centro-Oeste" , "Norte" ]
  clientes = [ f"Cliente_{i: 03d}" for i in range ( 1 , 31 )]
  data_inicio = datetime( 2024 , 1 , 1 )
  dados = []
  for i in range (n_registros):
    produto = random.choice(produtos)
    quantidade = random.randint( 1 , 10 )
    preco = precos[produto]
    data = data_inicio + timedelta(days=random.randint( 0 , 364 ))

    # Inserindo dados intencionalmente sujos para limpeza
    if random.random() < 0.05 : quantidade = None # valor nulo
    if random.random() < 0.04 : preco = None # valor nulo
    if random.random() < 0.03 : produto = " " + produto # espaço extra (string suja)
    data_str = data.strftime( "%Y-%m-%d" ) if random.random() > 0.02 else "DATA INVALIDA"

    dados.append({ "id_venda" : i + 1 , "data_venda" : data_str, "cliente" : random.choice(clientes),
                    "produto" : produto, "categoria" : categorias.get(produto.strip(), "Outros" ),
                    "regiao" : random.choice(regioes), "quantidade" : quantidade, "preco_unitario" : preco })
  return pd.DataFrame(dados)

# Gerar e salvar
df_bruto = gerar_dataset_vendas()
os.makedirs( 'data/raw' , exist_ok= True )
# Adicionado para garantir que o diretório exista
df_bruto.to_csv( "data/raw/vendas.csv" , index= False )
print (f"Dataset gerado com {len (df_bruto)} registros." )
print (df_bruto.head())

## RF02 – Inspecionar e Descrever os Dados
def inspecionar_dados(df_bruto):

    #Exibe informações básicas do DataFrame.

    print("\n=== INSPEÇÃO INICIAL DO DATASET ===")
    print(f"Shape: {df_bruto.shape}")
    print(f"\nColunas: {list(df_bruto.columns)}")
    print(f"\nTipos de dados:\n{df_bruto.dtypes}")
    print(f"\nValores nulos por coluna:\n{df_bruto.isnull().sum()}")
    print(f"\nPrimeiros registros:\n{df_bruto.head()}")
    print(f"\nEstatísticas descritivas:\n{df_bruto.describe()}")

    return df_bruto.describe(include="all").round(2)

inspecionar_dados(df_bruto)

