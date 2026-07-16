import streamlit as st
import plotly.graph_objects as go
import math
import unicodedata     # NOVÉ: Pro odstranění diakritiky
from fpdf import FPDF  # NOVÉ: Pro generování PDF
import io              # NOVÉ: Pro práci s daty v paměti
from datetime import datetime  # NOVÉ: Pro získání aktuálního data a času

# 1. Nastavení vzhledu aplikace
st.set_page_config(page_title="Modul pružnosti - Protokol", layout="centered")

# ==========================================
# INICIALIZACE PAMĚTI (State management)
# ==========================================
if 'krok' not in st.session_state:
    st.session_state.krok = 0

# --- Paměť pro Krok 1 ---
if 'jmeno' not in st.session_state:
    st.session_state.jmeno = ""
if 'spolupracovnik' not in st.session_state:
    st.session_state.spolupracovnik = ""
if 'skupina' not in st.session_state:
    st.session_state.skupina = ""
if 'tlak' not in st.session_state:
    st.session_state.tlak = "1013"
if 'teplota' not in st.session_state:
    st.session_state.teplota = "21.0"
if 'vlhkost' not in st.session_state:
    st.session_state.vlhkost = "50"

# --- Paměť pro Krok 2 ---
for i in range(1, 6):
    if f'd{i}' not in st.session_state:
        st.session_state[f'd{i}'] = "0.650"
if 'student_prumer' not in st.session_state:
    st.session_state.student_prumer = ""
if 'skutecny_prumer' not in st.session_state:
    st.session_state.skutecny_prumer = 0.0

# --- Paměť pro Krok 3 ---
if 'l0' not in st.session_state:
    st.session_state.l0 = "2.500"
if 'err_l0' not in st.session_state:
    st.session_state.err_l0 = "1.0" # Chyba délky l0 v milimetrech
    
hmotnosti = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5]
for h in hmotnosti:
    key = str(h).replace('.', '_')
    if f'zatez_{key}' not in st.session_state:
        st.session_state[f'zatez_{key}'] = "0.000" if h == 0.0 else ""
    if f'odleh_{key}' not in st.session_state:
        st.session_state[f'odleh_{key}'] = ""

# --- Paměť pro Krok 4 ---
if 'odhaleno' not in st.session_state:
    st.session_state.odhaleno = False
if 'a_skutecne' not in st.session_state:
    st.session_state.a_skutecne = 0.0
if 'err_a' not in st.session_state:
    st.session_state.err_a = 0.0 # Chyba směrnice    

# --- Paměť pro Krok 5 ---
if 'otazka_1' not in st.session_state:
    st.session_state.otazka_1 = ""
if 'otazka_2' not in st.session_state:
    st.session_state.otazka_2 = ""
if 'otazka_3' not in st.session_state:
    st.session_state.otazka_3 = ""
if 'zaver' not in st.session_state:
    st.session_state.zaver = ""

# Hlavní nadpis
st.title("Úloha 7.5: Stanovení modulu pružnosti")
st.markdown("---")

# ==========================================
# KROK 0: Vstupní test znalostí (NOVÉ)
# ==========================================
if st.session_state.krok == 0:
    st.header("Krok 0: Vstupní test znalostí")
    st.info("Před zahájením samotného měření musíte prokázat základní teoretické znalosti k této úloze. Pro odemčení protokolu odpovězte správně alespoň na 6 ze 7 otázek.")
    
    # Databáze otázek
    otazky = [
        {
            "q": "Které z následujících tvrzení nejlépe popisuje Hookův zákon pro tah v oblasti pružných deformací?",
            "opts": ["Prodloužení drátu je nepřímo úměrné působící síle.", "Normálové napětí je přímo úměrné relativnímu prodloužení materiálu.", "Modul pružnosti materiálu roste s rostoucím napětím.", "Deformace materiálu je trvalá a po odlehčení nezmizí."],
            "ans": "Normálové napětí je přímo úměrné relativnímu prodloužení materiálu."
        },
        {
            "q": "Jaká je základní fyzikální jednotka Youngova modulu pružnosti v tahu E v soustavě SI?",
            "opts": ["Newton (N)", "Newton na metr (N/m)", "Pascal (Pa)", "Jedná se o bezrozměrnou veličinu."],
            "ans": "Pascal (Pa)"
        },
        {
            "q": "Jak se vypočítá relativní (poměrné) prodloužení drátu?",
            "opts": ["Jako prostý rozdíl konečné a původní délky drátu.", "Jako podíl změny délky a původní délky drátu.", "Jako součin zatěžující síly a změny délky.", "Jako podíl původní délky a změny délky."],
            "ans": "Jako podíl změny délky a původní délky drátu."
        },
        {
            "q": "Ve vzorci pro výpočet modulu pružnosti figuruje průměr drátu d. S jakou mocninou se tento průměr ve vzorci nachází a proč?",
            "opts": ["V první mocnině (d), protože průměr je lineární rozměr.", "Ve druhé mocnině (d^2), protože napětí závisí na obsahu kruhového průřezu drátu.", "Ve třetí mocnině (d^3), protože modul pružnosti charakterizuje objemové vlastnosti tělesa.", "Průměr drátu ve vzorci vůbec nefiguruje."],
            "ans": "Ve druhé mocnině (d^2), protože napětí závisí na obsahu kruhového průřezu drátu."
        },
        {
            "q": "Která měřená veličina vnáší při experimentálním stanovení modulu pružnosti tenkého drátu do výsledku obvykle největší relativní chybu?",
            "opts": ["Hmotnost použitých závaží.", "Atmosférický tlak v laboratoři.", "Původní délka drátu.", "Průměr drátu."],
            "ans": "Průměr drátu."
        },
        {
            "q": "Proč se při laboratoři zaznamenává prodloužení drátu jak při postupném zatěžování, tak i při postupném odlehčování závažími?",
            "opts": ["Abychom získali více bodů do grafu a ušetřili čas.", "Aby se ověřilo, že nedošlo k překročení meze kluzu a k trvalé plastické deformaci drátu.", "Protože při odlehčování je modul pružnosti materiálů vždy vyšší.", "Jedná se pouze o kontrolu tření v kladce."],
            "ans": "Aby se ověřilo, že nedošlo k překročení meze kluzu a k trvalé plastické deformaci drátu."
        },
        {
            "q": "Co fyzikálně představuje směrnice (sklon) regresní přímky v grafu závislosti prodloužení na zatěžující síle F?",
            "opts": ["Pevnost drátu v tahu (mez pevnosti).", "Přímo samotný modul pružnosti materiálu E.", "Prodloužení drátu způsobené jednotkovou silou (např. 1 N).", "Plochu příčného průřezu drátu."],
            "ans": "Prodloužení drátu způsobené jednotkovou silou (např. 1 N)."
        }
    ]
    
    # Vykreslení otázek (index=None znamená, že není předem nic zakliknuto)
    odpovedi_studenta = []
    for i, otazka in enumerate(otazky):
        st.markdown(f"**{i+1}. {otazka['q']}**")
        vyber = st.radio(f"Otázka {i+1}", otazka['opts'], index=None, key=f"q_{i}", label_visibility="collapsed")
        odpovedi_studenta.append(vyber)
        st.write("---")
        
    # Vyhodnocení
    if st.button("Vyhodnotit kvíz a odemknout protokol"):
        if None in odpovedi_studenta:
            st.warning("⚠️ Před vyhodnocením musíte vybrat odpověď u všech 7 otázek!")
        else:
            skore = 0
            for i, odp in enumerate(odpovedi_studenta):
                if odp == otazky[i]['ans']:
                    skore += 1
                    
            if skore >= 6:
                st.success(f"🎉 Výborně! Máte {skore} ze 7 správně. Vaše teoretická příprava je dostatečná.")
                st.session_state.krok = 1
                st.rerun()
            else:
                st.error(f"❌ Zatím máte {skore} ze 7 správně. Pro odemčení protokolu potřebujete alespoň 6 bodů. Zamyslete se nad otázkami a zkuste to znovu.")

# ==========================================
# KROK 1: Identifikace a podmínky
# ==========================================
if st.session_state.krok == 1:
    st.header("Krok 1: Identifikační údaje")
    st.session_state.jmeno = st.text_input("Tvé jméno a příjmení", value=st.session_state.jmeno)
    st.session_state.spolupracovnik = st.text_input("Jméno spolupracovníka", value=st.session_state.spolupracovnik)
    st.session_state.skupina = st.text_input("Ročník / Skupina", value=st.session_state.skupina)
    
    st.header("Laboratorní podmínky")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.tlak = st.text_input("Tlak [hPa]", value=st.session_state.tlak)
    with col2:
        st.session_state.teplota = st.text_input("Teplota [°C]", value=st.session_state.teplota)
    with col3:
        st.session_state.vlhkost = st.text_input("Vlhkost [%]", value=st.session_state.vlhkost)
        
    st.markdown("---")
    if st.button("Uložit a pokračovat k měření průměru"):
        st.session_state.krok = 2
        st.rerun()

# ==========================================
# KROK 2: Měření průměru
# ==========================================
elif st.session_state.krok == 2:
    st.header("Krok 2: Měření průměru drátu")
    st.write("Změřte průměr drátu na 5 různých místech a hodnoty zapište v milimetrech:")
    
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.session_state[f'd{i+1}'] = st.text_input(f"d{i+1}", value=st.session_state[f'd{i+1}'])
            
    st.markdown("---")
    st.subheader("Ověření výpočtu")
    st.warning("⚠️ **Pozor:** Nezapomeňte svůj vypočtený průměr správně zaokrouhlit na **3 desetinná místa**!")
    st.session_state.student_prumer = st.text_input("Váš vypočtený průměr [mm]:", value=st.session_state.student_prumer)
    
    try:
        d_vals = [float(st.session_state[f'd{i}'].replace(',', '.')) for i in range(1, 6)]
        skutecny_prumer = sum(d_vals) / 5
        # Uložíme do paměti pro pozdější výpočet E
        st.session_state.skutecny_prumer = skutecny_prumer 
        
        if st.session_state.student_prumer.strip() != "":
            student_val = float(st.session_state.student_prumer.replace(',', '.'))
            
            if abs(student_val - skutecny_prumer) <= 0.0015:
                st.success("Trefa! Průměr máte vypočítaný i zaokrouhlený správně. 🔓 Protokol je odemčen.")
                # --- ZAČÁTEK NOVÉHO KÓDU PRO TECHNICKÝ ZÁPIS S EXPONENTEM ---
                # 1. Znovuvypočítání odchylek a chyb (v mm)
                odchylky = [abs(val - skutecny_prumer) for val in d_vals]
                prumerna_odchylka_mm = sum(odchylky) / 5
                relativni_chyba = (prumerna_odchylka_mm / skutecny_prumer) * 100
                
                # 2. Převod na základní SI jednotku (metry)
                prumer_m = skutecny_prumer * 1e-3
                odchylka_m = prumerna_odchylka_mm * 1e-3
                
                # 3. Určení společného exponentu (řádu) podle průměru
                if prumer_m > 0:
                    exponent = math.floor(math.log10(prumer_m))
                else:
                    exponent = 0
                    
                # 4. Přepočet hodnot na "základní" číslo před mocninou
                zaklad_prumer = prumer_m / (10**exponent)
                zaklad_odchylka = odchylka_m / (10**exponent)
                
                # 5. Nalezení první platné nenulové číslice pro zaokrouhlení odchylky (z upraveného základu)
                if zaklad_odchylka > 0:
                    pocet_mist = -math.floor(math.log10(zaklad_odchylka))
                    zaokrouhlena_odchylka = round(zaklad_odchylka, pocet_mist)
                    # Ošetření přetečení (např. 0.096 zaokrouhleno na 2 místa dá 0.10 -> posun řádu)
                    if zaokrouhlena_odchylka >= 10**(-(pocet_mist - 1)):
                        pocet_mist -= 1
                        zaokrouhlena_odchylka = round(zaklad_odchylka, pocet_mist)
                else:
                    pocet_mist = 2
                    zaokrouhlena_odchylka = 0.0
                    
                # Ošetření pro případ, že by počet míst vyšel záporný
                pocet_mist = max(0, pocet_mist)
                zaokrouhleny_prumer = round(zaklad_prumer, pocet_mist)
                
                # 6. Zobrazení v předepsaném technickém tvaru s mocninou 10
                st.write("**Výsledek měření (v základních jednotkách SI):**")
                
                # Vykreslení LaTex vzorce s dynamickým exponentem
                st.latex(rf"d = ({zaokrouhleny_prumer:.{pocet_mist}f} \pm {zaokrouhlena_odchylka:.{pocet_mist}f}) \cdot 10^{{{exponent}}} \text{{ m}} \quad \dots \quad {relativni_chyba:.2f} \text{{ \%}}")
                st.markdown("---")
                # --- KONEC NOVÉHO KÓDU ---
                
                
                if st.button("Pokračovat k zatěžování drátu (Krok 3)"):
                    st.session_state.krok = 3
                    st.rerun()
            else:
                st.error("Zatím to nevychází. Zkuste to přepočítat.")
    except ValueError:
        st.error("Zadejte prosím platná čísla.")
            
    st.markdown("---")
    if st.button("Zpět na Krok 1"):
        st.session_state.krok = 1
        st.rerun()

# ==========================================
# KROK 3: Zatěžování
# ==========================================
elif st.session_state.krok == 3:
    st.header("Krok 3: Namáhání drátu")
    st.write("Nejprve zadejte počáteční délku drátu $l_0$ a její chybu (zjistíte na vývěsce v laboratoři).")
    col_l0, col_err_l0 = st.columns(2)
    with col_l0:
        st.session_state.l0 = st.text_input("Původní délka drátu $l_0$ [m]:", value=st.session_state.l0)
    with col_err_l0:
        st.session_state.err_l0 = st.text_input("Chyba délky drátu $\Delta l_0$ [mm]:", value=st.session_state.err_l0)
        
    st.markdown("---")
    st.subheader("Tabulka prodloužení")
    
    c1, c2, c3, c4 = st.columns([1.5, 2.5, 2.5, 1.5])
    c1.markdown("**m (kg)**")
    c2.markdown("**Zatěž. $\Delta l_1$**(mm)")
    c3.markdown("**Odlehč. $\Delta l_2$**(mm)")
    c4.markdown("**Průměr**(mm)")
    
    vse_vyplneno = True
    
    for h in hmotnosti:
        key = str(h).replace('.', '_')
        c1, c2, c3, c4 = st.columns([1.5, 2.5, 2.5, 1.5])
        
        with c1:
            st.markdown(f"<div style='margin-top: 10px;'><b>{h}</b></div>", unsafe_allow_html=True)
        with c2:
            st.session_state[f'zatez_{key}'] = st.text_input(f"z_{key}", value=st.session_state[f'zatez_{key}'], label_visibility="collapsed")
        with c3:
            st.session_state[f'odleh_{key}'] = st.text_input(f"o_{key}", value=st.session_state[f'odleh_{key}'], label_visibility="collapsed")
        with c4:
            z_val_str = st.session_state[f'zatez_{key}'].replace(',', '.')
            o_val_str = st.session_state[f'odleh_{key}'].replace(',', '.')
            try:
                if z_val_str != "" and o_val_str != "":
                    prumer = (float(z_val_str) + float(o_val_str)) / 2
                    st.info(f"{prumer:.5f}")
                else:
                    st.write("...")
                    vse_vyplneno = False
            except ValueError:
                st.error("Chyba")
                vse_vyplneno = False
                
    st.markdown("---")
    col_back, col_fwd = st.columns(2)
    with col_back:
        if st.button("Zpět na Krok 2"):
            st.session_state.krok = 2
            st.rerun()
            
    with col_fwd:
        if vse_vyplneno:
            if st.button("Přejít na graf (Krok 4)"):
                st.session_state.krok = 4
                st.rerun()
        else:
            st.warning("Doplňte všechny hodnoty.")

# ==========================================
# KROK 4: Interaktivní graf
# ==========================================
elif st.session_state.krok == 4:
    st.header("Krok 4: Zpracování grafu")
    
    g_konst = 9.81
    sily_F = [m * g_konst for m in hmotnosti]
    
    prumerna_dl = []
    for h in hmotnosti:
        key = str(h).replace('.', '_')
        z_val = float(st.session_state[f'zatez_{key}'].replace(',', '.'))
        o_val = float(st.session_state[f'odleh_{key}'].replace(',', '.'))
        prumerna_dl.append((z_val + o_val) / 2)
        
    sum_xy = sum(f * dl for f, dl in zip(sily_F, prumerna_dl))
    sum_xx = sum(f**2 for f in sily_F)
    a_skutecne = sum_xy / sum_xx if sum_xx != 0 else 0
    st.session_state.a_skutecne = a_skutecne # Uložíme pro výpočet E
    
    # NOVÉ: Výpočet skutečné chyby směrnice a (z rozptylu reziduí)
    n = len(sily_F)
    if n > 1 and sum_xx != 0:
        suma_rezidui = sum((dl - a_skutecne * f)**2 for f, dl in zip(sily_F, prumerna_dl))
        rozptyl = suma_rezidui / (n - 1)
        err_a = math.sqrt(rozptyl / sum_xx)
    else:
        err_a = 0.0
    st.session_state.err_a = err_a
    
    st.info("Zkuste pomocí posuvníku natočit přímku tak, aby co nejlépe prokládala vaše body.")
    hruby_odhad = max(prumerna_dl) / max(sily_F) if max(sily_F) > 0 else 0.01
    
    a_odhad = st.slider("Vaše směrnice a (mm/N):", min_value=0.0, max_value=float(hruby_odhad * 2), value=float(hruby_odhad * 0.5), step=0.000001, format="%.6f")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sily_F, y=prumerna_dl, mode='markers', name='Vaše měření', marker=dict(size=10, color='red')))
    line_x = [0, max(sily_F)]
    line_y = [0, a_odhad * max(sily_F)]
    fig.add_trace(go.Scatter(x=line_x, y=line_y, mode='lines', name='Váš odhad přímky', line=dict(color='blue', width=3)))
    
    fig.update_layout(title="Závislost prodloužení drátu na síle", xaxis_title="Síla F [N]", yaxis_title="Prodloužení \Delta l [mm]", legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01), margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    if st.button("Odhalit výpočet metodou nejmenších čtverců"):
        st.session_state.odhaleno = True
        
    if st.session_state.odhaleno:
        st.markdown("### Porovnání metod a výpočet")
        
        # 1. Zobrazení výsledku z posuvníku
        st.write(f"**1. Grafická metoda (Váš vizuální odhad):**")
        st.write(f"$a_{{odhad}} = {a_odhad:.6f} \\text{{ mm/N}}$")
        
        # 2. Rozepsání metody nejmenších čtverců
        st.write("**2. Numerická metoda (Nejmenší čtverce):**")
        st.write("Pro přímku procházející počátkem ($y = ax$) se směrnice vypočítá vztahem:")
        
        # Vzorec v LaTeXu
        st.latex(r"a = \frac{\sum (F_i \cdot \Delta l_i)}{\sum F_i^2}")
        
        # Vzorec s dosazenými mezivýsledky (sumami)
        st.latex(rf"a = \frac{{{sum_xy:.4f}}}{{{sum_xx:.4f}}}")
        
        # Finální přesný výsledek
        st.success(f"Přesná hodnota směrnice: **$a = {a_skutecne:.6f} \\text{{ mm/N}}$**")
        
        # 3. Závěrečné zhodnocení s vysvětlující větou
        st.info("💡 **Závěr:** Grafická metoda (odhad z grafu) je skvělá pro rychlou kontrolu, ale není úplně přesná. Proto pro finální výpočet modulu pružnosti použijeme přesnější výsledek z numerické metody.")
        
        if st.button("Přejít na Závěr a Otázky (Krok 5)"):
            st.session_state.krok = 5
            st.rerun()
            
    st.markdown("---")
    if st.button("Zpět na Krok 3"):
        st.session_state.krok = 3
        st.rerun()

# ==========================================
# KROK 5: Finální výpočet a Zhodnocení
# ==========================================
elif st.session_state.krok == 5:
    st.header("Krok 5: Finále a výpočet chyby")
    
    # 1. Získání hodnot z paměti
    l0 = float(st.session_state.l0.replace(',', '.'))
    d_mm = st.session_state.skutecny_prumer
    a_mmn = st.session_state.a_skutecne
    
    # Převod na základní jednotky SI
    d_m = d_mm * 1e-3
    a_mn = a_mmn * 1e-3
    
    try:
        E_Pa = (4 * l0) / (math.pi * (d_m**2) * a_mn)
        E_GPa = E_Pa / 1e9
    except ZeroDivisionError:
        E_GPa = 0
        
    # --- ZOBRAZENÍ VZORCŮ A VÝSLEDKU E ---
    st.subheader("1. Výpočet modulu pružnosti $E$")
    st.write("Obecný definiční vzorec pro výpočet Youngova modulu pružnosti v tahu:")
    st.latex(r"E = \frac{4 l_0}{\pi d^2 a}")
    
    st.write("Po dosazení vašich zjištěných hodnot převedených na základní jednotky SI (metry, Newtony):")
    st.latex(rf"E = \frac{{4 \cdot {l0}}}{{\pi \cdot ({d_mm} \cdot 10^{{-3}})^2 \cdot {a_mmn:.5f} \cdot 10^{{-3}}}}")
    st.info(f"Předběžný výsledek: **E = {E_GPa:.2f} GPa**")
    
    # 1. Získání hodnot z paměti (doplněno o načtení chyb)
    l0 = float(st.session_state.l0.replace(',', '.'))
    err_l0_mm = float(st.session_state.err_l0.replace(',', '.')) # Zadáno z vývěsky
    
    d_mm = st.session_state.skutecny_prumer
    a_mmn = st.session_state.a_skutecne
    err_a_mmn = st.session_state.err_a # Skutečná chyba z regrese
    
    # Převod na základní jednotky SI
    d_m = d_mm * 1e-3
    a_mn = a_mmn * 1e-3
    
    try:
        E_Pa = (4 * l0) / (math.pi * (d_m**2) * a_mn)
        E_GPa = E_Pa / 1e9
    except ZeroDivisionError:
        E_GPa = 0
        
    # --- ZOBRAZENÍ VZORCŮ A VÝSLEDKU E ---
    st.subheader("1. Výpočet modulu pružnosti $E$")
    st.write("Obecný definiční vzorec pro výpočet Youngova modulu pružnosti v tahu:")
    st.latex(r"E = \frac{4 l_0}{\pi d^2 a}")
    
    st.write("Po dosazení vašich zjištěných hodnot převedených na základní jednotky SI (metry, Newtony):")
    st.latex(rf"E = \frac{{4 \cdot {l0}}}{{\pi \cdot ({d_mm} \cdot 10^{{-3}})^2 \cdot {a_mmn:.5f} \cdot 10^{{-3}}}}")
    st.info(f"Předběžný výsledek: **E = {E_GPa:.2f} GPa**")
    
    # --- VÝPOČET CELKOVÉ CHYBY ---
    st.subheader("2. Výpočet celkové chyby měření")
    st.write("Celková relativní chyba výsledku $\\delta_E$ se určí jako součet relativních chyb dílčích veličin. Všimněte si, že chyba průměru $d$ se díky mocnině ve jmenovateli násobí dvěma!")
    
    # Výpočet dílčích relativních chyb
    d_vals = [float(st.session_state[f'd{i}'].replace(',', '.')) for i in range(1, 6)]
    odchylka_d_mm = sum(abs(val - d_mm) for val in d_vals) / 5
    rel_d = odchylka_d_mm / d_mm if d_mm != 0 else 0
    
    # Dosazení reálných chyb
    rel_l0 = (err_l0_mm * 1e-3) / l0 if l0 != 0 else 0
    rel_a = err_a_mmn / a_mmn if a_mmn != 0 else 0
    
    rel_E = rel_l0 + (2 * rel_d) + rel_a
    abs_E_GPa = E_GPa * rel_E
    
    # Zobrazení postupu výpočtu chyby (s dosazenými konkrétními procenty)
    st.latex(r"\delta_E = \frac{\Delta l_0}{l_0} + 2\frac{\Delta d}{d} + \frac{\Delta a}{a}")
    st.latex(rf"\delta_E = {(rel_l0*100):.4f}\% + 2 \cdot {(rel_d*100):.4f}\% + {(rel_a*100):.4f}\% = {(rel_E*100):.2f}\%")
    
    st.write(f"Z této relativní chyby program vypočítal absolutní odchylku $\\Delta E = {abs_E_GPa:.2f} \\text{{ GPa}}$.")
    
    # --- FINÁLNÍ ZÁPIS PODLE PŘEDPISU ---
    if abs_E_GPa > 0:
        # 1. Zjistíme řád první nenulové číslice chyby
        rad = -math.floor(math.log10(abs_E_GPa))
        
        # 2. Zaokrouhlíme chybu na tuto první platnou číslici
        abs_E_zaokr = round(abs_E_GPa, rad)
        
        # 3. Ošetření "přetečení" (např. chyba 9.6 se zaokrouhlí na 10.0, čímž se jí změní řád)
        if abs_E_zaokr >= 10**(-(rad - 1)):
            rad -= 1
            abs_E_zaokr = round(abs_E_GPa, rad)
            
        # 4. Zaokrouhlíme samotný výsledek na stejný počet míst (na stejný řád) jako chybu
        E_zaokr = round(E_GPa, rad)
        
        # 5. Ošetření pro formátovaný výpis: 
        # Pokud je rad záporný (zaokrouhlujeme na desítky či stovky GPa), nesmíme chtít vypsat záporný počet desetinných míst
        format_rad = max(0, rad)
    else:
        abs_E_zaokr = 0.0
        E_zaokr = E_GPa
        format_rad = 1
        
    st.markdown("### Finální výsledek měření")
    
    st.write(r"Podle laboratorních pravidel zapisujeme výsledek v normovaném tvaru $X=(\overline{x}\pm\overline{\vartheta}(x))$:")
    
    st.success(f"$$E = ({E_zaokr:.{format_rad}f} \\pm {abs_E_zaokr:.{format_rad}f}) \\text{{ GPa}} \\quad \\dots \\quad {(rel_E*100):.1f} \\text{{ \\%}}$$")
    
    st.markdown("---")
    
    # --- FINÁLNÍ ZÁPIS PODLE PŘEDPISU ---
    # Zaokrouhlení odchylky na 1 platnou číslici
    if abs_E_GPa > 0:
        rad = -math.floor(math.log10(abs_E_GPa))
        if rad < 0: # Pokud je chyba > 10 GPa (např. 15 GPa), zaokrouhlíme na jednotky nebo desítky
            rad = 0 
        abs_E_zaokr = round(abs_E_GPa, rad)
        E_zaokr = round(E_GPa, rad)
    else:
        abs_E_zaokr = 0
        E_zaokr = E_GPa
        rad = 1
         
    st.markdown("---")
    st.subheader("3. Kontrolní otázky")
    st.info("Odpovězte na následující otázky, abyste prokázali pochopení úlohy.")
    
    st.session_state.otazka_1 = st.text_area("1. Jak se směrnice 'a' grafu změní, pokud bychom k měření použili ocelový drát o stejném složení a délce, ale s dvojnásobným průměrem?", value=st.session_state.otazka_1)
    st.session_state.otazka_2 = st.text_area("2. Proč je nutné měřit prodloužení drátu při zatěžování i postupném odlehčování? Co by znamenalo, kdyby se lišily?", value=st.session_state.otazka_2)
    st.session_state.otazka_3 = st.text_area("3. Jak by se na grafu projevilo, kdybyste drát zatížili silou, která by překročila mez úměrnosti materiálu?", value=st.session_state.otazka_3)
    
    st.markdown("---")
    st.subheader("Závěr")
    st.session_state.zaver = st.text_area("Zhodnoťte měření. Srovnejte váš výsledek s tabulkovou hodnotou (pro ocel cca 210 GPa) a zamyslete se nad zdroji chyb:", value=st.session_state.zaver)
    
    st.markdown("---")
    col_back, col_fwd = st.columns(2)
    
    with col_back:
        if st.button("Zpět na Krok 4"):
            st.session_state.krok = 4
            st.rerun()
            
    with col_fwd:
        # Nastavení minimálních limitů (můžeš si libovolně změnit)
        limit_otazky = 50
        limit_zaver = 100
        
        # Zjištění skutečné délky textu bez mezer na začátku a na konci
        delka_o1 = len(st.session_state.otazka_1.strip())
        delka_o2 = len(st.session_state.otazka_2.strip())
        delka_o3 = len(st.session_state.otazka_3.strip())
        delka_z = len(st.session_state.zaver.strip())
        
        # Kontrola, zda jsou všechny limity splněny
        if delka_o1 >= limit_otazky and delka_o2 >= limit_otazky and delka_o3 >= limit_otazky and delka_z >= limit_zaver:
            st.success("Všechny odpovědi jsou dostatečně podrobné.")
            if st.button("Ukončit a Odeslat protokol"):
                st.session_state.krok = 6
                st.rerun()
        else:
            # Pokud není splněno, tlačítko pro odeslání se neukáže a vypíše se dynamické varování
            st.warning("⚠️ Pro odeslání protokolu musíte odpovědět na všechny otázky a napsat závěr dostatečně podrobně.")
            
            # Vizuální nápověda pro studenty, kolik jim ještě chybí znaků
            if delka_o1 < limit_otazky: 
                st.write(f"- **Otázka 1:** {delka_o1}/{limit_otazky} znaků")
            if delka_o2 < limit_otazky: 
                st.write(f"- **Otázka 2:** {delka_o2}/{limit_otazky} znaků")
            if delka_o3 < limit_otazky: 
                st.write(f"- **Otázka 3:** {delka_o3}/{limit_otazky} znaků")
            if delka_z < limit_zaver: 
                st.write(f"- **Závěr:** {delka_z}/{limit_zaver} znaků")

# ==========================================
# KROK 6: Odeslání a generování PDF
# ==========================================
elif st.session_state.krok == 6:
    st.header("Krok 6: Generování a uložení protokolu 🎉")
    st.balloons()
    st.success(f"Všechny výpočty jsou hotové! Děkujeme za práci, {st.session_state.jmeno}.")
    
    # 1. Funkce pro odstranění diakritiky
    def bez_diakritiky(text):
        if not text:
            return ""
        return ''.join(c for c in unicodedata.normalize('NFD', str(text)) if unicodedata.category(c) != 'Mn')

    # 2. Extrakce příjmení pro název souboru
    jmeno_cele = st.session_state.jmeno.strip()
    kolega_cely = st.session_state.spolupracovnik.strip()
    
    prijmeni1 = bez_diakritiky(jmeno_cele.split(" ")[-1]) if jmeno_cele else "Student1"
    prijmeni2 = bez_diakritiky(kolega_cely.split(" ")[-1]) if kolega_cely else "Student2"
    
    nazev_souboru = f"{prijmeni1}_{prijmeni2}_Protokol_7-5.pdf"
    
    st.write(f"Váš soubor bude uložen jako: **{nazev_souboru}**")

    # 3. Získání aktuálního data a času
    aktualni_cas = datetime.now().strftime("%d. %m. %Y %H:%M:%S")
    
    # ---------------------------------------------------------
    # NOVÉ: Znovuvýpočet E a jeho chyby pro zápis do PDF
    # ---------------------------------------------------------
    l0_val = float(st.session_state.l0.replace(',', '.'))
    err_l0_val = float(st.session_state.err_l0.replace(',', '.'))
    d_mm_val = st.session_state.skutecny_prumer
    a_mmn_val = st.session_state.a_skutecne
    err_a_val = st.session_state.err_a
    
    # Převod na metry
    d_m_val = d_mm_val * 1e-3
    a_mn_val = a_mmn_val * 1e-3
    
    # Výpočet E
    try:
        E_Pa_val = (4 * l0_val) / (math.pi * (d_m_val**2) * a_mn_val)
        E_GPa_val = E_Pa_val / 1e9
    except ZeroDivisionError:
        E_GPa_val = 0
        
    # Výpočet celkové chyby
    d_vals_arr = [float(st.session_state[f'd{i}'].replace(',', '.')) for i in range(1, 6)]
    odchylka_d_val = sum(abs(v - d_mm_val) for v in d_vals_arr) / 5
    
    rel_d_val = odchylka_d_val / d_mm_val if d_mm_val != 0 else 0
    rel_l0_val = (err_l0_val * 1e-3) / l0_val if l0_val != 0 else 0
    rel_a_val = err_a_val / a_mmn_val if a_mmn_val != 0 else 0
    
    rel_E_val = rel_l0_val + (2 * rel_d_val) + rel_a_val
    abs_E_GPa_val = E_GPa_val * rel_E_val
    
    # Zaokrouhlení
    if abs_E_GPa_val > 0:
        rad_val = -math.floor(math.log10(abs_E_GPa_val))
        abs_E_zaokr_val = round(abs_E_GPa_val, rad_val)
        if abs_E_zaokr_val >= 10**(-(rad_val - 1)):
            rad_val -= 1
            abs_E_zaokr_val = round(abs_E_GPa_val, rad_val)
        E_zaokr_val = round(E_GPa_val, rad_val)
        format_rad_val = max(0, rad_val)
    else:
        abs_E_zaokr_val = 0.0
        E_zaokr_val = E_GPa_val
        format_rad_val = 1
        
    text_vysledek_E = f"{E_zaokr_val:.{format_rad_val}f} +/- {abs_E_zaokr_val:.{format_rad_val}f} GPa  (rel. chyba {rel_E_val*100:.1f} %)"
    # ---------------------------------------------------------

    # 4. Vytvoření PDF dokumentu v paměti
    pdf = FPDF()
    pdf.add_page()
    
    # Časové razítko (šedé, vpravo nahoře)
    pdf.set_font("helvetica", style="I", size=10)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 10, text=bez_diakritiky(f"Vygenerovano systemem: {aktualni_cas}"), new_x="LMARGIN", new_y="NEXT", align="R")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)
    
    # Pomocná funkce pro snadný zápis řádků
    def zapis_radek(text, font_style="", size=12):
        pdf.set_font("helvetica", style=font_style, size=size)
        pdf.cell(0, 10, text=bez_diakritiky(text), new_x="LMARGIN", new_y="NEXT")

    # Hlavička protokolu
    zapis_radek("PROTOKOL O MERENI - Uloha 7.5", "B", 16)
    zapis_radek(f"Vypracoval: {st.session_state.jmeno}")
    zapis_radek(f"Spolupracovnik: {st.session_state.spolupracovnik}")
    zapis_radek(f"Skupina: {st.session_state.skupina}")
    zapis_radek(f"Podminky: {st.session_state.tlak} hPa, {st.session_state.teplota} C, {st.session_state.vlhkost} %")
    pdf.ln(5)
    
    # Výsledky
    zapis_radek("HLAVNI VYSLEDKY", "B", 14)
    zapis_radek(f"Prumer dratu (d): {st.session_state.student_prumer} mm")
    zapis_radek(f"Puvodni delka (l0): {st.session_state.l0} m")
    zapis_radek(f"Smernice z regrese (a): {st.session_state.a_skutecne:.5f} mm/N")
    
    # NOVÉ: Přidání výsledného modulu E do PDF
    pdf.ln(2)
    zapis_radek(f"MODUL PRUZNOSTI (E): {text_vysledek_E}", "B", 12)
    pdf.ln(5)
    
    # Otázky a závěr
    zapis_radek("ODPOVEDI A ZAVER", "B", 14)
    
    zapis_radek("Otazka 1:", "B", 12)
    pdf.set_font("helvetica", size=12)
    pdf.multi_cell(0, 8, text=bez_diakritiky(st.session_state.otazka_1))
    pdf.ln(2)
    
    zapis_radek("Otazka 2:", "B", 12)
    pdf.set_font("helvetica", size=12)
    pdf.multi_cell(0, 8, text=bez_diakritiky(st.session_state.otazka_2))
    pdf.ln(2)
    
    zapis_radek("Otazka 3:", "B", 12)
    pdf.set_font("helvetica", size=12)
    pdf.multi_cell(0, 8, text=bez_diakritiky(st.session_state.otazka_3))
    pdf.ln(2)
    
    zapis_radek("Zaver:", "B", 12)
    pdf.set_font("helvetica", size=12)
    pdf.multi_cell(0, 8, text=bez_diakritiky(st.session_state.zaver))

    # 5. Vygenerování PDF a předání do stahovacího tlačítka
    pdf_bytes = bytes(pdf.output())
    
    st.markdown("---")
    st.download_button(
        label="📄 Stáhnout protokol v PDF",
        data=pdf_bytes,
        file_name=nazev_souboru,
        mime="application/pdf"
    )
    
    st.markdown("---")
    if st.button("Zpět na úpravu protokolu (Krok 5)"):
        st.session_state.krok = 5
        st.rerun()