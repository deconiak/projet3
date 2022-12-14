from PIL import Image
import streamlit as st
import pandas as pd
import seaborn as sns
import datetime
import plotly.express as px
import matplotlib.pyplot as plt
import squarify
from matplotlib.colors import Normalize
import geopandas as gpd
import numpy as np


#Images
logo = Image.open('logo_adn.png')
image_icon = Image.open('logo_w.jpg')


#Page config
st.set_page_config(layout = 'wide',page_title='Focus Marque "Qualité Tourisme" - Projet WCS',page_icon=image_icon)

#Imports 
df_global = pd.read_csv('df_matched_true.csv', sep=',')

## Import department list
liste_dpt_code = pd.read_csv("departements-france.csv", dtype={"code_region": object})
liste_dpt_code["nom_departement"] = liste_dpt_code["nom_departement"].str.lower()
liste_dpt_code["nom_region"] = liste_dpt_code["nom_region"].str.lower()

## Import Geojson
gdf_dpt = gpd.read_file("departement_avec_outremer_rapprochée.json")
gdf_reg = gpd.read_file("region_avec_outremer_rapprochée.json")

############################################################################################################################################
############################################################################################################################################
########################################################Fonction carte######################################################################
############################################################################################################################################
############################################################################################################################################

def choropleth_map_normalize(df1, df2, serie_1, serie_2, cmap, title, ax1_title, ax2_title, ax1_label, ax2_label):
    # colormap
    cmap = cmap
    # normalize color for reg
    vmin, vmax = 0, df1[serie_1].max()
    norm1 = Normalize(vmin=vmin, vmax=vmax)
    # create normalized colorbar for dpt
    cbar1 = plt.cm.ScalarMappable(norm=norm1, cmap=cmap)
    # normalize color for dpt
    vmin, vmax = 0, df2[serie_2].max()
    norm2 = Normalize(vmin=vmin, vmax=vmax)
    # create normalized colorbar for dpt
    cbar2 = plt.cm.ScalarMappable(norm=norm2, cmap=cmap)
    # Initialize the figure
    fig, ax = plt.subplots(figsize=(20, 10))
    # Map
    ax1 = plt.subplot(121)
    df1.plot(column=serie_1, 
                    cmap=cmap, 
                    norm=norm1, 
                    legend=False,
                    edgecolor='black',
                    linewidth=.1,
                    ax=ax1)
    ax2 = plt.subplot(122)
    df2.plot(column=serie_2, 
                    cmap=cmap, 
                    norm=norm2, 
                    legend=False,
                    edgecolor='black',
                    linewidth=.1,
                    ax=ax2)
    # add colorbar
    fig.colorbar(cbar1, ax=ax1, fraction=0.04, shrink=0.80, aspect=20, label=ax1_label)
    fig.colorbar(cbar2, ax=ax2, fraction=0.04, shrink=0.80, aspect=20, label=ax2_label)
    fig.suptitle(title, fontsize=18)
    ax1.set_title(ax1_title, fontsize=16)
    ax2.set_title(ax2_title, fontsize=16)
    ax1.axis('off')
    ax2.axis('off')
    ax.axis('off')
    st.pyplot(fig)



########################################################Fonction Groupby####################################################################
def groupby_departement(dataframe, column, col_to_count):
    df = dataframe.groupby(by=column)[col_to_count].count().to_frame().sort_values(col_to_count, ascending=False).reset_index()
    return df
    
    
#Sidebar
st.sidebar.success("Sélectionnez une page au dessus.")
st.sidebar.image(logo)

#Titre
st.title("Focus sur les organismes dont les marques 'Qualité Tourisme' sont manquantes.")

st.write("Afin d'introduire cette partie, voici deux cartes présentant à la fois par région et département le nombre de points d'intêret ne disposant pas de la marque 'Qualité Tourisme' bien qu'ayant été matché sur la base de données de Data.economie.gouv.fr. Comme l'on peut le voir, certaines régions ont un taux de labels manquants extrêmement élevé, notamment la région Rhône-Alpes (et plus particulièrement Savoie et Haute-Savoie) avec plus de 2500 marques 'Qualité Tourisme' manquantes.")

############################################################################################################################################
############################################################################################################################################
########################################################Carte###############################################################################
############################################################################################################################################
############################################################################################################################################

# nombre de POI matchés au total
departement_matched_global = groupby_departement(df_global, "department", "matched")
# nombre de POI matchés n'ayant pas la marque qualité
departement_matched_not_QT = groupby_departement(df_global[df_global["qualite_tourisme"] == False], "department", "matched")
# fusionner ces dataframe avec la liste des officielles des départements afin d'afficher les 101 départements français
dpt_match_global = pd.merge(liste_dpt_code, departement_matched_global, how="left", left_on="nom_departement", right_on="department").fillna(0)
dpt_match_results = pd.merge(dpt_match_global, departement_matched_not_QT, how="left", left_on="nom_departement", right_on="department", suffixes=["_total", "_notMQ"]).fillna(0)
dpt_match_results.sort_values(by="matched_total", ascending=False, inplace=True)
# suppression colonnes inutiles
del dpt_match_results["department_total"]
del dpt_match_results["department_notMQ"]
# les régions
region_matched_not_QT = pd.pivot_table(dpt_match_results, index=["code_region", "nom_region"], 
                                       values=["matched_total", "matched_notMQ"], 
                                       aggfunc=np.sum,
                                       margins=False).reset_index()
# fusionner toutes les infos nécessaires à la viz dans un geodataframe
department_total_notMQ = gdf_dpt.merge(dpt_match_results[["code_departement", "matched_notMQ"]], left_on=["code"], right_on=["code_departement"])
region_total_notMQ = gdf_reg.merge(region_matched_not_QT[["code_region", "matched_notMQ"]], left_on=["code"], right_on=["code_region"])
choropleth_map_normalize(region_total_notMQ, department_total_notMQ, "matched_notMQ", "matched_notMQ", "Oranges", "Nombre de points d'intérêt :\nMarque Qualité Tourisme manquante", "par région", "par département", "nbr POI", "nbr POI")

############################################################################################################################################
############################################################################################################################################
######################################################## FIN Carte###############################################################################
############################################################################################################################################
############################################################################################################################################


st.write("L'exemple ci-dessous mets en avant le taux en pourcentage d'efficacité en terme de matchs effectués depuis la base de données globale de DATATourisme avec la base de Data.economie.gouv.fr ET étant dans la base réduite de DATATourisme. Le premier graphique affiche en fonction du pourcentage de réussite et le second en terme de quantité de POI brute.")
st.write("Cela permet surtout de mettre en avant le fait que certains organismes ont un taux de succés de matchs élevé en pourcentage mais une faible quantité de POI globale.")

#Bloc 1 - 
no_selec = df_global[['publisher_legal_name','@id']]
no_selec = no_selec.groupby('publisher_legal_name').count().sort_values(['@id'], ascending=False)
select_only_true=df_global[df_global['qualite_tourisme']==True]
select_only_true = select_only_true[['publisher_legal_name','@id']]
select_only_true = select_only_true.groupby('publisher_legal_name').count().sort_values(['@id'], ascending=False)
mix = no_selec.merge(select_only_true, how='left', on='publisher_legal_name').fillna(0)
mix = mix.rename(columns={'@id_x':'Supposément Qualité Tourisme','@id_y':'Identifiés Qualité Tourisme dans DATATourisme'})
mix['Identifiés Qualité Tourisme dans DATATourisme'] = mix['Identifiés Qualité Tourisme dans DATATourisme'].astype(int)
mix['taux de comparaison'] = round((mix["Identifiés Qualité Tourisme dans DATATourisme"] - mix["Supposément Qualité Tourisme"] ) / (mix["Supposément Qualité Tourisme"]) * 100,2) +100
mix = mix.reset_index()
mix['publisher_legal_name'] = mix['publisher_legal_name'].str.replace('(62c8b2ca-8176-4b00-a97f-cbe5df0e3f9e)','')
mix['publisher_legal_name'] = mix['publisher_legal_name'].str.replace('(ec9e16c5-3c22-4f89-b841-c60ce3bdc220)','')
mix['publisher_legal_name'] = mix['publisher_legal_name'].str.replace('(5afbb216-4578-4092-9257-5073ea26c884)','')
mix['publisher_legal_name'] = mix['publisher_legal_name'].str.replace('(42325dda-b66f-43b0-862c-f552068f0e8d)','')
top_28 = mix.sort_values(['taux de comparaison'], ascending=False).head(28)
top_28_qt = mix.sort_values('Identifiés Qualité Tourisme dans DATATourisme', ascending =False).head(28)

#Graph 1 
fig = px.bar(top_28, x="publisher_legal_name", y="taux de comparaison", 
             title="Taux de POI identifiés par éditeurs en marque 'Qualité Tourisme'. ",
             labels={'publisher_legal_name':'Éditeur du POI', 'taux de comparaison':'taux de comparaison en %' })
fig.update(layout_yaxis_range = [0,100])
st.plotly_chart(fig, use_container_width=True)

#Graph 2 
fig_3 = px.bar(top_28_qt, x="publisher_legal_name", y="Identifiés Qualité Tourisme dans DATATourisme", 
             title="Organismes ayant le plus haut nombre de POI correctement enregistrés dans la base de DATATourisme",
             labels={'publisher_legal_name':'Éditeur du POI', 'Identifiés Qualité Tourisme dans DATATourisme':"Nombre d'organismes possédant la marque" })
st.plotly_chart(fig_3, use_container_width=True)

st.write("Il est possible de visualiser directement ci-dessous les éditeurs ayant au moins 1 POI matché correctement sur Data.economie.gouv.fr et étant présent dans la base réduite de DATATourisme.")

#Follow-up
col1, col2 = st.columns(2)

with col1:
   st.write("Éditeurs ayant au moins un match réussi sur Data.economie.gouv.fr")
   with st.expander("Vous pouvez cliquer ici afin d'accéder au dataset brut ⬇️ "):
    st.dataframe(mix[mix['taux de comparaison'] > 0].sort_values(['taux de comparaison'], ascending=False))
with col2:
   st.write("Éditeurs n'ayant aucun match réussi sur Data.economie.gouv.fr")
   with st.expander("Vous pouvez cliquer ici afin d'accéder au dataset brut ⬇️ "):
    st.dataframe(mix[mix['taux de comparaison'] == 0].sort_values(['Supposément Qualité Tourisme'], ascending=False))

  
#Bloc 2 - 
mix_0 = mix[mix['taux de comparaison'] == 0 ]
mix_0_test = mix_0.sort_values(['Supposément Qualité Tourisme'], ascending=False).head(50)
mix_orga = mix[mix['Supposément Qualité Tourisme'] > 0].sort_values(['Supposément Qualité Tourisme'], ascending=False).head(50)
mix_orga_10 = mix_orga.head(10)

#Graph 2 
fig_2 = px.bar(mix_orga_10, 
               x='publisher_legal_name', 
               y=['Supposément Qualité Tourisme', 'Identifiés Qualité Tourisme dans DATATourisme'], 
               title="Quantité de POI publiés par les 10 plus gros éditeurs", 
               labels={'publisher_legal_name':'Éditeur', 'value' : 'Total'},                                  
               text_auto=True
              )
fig_2.update_layout(autosize=False, 
                    width=1000, height=800,
                    legend_title_text='Nombre de POI :',
                   )
st.plotly_chart(fig_2, use_container_width=True)

st.write("Nous pouvons constater qu'une majorité des POI publiés par les 10 plus gros éditeurs devraient avoir la marque 'Qualité Tourisme' renseignée dans DATATourisme.")
