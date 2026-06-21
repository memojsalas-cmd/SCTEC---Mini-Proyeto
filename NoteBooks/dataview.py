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

# RF03 — Limpar e tratar os dados (regex + datas + nulos)

# LIMPEZA COM EXPRESSÕES REGULARES (módulo re)
  #re.sub(padrão, substituto, string) substitui todas as ocorrências do padrão pela string substituta.
  #r"\s+" é um padrão regex que significa "um ou mais espaços em branco" (incluindo espaços, tabs e quebras de linha).
  
import re
import os
import pandas as pd

def normalizar_texto(texto):
    """
    Limpa um valor de texto:
    - troca qualquer sequencia de espacos por um unico espaco
    - remove os espacos das pontas
    """
    if pd.isna(texto):
        return texto
    texto = str(texto)
    texto = re.sub(r"\s+", " ", texto)   # colapsa espacos repetidos
    return texto.strip()                 # remove espacos das pontas

def limpar_strings(df, colunas):
    """Aplica a normalizacao de texto nas colunas indicadas."""
    df = df.copy()
    for coluna in colunas:
        df[coluna] = df[coluna].apply(normalizar_texto)
    return df

def limpar_dados(df):
    """
    Limpa o DataFrame de vendas em etapas e devolve (df_limpo, relatorio).
    O relatorio guarda quantas linhas cada etapa removeu, para mostrar o impacto.
    """
    df = df.copy()
    relatorio = {}
    relatorio["registros_iniciais"] = len(df)

    # Etapa 1: normalizar textos (espacos extras em produto, cliente e regiao)
    df = limpar_strings(df, ["produto", "cliente", "regiao"])

    # Etapa 2: converter a coluna de data para o tipo datetime, e remover linhas sem data valida
    # errors="coerce" transforma datas invalidas em vazio (NaT)
    df["data_venda"] = pd.to_datetime(df["data_venda"], errors="coerce")
    antes = len(df)
    df = df.dropna(subset=["data_venda"])      # remove linhas sem data valida
    relatorio["datas_invalidas_removidas"] = antes - len(df)

    # Etapa 3: remover linhas sem cliente ou sem produto
    # Sem cliente ou produto nao é uma venda valida.
    antes = len(df)
    df = df.dropna(subset=["cliente", "produto"])
    relatorio["nulos_removidos"] = antes - len(df)

    # Etapa 4: remover devolucoes e precos invalidos
    # quantidade <= 0  -> devolucao / cancelamento
    # preco_unitario <= 0  -> ajuste contabil ou erro (nao é uma venda real)
    antes = len(df)
    df = df[(df["quantidade"] > 0) & (df["preco_unitario"] > 0)]
    relatorio["devolucoes_e_precos_invalidos_removidos"] = antes - len(df)

    # Etapa 5: (Removida) O ajuste do tipo de Customer ID não é aplicável pois 'cliente' é string.

    # Resumo final
    relatorio["registros_finais"] = len(df)
    relatorio["registros_removidos_total"] = relatorio["registros_iniciais"] - len(df)

    print("RELATORIO DE LIMPEZA")
    for etapa, valor in relatorio.items():
        print(f"  {etapa}: {valor}")

    return df, relatorio

# EXECUÇÃO: limpar o dataset bruto e salvar como versão v1 (com outliers)
# Nesta versão os outliers são MANTIDOS — eles serão tratados na RF04.
df_v1 , relatorio = limpar_dados ( df_bruto )
os . makedirs ( "data/processed/v1_com_outliers" , exist_ok = True )
# cria o diretório se não existir
df_v1 . to_csv ( "data/processed/v1_com_outliers/vendas_v1.csv" , index = False )
print ( "\nv1 salva em data/processed/v1_com_outliers/" )
df_v1 . head ()
  