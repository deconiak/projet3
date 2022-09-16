from PIL import Image
import streamlit as st
import pandas as pd
import seaborn as sns
import datetime
import plotly.express as px
import matplotlib.pyplot as plt
import squarify

#Images
logo = Image.open('logo_adn.png')
image_icon = Image.open('logo_w.jpg')
cartes = Image.open('choro_2_finale.jpg')

#Page config
st.set_page_config(layout = 'wide',page_title='Focus Label Qualité Tourisme - Projet WCS',page_icon=image_icon)

#Imports 
df_global = pd.read_csv('df_matched_true.csv', sep=',')

#Sidebar
st.sidebar.success("Sélectionnez une page au dessus.")
st.sidebar.image(logo)

#Titre
st.title("Focus sur les organismes dont les marques 'Qualité Tourisme' sont manquantes.")

st.write("Afin d'introduire cette partie, voici deux cartes présentant à la fois par région & département le nombre de points d'intêret ne disposant pas de la marque 'Qualité Tourisme' bien qu'ayant été matché sur la base de données de DataGouv. Comme l'on peut le voir, certaines régions ont un taux de labels manquants extrêmement élevé, notamment la région Rhône-Alpes (et plus particulièrement Savoie & Haute-Savoie) avec plus de 2500 marques 'Qualité Tourisme' manquantes.")

st.image(cartes)

st.write("L'exemple ci-dessous mets en avant le taux en pourcentage d'efficacité en terme de matchs effectués depuis la base de données globale de DataTourisme avec la base de DataGouv ET étant dans la base réduite de DataTourisme. Le premier graphique affiche en fonction du pourcentage de réussite et le second en terme de quantité de POI brute.")
st.write("Cela permets surtout de mettre en avant le fait que certains organismes ont un taux de succés de matchs élevé en pourcentage mais une faible quantité de POI globale.")

#Bloc 1 - 
no_selec = df_global[['publisher_legal_name','@id']]
no_selec = no_selec.groupby('publisher_legal_name').count().sort_values(['@id'], ascending=False)
select_only_true=df_global[df_global['qualite_tourisme']==True]
select_only_true = select_only_true[['publisher_legal_name','@id']]
select_only_true = select_only_true.groupby('publisher_legal_name').count().sort_values(['@id'], ascending=False)
mix = no_selec.merge(select_only_true, how='left', on='publisher_legal_name').fillna(0)
mix = mix.rename(columns={'@id_x':'Total_des_PoI','@id_y':'PoI_label_Qualité_Tourisme'})
mix['PoI_label_Qualité_Tourisme'] = mix['PoI_label_Qualité_Tourisme'].astype(int)
mix['taux de comparaison'] = round((mix.PoI_label_Qualité_Tourisme - mix.Total_des_PoI ) / (mix.Total_des_PoI) * 100,2) +100
mix = mix.reset_index()
mix['publisher_legal_name'] = mix['publisher_legal_name'].str.replace('(62c8b2ca-8176-4b00-a97f-cbe5df0e3f9e)','')
mix['publisher_legal_name'] = mix['publisher_legal_name'].str.replace('(ec9e16c5-3c22-4f89-b841-c60ce3bdc220)','')
mix['publisher_legal_name'] = mix['publisher_legal_name'].str.replace('(5afbb216-4578-4092-9257-5073ea26c884)','')
mix['publisher_legal_name'] = mix['publisher_legal_name'].str.replace('(42325dda-b66f-43b0-862c-f552068f0e8d)','')
top_28 = mix.sort_values(['taux de comparaison'], ascending=False).head(28)
top_28_qt = mix.sort_values('PoI_label_Qualité_Tourisme', ascending =False).head(28)

#Graph 1 
fig = px.bar(top_28, x="publisher_legal_name", y="taux de comparaison", 
             title="Taux de POI identifiés par éditeurs en label Qualité Tourisme ",
             labels={'publisher_legal_name':'Éditeur du POI', 'taux de comparaison':'taux de comparaison en %' })
fig.update(layout_yaxis_range = [0,100])
st.plotly_chart(fig, use_container_width=True)

#Graph 2 
fig_3 = px.bar(top_28_qt, x="publisher_legal_name", y="PoI_label_Qualité_Tourisme", 
             title="Organismes ayant le plus haut nombre de POI correctement enregistrés dans la base de Data Tourisme",
             labels={'publisher_legal_name':'Éditeur du POI', 'PoI_label_Qualité_Tourisme':"Nombre d'organismes possédant le label" })
st.plotly_chart(fig_3, use_container_width=True)

st.write("Il est possible de visualiser directement ci-dessous les éditeurs ayant au moins 1 POI matché correctement sur DataGouv et étant présent dans la base réduite de DataTourisme.")

#Follow-up
col1, col2 = st.columns(2)

with col1:
   st.write("Éditeurs ayant au moins un match réussi sur DataGouv")
   with st.expander("Vous pouvez cliquer ici afin d'accéder au dataset brut ⬇️ "):
    st.dataframe(mix[mix['taux de comparaison'] > 0].sort_values(['taux de comparaison'], ascending=False))
with col2:
   st.write("Éditeurs n'ayant aucun match réussi sur DataGouv")
   with st.expander("Vous pouvez cliquer ici afin d'accéder au dataset brut ⬇️ "):
    st.dataframe(mix[mix['taux de comparaison'] == 0].sort_values(['Total_des_PoI'], ascending=False))

  
#Bloc 2 - 
mix_0 = mix[mix['taux de comparaison'] == 0 ]
mix_0_test = mix_0.sort_values(['Total_des_PoI'], ascending=False).head(50)
mix_orga = mix[mix['Total_des_PoI'] > 0].sort_values(['Total_des_PoI'], ascending=False).head(50)
mix_orga_10 = mix_orga.head(10)

#Graph 2 
fig_2 = px.bar(mix_orga_10, x='publisher_legal_name', y=['Total_des_PoI', 'PoI_label_Qualité_Tourisme'], title="Les 10 éditeurs ayant le plus de points d'intêrets publiés", labels={'publisher_legal_name':'Éditeur du POI', 'value' : 'Total' }, text_auto=True)
fig_2.update_layout(autosize=False, width=1000, height=800)
st.plotly_chart(fig_2, use_container_width=True)