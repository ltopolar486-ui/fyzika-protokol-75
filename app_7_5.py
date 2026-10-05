import streamlit as st
import plotly.graph_objects as go
import math
import unicodedata     # NOVÉ: Pro odstranění diakritiky
from fpdf import FPDF  # NOVÉ: Pro generování PDF
from datetime import datetime  # NOVÉ: Pro získání aktuálního data a času
import io  # NOVÉ: Pro držení obrázku grafu v paměti
import matplotlib.pyplot as plt # NOVÉ: Spolehlivá knihovna pro vyfocení grafu do PDF

# 1. Nastavení vzhledu aplikace
st.set_page_config(page_title="7.5 Modul pružnosti v tahu přímou metodou", layout="centered")

# ==========================================
# VLASTNÍ CSS PRO ZMENŠENÍ PÍSMA A POLÍ
# ==========================================
st.markdown("""
    <style>
        /* Zmenšení běžného textu a odstavců (bez narušení LaTeX vzorců) */
        html, body, p {
            font-size: 16px !important;
        }
        
        /* Zmenšení textu u popisků vstupních polí (např. Jméno, Tlak...) */
        .stTextInput label, .stNumberInput label {
            font-size: 16px !important;
        }
        
        /* Zmenšení textu uvnitř samotných políček a zmenšení jejich "nafouknutí" */
        input {
            font-size: 16px !important;
            padding: 8px 10px !important;
            text-align: center !important;
        }
        
        /* Úprava velikosti nadpisů, aby nezabíraly půl obrazovky */
        h1 {
            font-size: 24px !important;
            padding-bottom: 10px !important;
        }
        h2 {
            font-size: 18px !important;
            padding-bottom: 8px !important;
        }
        h3 {
            font-size: 16px !important;
        }
        
        /* Drobná horní vycpávka, aby se exponenty do rámečku s jistotou vešly */
        .katex-display {
            padding-top: 0.5em !important;
        }
    </style>
""", unsafe_allow_html=True)

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
        st.session_state[f'd{i}'] = ""
if 'student_prumer' not in st.session_state:
    st.session_state.student_prumer = ""
if 'skutecny_prumer' not in st.session_state:
    st.session_state.skutecny_prumer = 0.0

# --- Paměť pro Krok 3 ---
if 'l0' not in st.session_state:
    st.session_state.l0 = ""
if 'err_l0' not in st.session_state:
    st.session_state.err_l0 = "" # Chyba délky l0 v milimetrech
    
hmotnosti = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5]
for h in hmotnosti:
    key = str(h).replace('.', '_')
    if f'zatez_{key}' not in st.session_state:
        st.session_state[f'zatez_{key}'] = "" 
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
st.title("Úloha 7.5: Stanovení modulu pružnosti v tahu přímou metodou")
st.markdown("---")

# ==========================================
# KROK 0: Vstupní test znalostí (NOVÉ)
# ==========================================
if st.session_state.krok == 0:
    st.header("Krok 0: Vstupní test znalostí")
    st.info("Před zahájením samotného měření musíte prokázat základní teoretické znalosti k této úloze. Pro odemčení protokolu odpovězte správně alespoň na 6 ze 7 otázek.")
    
    # --- 1. NATAŽENÍ DATABÁZE A LOSOVÁNÍ (do paměti) ---
    if 'vybrane_otazky' not in st.session_state:
        import random
        
        # Kompletní zásobník 21 otázek
        databaze_otazek = [
            # Okruh 1: Hookův zákon a modul pružnosti
            {
                "okruh": 1,
                "q": "Jak zní Hookův zákon pro tah zapsaný pomocí normálového napětí σ a relativního prodloužení ε?",
                "opts": ["σ = ε / E", "σ = E · ε", "σ = E + ε", "σ = E · ε²"],
                "ans": "σ = E · ε"
            },
            {
                "okruh": 1,
                "q": "Proč má modul pružnosti E stejnou jednotku jako napětí?",
                "opts": ["Protože modul pružnosti je definován jako síla působící na jednotku délky drátu.", "Protože prodloužení drátu se měří v metrech.", "Protože relativní prodloužení ε je bezrozměrná veličina.", "Shoda jednotek je náhodná a nemá fyzikální důvod."],
                "ans": "Protože relativní prodloužení ε je bezrozměrná veličina."
            },
            {
                "okruh": 1,
                "q": "Jak se změní modul pružnosti E, změříme-li drát ze stejného materiálu, ale s dvojnásobnou délkou a dvojnásobným průměrem?",
                "opts": ["Zdvojnásobí se.", "Zmenší se na polovinu.", "Zčtyřnásobí se.", "Nezmění se, protože modul pružnosti je materiálová konstanta."],
                "ans": "Nezmění se, protože modul pružnosti je materiálová konstanta."
            },
            # Okruh 2: Meze a druhy deformací, smysl odlehčovací řady
            {
                "okruh": 2,
                "q": "Co platí pro deformaci drátu, dokud napětí nepřekročí mez pružnosti?",
                "opts": ["Deformace je vratná – po odlehčení zcela vymizí.", "Deformace je trvalá, ale nepřesahuje setiny milimetru.", "Drát se prodlužuje i bez dalšího zvyšování zatížení.", "Prodloužení je nepřímo úměrné působící síle."],
                "ans": "Deformace je vratná – po odlehčení zcela vymizí."
            },
            {
                "okruh": 2,
                "q": "Co nastane po překročení meze kluzu?",
                "opts": ["Drát se okamžitě přetrhne.", "Vzniká trvalá (plastická) deformace, která po odlehčení nezmizí.", "Modul pružnosti materiálu se zdvojnásobí.", "Prodloužení drátu přestane záviset na zatížení."],
                "ans": "Vzniká trvalá (plastická) deformace, která po odlehčení nezmizí."
            },
            {
                "okruh": 2,
                "q": "Podle čeho během měření poznáte, že drát zůstal v oblasti pružných deformací?",
                "opts": ["Při zatěžování se ručička indikátorových hodinek pohybuje stále rychleji.", "Prodloužení při posledním závaží je větší než 1 mm.", "Mikrometr ukáže po zatížení větší průměr drátu než před ním.", "Po úplném odlehčení se ručička indikátorových hodinek vrátí (v rámci přesnosti odečtu) na počáteční údaj."],
                "ans": "Po úplném odlehčení se ručička indikátorových hodinek vrátí (v rámci přesnosti odečtu) na počáteční údaj."
            },
            # Okruh 3: Napětí, průřez a odvození vztahu pro E
            {
                "okruh": 3,
                "q": "Který vztah pro výpočet modulu pružnosti E je uveden v návodu (a = Δl / F)?",
                "opts": ["E = π·d²·a / (4·l₀)", "E = 4·l₀ / (π·d²·a)", "E = 4·l₀·a / (π·d²)", "E = 4·l₀ / (π·d·a)"],
                "ans": "E = 4·l₀ / (π·d²·a)"
            },
            {
                "okruh": 3,
                "q": "Jak se při stejné zatěžující síle změní prodloužení drátu ze stejného materiálu a stejné délky, má-li dvojnásobný průměr?",
                "opts": ["Bude dvakrát menší.", "Bude dvakrát větší.", "Bude čtyřikrát menší.", "Nezmění se."],
                "ans": "Bude čtyřikrát menší."
            },
            {
                "okruh": 3,
                "q": "Co označuje veličina S ve vztahu pro napětí σ = F / S?",
                "opts": ["Obvod průřezu drátu, S = π·d.", "Povrch pláště drátu, S = π·d·l₀.", "Obsah příčného průřezu drátu, S = π·d².", "Obsah příčného průřezu drátu, S = π·d² / 4."],
                "ans": "Obsah příčného průřezu drátu, S = π·d² / 4."
            },
            # Okruh 4: Směrnice a, graf Δl = f(F)
            {
                "okruh": 4,
                "q": "Jakou jednotku má směrnice a = Δl / F?",
                "opts": ["m·N⁻¹ (v praxi mm·N⁻¹)", "N·m⁻¹", "Pa", "Je bezrozměrná."],
                "ans": "m·N⁻¹ (v praxi mm·N⁻¹)"
            },
            {
                "okruh": 4,
                "q": "Jak souvisí sklon přímky v grafu Δl = f(F) s modulem pružnosti E při stejných rozměrech drátu?",
                "opts": ["Čím větší sklon, tím větší modul pružnosti E.", "Sklon přímky je přímo roven modulu pružnosti E.", "Čím menší sklon (směrnice a), tím větší modul pružnosti E.", "Sklon přímky na modulu pružnosti nezávisí."],
                "ans": "Čím menší sklon (směrnice a), tím větší modul pružnosti E."
            },
            {
                "okruh": 4,
                "q": "Jak by se v grafu Δl = f(F) projevilo překročení meze úměrnosti?",
                "opts": ["Přímka by procházela přesně počátkem souřadnic.", "Směrnice přímky by vyšla záporná.", "Na grafu by se to neprojevilo, změnil by se jen průměr drátu.", "Naměřené body by se odchylovaly od přímky."],
                "ans": "Naměřené body by se odchylovaly od přímky."
            },
            # Okruh 5: Chyby měření
            {
                "okruh": 5,
                "q": "Proč se relativní chyba průměru drátu uplatní ve výsledné relativní chybě modulu pružnosti dvojnásobně?",
                "opts": ["Protože se průměr měří ve dvou na sebe kolmých směrech.", "Protože průměr d vystupuje ve vztahu pro E ve druhé mocnině.", "Protože se měří při zatěžování i při odlehčování.", "Protože mikrometr odečítá na dvě desetinná místa."],
                "ans": "Protože průměr d vystupuje ve vztahu pro E ve druhé mocnině."
            },
            {
                "okruh": 5,
                "q": "Relativní chyba průměru drátu je 1 %. Jak velkou relativní chybou se tato nepřesnost promítne do modulu pružnosti E?",
                "opts": ["0,5 %", "1 %", "2 %", "4 %"],
                "ans": "2 %"
            },
            {
                "okruh": 5,
                "q": "Relativní chyby kterých veličin se podle návodu skládají do relativní chyby modulu pružnosti E?",
                "opts": ["Délky drátu l₀, průměru drátu d a čísla π.", "Délky drátu l₀, průměru drátu d a směrnice a.", "Pouze průměru drátu d.", "Tíhového zrychlení g, atmosférického tlaku a teploty v laboratoři."],
                "ans": "Délky drátu l₀, průměru drátu d a směrnice a."
            },
            # Okruh 6: Postup měření
            {
                "okruh": 6,
                "q": "Jak se podle návodu správně měří průměr drátu d?",
                "opts": ["Opakovaně na různých místech podél drátu a v různých směrech, s odhadem tisícin milimetru.", "Jednou uprostřed drátu, s přesností na desetiny milimetru.", "Opakovaně na stále stejném místě, aby se vyloučil vliv nerovnoměrnosti drátu.", "Průměr se neměří, je uveden na vývěsce v laboratoři."],
                "ans": "Opakovaně na různých místech podél drátu a v různých směrech, s odhadem tisícin milimetru."
            },
            {
                "okruh": 6,
                "q": "Jak se při měření průměru drátu dotahuje měřicí šroub mikrometru?",
                "opts": ["Co nejpevněji, aby drát v mikrometru neprokluzoval.", "Na síle dotažení nezáleží.", "Citlivě pomocí řehtačky (ráčny), aby se drát nestlačil.", "Šroub se nedotahuje, průměr se odhaduje pohledem na stupnici."],
                "ans": "Citlivě pomocí řehtačky (ráčny), aby se drát nestlačil."
            },
            {
                "okruh": 6,
                "q": "Na misku byla přidána závaží o celkové hmotnosti 1,5 kg. Jaká je zatěžující síla F (g = 9,81 m·s⁻²)?",
                "opts": ["0,15 N", "1,5 N", "14,7 N", "147 N"],
                "ans": "14,7 N"
            },
            # Okruh 7: Modul pružnosti ve stavební praxi
            {
                "okruh": 7,
                "q": "Jaká hodnota modulu pružnosti konstrukční oceli se uvažuje ve výpočtech podle Eurokódu 3?",
                "opts": ["21 GPa", "210 GPa", "2 100 GPa", "210 MPa"],
                "ans": "210 GPa"
            },
            {
                "okruh": 7,
                "q": "Proč se pro beton ve výpočtech podle Eurokódu 2 zavádí sečnový modul pružnosti E_cm?",
                "opts": ["Protože pracovní diagram betonu je výrazně nelineární.", "Protože beton je dokonale izotropní a lineárně pružný materiál.", "Protože beton nemá v tlaku žádnou pevnost.", "Protože modul pružnosti betonu je vyšší než u oceli."],
                "ans": "Protože pracovní diagram betonu je výrazně nelineární."
            },
            {
                "okruh": 7,
                "q": "Co znamená, že dřevo je anizotropní materiál?",
                "opts": ["Jeho modul pružnosti je ve všech směrech stejný.", "Jeho modul pružnosti je vyšší než u oceli.", "Při jakémkoli zatížení se deformuje pouze plasticky.", "Jeho tuhost závisí na směru zatížení vzhledem k vláknům – kolmo k vláknům je modul pružnosti mnohonásobně nižší."],
                "ans": "Jeho tuhost závisí na směru zatížení vzhledem k vláknům – kolmo k vláknům je modul pružnosti mnohonásobně nižší."
            }
        ]
        
        vyber = []
        okruhy = sorted({o["okruh"] for o in databaze_otazek})
        for k in okruhy:
            # Filtrace pro aktuální okruh
            dostupne = [x for x in databaze_otazek if x["okruh"] == k]
            vybrana = dict(random.choice(dostupne))
            
            # Zamíchání možností a, b, c, d
            vybrana["opts"] = random.sample(vybrana["opts"], len(vybrana["opts"]))
            vyber.append(vybrana)
            
        st.session_state.vybrane_otazky = vyber

    # --- 2. VYKRESLENÍ VYLOSOVANÝCH OTÁZEK ---
    odpovedi_studenta = []
    for i, otazka in enumerate(st.session_state.vybrane_otazky):
        st.markdown(f"**{i+1}. {otazka['q']}**")
        vyber = st.radio(f"Otázka {i+1}", otazka['opts'], index=None, key=f"q_{i}", label_visibility="collapsed")
        odpovedi_studenta.append(vyber)
        st.write("---")
        
   # --- 3. VYHODNOCENÍ S PAUZOU ---
    if st.button("Vyhodnotit kvíz a odemknout protokol"):
        if None in odpovedi_studenta:
            st.warning("⚠️ Před vyhodnocením musíte vybrat odpověď u všech 7 otázek!")
        else:
            skore = 0
            for i, odp in enumerate(odpovedi_studenta):
                if odp == st.session_state.vybrane_otazky[i]['ans']:
                    skore += 1
                    
            if skore >= 6:
                st.success(f"🎉 Výborně! Máte {skore} ze 7 správně. Vaše teoretická příprava je dostatečná. Protokol se odemyká...")
                import time
                time.sleep(3) # Aplikace počká 3 sekundy, aby si student stihl přečíst pochvalu
                st.session_state.krok = 1
                st.rerun()
            else:
                st.error(f"❌ Zatím máte {skore} ze 7 správně. Pro odemčení protokolu potřebujete alespoň 6 bodů. Zamyslete se nad svými chybami a zkuste to znovu.")

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
        st.session_state.tlak = st.text_input("Tlak (hPa)", value=st.session_state.tlak)
    with col2:
        st.session_state.teplota = st.text_input("Teplota (°C)", value=st.session_state.teplota)
    with col3:
        st.session_state.vlhkost = st.text_input("Vlhkost (%)", value=st.session_state.vlhkost)
        
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
            st.session_state[f'd{i+1}'] = st.text_input(f"d{i+1} (mm)", value=st.session_state[f'd{i+1}'])
            
    st.markdown("---")
    st.subheader("Ověření výpočtu")
    st.warning("⚠️ **Pozor:** Nezapomeňte svůj vypočtený průměr správně zaokrouhlit na **3 desetinná místa**!")
    st.session_state.student_prumer = st.text_input("Váš vypočtený průměr [mm]:", value=st.session_state.student_prumer)
    
    # NOVÉ: Hmatatelné tlačítko pro explicitní aktualizaci na mobilech a po návratu
    if st.button("🔄 Aktualizovat a ověřit výpočet"):
        pass # Streamlit po stisknutí tlačítka automaticky uloží všechna rozepsaná pole a stránku znovunačte
        
    try:
        d_vals = [float(st.session_state[f'd{i}'].replace(',', '.')) for i in range(1, 6)]
        skutecny_prumer = sum(d_vals) / 5
        st.session_state.skutecny_prumer = skutecny_prumer 
        
        if st.session_state.student_prumer.strip() != "":
            student_val = float(st.session_state.student_prumer.replace(',', '.'))
            
            if abs(student_val - skutecny_prumer) <= 0.0015:
                st.success("Trefa! Průměr máte vypočítaný i zaokrouhlený správně. 🔓 Protokol je odemčen.")
                
                # --- VÝPOČET A ZOBRAZENÍ V TECHNICKÉM ZÁPISU (Pevně 10^-3) ---
                odchylky = [abs(val - skutecny_prumer) for val in d_vals]
                prumerna_odchylka_mm = sum(odchylky) / 5
                relativni_chyba = (prumerna_odchylka_mm / skutecny_prumer) * 100 if skutecny_prumer != 0 else 0
                
                # Pevné nastavení řádu na milimetry (10^-3 m)
                exponent = -3
                zaklad_prumer = skutecny_prumer
                zaklad_odchylka = prumerna_odchylka_mm
                
                # Nalezení první platné nenulové číslice odchylky pro zaokrouhlení
                if zaklad_odchylka > 0:
                    pocet_mist = -math.floor(math.log10(zaklad_odchylka))
                    zaokrouhlena_odchylka = round(zaklad_odchylka, pocet_mist)
                    if zaokrouhlena_odchylka >= 10**(-(pocet_mist - 1)):
                        pocet_mist -= 1
                        zaokrouhlena_odchylka = round(zaklad_odchylka, pocet_mist)
                else:
                    pocet_mist = 3 # Výchozí pro čistou nulu (mikrometr)
                    zaokrouhlena_odchylka = 0.0
                    
                pocet_mist = max(0, pocet_mist)
                zaokrouhleny_prumer = round(zaklad_prumer, pocet_mist)
                
                st.write("**Výsledek měření (v základních jednotkách SI):**")
                st.latex(rf"d = ({zaokrouhleny_prumer:.{pocet_mist}f} \pm {zaokrouhlena_odchylka:.{pocet_mist}f}) \cdot 10^{{{exponent}}} \text{{ m}} \quad \dots \quad {relativni_chyba:.2f} \text{{ \%}}")
                st.markdown("---")
                # --- KONEC VÝPOČTU ---
                
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
        st.session_state.l0 = st.text_input("Původní délka drátu $l_0$ (m):", value=st.session_state.l0)
    with col_err_l0:
        st.session_state.err_l0 = st.text_input(r"Chyba délky drátu $\Delta l_0$ (m):", value=st.session_state.err_l0)
        
    st.markdown("---")
    st.subheader("Tabulka prodloužení")
    
    # Úprava na 5 sloupců pro vložení síly F
    c1, c2, c3, c4, c5 = st.columns([1.0, 1.2, 2.0, 2.0, 1.5])
    with c1:
        st.write("**m (kg)**")
    with c2:
        st.write("**F (N)**") # NOVÝ SLOUPEC
    with c3:
        st.write("**Zatěžování (mm)**")
    with c4:
        st.write("**Odlehčování (mm)**")
    with c5:
        st.write("**Průměr (mm)**")
        
    vse_vyplneno = True
    vse_nuly = True  # NOVÉ: Hlídač, zda jsou všechny vstupy čisté nuly
    
    for h in hmotnosti:
        # Pět sloupců i pro samotné řádky s daty
        c1, c2, c3, c4, c5 = st.columns([1.0, 1.2, 2.0, 2.0, 1.5])
        key = str(h).replace('.', '_')
        
        with c1:
            st.info(f"{h:.1f}")
            
        with c2:
            sila = h * 9.81
            st.info(f"{sila:.2f}")
            
        with c3:
            st.session_state[f'zatez_{key}'] = st.text_input("Zatěž", value=st.session_state.get(f'zatez_{key}', ""), key=f"z_{key}", label_visibility="collapsed")
                
        with c4:
            st.session_state[f'odleh_{key}'] = st.text_input("Odleh", value=st.session_state.get(f'odleh_{key}', ""), key=f"o_{key}", label_visibility="collapsed")
            
        with c5:
            z_val_str = st.session_state[f'zatez_{key}'].replace(',', '.')
            o_val_str = st.session_state[f'odleh_{key}'].replace(',', '.')
            try:
                z_val = float(z_val_str)
                o_val = float(o_val_str)
                prumer = (z_val + o_val) / 2
                st.info(f"{prumer:.3f}")
                
                # Zrušení nultého stavu, pokud je cokoliv nenulové
                if z_val != 0.0 or o_val != 0.0:
                    vse_nuly = False
                    
            except ValueError:
                st.warning("?")
                vse_vyplneno = False

    st.markdown("---")
    
    # NOVÉ: Kontrola zadané délky drátu l0 a její chyby
    l0_ok = False
    try:
        if st.session_state.l0.strip() != "":
            float(st.session_state.l0.replace(',', '.'))
            l0_ok = True
    except ValueError:
        pass

    err_l0_ok = False
    try:
        if st.session_state.err_l0.strip() != "":
            float(st.session_state.err_l0.replace(',', '.'))
            err_l0_ok = True
    except ValueError:
        pass
    
    col_back, col_fwd = st.columns(2)
    with col_back:
        if st.button("Zpět na Krok 2"):
            st.session_state.krok = 2
            st.rerun()
            
    with col_fwd:
        # Větvení logiky pro pokračování
        if not (l0_ok and err_l0_ok):
            st.warning("⚠️ Než budete moci pokračovat, musíte nahoře vyplnit platnou původní délku drátu a její chybu.")
        elif not vse_vyplneno:
            st.warning("⚠️ Pro pokračování doplňte všechny hodnoty prodloužení do tabulky.")
        else:
            if vse_nuly:
                st.warning("🤔 Všechny zadané hodnoty prodloužení jsou nulové. Pokud je to správně (např. test), potvrďte to níže:")
                if st.checkbox("Ano, chci pokračovat se samými nulami."):
                    if st.button("Přejít ke grafu a analýze (Krok 4)"):
                        st.session_state.krok = 4
                        st.rerun()
            else:
                if st.button("Přejít ke grafu a analýze (Krok 4)"):
                    st.session_state.krok = 4
                    st.rerun()

# ==========================================
# KROK 4: Interaktivní graf
# ==========================================
elif st.session_state.krok == 4:
    st.header("Krok 4: Zpracování grafu")
    st.write("Z naměřených hodnot nyní sestrojíme graf závislosti prodloužení na síle.")
    
    # 1. Získání dat z paměti (Kroku 3)
    hmotnosti = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5]
    sily_F = [h * 9.81 for h in hmotnosti]
    prumerna_dl = []
    
    for h in hmotnosti:
        key = str(h).replace('.', '_')
        z_val = float(st.session_state.get(f'zatez_{key}', 0).replace(',', '.')) if st.session_state.get(f'zatez_{key}', '') != '' else 0.0
        o_val = float(st.session_state.get(f'odleh_{key}', 0).replace(',', '.')) if st.session_state.get(f'odleh_{key}', '') != '' else 0.0
        prumerna_dl.append((z_val + o_val) / 2)
        
    # 2. Skutečná regrese (y = ax + b)
    n = len(sily_F)
    sum_x = sum(sily_F)
    sum_y = sum(prumerna_dl)
    sum_xy = sum(x*y for x, y in zip(sily_F, prumerna_dl))
    sum_xx = sum(x**2 for x in sily_F)
    
    jmenovatel = (n * sum_xx - sum_x**2)
    if jmenovatel != 0:
        a_skutecne = (n * sum_xy - sum_x * sum_y) / jmenovatel
        b_skutecne = (sum_y - a_skutecne * sum_x) / n
    else:
        a_skutecne = 0.0
        b_skutecne = 0.0
        
    st.session_state.a_skutecne = a_skutecne 
    
    # Výpočet skutečné chyby směrnice a (z rozptylu reziduí)
    if n > 2 and jmenovatel != 0:
        suma_rezidui = sum((y - (a_skutecne * x + b_skutecne))**2 for x, y in zip(sily_F, prumerna_dl))
        rozptyl = suma_rezidui / (n - 2) # n-2 stupňů volnosti pro přímku s absolutním členem
        err_a = math.sqrt((n * rozptyl) / jmenovatel)
    else:
        err_a = 0.0
    st.session_state.err_a = err_a
    
    # 3. Interaktivní posuvníky (Výchozí bod je záměrně mimo)
    st.info("💡 **Váš úkol:** Přímka v grafu je nyní zcela mimo naměřené body (má nulový sklon). Použijte oba posuvníky tak, abyste přímku co nejlépe proložili vašimi body.")
    
    col_b, col_a = st.columns(2)
    with col_b:
        # Posuvník B (Počáteční posun) - začíná záměrně např. na 0.1 mm
        b_odhad = st.slider("Počáteční posun b [mm]:", min_value=-0.500, max_value=0.500, value=0.100, step=0.001, format="%.3f")
    with col_a:
        # Posuvník A (Směrnice) - začíná na 0 (vodorovná čára)
        hruby_odhad = (prumerna_dl[-1] - prumerna_dl[0]) / (sily_F[-1] - sily_F[0]) if sily_F[-1] != sily_F[0] else 0.01
        a_odhad = st.slider("Směrnice a [mm/N]:", min_value=-float(hruby_odhad), max_value=float(hruby_odhad * 3), value=0.00000, step=0.00001, format="%.5f")
        
    # 4. Vykreslení interaktivního grafu
    fig = go.Figure()
    
    # Naměřené body
    fig.add_trace(go.Scatter(x=sily_F, y=prumerna_dl, mode='markers', name='Naměřené body', marker=dict(size=10, color='red')))
    
    # Odhadnutá přímka
    x_line = [0, max(sily_F) * 1.1] if sily_F else [0, 50]
    y_line = [a_odhad * x + b_odhad for x in x_line]
    fig.add_trace(go.Scatter(x=x_line, y=y_line, mode='lines', name='Vaše přímka', line=dict(color='blue', width=2)))
    
    # 4.1 Bezpečné zjištění maximálních hodnot pro správné nastavení os
    max_F = max(sily_F) if sily_F else 50
    max_dl = max(prumerna_dl) if prumerna_dl and max(prumerna_dl) > 0 else 0.5

    # 4.2 Nastavení os grafu, mřížky a viditelného počátku (0,0)
    fig.update_layout(
        xaxis_title="Zatěžující síla F [N]",
        yaxis_title="Průměrné prodloužení Δl [mm]",
        plot_bgcolor='white', # Bílé pozadí pro vyniknutí mřížky
        xaxis=dict(
            zeroline=True, zerolinewidth=2, zerolinecolor='black', # Vykreslí výraznou osu Y
            showgrid=True, gridwidth=1, gridcolor='lightgray',     # Hlavní mřížka
            minor=dict(showgrid=True, gridcolor='whitesmoke'),     # Jemná (milimetrová) mřížka
            range=[-max_F * 0.05, max_F * 1.1]                     # Graf začne lehce v mínusu (posun od okraje)
        ),
        yaxis=dict(
            zeroline=True, zerolinewidth=2, zerolinecolor='black', # Vykreslí výraznou osu X
            showgrid=True, gridwidth=1, gridcolor='lightgray',
            minor=dict(showgrid=True, gridcolor='whitesmoke'),
            range=[-max_dl * 0.1, max_dl * 1.2]                    # Osa Y začne lehce v mínusu
        ),
        margin=dict(l=20, r=20, t=30, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 5. Odhalení výpočtu
    if st.button("Odhalit výpočet metodou nejmenších čtverců"):
        st.session_state.odhaleno = True
        
    if st.session_state.odhaleno:
        st.markdown("### Porovnání metod a výpočet")
        
        st.write("**1. Grafická metoda (Váš vizuální odhad):**")
        st.write(f"Rovnice: $\\Delta l = {a_odhad:.5f} \\cdot F + ({b_odhad:.3f})$")
        
        st.write("**2. Numerická metoda (Nejmenší čtverce):**")
        st.write("Počítač proložil body ideální přímkou $y = aF + b$. Hodnota $b$ představuje absolutní člen (počáteční nepřesnost a vůli aparatury). Pro výpočet modulu pružnosti nás zajímá pouze naklonění, tedy směrnice $a$.")
        
        st.success(f"Přesná hodnota směrnice: **$a = {a_skutecne:.5f} \\text{{ mm/N}}$**")
        st.info(f"Počáteční posun (vůle aparatury): **$b = {b_skutecne:.3f} \\text{{ mm}}$**")
        
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
    
   # 1. Bezpečné načtení hodnot z paměti
    try:
        l0 = float(st.session_state.l0.replace(',', '.'))
        err_l0 = float(st.session_state.err_l0.replace(',', '.')) # Zadáno z vývěsky v metrech
    except ValueError:
        st.warning("⚠️ Chybí nebo je špatně zadána původní délka drátu (l0) či její chyba. Prosím, vraťte se do Kroku 3 a zkontrolujte, že jsou obě pole vyplněna číslem.")
        st.stop() # Zastaví výpočet a zabrání pádu aplikace s červenou chybou
        
    d_mm = st.session_state.skutecny_prumer
    a_mmn = st.session_state.a_skutecne
    err_a_mmn = st.session_state.err_a # Skutečná chyba z regrese
    
    # --- VÝPOČTY PRO SHRNUTÍ A KONTROLU (NA POZADÍ) ---
    d_m = d_mm * 1e-3
    a_m_N = a_mmn * 1e-3
    err_a_m_N = err_a_mmn * 1e-3
    
    d_vals = [float(st.session_state[f'd{i}'].replace(',', '.')) for i in range(1, 6)]
    odchylka_d_mm = sum(abs(val - d_mm) for val in d_vals) / 5
    odchylka_d_m = odchylka_d_mm * 1e-3
    
    rel_d = odchylka_d_m / d_m if d_m != 0 else 0
    rel_l0 = err_l0 / l0 if l0 != 0 else 0
    rel_a = err_a_m_N / a_m_N if a_m_N != 0 else 0
    rel_E = math.sqrt(rel_l0**2 + (2 * rel_d)**2 + rel_a**2)
    
    try:
        E_Pa = (4 * l0) / (math.pi * (d_m**2) * a_m_N)
        E_GPa = E_Pa / 1e9
    except ZeroDivisionError:
        E_Pa = 0
        E_GPa = 0
        
    abs_E_GPa = E_GPa * rel_E

    # --- ZOBRAZENÍ 1: SHRNUTÍ VELIČIN ---
    st.subheader("1. Shrnutí naměřených veličin (SI jednotky)")
    st.write("Pro výpočet modulu pružnosti musíme nejprve převést všechny hodnoty na základní jednotky SI (metry, Newtony). Program automaticky zformátoval hodnoty podle velikosti absolutní chyby:")
    
    # Pomocná funkce pro správné formátování s exponentem a zaokrouhlením
    def format_vysledek(nazev, hodnota, chyba, jednotka, forced_exponent=None):
        if chyba == 0:
            return rf"{nazev} = {hodnota} \text{{ {jednotka}}}"
            
        if forced_exponent is not None:
            exponent = forced_exponent
        else:
            if hodnota != 0:
                exponent = math.floor(math.log10(abs(hodnota)))
                if -2 <= exponent <= 2: # Pro běžná čísla (0.01 až 999) exponent nevnucujeme
                    exponent = 0
            else:
                exponent = 0
                
        zaklad_hodnota = hodnota / (10**exponent)
        zaklad_chyba = chyba / (10**exponent)
        
        # Zaokrouhlení chyby na 1 platnou číslici
        if zaklad_chyba > 0:
            rad = -math.floor(math.log10(zaklad_chyba))
            chyba_zaokr = round(zaklad_chyba, rad)
            if chyba_zaokr >= 10**(-(rad - 1)):
                rad -= 1
                chyba_zaokr = round(zaklad_chyba, rad)
        else:
            rad = 0
            chyba_zaokr = 0.0
            
        hodnota_zaokr = round(zaklad_hodnota, rad)
        pocet_mist = max(0, rad)
        
        # Český formát s čárkou
        h_str = f"{hodnota_zaokr:.{pocet_mist}f}".replace('.', ',')
        ch_str = f"{chyba_zaokr:.{pocet_mist}f}".replace('.', ',')
        rel_str = f"{(chyba / abs(hodnota) * 100):.2f}".replace('.', ',')
        
        if exponent != 0:
            return rf"{nazev} = ({h_str} \pm {ch_str}) \cdot 10^{{{exponent}}} \text{{ {jednotka}}} \quad \dots \quad {rel_str} \text{{ \%}}"
        else:
            return rf"{nazev} = ({h_str} \pm {ch_str}) \text{{ {jednotka}}} \quad \dots \quad {rel_str} \text{{ \%}}"

    st.latex(format_vysledek("l_0", l0, err_l0, "m"))
    st.latex(format_vysledek("d", d_m, odchylka_d_m, "m", forced_exponent=-3))
    st.latex(format_vysledek("a", a_m_N, err_a_m_N, "m/N"))
    st.markdown("---")

    # --- ZOBRAZENÍ 2: VÝPOČET E ---
    st.subheader("2. Výpočet modulu pružnosti $E$")
    st.write("Dosad'te hodnoty ze shrnutí výše do definičního vzorce a zapište váš výsledek ve vědeckém tvaru.")
    st.latex(r"E = \frac{4 l_0}{\pi d^2 a}")
    
    col_z, col_kr, col_e, col_pa = st.columns([2.0, 0.5, 1.5, 1.0])
    with col_z:
        student_E_zaklad = st.text_input("Základ (např. 2.05)", key="se_zaklad")
    with col_kr:
        st.markdown("<h3 style='text-align: center; margin-top: 10px;'>&middot; 10</h3>", unsafe_allow_html=True)
    with col_e:
        student_E_exp = st.text_input("Exponent (např. 11)", key="se_exp")
    with col_pa:
        st.markdown("<h3 style='margin-top: 10px;'>Pa</h3>", unsafe_allow_html=True)

    # --- ZOBRAZENÍ 3: VÝPOČET CHYB ---
    st.subheader("3. Výpočet celkové relativní chyby")
    st.write("Doplňte dílčí relativní chyby v procentech a zjistěte celkovou relativní chybu $\\rho(E)$ pomocí věty o přenosu chyb (odmocnina ze součtu čtverců). Zvláštní pozornost věnujte chybě průměru!")
    st.latex(r"\rho(E) = \sqrt{\rho(l_0)^2 + (2\rho(d))^2 + \rho(a)^2}")
    
    c_rl0, c_rd, c_ra, c_re = st.columns(4)
    with c_rl0:
        student_rl0 = st.text_input("ρ(l0) [%]", key="s_rl0")
    with c_rd:
        student_rd = st.text_input("ρ(d) [%]", key="s_rd")
    with c_ra:
        student_ra = st.text_input("ρ(a) [%]", key="s_ra")
    with c_re:
        student_rE = st.text_input("Celková ρ(E) [%]", key="s_rE")

    st.markdown("---")
    
   # --- VYHODNOCENÍ A FINÁLE ---
    vse_ok = False
    
    if student_E_zaklad and student_E_exp and student_rl0 and student_rd and student_ra and student_rE:
        try:
            s_zaklad = float(student_E_zaklad.replace(',', '.'))
            s_exp = float(student_E_exp.replace(',', '.'))
            s_E_Pa = s_zaklad * (10**s_exp)
            
            s_l0 = float(student_rl0.replace(',', '.'))
            s_d = float(student_rd.replace(',', '.'))
            s_a = float(student_ra.replace(',', '.'))
            s_E_rel = float(student_rE.replace(',', '.'))
            
            # Tolerance pro drobné rozdíly v zaokrouhlování na kalkulačce studentů
            e_match = abs(s_E_Pa - E_Pa) / E_Pa < 0.02 if E_Pa != 0 else False
            err_match = (
                abs(s_l0 - rel_l0*100) < 0.15 and
                abs(s_d - rel_d*100) < 0.15 and
                abs(s_a - rel_a*100) < 0.15 and
                abs(s_E_rel - rel_E*100) < 0.3
            )
            
            if e_match and err_match:
                st.success("🎉 Výborně! Váš modul pružnosti i výpočet chyby jsou naprosto přesné.")
                vse_ok = True
            elif not e_match:
                st.error("❌ Výsledek modulu pružnosti zatím nesouhlasí. Zkontrolujte dosazení čísel a exponentů.")
            elif not err_match:
                st.error("❌ Modul E je správně, ale v relativních chybách máte nepřesnost. Nezapomněli jste vynásobit chybu průměru 2x a použít odmocninu ze součtu čtverců?")
        except ValueError:
            st.warning("⚠️ Do všech polí zadejte platná čísla.")
            
    if vse_ok:
        st.markdown("### Finální výsledek měření")
        st.write(r"Podle laboratorních pravidel program vygeneroval zápis výsledku v normovaném tvaru $X=(\overline{x}\pm\overline{\vartheta}(x))$:")
        
        # Absolutní chyba v základních jednotkách (Pa)
        abs_E_Pa = E_Pa * rel_E
        
        # Přečtení exponentu zadaného studentem pro formátování finálního výsledku
        s_exp_val = int(float(student_E_exp.replace(',', '.')))
        
        # Využití naší univerzální formátovací funkce
        final_latex = format_vysledek("E", E_Pa, abs_E_Pa, "Pa", forced_exponent=s_exp_val)
        
        st.success(f"$${final_latex}$$")
    else:
        st.info("🔒 Vypočítejte modul a doplňte správné chyby pro odemčení finálního normovaného zápisu.")
        
    st.markdown("---")
    
    st.subheader("3. Kontrolní otázky")
    st.info("Odpovězte na následující otázky, abyste prokázali pochopení úlohy.")
    
    st.session_state.otazka_1 = st.text_area("1. Jak se směrnice 'a' grafu změní, pokud bychom k měření použili ocelový drát o stejném složení a délce, ale s dvojnásobným průměrem?", value=st.session_state.otazka_1)
    st.session_state.otazka_2 = st.text_area("2. Proč je nutné měřit prodloužení drátu při zatěžování i postupném odlehčování? Co by znamenalo, kdyby se lišily?", value=st.session_state.otazka_2)
    st.session_state.otazka_3 = st.text_area("3. Kde jste se již setkali či byste se mohli setkat s modulem pružnosti v tahu ve stavební praxi?", value=st.session_state.otazka_3)
    
    st.markdown("---")
    st.subheader("Závěr")
    st.session_state.zaver = st.text_area("Zhodnoťte měření. Srovnejte váš výsledek s tabulkovou hodnotou a zamyslete se nad zdroji chyb. Napište, jak se Vám úloha líbila/nelíbila, čím bychom ji mohli vylepšit?:", value=st.session_state.zaver)
    
    st.markdown("---")
    col_back, col_fwd = st.columns(2)
    
    with col_back:
        if st.button("Zpět na Krok 4"):
            st.session_state.krok = 4
            st.rerun()
            
    with col_fwd:
        limit_otazky = 50
        limit_zaver = 100
        
        delka_o1 = len(st.session_state.otazka_1.strip())
        delka_o2 = len(st.session_state.otazka_2.strip())
        delka_o3 = len(st.session_state.otazka_3.strip())
        delka_z = len(st.session_state.zaver.strip())
        
        if delka_o1 >= limit_otazky and delka_o2 >= limit_otazky and delka_o3 >= limit_otazky and delka_z >= limit_zaver and vse_ok:
            st.success("Všechny odpovědi i matematické výpočty jsou v pořádku.")
            if st.button("Ukončit vypracování protokolu"):
                st.session_state.krok = 6
                st.rerun()
        else:
            st.warning("⚠️ Pro ukončení protokolu musíte bezchybně vypočítat modul E (včetně chyby), a odpovědět na všechny otázky v požadované délce.")
            
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
    # 4. Znovuvýpočet E a jeho chyby pro zápis do PDF
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
        
    # Výpočet celkové chyby kvadraticky
    d_vals_arr = [float(st.session_state[f'd{i}'].replace(',', '.')) for i in range(1, 6)]
    odchylka_d_val = sum(abs(v - d_mm_val) for v in d_vals_arr) / 5
    
    rel_d_val = odchylka_d_val / d_mm_val if d_mm_val != 0 else 0
    rel_l0_val = err_l0_val / l0_val if l0_val != 0 else 0
    rel_a_val = err_a_val / a_mmn_val if a_mmn_val != 0 else 0
    
    rel_E_val = math.sqrt(rel_l0_val**2 + (2 * rel_d_val)**2 + rel_a_val**2)
    abs_E_GPa_val = E_GPa_val * rel_E_val
    
    # Zaokrouhlení pro hrubý výpis v PDF
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
        
    text_vysledek_E = f"{E_zaokr_val:.{format_rad_val}f} ± {abs_E_zaokr_val:.{format_rad_val}f} GPa  (relativní chyba {rel_E_val*100:.1f} %)".replace('.', ',')

    # ---------------------------------------------------------
    # 5. Znovuvytvoření grafu a jeho vyfocení do paměti (Matplotlib)
    # ---------------------------------------------------------
    with st.spinner("Generuji graf a PDF dokument..."):
        hmotnosti_pdf = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5]
        sily_pdf = [h * 9.81 for h in hmotnosti_pdf]
        prumerna_dl_pdf = []
        
        for h in hmotnosti_pdf:
            key = str(h).replace('.', '_')
            try:
                z = float(st.session_state.get(f'zatez_{key}', '0').replace(',', '.'))
                o = float(st.session_state.get(f'odleh_{key}', '0').replace(',', '.'))
                prumerna_dl_pdf.append((z + o) / 2)
            except ValueError:
                prumerna_dl_pdf.append(0.0)

        # Matematický výpočet posunu b
        a_pdf = st.session_state.a_skutecne
        n_pdf = len(sily_pdf)
        sum_x = sum(sily_pdf)
        sum_y = sum(prumerna_dl_pdf)
        b_pdf = (sum_y - a_pdf * sum_x) / n_pdf if n_pdf > 0 else 0

        # Konstrukce vizuálu pomocí Matplotlib
        fig_pdf, ax = plt.subplots(figsize=(8, 4.5))
        
        ax.plot(sily_pdf, prumerna_dl_pdf, 'ro', markersize=8, label='Naměřené body')
        x_line = [0, max(sily_pdf) * 1.1] if sily_pdf else [0, 50]
        y_line = [a_pdf * x + b_pdf for x in x_line]
        ax.plot(x_line, y_line, 'b-', linewidth=2, label='Regresní přímka')

        ax.set_title("Graf závislosti prodloužení na síle")
        ax.set_xlabel("Zatěžující síla F [N]")
        ax.set_ylabel("Průměrné prodloužení Δl [mm]")
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend()
        
        # Zvýraznění os X a Y
        ax.axhline(0, color='black', linewidth=1)
        ax.axvline(0, color='black', linewidth=1)

        max_f_pdf = max(sily_pdf) if sily_pdf else 50
        max_dl_pdf = max(prumerna_dl_pdf) if prumerna_dl_pdf and max(prumerna_dl_pdf) > 0 else 0.5
        ax.set_xlim(left=-max_f_pdf * 0.05, right=max_f_pdf * 1.1)
        ax.set_ylim(bottom=-max_dl_pdf * 0.1, top=max_dl_pdf * 1.2)

        # Vyfocení grafu jako PNG do virtuálního souboru v paměti
        img_stream = io.BytesIO()
        fig_pdf.savefig(img_stream, format='png', bbox_inches='tight', dpi=150)
        img_stream.seek(0)
        plt.close(fig_pdf) # Uvolnění paměti

        # ---------------------------------------------------------
        # 6. Vytvoření PDF dokumentu v paměti
        # ---------------------------------------------------------
        pdf = FPDF()
        pdf.add_page()
        
        # --- NOVÉ: Načtení českého fontu z Windows ---
        import os
        use_diacritics = False
        font_name = "helvetica" # Záložní font
        
        font_regular = r"C:\Windows\Fonts\arial.ttf"
        font_bold = r"C:\Windows\Fonts\arialbd.ttf"
        
        # Pokud najde Arial ve Windows, nahraje ho a zapne češtinu
        if os.path.exists(font_regular) and os.path.exists(font_bold):
            try:
                pdf.add_font("ArialCS", "", font_regular)
                pdf.add_font("ArialCS", "B", font_bold)
                font_name = "ArialCS"
                use_diacritics = True
            except:
                pass
                
        # Chytrá funkce: Pokud má font, nechá háčky. Pokud ne, odstraní je.
        def uprav_text(text):
            if not text: return ""
            if use_diacritics:
                return str(text)
            return bez_diakritiky(text)
        
       # Časové razítko (menší šedé, bez kurzívy)
        pdf.set_font(font_name, style="", size=9)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(0, 8, text=uprav_text(f"Vygenerováno systémem: {aktualni_cas}"), new_x="LMARGIN", new_y="NEXT", align="R")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(3)
        
        # Pomocná funkce pro zápis řádků (Zmenšeno z 12 na 11)
        def zapis_radek(text, font_style="", size=11):
            pdf.set_font(font_name, style=font_style, size=size)
            pdf.cell(0, 7, text=uprav_text(text), new_x="LMARGIN", new_y="NEXT")

       # Hlavička protokolu (Zmenšené nadpisy a sdružené řádky)
        zapis_radek("PROTOKOL O MĚŘENÍ - Úloha 7.5", "B", 14)
        zapis_radek(f"Vypracoval: {st.session_state.jmeno}   |   Spolupracovník: {st.session_state.spolupracovnik}")
        
        tlak_cs = str(st.session_state.tlak).replace('.', ',')
        teplota_cs = str(st.session_state.teplota).replace('.', ',')
        vlhkost_cs = str(st.session_state.vlhkost).replace('.', ',')
        zapis_radek(f"Skupina: {st.session_state.skupina}   |   Podmínky: {tlak_cs} hPa; {teplota_cs} °C; {vlhkost_cs} %")
        pdf.ln(4)
        
        # Výsledky (Sdružené do jednoho řádku s českými čárkami)
        zapis_radek("HLAVNÍ VÝSLEDKY", "B", 12)
        d_cs = str(st.session_state.student_prumer).replace('.', ',')
        l0_cs = str(st.session_state.l0).replace('.', ',')
        a_cs = f"{st.session_state.a_skutecne:.5f}".replace('.', ',')
        zapis_radek(f"d = {d_cs} mm   |   l0 = {l0_cs} m   |   a = {a_cs} mm/N")
        
        pdf.ln(2)
        zapis_radek(f"MODUL PRUŽNOSTI (E): {text_vysledek_E}", "B", 11)
        pdf.ln(4)
        
        # Vložení vyfoceného grafu do PDF (Zmenšený a vycentrovaný)
        zapis_radek("GRAF ZÁVISLOSTI PRODLOUŽENÍ NA SÍLE", "B", 12)
        # Šířka zmenšena ze 170 na 140, posunuto zleva (x=35) doprostřed A4
        pdf.image(img_stream, x=35, w=140) 
        pdf.ln(4)
        
        # Otázky a závěr
        zapis_radek("ODPOVĚDI A ZÁVĚR", "B", 12)
        
        zapis_radek("Otázka 1:", "B", 11)
        pdf.set_font(font_name, size=11)
        # Zmenšené řádkování pro multi_cell (z 8 na 6)
        pdf.multi_cell(0, 6, text=uprav_text(st.session_state.otazka_1)) 
        pdf.ln(2)
        
        zapis_radek("Otázka 2:", "B", 11)
        pdf.set_font(font_name, size=11)
        pdf.multi_cell(0, 6, text=uprav_text(st.session_state.otazka_2))
        pdf.ln(2)
        
        zapis_radek("Otázka 3:", "B", 11)
        pdf.set_font(font_name, size=11)
        pdf.multi_cell(0, 6, text=uprav_text(st.session_state.otazka_3))
        pdf.ln(2)
        
        zapis_radek("Závěr:", "B", 11)
        pdf.set_font(font_name, size=11)
        pdf.multi_cell(0, 6, text=uprav_text(st.session_state.zaver))

    # 7. Vygenerování PDF a předání do stahovacího tlačítka
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