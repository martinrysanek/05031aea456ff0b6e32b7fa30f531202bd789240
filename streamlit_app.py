import streamlit as st
import requests
import pandas as pd
import io
import time

# Configure Streamlit page layout for a wide style
st.set_page_config(
    layout="wide",  # Set the layout to wide
    initial_sidebar_state="auto"  # Set the initial state of the sidebar
)

# Define the CSS style
css = """
{visibility: hidden;}
footer {visibility: hidden;}
body {overflow: hidden;}
data-testid="ScrollToBottomContainer"] {overflow: hidden;}
            # .sidebar .sidebar-content {{
            #     width: 375px;
            # }}
section[data-testid="stSidebar"] {
    width: 400px !important; # Set the width to your desired value
}
"""

# Display the dataframe with the custom CSS style
st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

loading_text = st.text('Loading data...')
# URL of the raw Excel file in your GitHub repository
excel_file_url = 'https://raw.githubusercontent.com/martinrysanek/sl_experiment/main/slevy.xlsx'
# Retrieve the Excel file data from GitHub using requests
response = requests.get(excel_file_url)

# Check if the file exists in the GitHub repository
if response.status_code == 200:
    # Read the Excel file from the bytes object using BytesIO and pandas
    data = pd.read_excel(io.BytesIO(response.content))
else:
    st.error(f"Failed to download file. Status code: {response.status_code}")
    exit(1)

loading_text.empty()

NADPISY = False
BOTTOM = True
RADKY = True

# data.sort_values(by='Unit_num', ascending=True, inplace = True)
if NADPISY:
    st.sidebar.header('Hlavní kategorie zboží')
L1_selected = st.sidebar.selectbox('Vyber hlavní kategorii zboží', data['Kategorie'].unique())
if RADKY:
    st.sidebar.write("&nbsp;")
filtered_data = data[data['Kategorie'] == L1_selected].sort_values(by='Podkategorie', ascending=True)

if NADPISY:
    st.sidebar.header('Vedlejší kategorie zboží')
L2_selected = st.sidebar.selectbox('Vyber vedlejší kategorii zboží', filtered_data['Podkategorie'].unique(), index=0)
if RADKY:
    st.sidebar.write("&nbsp;")
filtered_data = filtered_data[filtered_data['Podkategorie'] == L2_selected].sort_values(by='Druh', ascending=True)

if NADPISY:
    st.sidebar.header('Druh zboží')
L3_selected = st.sidebar.multiselect('Vyber druh zboží', filtered_data['Druh'].unique(), default=filtered_data['Druh'].unique())

# st.title('Tabulka zboží')
st.write(f"**Hlavní kategorie**: *{L1_selected}* &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + f"**Vedlejší kategorie**: *{L2_selected}* &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + f"**Druh**: *{', '.join(L3_selected)}*")

# Filter the data 
filtered_data = filtered_data[filtered_data['Druh'].isin(L3_selected)].sort_values(by='Unit_num', ascending=True)
# selected_columns = ['Kategorie', 'Podkategorie', 'Druh', 'Název', 'Obchod', 'Cena', 'Cena za', 'Jednotková cena', 'Platnost']
selected_columns = ['Druh', 'Název', 'Obchod', 'Cena', 'Cena za', 'Jednotková cena', 'Platnost']
st.dataframe(filtered_data[selected_columns], hide_index=True, use_container_width=True, height=770)

with st.sidebar:
    st.divider() 
    st.write('Postup: *Po vyběru hlavní a vedlejší kategorie, jsou vždy vybrány všechny druhy, některé můžete odstranit nebo všechny najednou smazat a přidat vlastní. Zboží je tříděno podle ceny za jednotku, aby bylo zřejmé, kde se dá pořídit nejlevněji.*')
    st.write('*Děkuji za Vaše kometáře a zkušenosti, návrhy dalšího zboží, jiné třídění či uspořádání druhů.*')
    email = st.text_input('E-mail')
    message = st.text_area('Text e-mailu')
    st.button('Odešli') 
    
with st.sidebar:
    link = '[kupi.cz](https://www.kupi.cz/) &nbsp;[akcniceny.cz](https://www.akcniceny.cz/) &nbsp;[iletaky.cz](https://www.iletaky.cz/) &nbsp;[akcniletaky.com](https://www.akcniletaky.com/)'
    st.markdown(link, unsafe_allow_html=True)    



