from PIL import Image
import streamlit as st
import pandas as pd
import seaborn as sns
import datetime
import plotly.express as px
import matplotlib.pyplot as plt

#Image loader
image = Image.open('logo_adn.png')
image_icon = Image.open('logo_w.jpg')

#Imports
data_gouv = pd.read_csv("df_datagouv.csv", sep=",")
data_tourisme = pd.read_csv("data_tourisme.csv", sep=",")

#Page config
st.set_page_config(layout="wide", page_title='Sommaire - Projet Wild Code School', page_icon=image_icon)

#Sidebar
st.sidebar.success("Sélectionnez une page au dessus.")
st.sidebar.image(image)

#Content
st.title("Projet d'étude de la Wild Code School en collaboration avec l'organisme ADN Tourisme")
st.write("👈 Cliquez sur l'un des liens dans le menu de gauche afin d'accéder à la page de votre choix.")

st.subheader(" Objectifs du projet :bulb:")
st.write(":arrow_right: Comparer les données disponibles dans DataTourisme avec celles disponibles sur le site de Data.economie.gouv.fr.")
st.write(":arrow_right: Focus sur la marque 'Qualité Tourisme'.")
st.write(":arrow_right: Livrable sous forme de « photographie à un instant T » : cartes, graphiques, chiffres clés, exemples significatifs, infographie permettant d’identiquer les manques/écarts.")

st.write('Il est possible de télécharger le fichier readme du projet en cliquant sur le bouton ci-dessous. :arrow_lower_left:') 
text_contents = '''Fichier d'aide à l'utilisation des fichiers fournis.


Dans le dossier que nous vous remettons, vous retrouverez éléments suivants :

- Diaporama "Tuto Github/Streamlit" :

Il s'agit du tutoriel pas à pas qui explique la création d'un compte Github et d'un compte Streamlit, puis comment importer les fichiers nécessaire au fonctionnement de l'application.

C'est quoi Github ? C'est une plateforme en ligne qui permet de "stocker" du code dans des repository (une forme de dossier qui permet de gérer le code d'un projet).
Et Streamlit ? C'est un site qui fait le lien avec un repository Github et permet d'héberger et lancer le code sous forme d'application interactive utilisable sur un navigateur internet. (L'URL de l'appli est partageable).

- Le fichier "ODT_mislabelled.xlsx" :

C'est la liste des Offices de tourismes dont la catégorie est potentiellement mal référencée.
Le jeu de données ne montre que les offices de tourisme dont la catégorie est :"touristinformationcenter".

- Dossier "Streamlit" :

Il contient les fichiers qui seront à mettre dans un repository Github afin que l'application puisse être hébergée en ligne.

Le fichier "blablba.py" est le code de notre application, il fait appel aux fichiers présents dans le dossier "pages" qui contient le code des différentes pages de l'application.

"Requirements.txt" est un fichier texte qui indique quels modules Python l'application doit utiliser, rien n'est à modifier dans son contenu.

Plusieurs fichiers CSV qui sont les différentes bases de données que nous utilisons pour le rendu :
    
    - "df_matched_true.csv" Est la base de données des POI que nous avons réussi à faire matcher sur les données de DataGouv.
    - "df_datagouv_clean.csv" C'est le fichier officiel de la marque "Qualité Tourisme" issu de la DGE.
    - "df_QT_notmatched.csv"  La base des POI ayant la marque Qualité Tourisme qui n'ont pas matché.
    - "departements-france.csv" est la liste des départements Français.
    - "data_tourisme_MQ_clean.csv" C'est la base de tous les POI marque Qualité de Datatourisme.'''
st.download_button('ReadMe_Projet_Partenaire', text_contents)

st.subheader("Sommaire :bulb:")
st.write('''
    - Un état des lieux concernant les deux bases de données utilisées.
    - Démarche de comparaison des points d'intêret entre DataTourisme et DataGouv. 
    - Focus sur les organismes dont la marque 'Qualité Tourisme' est absente.  
    - Observations des offices de tourisme. 
  '''
    )

st.warning(":warning: **Mise en garde** : Du côté DataTourisme, une grande partie des POI ont été mis à jour en 2022. Tandis que pour les données de Datagouv, la dernière mise à jour date de février 2021. Il convient de garder en tête que la différence du nombre d'établissements Marque Qualité Tourisme  entre les deux bases de données peut être en partie due à cette différence temporelle.")

st.warning(":warning: Le terme POI utilisé de nombreuses fois sur ce support correspond au terme 'Point d'intêret touristique'.")

with st.expander("Vous pouvez cliquer ici afin d'accéder aux différents datasets bruts ayant servi de fondation pour ce projet ⬇️ "):
  tab1, tab2 = st.tabs(["Dataframe de Data Tourisme", "Dataframe de Data.économie.gouv"])
  with tab1:
   st.header("Dataframe de Data Tourisme")
   st.dataframe(data_tourisme)

  with tab2:
   st.header("Dataframe de Data.économie.gouv")
   st.dataframe(data_gouv)


