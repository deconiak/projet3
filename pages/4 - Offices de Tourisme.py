import streamlit as st
import pandas as pd
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from pywaffle import Waffle
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image


image = Image.open('logo_adn.png')
image_icon = Image.open('logo_w.jpg')
st.set_page_config(layout="wide",page_icon=image_icon)

#Sidebar
st.sidebar.success("Sélectionnez une page au dessus.")
st.sidebar.image(image)

df = pd.read_csv("df_matched_true.csv", low_memory=False, dtype={"zipcode":object, "department_code":object})

#DF POI offices de tourisme uniquement.
df_ot = df[df['category'].str.contains('localtouristoffice') == True]

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



st.title("Offices de tourisme marque 'Qualité Tourisme'")

st.write("")
st.write("")
st.write("")
st.write("")


st.write("Nous avons filtré les offices de tourisme en utilisant la catégorie “localtouristoffice” des POI que nous avons réussi à faire correspondre avec la base de DataGouv.")
st.write("Parmi ces 593 établissements, nous regardons combien d’établissements ont la marque Qualité Tourisme dans les données DataTourisme.")

st.write("")
st.write("")
st.write("")
st.write("")



######################################################################################################################################################
######################################################################################################################################################
###############################################################WAFFLE#################################################################################
######################################################################################################################################################
######################################################################################################################################################

col1, col2, col3 = st.columns(3)

with col2 : 

#Variable pour le Waffle
    data = { 'Marque Qualité': len(df_ot[df_ot['qualite_tourisme'] == True]),
	        'Non marque Qualité' : len(df_ot[df_ot['qualite_tourisme'] == False])
	                                                           }
    my_waffle(data, "Offices de tourisme")

st.write("")
st.write("")
st.write("")
st.write("")

st.write("396 établissements devraient avoir la marque. Nous nous intéressons à la répartition des éditeurs afin d’identifier lesquels sont à l’origine de cette absence d'informations.")



######################################################################################################################################################
######################################################################################################################################################
###############################################################PIE CHART##############################################################################
######################################################################################################################################################
######################################################################################################################################################



df_ot_false = df_ot[df_ot["qualite_tourisme"]==False]
df_ot_false.dropna(subset=["publisher_legal_name"], inplace=True)
df_ot_count = pd.DataFrame(df_ot_false["publisher_legal_name"].value_counts())
df_ot_count.reset_index(inplace=True)
df_ot_count.rename(columns={"index" : "Publisher", "publisher_legal_name" : "Quantite"}, inplace=True)
	

fig2 = go.Figure(data=[go.Pie(
    labels = df_ot_count["Publisher"], 
    values= df_ot_count["Quantite"],
    hole=.5, 
    
    )])
fig2.update_layout(
    width=1400, height=900,
    #title_text="Répartition des publishers en écart sur le remplissage de la marque Qualité Tourisme. "
    )
st.plotly_chart(fig2,)

st.write("Nous pouvons constater que 63.5% des valeurs manquantes proviennent du même éditeur.")
st.write("Nous vous mettons à disposition la possibilité d’exporter la liste des POI aux formats CSV ou XSLX en sélectionnant directement le ou les éditeurs qui vous intéressent.")
st.write("")
st.write("")
######################################################################################################################################################
######################################################################################################################################################
###############################################################Multi select###########################################################################
######################################################################################################################################################
######################################################################################################################################################


#Liste du multi-select
select = df_ot_count["Publisher"].unique()

#Choix et génération du DF filtré selon la selec.
selected = st.multiselect("Selectionnez les éditeurs.", select)
pattern = "|".join(selected)
df_export = df_ot_false[df_ot_false["publisher_legal_name"].str.contains(pattern)]



st.write(pattern)

df_export[['@id', 'last_update', 'name', 'email', 'telephone',
  'siret', 'website', 'publisher_id', 'publisher_legal_name', 'zipcode',
  'address', 'city', 'department', 'department_code', 'region', 'coordinates']]



######################################################################################################################################################
######################################################################################################################################################
###############################################################Téléchargement des données#############################################################
######################################################################################################################################################
######################################################################################################################################################


@st.cache
def convert_csv(df):
    return df.to_csv().encode('utf-8')


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

   


data_csv = convert_csv(df_export[['@id', 'last_update', 'name', 'email', 'telephone',
  'siret', 'website', 'publisher_id', 'publisher_legal_name', 'zipcode',
  'address', 'city', 'department', 'department_code', 'region', 'coordinates']])
data_xlsx = convert_xlsx(df_export[['@id', 'last_update', 'name', 'email', 'telephone',
  'siret', 'website', 'publisher_id', 'publisher_legal_name', 'zipcode',
  'address', 'city', 'department', 'department_code', 'region', 'coordinates']])    


#Bouton de DL
st.download_button("Télécharger les données au format CSV", data = data_csv, file_name='Datas_ODT.csv', mime='text/csv')
st.download_button("Télécharger les données au format XSLX", data = data_xlsx, file_name='Datas_ODT.xlsx', mime='application/vnd.ms-excel')