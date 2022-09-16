import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np
from matplotlib_venn import venn2, venn2_circles
from io import BytesIO
from PIL import Image

#Images
logo = Image.open('logo_adn.png')
image_icon = Image.open('logo_w.jpg')

st.set_page_config(layout="wide",page_icon=image_icon)

#Sidebar
st.sidebar.success("Sélectionnez une page au dessus.")
st.sidebar.image(logo)

## Imports dataframes marque qualité

df_match = pd.read_csv("df_matched_true.csv", dtype={"zipcode": object})
df_datatourisme= pd.read_csv("data_tourisme.csv", dtype={"zipcode":object, "department_code":object})
df_not_match = pd.read_csv("df_QT_notmatched.csv", dtype={"zipcode": object})

######################################################################################################################################################
#######FONCTION CONVERSION EXCEL############################################################################################################
######################################################################################################################################################

def convert_xlsx(df):

    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.save()
    processed_data = output.getvalue()
    return processed_data


######################################################################################################################################################
#######FONCTION NB MATCH PAR CRITERES############################################################################################################
######################################################################################################################################################

def graph_match_criteria(dataframe, col_x, col_y, title):
    fig = px.bar(dataframe, 
                 x=col_x,
                 y=col_y,
                    #range_x=[range_start, range_stop],
                    color_discrete_sequence=["#5EBD91"],
                    title=title,
                    labels={
                        col_x: "Points d'intérêt",
                        col_y: 'Critères'
                    },
                    template='simple_white',
                 orientation='h'
                    )
                    

    fig.update_layout({
    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
    'paper_bgcolor': 'rgba(0, 0, 0, 0)'
    })

    fig.update_layout(
        hoverlabel=dict(bgcolor="white"),
        bargap=0.2
    )

    fig.update_traces(hovertemplate =
                    '<b>Critères en commun</b>: %{x}'+
                    '<br><b>POI concernés</b>: %{y}<br>',
        showlegend = False)

    st.plotly_chart(fig, use_container_width=True)

######################################################################################################################################################
#######FONCTION NB CRITERES MATCHÉ PAR POI############################################################################################################
######################################################################################################################################################

def graph_nb_criteria(dataframe, col_x, col_y, title):
    fig = px.bar(dataframe, 
                 x=col_x,
                 y=col_y,
                 color_discrete_sequence=["#5EBD91"],
                 title=title,
                 labels={
                        col_x: 'Critères en commun',
                        col_y: "Points d'intérêt"
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

    fig.update_traces(hovertemplate =
                    '<b>Critères en commun</b>: %{y}'+
                    '<br><b>POI concernés</b>: %{x}<br>',
        showlegend = False)

    st.plotly_chart(fig, use_container_width=True)

######################################################################################################################################################
#######FONCTION VENN DIAGRAM############################################################################################################
######################################################################################################################################################

def venndiagram_results(set_1, set_2, set_3):
    fig = plt.figure(figsize=(7,7))

    # Diagramme de Venn basique
    v = venn2(subsets=(set_1, set_2, set_3), set_labels=('A', 'B', 'C'))
    
    # Customisation
    v.get_patch_by_id('A').set_alpha(1.0)
    v.get_patch_by_id('B').set_alpha(1.0)

    v.get_patch_by_id('A').set_color('#5EBD91')
    v.get_patch_by_id('B').set_color('#F86F11')
    v.get_patch_by_id('C').set_color('#5C4F18')

    v.get_label_by_id('A').set_text('comparaisons réussies')
    v.get_label_by_id('B').set_text('marque qualité')

    c = venn2_circles(subsets=(set_1, set_2, set_3), linestyle='dashed')
    c[0].set_lw(1.0)
    c[1].set_lw(1.0)
    
    #  Titre et annotation
    plt.title("Résultat des comparaisons", fontsize=16)

    plt.annotate("POI n'ayant pas la marque qualité tourisme", 
                xy=v.get_label_by_id('10').get_position() - np.array([0, 0]), 
                xytext=(-170,-140),
                ha='center', 
                textcoords='offset points', 
                bbox=dict(boxstyle='round,pad=0.5', fc='gray', alpha=0.1),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.5',color='gray')
                )

    plt.annotate('POI qualité tourisme sans équivalent Datagouv', 
                xy=v.get_label_by_id('01').get_position() - np.array([0, 0]), 
                xytext=(100,80),
                ha='center', 
                textcoords='offset points', 
                bbox=dict(boxstyle='round,pad=0.5', fc='gray', alpha=0.1),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.5',color='gray')
                )
    
    st.pyplot(fig)

######################################################################################################################################################
#############################################################MISE EN PAGE#############################################################################
######################################################################################################################################################



st.title("Comparaisons des POI")


#########DEMARCHE DE COMPARAISON#######################################################################################################

st.header("Démarche de comparaison")


st.write("""Nous avons récupéré les informations d'environ 360 000 POI sur la plateforme DataTourisme et les avons comparées aux données Datagouv. Cela nous a permis d'identifier des POI marqués comme "Qualité Tourisme" sur Datagouv mais manquants sur les données "Qualité tourisme" de Datatourisme.

Les POI ont été comparés étape par étape sur les critères suivants:
- Numéro de téléphone ;
- Adresse email ;
- Site internet ;
- Nom d'établissement ;
- Adresse postale ;
- Coordonnées géographiques.
 """)

#########RESULTAT DE COMPARAISON###################################

st.header("Résultats")

nb_match_total = int((df_match['matched'] == True).sum())

col1, col2, col3= st.columns(3)
col1.metric("Matchs total",f'{nb_match_total} POI')

st.write(""" Nous avons également remarqué un grand nombre de POI "dédoublés" dans Datatourisme. 
Un même établissement peut être divisé en un POI et sous-POI dans la base Datatourisme. Par exemple, un complexe hôtelier peut avoir un identifiant différent pour l'hôtel, le restaurant et le spa. Cependant, du côté de Datagouv, ce même complexe hôtelier correspondra à un seul POI. 
Cela explique le fait que l'on retrouve plus de résultats de comparaison que de POI de la base Datagouv.
""")

example_schema = Image.open('schema_poi.JPG')
st.image(example_schema)


st.caption("Exemple pour le manoir de l'espérance")

#######NB MATCH PAR CRITERE ##############################################################################

st.subheader("Résultats critères par critères")


# compter le nombre de True dans chaque colonne de comparaison
nb_match_per_criteria = df_match[['comp_on_email_ok', 'comp_on_tel_ok', 'comp_on_web_ok', 'comp_on_address_ok',
                            'comp_full_name_ok', 'comp_on_geo_ok']].sum().sort_values(ascending=False)

df_graph_01 = pd.DataFrame(nb_match_per_criteria, columns=["nb_match"]).reset_index()
df_graph_01.rename(columns={"index":"criteria"}, inplace=True)

label_dico ={"comp_on_email_ok": "Email",
             "comp_on_web_ok": "Site internet",
             "comp_on_tel_ok": "Telephone",
             "comp_on_address_ok": "Adresse",
             "comp_full_name_ok": "Nom",
             "comp_on_geo_ok": "Géolocalisation"
             }

df_graph_01.replace({"criteria": label_dico}, inplace=True)

df_graph_01.sort_values(by="nb_match", inplace=True)

# plot
graph_match_criteria(df_graph_01, "nb_match", "criteria", "Comparaisons réussies par critères")

st.write("""L'adresse postale, la géolocalisation et les numéros SIRET ne sont pas des critères efficaces de comparaison. 
- Même adresse pour plusieurs POI ;
- Géolocalisation aléatoire ;
- Valeurs manquantes pour les numéros SIRET.
""")

#########CRITERES MATCHÉ PAR POI#######################################################################################################

# compter le nombre de True par ligne et compter les occurences de chaque valeur
nb_criteria_matched = df_match[['comp_on_email_ok', 'comp_on_tel_ok', 'comp_on_web_ok', 'comp_on_address_ok', 
                                   'comp_full_name_ok', 'comp_on_geo_ok']].sum(axis=1).value_counts()

df_graph_02 = pd.DataFrame(nb_criteria_matched).reset_index()
df_graph_02.rename(columns={"index":"nb_criteria", 0: "sum_poi"}, inplace=True)
df_graph_02.sort_values(by="nb_criteria", ascending=True,inplace=True)

# plot
graph_nb_criteria(df_graph_02, "nb_criteria", "sum_poi", "Nombre de critères avec comparaison réussie par points d'intérêt")

st.write("""Bien que le travail de comparaison ait été réalisé sur six critères. Très peu de POI sont identiques sur la totalité de ces critères. 
""")

#####VENN DIAGRAM ###############################W#################################################################################

st.subheader("POI communs à Datatourisme et Datagouv")


# poi ayant matché sans marque qualité
set_a = int((df_match['matched'] == True).sum() - (df_match['qualite_tourisme'] == True).sum())

# poi n'ayant pas matché avec marque qualité
set_b = int(df_datatourisme["id"].nunique() - (df_match['qualite_tourisme'] == True).sum())

# poi ayant matché avec marque qualité
set_c = int((df_match['qualite_tourisme'] == True).sum())
 
# plot
venndiagram_results(set_a, set_b, set_c)

st.write("""
- 2/3 des POI marque "Qualité Tourisme" de Datatourisme correspondent à des POI marque "Qualité Tourisme" chez Datagouv. 
- Un grand nombre de POI Datatourisme n'ayant pas la marque "Qualité Tourisme" ont trouvé un match dans la base Datagouv. 

Plusieurs explications possibles : 
- Les POI ont perdu la marque et ont été mis à jour du côté de Datatourisme ;
- Les éditeurs du POI n'ont pas mentionné la marque lors de la saisie dans la base Datatourisme.
""")

st.subheader("Exports des données")

data_xlsx_QT = convert_xlsx(df_not_match[['@id', 'last_update', 'name', 'email', 'telephone',
  'siret', 'website', 'publisher_id', 'publisher_legal_name', 'zipcode',
  'address', 'city', 'department', 'department_code', 'region']])  

data_xlsx_match = convert_xlsx(df_match[['@id', 'last_update', 'name', 'email', 'telephone',
  'siret', 'website', 'publisher_id', 'publisher_legal_name', 'zipcode',
  'address', 'city', 'department', 'department_code', 'region']])  

col1, col2 = st.columns(2)

with col1:
    st.write("""
    La liste complète des POI communs à Datatourisme et Datagouv
    """)
    st.download_button("Télécharger les données au format XSLX", data = data_xlsx_match, file_name='Datas_MQ_total.xlsx', mime='application/vnd.ms-excel')

with col2:
    st.write("""
    POI Datatourisme "Qualité Tourisme" sans équivalent Datagouv
    """)
    st.download_button("Télécharger les données au format XSLX", data = data_xlsx_QT, file_name='Datas_MQ_notmatched.xlsx', mime='application/vnd.ms-excel')


