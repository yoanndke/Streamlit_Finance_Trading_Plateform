import streamlit as st
import app_V2
import importlib
importlib.reload(app_V2)
import pandas as pd
import pandas_datareader.data as web
from datetime import date, timedelta
from fbprophet import Prophet
from fbprophet.plot import plot_plotly


def app(username, capital_dispo, capital_investi, capital_total):
    df = pd.read_csv("/Users/yoann/Desktop/Python/Trading/nasdaq_screener_1641419780590.csv", sep=",",
                     usecols=["Symbol", "Name", "Country", "Sector", "Industry"])
    df['Name'] = [i.upper() for i in df['Name']]
    st.title('Prédiction')
    col1, col2 = st.columns((3, 1))
    with col1:
        #####Champ de recherche
        tick = ""
        form = st.form(key='my_form')
        rech = form.text_input(label='Recherche').upper()
        startdate = form.date_input("Startdate", min_value=pd.to_datetime("1990-1-1").date(),
                                  max_value=pd.to_datetime(date.today() - timedelta(days=1)).date(),
                                  value=pd.to_datetime("2017-1-1").date()).strftime("%d/%m/%Y")
        submit = form.form_submit_button(label='Rechercher')

        if rech == "":
            st.warning("Veuillez entrer un ticker ou un nom d'action")
        elif submit and rech == "":
            st.warning("Veuillez entrer un ticker ou un nom d'action")
        else:
            if rech in df["Symbol"].tolist():
                tick = df[df["Symbol"] == rech]["Symbol"].to_string(index=False)
            else:
                nb_elem = []
                for elem in df["Name"].tolist():
                    if rech in elem:
                        nb_elem.append(elem)
                if len(nb_elem) == 0:
                    st.error("Aucune action à ce nom existe")
                    return ''
                elif len(nb_elem) == 1:
                    tick = df[df["Name"] == nb_elem[0]]["Symbol"].to_string(index=False)
                else:
                    optn = st.selectbox('Quelle action contenant "{}" souhaitez vous regarder ?'.format(rech.lower()),
                                        (nb_elem))
                    tick = df[df["Name"] == optn]["Symbol"].to_string(index=False)
    with col2:
        n_years = st.slider('Années à prédire :', 1, 5)

    if rech != "":
        ticker = df[df["Symbol"] == tick]["Symbol"].to_string(index=False).upper()
        name = df[df["Symbol"] == tick]["Name"].to_string(index=False).title()
        if n_years > 1:
            st.header("Prédiction pour " + ticker + " - " + name + " sur {} ans".format(n_years))
        else:
            st.header("Prédiction pour " + ticker + " - " + name + " sur {} an".format(n_years))

        today = date.today().strftime("%Y-%m-%d")

        data = web.DataReader(ticker, data_source="yahoo", start=startdate, end=today)
        data.reset_index(inplace=True)

        '''fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name="stock_open"))
        fig.add_trace(go.Scatter(x=data["Date"], y=data["Close"], name="stock_close"))
        fig.layout.update(xaxis_rangeslider_visible=True)
        st.plotly_chart(fig)'''

        # Prédiction
        df_no_weekdays = data[data['Date'].dt.dayofweek < 5] #on enlève les weekends du dataset d'entrée
        df_train = df_no_weekdays[['Date', 'Close']] #on sélectionne la colonne Date et la Fermeture
        df_train = df_train.rename(columns={"Date": "ds", "Close": "y"}) #on renomme les colonnes

        model = Prophet()
        model.fit(df_train) #on entraîne notre model
        period = n_years * 365
        future = model.make_future_dataframe(periods=period) #on créer un nouveau dataset sur x années
        future_no_weekdays = future[future['ds'].dt.dayofweek < 5] #on enlève les weekends du dataset prédits
        forecast = model.predict(future_no_weekdays) #on teste le modèle

        col1, col2 = st.columns((2, 1))
        with col1:
            # Faire un graphique de la prévision
            fig1 = plot_plotly(model, forecast)
            fig1.layout.update(xaxis_rangeslider_visible=True)
            st.plotly_chart(fig1)
        with col2:
            st.write("")
            st.write("")
            st.write("Éléments de prévision")
            fig2 = model.plot_components(forecast)
            st.write(fig2)

    #https://www.python-engineer.com/posts/stockprediction-app/

    st.markdown("""<style> .footer {
                                    position: fixed; left: 0; bottom: 0; width: 100%; background-color: rgb(38, 39, 48);
                                    color: white; text-align: right; padding: 30px 40px; z-index: 101;}
                                    .footer-cols {display: flex; justify-content: space-between;}
                                    .footer-col {flex: 1;text-align: center;border-right:solid rgb(14, 17, 23) 1px;}
                                    </style>""", unsafe_allow_html=True)
    st.markdown("""<style> .footer-p {font-size: 25px !important;font-weight: bold;}</style>""", unsafe_allow_html=True)

    st.markdown('<footer class="footer"><div class="footer-cols">'
                '<div class="footer-col">Disponible : <p class="footer-p">$' + str(round(capital_dispo, 2)) + '</p></div>'
                '<div class="footer-col">Investi : <p class="footer-p">$' + str(round(capital_investi, 2)) + '</p></div>'
                '<div class="footer-col">Capital : <p class="footer-p">$' + str(round(capital_total, 2)) + '</p></div>'
                '</div></footer>', unsafe_allow_html=True)