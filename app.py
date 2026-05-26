# --- IMPORTURILE ---
# Streamlit este framework-ul principal folosit pentru crearea interfeței web (UI)
import streamlit as st
# Pandas este folosit pentru lucrul cu tabele de date (citire, scriere, procesare CSV)
import pandas as pd
# Plotly Express este o librărie pentru crearea de grafice interactive
import plotly.express as px
# OS (Operating System) ne ajută să verificăm dacă fișierele există deja pe disc
import os
# Datetime ne ajută să lucrăm cu data și ora curentă
from datetime import datetime
# Relativedelta ne permite să adăugăm sau să scădem luni din data curentă (pentru simulator)
from dateutil.relativedelta import relativedelta

# --- 1. CONFIGURARE UI (Interfața cu Utilizatorul) ---
# Setăm titlul paginii (vizibil în tab-ul browserului), iconița și alinierea centrală a conținutului
st.set_page_config(page_title="EcoSmart Ultimate", page_icon="📊", layout="centered")

# Folosim HTML și CSS pentru a stiliza aplicația și a o face să arate modern
# 'unsafe_allow_html=True' îi permite lui Streamlit să randeze codul HTML, nu doar text simplu
st.markdown("""
    <style>
    /* Schimbăm culoarea de fundal a întregii aplicații */
    .stApp { background-color: #f8fafc; }
    /* Limităm lățimea conținutului pentru a arăta bine pe ecrane mari */
    section.main > div { max-width: 500px; margin: auto; padding: 1rem; }
    /* Setăm fontul și culoarea textului peste tot în aplicație */
    html, body, [data-testid="stWidgetLabel"], .stMarkdown p, h1, h2, h3, h4, span, label { 
        color: #1e293b !important; font-family: 'Inter', sans-serif; 
    }
    /* Creăm o clasă CSS personalizată 'card' pentru a pune elementele în "cutii" cu umbră */
    .card { background: white; padding: 20px; border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 15px; border: 1px solid #e2e8f0; }
    /* Stilizăm butoanele standard din Streamlit să fie albastre, mari și cu margini rotunjite */
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5rem; background-color: #2563eb !important; color: white !important; font-weight: 700; }
    /* Stilizăm special textul pentru prețuri (verde, îngroșat) */
    .price-tag { color: #16a34a; font-weight: bold; font-size: 1.4rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATE ȘI TARIFE (Variabile Globale) ---
USER_DB = "utilizatori.csv"  # Fișierul unde salvăm conturile
DATA_DB = "date_consum.csv"  # Fișierul unde salvăm indexurile lunare
PRET_KWH = 1.80  # Prețul energiei
PRET_MC = 8.50  # Prețul apei


# Funcție pentru a ne asigura că fișierele CSV există
def init_dbs():
    # Dacă fișierul utilizatori nu există, îl creăm gol, doar cu coloanele (capul de tabel)
    if not os.path.exists(USER_DB):
        pd.DataFrame(columns=["user", "password"]).to_csv(USER_DB, index=False)
    # La fel facem și pentru datele de consum
    if not os.path.exists(DATA_DB):
        pd.DataFrame(columns=["data", "user", "index_en", "index_wa"]).to_csv(DATA_DB, index=False)


# Apelăm funcția de mai sus la fiecare rulare a aplicației
init_dbs()

# --- INITIALIZARE SESSION STATE ---
# Streamlit se re-rulează complet de fiecare dată când apeși un buton.
# 'st.session_state' este "memoria" aplicației. Aici salvăm variabile care nu vrem să se șteargă la re-rulare.
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False  # Inițial, utilizatorul nu este logat
if 'month_offset' not in st.session_state:
    st.session_state.month_offset = 0  # Offset-ul pentru simulatorul de timp pornește de la 0

# --- 3. LOGIN & INREGISTRARE ---
# Dacă utilizatorul NU este logat, afișăm meniul de autentificare
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🌱 VGA Smart</h1>", unsafe_allow_html=True)

    # Creăm două tab-uri vizuale
    auth = st.tabs(["🔐 Conectare", "✍️ Cont Nou"])

    # --- TAB-UL 1: CONECTARE ---
    with auth[0]:
        u = st.text_input("User")  # Câmp pentru introducerea numelui
        p = st.text_input("Parolă", type="password")  # type="password" ascunde caracterele

        # Dacă se apasă butonul LOGARE
        if st.button("LOGARE"):
            # Citim tabelul de utilizatori din CSV și îl transformăm tot în text (string)
            df_u = pd.read_csv(USER_DB).astype(str)
            # Verificăm dacă există vreun rând unde userul și parola se potrivesc cu ce s-a introdus
            if ((df_u['user'].str.strip() == u.strip()) & (df_u['password'].str.strip() == p.strip())).any():
                st.session_state.logged_in = True  # Salvăm în memorie că este logat
                st.session_state.username = u.strip()  # Salvăm numele pentru a-l folosi mai târziu
                st.rerun()  # Reîncărcăm pagina pentru a dispărea ecranul de login și a apărea Dashboard-ul
            else:
                st.error("Date incorecte!")  # Afișăm o eroare cu roșu

    # --- TAB-UL 2: CONT NOU ---
    with auth[1]:
        nu = st.text_input("User Nou")
        np = st.text_input("Parolă Nouă", type="password")

        # Dacă se apasă CREEAZĂ CONT
        if st.button("CREEAZĂ CONT"):
            # Creăm un mic dataframe cu noul user și parolă și îl atașăm (mode='a' - append) la CSV-ul existent
            pd.DataFrame([[nu.strip(), np.strip()]], columns=["user", "password"]).to_csv(USER_DB, mode='a',
                                                                                          header=False, index=False)
            st.success("Cont creat! Acum te poți conecta.")

# --- 4. DASHBOARD (Aplicația principală) ---
# Dacă utilizatorul ESTE logat, intrăm pe ramura asta
else:
    # Setăm bara laterală (meniul din stânga)
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.username}")  # Salutăm utilizatorul
        st.divider()  # Tragem o linie despărțitoare
        st.subheader("⏳ Simulator Timp")

        # --- LOGICA SIMULATORULUI DE TIMP ---
        # Calculăm data simulată: Data de azi + (plus sau minus) un număr de luni (month_offset)
        dt_sim = datetime.now() + relativedelta(months=st.session_state.month_offset)
        txt_luna = dt_sim.strftime("%B %Y")  # Formatăm data frumos ex: "May 2026"
        key_luna = dt_sim.strftime("%Y-%m")  # Format folosit pentru baza de date ex: "2026-05"
        anul_sel = dt_sim.year  # Extragem doar anul

        # Punem butoanele de simulator unul lângă altul pe 2 coloane
        c_p, c_n = st.columns(2)
        with c_p:
            if st.button("◀️"):
                st.session_state.month_offset -= 1  # Scădem o lună
                st.rerun()  # Rulăm din nou ca să se actualizeze ecranul
        with c_n:
            if st.button("▶️"):
                st.session_state.month_offset += 1  # Adăugăm o lună
                st.rerun()

        st.info(f"Luna Curentă Simulată:\n**{txt_luna}**")
        st.divider()
        st.caption(f"⚡ Tarif E: {PRET_KWH} RON | 💧 Tarif W: {PRET_MC} RON")

        # Buton util pentru a curăța tabela de date (doar pentru prezentare la facultate)
        if st.button("🗑️ Resetare Istoric Demo"):
            # Rescriem fișierul CSV cu un tabel gol, lăsând doar coloanele
            pd.DataFrame(columns=["data", "user", "index_en", "index_wa"]).to_csv(DATA_DB, index=False)
            st.success("Istoric șters!")
            st.rerun()

        # Butonul de Logout curăță datele din sesiune
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.month_offset = 0
            st.rerun()

    # --- TITLUL PRINCIPAL ---
    st.markdown(f'<h2 style="text-align: center;">EcoMonitor {anul_sel}</h2>', unsafe_allow_html=True)

    # Creăm 3 tab-uri pentru funcționalitățile aplicației
    tabs = st.tabs(["📥 Index", "📈 Grafice Consum", "📑 Analiză & Costuri"])

    # --- TAB 1: INTRODUCERE DATE ---
    with tabs[0]:
        # Citim tot CSV-ul cu consum și filtrăm doar datele utilizatorului curent
        df_d = pd.read_csv(DATA_DB)
        user_hist = df_d[df_d['user'] == st.session_state.username].copy()

        # Verificăm dacă utilizatorul a introdus deja date pentru luna simulată
        # str.startswith caută dacă există vreo dată care începe cu "2026-05" de exemplu
        deja = not user_hist[user_hist['data'].str.startswith(key_luna)].empty

        # Căutăm cel mai mare index introdus până acum ca să îl setăm ca valoare minimă în formular
        max_e = user_hist['index_en'].max() if not user_hist.empty else 0.0
        max_w = user_hist['index_wa'].max() if not user_hist.empty else 0.0

        if deja:
            # Dacă luna e deja în baza de date, blocăm introducerea altor date pentru luna respectivă
            st.success(f"💡 Indexul pentru {txt_luna} este deja înregistrat.")
        else:
            # Dacă nu are istoric deloc, îl anunțăm că prima lună e doar de setare a bazei
            if user_hist.empty:
                st.info(
                    "ℹ️ Prima înregistrare reprezintă indexul de bază. Consumul se va calcula începând cu luna următoare.")

            st.write(f"Raportare: **{txt_luna}**")

            # Formular pentru Energie
            st.markdown(f'<div class="card">⚡ Energie (kWh) - Ultimul index: {max_e}</div>', unsafe_allow_html=True)
            e_in = st.number_input("E", min_value=0.0, value=float(max_e), step=1.0, label_visibility="collapsed")

            # Formular pentru Apă
            st.markdown(f'<div class="card">💧 Apă (mc) - Ultimul index: {max_w}</div>', unsafe_allow_html=True)
            w_in = st.number_input("W", min_value=0.0, value=float(max_w), step=0.1, label_visibility="collapsed")

            # Validare: Nu poți avea un index mai mic decât cel anterior (apometrele nu dau înapoi)
            if e_in < max_e or w_in < max_w:
                st.error("Noul index nu poate fi mai mic decât cel anterior!")
            elif st.button("SALVEAZĂ DATE"):
                # Salvăm noile date în CSV folosind mode='a' (append)
                pd.DataFrame([[f"{key_luna}-01", st.session_state.username, e_in, w_in]],
                             columns=["data", "user", "index_en", "index_wa"]).to_csv(DATA_DB, mode='a', header=False,
                                                                                      index=False)
                st.balloons()  # Animație de succes specifică Streamlit
                st.rerun()

    # --- PROCESAREA DATELOR (Inima logică a aplicației) ---
    df_all = pd.read_csv(DATA_DB)
    my_df = df_all[df_all['user'] == st.session_state.username].copy()

    if not my_df.empty:
        # Transformăm coloana 'data' din text în obiect de tip Datetime pentru a putea sorta și extrage luna/anul
        my_df['data'] = pd.to_datetime(my_df['data'])
        # Sortăm cronologic. Este esențial în cazul în care cu simulatorul am introdus date din trecut/viitor amestecat
        my_df = my_df.sort_values('data')

        # 'diff()' scade valoarea de pe rândul anterior din valoarea de pe rândul curent
        # Așa aflăm CÂT am consumat într-o lună (Indexul actual - Indexul trecut).
        # 'fillna(0)' înlocuiește rezultatul gol (NaN) al primei luni cu 0.
        my_df['Consum_E'] = my_df['index_en'].diff().fillna(0)
        my_df['Consum_W'] = my_df['index_wa'].diff().fillna(0)

        # O extra securitate ca să nu avem consum negativ
        my_df.loc[my_df['Consum_E'] < 0, 'Consum_E'] = 0
        my_df.loc[my_df['Consum_W'] < 0, 'Consum_W'] = 0

        # Calculăm costul total pe rândul respectiv
        my_df['Cost_Total'] = (my_df['Consum_E'] * PRET_KWH) + (my_df['Consum_W'] * PRET_MC)

        # Creăm o listă cu toate cele 12 luni ale anului curent (pentru grafice)
        luni_full = pd.date_range(start=f"{anul_sel}-01-01", end=f"{anul_sel}-12-01", freq='MS')

        # Îmbinăm lista de luni pline cu datele noastre (Left Join).
        # Asta asigură că și lunile viitoare fără date apar în grafic (dar goale).
        plot_df = pd.merge(pd.DataFrame({'data': luni_full}), my_df[my_df['data'].dt.year == anul_sel], on='data',
                           how='left')
        plot_df['Luna_Nume'] = plot_df['data'].dt.strftime('%b')  # Extragem numele scurt (Jan, Feb...)

        # Definim ordinea pe care o vom impune graficelor (să nu le ordoneze alfabetic: Apr, Aug, Dec, Feb...)
        luni_ord = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        # --- TAB 2: GRAFICE ---
        with tabs[1]:
            # Construim graficul cu coloane pentru Energie
            fig_e = px.bar(plot_df, x='Luna_Nume', y='Consum_E', title="⚡ Energie (kWh)",
                           color_discrete_sequence=['#f59e0b'], text_auto='.0f')
            # Setăm ordinea lunilor și facem fundalul transparent
            fig_e.update_layout(xaxis={'categoryorder': 'array', 'categoryarray': luni_ord},
                                plot_bgcolor='rgba(0,0,0,0)')
            # Afișăm graficul în pagină
            st.plotly_chart(fig_e, use_container_width=True)

            # Similar pentru Apă
            fig_w = px.bar(plot_df, x='Luna_Nume', y='Consum_W', title="💧 Apă (mc)",
                           color_discrete_sequence=['#3b82f6'], text_auto='.1f')
            fig_w.update_layout(xaxis={'categoryorder': 'array', 'categoryarray': luni_ord},
                                plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_w, use_container_width=True)

        # --- TAB 3: ANALIZĂ AVANSATĂ ---
        with tabs[2]:
            st.subheader("🧐 Raport Detaliat")

            # Dacă avem un singur rând, înseamnă că e prima lună înregistrată (nu se poate calcula consum/cost)
            if len(my_df) == 1:
                st.info(
                    "Aceasta este luna de instalare (index de pornire). Analiza de cost va fi disponibilă luna viitoare.")

            # Dacă avem 2 sau mai multe rânduri, putem compara ultima lună cu cea precedentă
            if len(my_df) >= 2:
                ultima = my_df.iloc[-1]  # Extragem ultimul rând din tabel
                trecut = my_df.iloc[-2]  # Extragem penultimul rând din tabel

                # Afișăm factura totală
                st.markdown(
                    f'<div class="card">Factură estimată pentru {ultima["data"].strftime("%B")}:<br><span class="price-tag">{ultima["Cost_Total"]:.2f} RON</span></div>',
                    unsafe_allow_html=True)


                # Funcție pentru a calcula diferența procentuală dintre două valori (Curent vs Trecut)
                def get_delta(a, t): return ((a - t) / t * 100) if t > 0 else 0


                de = get_delta(ultima['Consum_E'], trecut['Consum_E'])
                dw = get_delta(ultima['Consum_W'], trecut['Consum_W'])
                dc = ultima['Cost_Total'] - trecut['Cost_Total']  # Diferența valorică la bani

                # st.columns ne permite să afișăm elemente unele lângă altele
                c1, c2 = st.columns(2)
                # st.metric este perfect pentru a afișa un KPI și săgeata roșie/verde pentru evoluție
                c1.metric("Energie (kWh)", f"{ultima['Consum_E']:.0f}", f"{de:+.1f}%")
                c2.metric("Apă (mc)", f"{ultima['Consum_W']:.1f}", f"{dw:+.1f}%")

                # Afișăm o mică concluzie de preț
                st.write(
                    f"💵 Factura este cu **{abs(dc):.2f} RON** {'mai mare' if dc > 0 else 'mai mică'} decât luna precedentă.")

            st.divider()

            # --- MEDII ȘI RECORDURI ---
            # Nu luăm în calcul prima lună (indexul 0) pentru calcularea mediilor, altfel ar trage media în jos
            valid_rows = my_df.iloc[1:]

            # Verificăm dacă avem date valide pentru a calcula o medie
            if not valid_rows.empty and valid_rows['Consum_E'].sum() > 0:
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write("**⚡ ENERGIE**")
                    # Calculăm media folosind .mean() pe toată coloana
                    st.write(f"Medie: `{valid_rows['Consum_E'].mean():.1f} kWh`")
                    # Găsim luna în care a fost cel mai mare consum folosind .idxmax() (index of max)
                    top_e = valid_rows.loc[valid_rows['Consum_E'].idxmax()]
                    st.write(f"Peak: `{top_e['Consum_E']:.0f} kWh` ({top_e['data'].strftime('%b')})")
                with col_b:
                    st.write("**💧 APĂ**")
                    st.write(f"Medie: `{valid_rows['Consum_W'].mean():.1f} mc`")
                    top_w = valid_rows.loc[valid_rows['Consum_W'].idxmax()]
                    st.write(f"Peak: `{top_w['Consum_W']:.1f} mc` ({top_w['data'].strftime('%b')})")

                st.write("")
                # Extragem totalul banilor cheltuiți doar în anul selectat curent
                st.write(
                    f"💰 **Total Anual Cheltuit ({anul_sel}):** `{my_df[my_df['data'].dt.year == anul_sel]['Cost_Total'].sum():.2f} RON`")

                # --- GRAFIC EVOLUȚIE COSTURI ---
                st.divider()
                # Creăm un grafic cu linii (px.line) pentru a vedea evoluția facturilor
                fig_cost = px.line(plot_df, x='Luna_Nume', y='Cost_Total', title="📈 Evoluție Buget (RON)", markers=True,
                                   color_discrete_sequence=['#16a34a'])
                fig_cost.update_layout(xaxis={'categoryorder': 'array', 'categoryarray': luni_ord},
                                       plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_cost, use_container_width=True)

    else:
        # Dacă tabelul utilizatorului este gol (nu a introdus niciodată un index)
        st.info("ℹ️ Adaugă date pentru a genera analizele.")