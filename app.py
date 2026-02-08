import streamlit as st
import json
import os

# --- KONFIGURATION ---
st.set_page_config(page_title="FFW Übung", page_icon="🚒")

def load_questions():
    if os.path.exists('fragen.json'):
        with open('fragen.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

fragen = load_questions()

# --- SESSION STATE INITIALISIERUNG ---
if 'seite' not in st.session_state:
    st.session_state.seite = 'start'
    st.session_state.index = 0
    st.session_state.konnte = 0
    st.session_state.konnte_nicht = 0
    st.session_state.falsche_fragen = [] 
    st.session_state.modus = 'alle' 
    st.session_state.show_solution_for = -1

# --- NAVIGATION FUNKTIONEN ---
def gehe_zu_quiz(modus):
    st.session_state.seite = 'quiz'
    st.session_state.index = 0
    st.session_state.konnte = 0
    st.session_state.konnte_nicht = 0
    st.session_state.modus = modus
    st.session_state.show_solution_for = -1

def gehe_zu_start():
    st.session_state.seite = 'start'
    st.rerun()

# --- 1. STARTSEITE ---
if st.session_state.seite == 'start':
    st.title("🚒 Jugendleistungsspange")
    st.write("Bereit für die Übung? Wähle einen Modus:")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📚 Alle Fragen", use_container_width=True, type="primary"):
            gehe_zu_quiz('alle')
            st.rerun()
    
    with col2:
        anzahl_falsch = len(st.session_state.falsche_fragen)
        if st.button(f"🔄 Wiederholen ({anzahl_falsch})", use_container_width=True, disabled=(anzahl_falsch == 0)):
            gehe_zu_quiz('falsche')
            st.rerun()

# --- 2. QUIZ-MODUS ---
elif st.session_state.seite == 'quiz':
    # Fragen auswählen basierend auf Modus
    if st.session_state.modus == 'falsche':
        aktuelle_liste = [fragen[i] for i in st.session_state.falsche_fragen]
    else:
        aktuelle_liste = fragen

    # Prüfen, ob noch Fragen übrig sind
    if st.session_state.index < len(aktuelle_liste):
        q = aktuelle_liste[st.session_state.index]
        
        st.subheader(f"Frage {st.session_state.index + 1} von {len(aktuelle_liste)}")
        st.progress((st.session_state.index + 1) / len(aktuelle_liste))
        
        # Die Frage selbst
        st.info(f"### {q['frage']}")

        # Lösung anzeigen
        if st.button("Lösung anzeigen 👁️", use_container_width=True):
            st.session_state.show_solution_for = st.session_state.index

        if st.session_state.show_solution_for == st.session_state.index:
            with st.expander("✅ LÖSUNG ANZEIGEN", expanded=True):
                # Formatiert Komma-Listen als Aufzählung
                if "," in q['loesung']:
                    for punkt in q['loesung'].split(","):
                        st.write(f"• {punkt.strip()}")
                else:
                    st.write(q['loesung'])
                
                if q.get('erklaerung'):
                    st.caption(f"Info: {q['erklaerung']}")

        st.divider()

        # Buttons für die Bewertung
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Konnte ich", use_container_width=True):
                if st.session_state.modus == 'falsche':
                    # Aus der Fehlerliste entfernen
                    original_idx = st.session_state.falsche_fragen.pop(st.session_state.index)
                    # Index nicht erhöhen, da die Liste geschrumpft ist!
                else:
                    st.session_state.index += 1
                
                st.session_state.konnte += 1
                st.session_state.show_solution_for = -1
                st.rerun()

        with c2:
            if st.button("❌ Nicht gewusst", use_container_width=True):
                if st.session_state.modus == 'alle':
                    if st.session_state.index not in st.session_state.falsche_fragen:
                        st.session_state.falsche_fragen.append(st.session_state.index)
                
                st.session_state.index += 1
                st.session_state.konnte_nicht += 1
                st.session_state.show_solution_for = -1
                st.rerun()
    else:
        # Quiz fertig -> Umschalten auf Ergebnis
        st.session_state.seite = 'ergebnis'
        st.rerun()

# --- 3. ERGEBNIS-SCREEN ---
elif st.session_state.seite == 'ergebnis':
    st.title("🏁 Ergebnis")
    
    # Große Metriken
    k1, k2, k3 = st.columns(3)
    k1.metric("Richtig", st.session_state.konnte)
    k2.metric("Falsch", st.session_state.konnte_nicht)
    
    gesamt = st.session_state.konnte + st.session_state.konnte_nicht
    quote = (st.session_state.konnte / gesamt * 100) if gesamt > 0 else 0
    k3.metric("Erfolg", f"{quote:.0f}%")

    if quote >= 80:
        st.balloons()
        st.success("Super Leistung! Du bist bereit für die Leistungsspanne!")
    elif quote >= 50:
        st.warning("Gut gemacht! Noch ein bisschen Übung, dann sitzt alles.")
    else:
        st.error("Das sollten wir nochmal wiederholen.")

    st.divider()
    
    if st.button("🔙 Zurück zum Hauptmenü", use_container_width=True):
        gehe_zu_start()
