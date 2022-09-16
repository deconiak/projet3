import streamlit as st
import pandas as pd
import plotly.express as px
from pywaffle import Waffle
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from datetime import date
from PIL import Image

image = Image.open('logo_adn.png')
image_icon = Image.open('logo_w.jpg')
st.set_page_config(layout="wide",page_icon=image_icon)

#Sidebar
st.sidebar.success("Sélectionnez une page au dessus.")
st.sidebar.image(image)

## Imports dataframes marque qualité
df_datagouv = pd.read_csv("df_datagouv.csv", dtype={"CP": object, "SIRET": object})
df_datatourisme= pd.read_csv("data_tourisme.csv", dtype={"zipcode":object, "department_code":object})

## Import department list
liste_dpt_code = pd.read_csv("departements-france.csv", dtype={"code_region": object})
liste_dpt_code["nom_departement"] = liste_dpt_code["nom_departement"].str.lower()
liste_dpt_code["nom_region"] = liste_dpt_code["nom_region"].str.lower()

######################################################################################################################################################
######################################################################################################################################################
###############################################################Fonction WAFFLE########################################################################
######################################################################################################################################################
######################################################################################################################################################


def my_waffle(data_dict, graph_title):
    """
    INFO: fonction pour faire un waffle pie
    PARAMETRE: passer un dictionnaire sous la forme {categorie_1 : data_1, categorie_2 : data_2}
    """
    data = data_dict
    # Création de la figure
    fig = plt.figure(
    	
        FigureClass=Waffle,
        rows=5,
        columns=10,
        values=data,
        colors=["#5EBD91",
                "#F86F11"
                ],
        title={
            'label': graph_title,
            'loc': 'center',
            #'color': "white",
            'fontdict': {
                'fontsize': 12
            }
        },
        icon_legend=True,
        font_size=15,
        legend={
            'labels': [f"{k} ({v})" for k, v in data.items()],
            'loc': 'lower left',
            'bbox_to_anchor': (0, -0.4),
            'ncol': len(data),
            'framealpha': 0,
            #'labelcolor': "white",
            'fontsize': 10
         },
        block_arranging_style='snake',
        vertical=False
    )
    # pour avoir un fond transparent
    # fig.set_facecolor((0, 0, 0, 0))
    
    st.pyplot(fig)


######################################################################################################################################################
################FONCTION WORDCLOUD####################################################################################################################
######################################################################################################################################################


def my_wordcloud(df, serie_list, collocations=False): 

    """
    Info : wordcloud à partir d'une série de dataframe
    Usage : my_wordcloud(dataframe, ["colonne_name", colonne_name2"...], True)
    collocations : True pour admettre les bigrammes
    """

    # on récupère notre série de catégories sous forme d'une chaine de caractère
    my_string = ""
    for i in serie_list:
        my_string = df[i].str.cat(sep = " ") 

    # initialize wordcloud
    wordcloud = WordCloud(width=1000, height=700, 
                        max_font_size=300, 
                        min_font_size=10,
                        background_color="white",
                        colormap="BrBG",
                        collocations=collocations,
                        random_state=3,
                        stopwords=["de"]
                        )

    # generate wordcloud
    wordcloud.generate_from_text(my_string)

    # affichage
    fig, ax = plt.subplots(figsize = (10,7))
    ax.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    st.pyplot(fig)


######################################################################################################################################################
###########FONCTION HISTO DATE PLOTLY#################################################################################################################
######################################################################################################################################################

def graph_date_maj(dataframe, col_date, range_start, range_stop, title):

    fig = px.histogram(dataframe, 
                    x=col_date,
                    range_x=[range_start, range_stop],
                    color_discrete_sequence=["#5EBD91"],
                    title=title,
                    labels={
                        'last_update':'mois',
                        'count': 'somme des POI mis à jour'
                    },
                    template='simple_white'
                    )
                    
    fig.update_layout({
    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
    'paper_bgcolor': 'rgba(0, 0, 0, 0)'
    })

    fig.update_layout(
        hoverlabel=dict(bgcolor="white"),
        bargap=0.2
    )

    fig.update_traces(hovertemplate = '<b>Mois</b>: %{x}'+
                    '<br><b>Nombre de POI</b>: %{y}<br>',
        showlegend = False)

    st.plotly_chart(fig, use_container_width=True)



######################################################################################################################################################
#############################################################MISE EN PAGE#############################################################################
######################################################################################################################################################



st.title("Etats des lieux")

st.write("""Les données de Datagouv et Datatourisme concernant la marque “Qualité Tourisme” ne présentent pas le même nombre de POI. 
L’objectif de notre étude est d’identifier les POI communs aux deux sources de données. 
""")

col1, col2, col3, col4= st.columns(4)
col2.metric("Source Datatourisme",f'{df_datatourisme["id"].nunique()} POI')
col3.metric("Source Datagouv", f'{df_datagouv["id"].nunique()} POI')


st.write("""Problème principal : Les données à comparer proviennent de sources différentes et n’ont pas été compilées de la même façon.
""")


st.header("Premières différences constatées")

st.subheader("Au niveau de la fraîcheur des données")

###############################################################HISTO DATE##############################################################################
    
# date de début et de fin
date_1 = date(2021, 8, 31)
date_2 = date(2022, 8, 31)  
graph_date_maj(df_datatourisme, 'last_update', date_1, date_2, "Nombre de POI mis à jour sur l'année")

st.write("""Du côté Datatourisme, une grande partie des POI ont été mis à jour en 2022. 
    Tandis que pour les données de Datagouv, la dernière mise à jour date de février 2021. 
    Il convient de garder en tête que la différence du nombre de POI "Qualité Tourisme" entre les deux sources de données peut être en partie due à cette différence temporelle.""")

#############################################################WORDCLOUDS#################################################################################

st.subheader("Au niveau des catégories")

# wordcloud
col1, col2 = st.columns(2, gap="medium")
with col1 : 
    my_wordcloud(df_datatourisme, ["category"])
    st.caption("Datatourisme")

with col2 : 
    my_wordcloud(df_datagouv, ["CATEGORIE / FILIERE", "ACTIVITE"], True)
    st.caption("Datagouv")



st.write("""Du côté Datatourisme, les catégories et sous-catégories de POI sont nombreuses (plus d’une centaine). 
    Ces catégories sont indiquées principalement en anglais avec pour catégorie la plus présente : les hébergements (accommodation, lodging business, hotel trade, camping etc).
    """)

st.write("""Du côté Datagouv, les catégories sont moins nombreuses (une dizaine environ). 
    La catégorie la plus représentée est celle des hôtels-restaurants. 
    """)

st.write("""Ces différences empêchent une comparaison directe sur les catégories. 
    Une uniformisation serait donc à recommander.  
    """)

###############################################################WAFFLE#################################################################################
    
st.subheader("Au niveau des départements et régions")

col1, col2= st.columns(2)
with col1 : 
    # Pour waffle nombre de département pour les établissemnent marque qualité de Datatourisme
    data_DT_MQ = {'Département représentés': df_datatourisme["department"].nunique(),
              'Département non-représentés': 101-df_datatourisme["department"].nunique()
              }
    my_waffle(data_DT_MQ, 'Marque "Qualité Tourisme"\nDataTourisme')

with col2 : 
    # nombre de département pour les établissemnent marque qualité de Datagouv
    data_DG_MQ = {'Département représentés': df_datagouv["DEPARTEMENT"].nunique(),
              'Département non-représentés': 101-df_datagouv["DEPARTEMENT"].nunique()
              }
    my_waffle(data_DG_MQ, 'Marque "Qualité Tourisme"\nDataGouv')


st.write("""On ne retrouve que 58 départements différents du côté Datatourisme contre 99 du côté Datagouv (Mayotte et La Guadeloupe ne figurent pas dans la liste).""")

###############################################################CARTES#################################################################################
    
# Image

carte_choro_1 = Image.open('choro_1_finale.JPG')

st.image(carte_choro_1)

st.caption("""Nombre de POI = nombre POI Datatourisme - nombre POI Datagouv. En vert: les régions et départements pour lesquels on retrouve plus de POI chez Datatourisme par rapport à Datagouv. 
En marron: les régions et départements pour lesquels on retrouve moins de POI chez Datatourisme par rapport à Datagouv. 
""")

st.write("""On met déjà en avant des régions ayant enregistré peu de POI marque "Qualité Tourisme” sur la base Datatourisme: Auvergne-Rhône-Alpes et Provence-Alpes-Côte d’Azur. 
À l'inverse, le Grand-Est et les Pays de la Loire enregistrent davantage de POI. 
""")
###########DATAFRAME#####################################

def groupby_departement(dataframe, column, col_to_count):
    df = dataframe.groupby(by=column)[col_to_count].count().to_frame().sort_values(col_to_count, ascending=False).reset_index()
    return df

# compte nombre de poi par departement datatourisme
dpt_count_DT = groupby_departement(df_datatourisme, "department", "qualite_tourisme")
dpt_count_DT.rename(columns={"qualite_tourisme":"nb POI datatourisme"}, inplace=True)

# compte nombre de poi par département datagouv
dpt_count_DG = groupby_departement(df_datagouv, "DEPARTEMENT", "NOM ETABLISSEMENT")
dpt_count_DG.rename(columns={"NOM ETABLISSEMENT":"nb POI datagouv", "DEPARTEMENT":"department"}, inplace=True)

# fusionner ces dataframe avec la liste des officielles des départements afin d'afficher les 101 départements français
poi_count = pd.merge(liste_dpt_code, dpt_count_DT, how="left", left_on="nom_departement", right_on="department").fillna(0)
poi_count_total = pd.merge(poi_count, dpt_count_DG, how="left", left_on="nom_departement", right_on="department").fillna(0)
poi_count_total.sort_values(by="nb POI datagouv", ascending=False, inplace=True)

# ajout colonne différence
# pour identifer le nombre de POI manquants (valeur négative) ou en plus (valeur positive) dans DATAtourisme
poi_count_total["difference"] = poi_count_total["nb POI datatourisme"] - poi_count_total["nb POI datagouv"]

# suppression colonnes inutiles
col_to_drop = ["department_x", "department_y", "code_region"]
poi_count_total.drop(columns=col_to_drop, inplace=True)
poi_count_total.rename(columns={"nom_departement" : "departement", "difference": "différence"}, inplace=True)
poi_count_total.set_index("code_departement", inplace=True)

with st.expander("Vous pouvez cliquer ici afin d'accéder aux détails des régions et département ⬇️ "):

    #Liste du multi-select
    select = poi_count_total["nom_region"].unique()

    #Choix et génération du DF filtré selon la selec.
    selected = st.selectbox("Selectionnez une région", select)
    st.dataframe(poi_count_total[["departement", "nb POI datatourisme", "nb POI datagouv", "différence"]][poi_count_total["nom_region"] == selected].style.set_precision(0))

###############################################################CONCLUSION PARTIE#######################################################################
 
