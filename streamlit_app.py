import streamlit as st
import requests
import pandas as pd
import io
import time
from email.mime.text import MIMEText
import smtplib
import sys
import pickle
from streamlit_js_eval import streamlit_js_eval

NADPISY = False
RADKY = False
# min_val= {}
MAX_VALUE = 9999

if "MODE" not in st.session_state:
    st.session_state.MODE = 0
if "selection" not in st.session_state:
    selection = []
    st.session_state.selection = pickle.dumps(selection)
if "num_rows" not in st.session_state:
    st.session_state.num_rows = 0
if "L4_selected" not in st.session_state:
    st.session_state.L4_selected = ""

# locale.setlocale(locale.LC_ALL, "cs_CZ.UTF-8")

# Configure Streamlit page layout for a wide style
st.set_page_config(
    layout="wide",  # Set the layout to wide
    initial_sidebar_state="auto",  # Set the initial state of the sidebar
)

# Define the CSS style
css = """
{visibility: hidden;}
footer {visibility: hidden;}
body {overflow: hidden;}
data-testid="ScrollToBottomContainer"] {overflow: hidden;}
section[data-testid="stSidebar"] {
    width: 400px !important; # Set the width to your desired value
}
"""

@st.cache_data(ttl=900)
def load_data(excel_file_url):
    return requests.get(excel_file_url)

def make_pretty(styler):
    styler.background_gradient(axis=1, cmap="Greens")
    return styler

# Display the dataframe with the custom CSS style
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

loading_text = st.text("Loading data...")
# URL of the raw Excel file in your GitHub repository
excel_file_url = (
    "https://raw.githubusercontent.com/martinrysanek/sl_experiment/main/slevy.xlsx"
)
# Retrieve the Excel file data from GitHub using requests

response = load_data(excel_file_url)

# Check if the file exists in the GitHub repository
if response.status_code == 200:
    # Read the Excel file from the bytes object using BytesIO and pandas
    data = pd.read_excel(io.BytesIO(response.content))
else:
    st.error(f"Failed to download file. Status code: {response.status_code}")
    exit(1)

loading_text.empty()

def on_L1_change():
    st.session_state.L4_selected = ""
    
    
def on_L2_change():
    st.session_state.L4_selected = ""

if NADPISY:
    st.sidebar.header("Hlavní kategorie zboží")
L1_selected = st.sidebar.selectbox(
    "Vyber hlavní kategorii zboží",
    data["Kategorie"].unique(),
    help="Začněte výběrem hlavní kategorie zboží.",
    on_change=on_L1_change
)
if RADKY:
    st.sidebar.write("&nbsp;")
filtered_data = data[data["Kategorie"] == L1_selected].sort_values(
    by="Podkategorie", ascending=True
)

if NADPISY:
    st.sidebar.header("Vedlejší kategorie zboží")
L2_selected = st.sidebar.selectbox(
    "Vyber vedlejší kategorii zboží",
    filtered_data["Podkategorie"].unique(),
    index=0,
    help="Pokračujte výběrem vedlejší kategorie zboží, který zobrazí druhy.",
    on_change=on_L2_change
)
if RADKY:
    st.sidebar.write("&nbsp;")
filtered_data = filtered_data[filtered_data["Podkategorie"] == L2_selected].sort_values(
    by="Druh", ascending=True
)

if NADPISY:
    st.sidebar.header("Druh zboží")
L3_selected = st.sidebar.multiselect(
    "Vyber druh zboží",
    filtered_data["Druh"].unique(),
    default=filtered_data.iloc[0]["Druh"],
    help="Nejprve jsou zobrazeny všechny druhy kategorií zboží k daným kategoriím. Vyberte ty druhy zboží, které Vás zajímají, ostatní postupně smažte nebo smažte všechny najednou a začněte prvním druhem.",
)

st.sidebar.write("&nbsp;")
L4_selected = st.sidebar.text_input("Upřesni název zboží", value = "", max_chars=20, placeholder="upřesni název, může zůstat nevyplněný ...", help="Upřesněte název zboží, tento údaj může zůstat nevyplněný", key="L4_selected")
# st.sidebar.info(f"L4: {L4_selected}")
# st.sidebar.info(f"st.session_state.L4: {st.session_state.L4_selected}")

if st.sidebar.button("Vložit vybrané kategorie do porovnání"):
    new_row = [L1_selected, L2_selected, L3_selected, L4_selected, 1]
    selection = pickle.loads(st.session_state.selection)
    selection.append(new_row)
    st.session_state.selection = pickle.dumps(selection)
    st.session_state.num_rows += 1

if st.sidebar.button("Přepnout mód porovnání"):
    st.session_state.MODE = (st.session_state.MODE + 1) % 2

if st.session_state.MODE == 0:
    # st.title('Tabulka zboží')
    st.write(
        f"**Hlavní kategorie**: *{L1_selected}* &nbsp;&nbsp;&nbsp;"
        + f"**Vedlejší kategorie**: *{L2_selected}* &nbsp;&nbsp;&nbsp;"
        + f"**Druh**: *{', '.join(L3_selected)}* &nbsp;&nbsp;&nbsp;" + f"**Upřesnění**: \"{L4_selected}\""
    )

    filtered_data = filtered_data[filtered_data["Druh"].isin(L3_selected)].sort_values(
        by="Unit_num", ascending=True
    )
    if L4_selected != "":
        filtered_data = filtered_data[filtered_data["Název"].str.contains(L4_selected)]
        
    selected_columns = [
        "Druh",
        "Název",
        "Obchod",
        "Price_num",
        "Cena za",
        "Unit_num",
        "Unit_amount",
        "Platnost"
    ]
    # print (filtered_data[selected_columns].columns)
    st.data_editor(
        filtered_data[selected_columns],
        column_config={
            "Druh": st.column_config.TextColumn(
                "Druh",
                help="Druh zboží",
                disabled=True,
                max_chars=100,
            ),
            "Název": st.column_config.TextColumn(
                "Název",
                help="Název zboží",
                disabled=True,
                max_chars=100,
            ),
            "Obchod": st.column_config.TextColumn(
                "Obchod",
                help="Obchod prodávající zboží",
                disabled=True,
                max_chars=100,
            ),
            "Price_num": st.column_config.NumberColumn(
                "Cena",
                help="Cena [Kč]",
                min_value=0,
                max_value=10000,
                step=0.01,
                format="%.2f Kč",
                disabled=True                
            ),
            "Cena za": st.column_config.TextColumn(
                "Cena za",
                help="Uvedená cena je za toto uvedené množství",
                disabled=True,
                max_chars=100,
            ),
            "Unit_num": st.column_config.NumberColumn(
                "Jednotková cena",
                help="Jednotková cena [Kč]",
                min_value=0,
                max_value=10000,
                step=0.01,
                format="%.2f Kč",
                disabled=True                
            ),
            "Unit_amount": st.column_config.TextColumn(
                "Množství za jednotku",
                help="Množství za jednotku",
                disabled=True,
                max_chars=100,
            ),
            "Platnost": st.column_config.TextColumn(
                "Platnost",
                help="Akce k danému zboží má zde zvedenou platnost",
                disabled=True,
                max_chars=100,
            )
        },
        hide_index=True,
        use_container_width=True,
        height=770
    )
    
elif st.session_state.MODE == 1 and "selection" in st.session_state and st.session_state.num_rows > 0:
    st.header("Přehled vybraných kategorií")

    num_rows = st.session_state.num_rows
    selection = pickle.loads(st.session_state.selection)

    df = pd.DataFrame(
        selection,
        columns=[
            "Hlavní kategorie",
            "Vedlejší kategorie",
            "Druh",
            "Upřesnění",
            "Relativní zastoupení"
        ],
    )
    df.reset_index(inplace=True)     
    df['index'] = df['index'].apply(str)
    df = df.rename(columns={'index': 'Výběr kategorií'})
    
    edited_df = st.data_editor(
        df,
        column_config={
            "Relativní zastoupení": st.column_config.SelectboxColumn(
                "Relativní zastoupení",
                help="Relativní zastoupení",
                options=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
                required=True,
            ),
            "Hlavní kategorie": st.column_config.TextColumn(
                "Hlavní kategorie",
                help="Hlavní kategorie",
                disabled=True,
                max_chars=100,
            ),
            "Vedlejší kategorie": st.column_config.TextColumn(
                "Vedlejší kategorie",
                help="Vedlejší kategorie",
                disabled=True,
                max_chars=100,
            ),
            "Výběr kategorií": st.column_config.TextColumn(
                                    "Výběr kategorií",
                                    help="Číslo výběru kategorií",
                                    disabled=True
            ),
            "Upřesnění": st.column_config.TextColumn(
                                    "Upřesnění",
                                    help="Upřesnění názvu zboží",
                                    disabled=True
            ),
            "Druh": st.column_config.ListColumn("Druhy", help="Seznam vybraných druhů k daným kategoriím")
        },
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
    )
    
    for index, row in edited_df.iterrows():
        value = row["Relativní zastoupení"]
        selection[index][4] = value
    st.session_state.selection = pickle.dumps(selection)

    set_obchody = set(data["Obchod"].unique())
    # for row in selection:
        # filtered_data = data[
        #     (data["Kategorie"] == row[0])
        #     & (data["Podkategorie"] == row[1])
        #     & data["Druh"].isin(row[2])
        # ]
        # if row[3] != "":
        #     filtered_data = filtered_data[filtered_data["Název"].str.contains(row[3])]
        # set_obchody = set_obchody.intersection(set(filtered_data["Obchod"].unique()))

    if len(set_obchody) > 0:

        df_obchody = pd.DataFrame()
        for obchod in set_obchody:
            values = None
            for row in selection:
                vyber = data[
                    (data["Obchod"] == obchod)
                    & (data["Kategorie"] == row[0])
                    & (data["Podkategorie"] == row[1])
                    & data["Druh"].isin(row[2])]
                if not vyber.empty and row[3] != "":
                    vyber = vyber[vyber["Název"].str.contains(row[3])]
                if vyber.empty:
                    value = MAX_VALUE
                else:
                    value = vyber["Price_num"].min() * row[4]    
                if values == None:
                    values = [value]
                else:
                    values.append(value)
            # print (obchod, values)
            new_df = pd.DataFrame({obchod: values})
            if df_obchody.empty:
                df_obchody = new_df
            else:
                df_obchody = pd.concat([df_obchody, new_df], axis=1)

        len_obchody = len(df_obchody.index) - 1
        

        if len_obchody >= 0:
            df_obchody.loc[len(df_obchody.index)] = df_obchody.sum()
            df_obchody = df_obchody.rename(index={(len(df_obchody)-1): 'Součet'})
            last_row = df_obchody.iloc[-1]
            df_obchody = df_obchody[last_row.sort_values(ascending=True).index]
            df_obchody = df_obchody.iloc[:, :8]
                
            st.header("Obchody a ceny za vybrané kategorie")
            df_config = {}
            for column in df_obchody.columns:
                df_config[column] = st.column_config.NumberColumn(
                                            column,
                                            help="Cena [Kč]",
                                            min_value=0,
                                            max_value=10000,
                                            step=0.01,
                                            format="%.2f Kč",
                                            disabled=True                
                                    )
        
            df_obchody.reset_index(inplace=True)      
            df_obchody['index'] = df_obchody['index'].apply(str)
# df_obchody = df_obchody.style.pipe(make_pretty)    
            df_config['index'] = st.column_config.TextColumn(
                                            "Výběr kategorií",
                                            help="Číslo výběru kategorií",
                                            disabled=True
                    )
            st.data_editor(df_obchody, 
                            column_config=df_config, 
                            hide_index=True,
                            use_container_width=True
                            )
            st.markdown('*Cena 9999.00 Kč u obchodu znamená, že daný obchod nem8 vybrané zboží v akci podle letáků. Obchody jsou tříděny zleva od nejlevnějšího k nejdražšímu.*')
        else:
            st.header("Není obchod, který má nabídky pro všechny kategorie. Začněte od začátku.")
    else:
        st.header("Není obchod, který má nabídky pro všechny kategorie. Začněte od začátku.")
      
    st.write("")
    if st.button("Smazat výběr kategorií"):
        selection = []
        st.session_state.selection = pickle.dumps(selection)
        st.session_state.num_rows = 0
        st.session_state.MODE = 0
        streamlit_js_eval(js_expressions="parent.window.location.reload()")

with st.sidebar:
    # st.divider()
    st.sidebar.write("")
    # st.write('Postup: *Po vyběru hlavní a vedlejší kategorie, jsou vždy vybrány všechny druhy, některé nebo všechny najednou můžete odstranit a nasledně vybrat vlastní. Zboží je tříděno podle Jednotkové ceny, aby bylo zřejmé, kde se dá pořídit nejlevněji.*')
    st.write(
        "*Děkuji za Vaše kometáře a zkušenosti, návrhy dalšího zboží, jiné třídění či uspořádání druhů.*"
    )
    email = st.text_input("E-mail", placeholder="Váše e-mail adresa ...")
    content = st.text_area("Text e-mailu", placeholder="napište sdělení do e-mailu ...")
    if st.button("Odešli"):
        username = "jiri.sladek.praha@gmail.com"
        password = "npynbtxdlynynuyc"  # Heslo pro aplikaci

        message = MIMEText(content)
        message["Subject"] = "Nová zpráva z streamlit.app"
        message["From"] = email
        recipient = username

        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            try:
                smtp.login(username, password)
            except Exception as e:
                st.error("Přihlášení se nepovedlo.", e)
                sys.exit()
            try:
                smtp.sendmail(username, recipient, message.as_string())
            except Exception as e:
                st.error("Odeslání se nepovedlo.", e)
                sys.exit()

            sent = st.success("E-mail odeslán")
            time.sleep(0.5)
            sent.empty()


with st.sidebar:
    link = "[kupi.cz](https://www.kupi.cz/) &nbsp;[akcniceny.cz](https://www.akcniceny.cz/) &nbsp;[iletaky.cz](https://www.iletaky.cz/) &nbsp;[akcniletaky.com](https://www.akcniletaky.com/)"
    st.markdown(link, unsafe_allow_html=True)
