#Run with : streamlit run /Users/yoann/Desktop/Python/Trading/app_V2.py
import Client, Portefeuille, Profiles, Recherche, Historique
import streamlit as st
import hashlib
import sqlite3
import pandas as pd
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

pages_user = ["Mon compte",
             "Portefeuille",
             "Recherche",
             "Historique de transactions"]

pages_admin = ["Mon compte",
             "Portefeuille",
             "Recherche",
             "Historique de transactions",
             "Profils"]

conn = sqlite3.connect('trading_v29.db', check_same_thread=False)
c = conn.cursor()


def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()


def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False


def create_table():
    c.execute('CREATE TABLE IF NOT EXISTS users([username] TEXT not null, [firstname] TEXT, [name] TEXT, [birthdate] DATE, '
              '[password] TEXT, [account_creation] DATE, [capital_dispo] FLOAT, [capital_investi] FLOAT, [capital_total] FLOAT)')
    c.execute('CREATE TABLE IF NOT EXISTS transactions([id] INTEGER PRIMARY KEY AUTOINCREMENT, [transac_id] TEXT, '
              '[username] TEXT not null, [ticker] TEXT, [name] TEXT, [position] TEXT, [status] TEXT, [type] TEXT, '
              '[quantity] FLOAT, [investment] FLOAT,[opening_rate] FLOAT, [closing_rate] FLOAT, [gain_perte] FLOAT, '
              '[open] DATE, [close] DATE)')

    cur = c.execute('select * from users')
    results = cur.fetchall()
    if len(results) == 0:
        c.execute('INSERT INTO users(username, firstname, name, birthdate, password, account_creation, '
                  'capital_dispo, capital_investi, capital_total) VALUES (?,?,?,?,?,?,?,?,?)',
                  ('admin', 'Admin', 'Admin', '07-01-1999', make_hashes('admin'), datetime.now(tz=None).strftime("%m/%d/%Y"),
                   1000, 0, 1000))
        c.execute('INSERT INTO users(username, firstname, name, birthdate, password, account_creation, '
                  'capital_dispo, capital_investi, capital_total) VALUES (?,?,?,?,?,?,?,?,?)',
                  ('yoanndke', 'Yoann', 'Donkerque', '07-01-1999', make_hashes('azerty'),
                   datetime.now(tz=None).strftime("%m/%d/%Y"), 1000, 0, 1000))
        c.execute('INSERT INTO users(username, firstname, name, birthdate, password, account_creation, '
                  'capital_dispo, capital_investi, capital_total) VALUES (?,?,?,?,?,?,?,?,?)',
                  ('yinoda', 'Laura', 'Candoni', '01-01-1997', make_hashes('azerty'),
                   datetime.now(tz=None).strftime("%m/%d/%Y"), 1000, 0, 1000))
        conn.commit()


def add_user(firstname, name, username, birthdate, password):
    c.execute('INSERT INTO users(username, firstname, name, birthdate, password, account_creation, '
              'capital_dispo, capital_investi, capital_total) VALUES (?,?,?,?,?,?,?,?,?)',
              (username, firstname, name, birthdate, password, datetime.now(tz=None).strftime("%m/%d/%Y"), 0, 0, 0))
    conn.commit()


def login_user(username, password):
    c.execute('SELECT * FROM users WHERE username = (?) AND password = (?)', (username, password))
    data = c.fetchall()
    return data


def view_all_users():
    c.execute('SELECT * FROM users')
    data = c.fetchall()
    return data


def view_one_user(username):
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    data = c.fetchone()
    return data

def add_capital(depot_K_tot, depot_K_avai, username, depot):
    c.execute('UPDATE users SET capital_total=(?), capital_dispo=(?) WHERE username=(?)', (depot_K_tot, depot_K_avai, username))
    add_transaction(username, None, None, None, None, "Refund", None, depot, None)
    conn.commit()

def update_capital(prix, k_investi, username):
    c.execute('UPDATE users SET capital_dispo=(?), capital_investi=(?) WHERE username=(?)', (prix, k_investi, username))
    conn.commit()


def view_all_transactions(username):
    c.execute('SELECT transac_id, ticker, name, position, status, type, quantity, investment, opening_rate, closing_rate, '
              'gain_perte, open, close FROM transactions WHERE username = ?', (username,))
    data = c.fetchall()
    return data

def view_specific_transactions(username, id):
    c.execute('SELECT transac_id, ticker, name, position, status, type, quantity, investment, opening_rate, closing_rate, '
              'gain_perte, open, close FROM transactions WHERE username = (?) and transac_id=(?)', (username, id))
    data = c.fetchall()
    return data


def add_transaction(username, ticker, name, position, status, type, quantity, investment, opening_rate):
    now = str(datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
    c.execute('INSERT INTO transactions(transac_id, username, ticker, name, position, status, type, quantity, investment, '
              'opening_rate, closing_rate, gain_perte, open, close) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
              (None, username, ticker, name, position, status, type, quantity, investment, opening_rate, None, None,
               now, None))
    if type == "Multiple":
        c.execute('SELECT id FROM transactions WHERE username = (?) and type=(?) AND open = (?)', (username, "Multiple", now))
        id = c.fetchone()[0]
        c.execute('UPDATE transactions SET transac_id = UPPER(type) || (?) WHERE username = (?) and type=(?) and open = (?)',
                  (id, username, "Multiple", now))
    elif type == "Seul":
        c.execute('UPDATE transactions SET transac_id = UPPER(type) || id WHERE username=(?) and type=(?)',
                  (username, "Seul"))
    else:
        c.execute('UPDATE transactions SET transac_id = UPPER(type) || id WHERE username=(?) and type=(?)',
                  (username, "Refund"))
    conn.commit()


def update_transaction(username, id_transaction, ticker, closing_rate, gain_perte):
    c.execute('UPDATE transactions SET status=(?), closing_rate=(?), gain_perte=(?), close=(?)'
              'WHERE username=(?) and transac_id=(?) and ticker=(?)', ("Fermé", closing_rate, gain_perte,
                                                        datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
                                                        str(username), id_transaction, ticker))
    conn.commit()


def main():
    st.set_page_config(layout='wide')
    create_table()
    menu = ["Se connecter", "Créer un compte"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Se connecter":
        username = st.sidebar.text_input("Nom d'utilisateur")
        password = st.sidebar.text_input("Mot de passe", type='password')

        if st.sidebar.checkbox("Je me connecte"):
            hashed_pswd = make_hashes(password)

            result = login_user(username, check_hashes(password, hashed_pswd))

            if result and username != 'admin':
                page = st.selectbox("Page", pages_user)
                st.sidebar.success("Connecté en tant que {}".format(username))
                user_result = view_one_user(username)
                username = user_result[0]
                firstname = user_result[1]
                name = user_result[2]
                birthdate = user_result[3]
                password = user_result[4]
                account_creation = user_result[5]
                capital_dispo = user_result[6]
                capital_investi = user_result[7]
                capital_total = user_result[8]

                if page == "Mon compte":
                    Client.app(username, firstname, name, birthdate, account_creation, capital_dispo, capital_investi,
                               capital_total)
                elif page == "Portefeuille":
                    Portefeuille.app(username, capital_dispo, capital_investi, capital_total)
                elif page == "Recherche":
                    Recherche.app(username, capital_dispo, capital_investi, capital_total)
                elif page == "Historique de transactions":
                    Historique.app(username, capital_dispo, capital_investi, capital_total)

            elif result and username == 'admin':
                page = st.selectbox("Page", pages_admin)
                st.sidebar.success("Connecté en tant que {}".format(username))
                user_result = view_one_user(username)
                username = user_result[0]
                firstname = user_result[1]
                name = user_result[2]
                birthdate = user_result[3]
                password = user_result[4]
                account_creation = user_result[5]
                capital_dispo = user_result[6]
                capital_investi = user_result[7]
                capital_total = user_result[8]

                if page == "Mon compte":
                    Client.app(username, firstname, name, birthdate, account_creation, capital_dispo,
                               capital_investi,
                               capital_total)
                elif page == "Portefeuille":
                    Portefeuille.app(username, capital_dispo, capital_investi, capital_total)
                elif page == "Recherche":
                    Recherche.app(username, capital_dispo, capital_investi, capital_total)
                elif page == "Historique de transactions":
                    Historique.app(username, capital_dispo, capital_investi, capital_total)
                elif page == "Profils":
                    Profiles.app(username)
            else:
                st.error("Nom d'utilisateur/Mot de passe incorrect")
    elif choice == "Créer un compte":
        st.subheader("Créer un compte")
        form = st.form(key='my_form')
        new_firstname = form.text_input("Prénom").title()
        new_name = form.text_input("Nom").title()
        new_username = form.text_input("Nom d'utilisateur")
        new_birthdate = form.date_input("Date de naissance", min_value=pd.to_datetime("1900-1-1").date(),
                                      max_value=pd.to_datetime(datetime.now(tz=None)).date()).strftime("%d/%m/%Y")
        new_password = form.text_input("Mot de Passe", type='password')
        submit = form.form_submit_button(label='Je crée un compte')

        if submit:
            user_result = view_all_users()
            clean_db = pd.DataFrame(user_result, columns=["Username", "Firstname", "Name", "Birthdate",
                                                          "Password", "Account Creation", "Capital Disponible",
                                                          "Capital Investi", "Capital Total"])
            users = []
            checking_age = pd.to_datetime((pd.to_datetime(date.today()) - relativedelta(years=18)))
            for user in clean_db["Username"]:
                users.append(user)
            if new_username in users:
                st.error("Cet utilisateur existe déjà.")
            elif len(new_firstname.strip()) == 0 or len(new_name.strip()) == 0 or len(new_username.strip()) == 0 or len(new_birthdate.strip()) == 0 or len(new_password.strip()) == 0:
                st.error("Veuillez remplir les champs")
            elif pd.to_datetime(new_birthdate) > checking_age:
                st.error("Vous n'avez pas 18 ans")
            else:
                add_user(new_firstname, new_name, new_username, new_birthdate, make_hashes(new_password))
                st.success("Votre compte à été créé")
                st.info("Retournez à la page de connexion")


if __name__ == '__main__':
    main()
