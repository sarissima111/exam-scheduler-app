# app.py
import streamlit as st
from itertools import product
from datetime import datetime

st.set_page_config(page_title="Pianificatore Esami", layout="centered")

mesi_italiani = {
    'gennaio': '01', 'febbraio': '02', 'marzo': '03', 'aprile': '04',
    'maggio': '05', 'giugno': '06', 'luglio': '07', 'agosto': '08',
    'settembre': '09', 'ottobre': '10', 'novembre': '11', 'dicembre': '12'
}

def parse_date(data_str):
    parts = data_str.lower().strip().split()
    giorno = parts[0]
    mese = mesi_italiani[parts[1]]
    anno = parts[2]
    return datetime.strptime(f"{giorno}-{mese}-{anno}", "%d-%m-%Y")

st.title("📚 Pianificatore Esami Universitari")

num_exams = st.number_input("Quanti esami devi sostenere?", min_value=1, max_value=10, step=1)
exams = []

for i in range(num_exams):
    name = st.text_input(f"Nome esame {i+1}", key=f"nome_{i}")
    importance = st.slider(f"Importanza di {name}", 1, 10, 5, key=f"importanza_{i}")
    num_dates = st.number_input(f"Numero di appelli per {name}", 1, 5, key=f"num_date_{i}")
    date_inputs = []
    for j in range(num_dates):
        date_str = st.text_input(f"Data appello {j+1} per {name} (es. 12 luglio 2025)", key=f"{i}_{j}")
        date_inputs.append(date_str)
    exams.append({'name': name, 'importance': importance, 'dates': date_inputs})

start_date_str = st.text_input("Inizio sessione (es. 10 luglio 2025)")
end_date_str = st.text_input("Fine sessione (es. 30 luglio 2025)")
min_distance = st.number_input("Distanza minima tra esami (in giorni)", min_value=0, value=3)

if st.button("Calcola combinazione ottimale"):
    try:
        start_date = parse_date(start_date_str)
        end_date = parse_date(end_date_str)

        for exam in exams:
            exam['dates'] = [parse_date(d) for d in exam['dates'] if d.strip()]
            exam['dates'] = [d for d in exam['dates'] if start_date <= d <= end_date]

        all_date_options = [exam['dates'] for exam in exams]
        all_combinations = list(product(*all_date_options))

        def is_valid_combination(combo, min_distance):
            sorted_dates = sorted(combo)
            for i in range(1, len(sorted_dates)):
                if (sorted_dates[i] - sorted_dates[i-1]).days < min_distance:
                    return False
            return True

        def describe_combination(combo):
            return [(exams[i]['name'], combo[i].strftime("%d %B %Y")) for i in range(len(combo))]

        valid_combinations = [combo for combo in all_combinations if is_valid_combination(combo, min_distance)]
        scored_combinations = [
            (describe_combination(combo), sum(exams[i]['importance'] for i in range(len(combo))))
            for combo in valid_combinations
        ]
        scored_combinations.sort(key=lambda x: x[1], reverse=True)

        if scored_combinations:
            st.success("✅ Combinazione ottimale trovata:")
            for name, date in sorted(scored_combinations[0][0], key=lambda x: datetime.strptime(x[1], "%d %B %Y")):
                st.write(f"- {name}: {date}")
            st.write(f"Totale importanza: **{scored_combinations[0][1]}**")
        else:
            st.error("❌ Nessuna combinazione soddisfa i criteri.")
    except Exception as e:
        st.error(f"Errore: {str(e)}")
from fpdf import FPDF
import io

def salva_risultati_txt(scored_combinations):
    output = "✅ Combinazione ottimale:\n"
    for name, date in sorted(scored_combinations[0][0], key=lambda x: datetime.strptime(x[1], "%d %B %Y")):
        output += f"- {name}: {date}\n"
    output += f"Totale importanza: {scored_combinations[0][1]}\n\n"

    output += "📋 Altre combinazioni:\n"
    for combo, score in scored_combinations[1:]:
        combo_sorted = sorted(combo, key=lambda x: datetime.strptime(x[1], "%d %B %Y"))
        combo_str = ", ".join([f"{n}: {d}" for n, d in combo_sorted])
        output += f"- {combo_str} → importanza: {score}\n"
    return output

def salva_risultati_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in text.split("\n"):
        pdf.cell(200, 10, txt=line, ln=True)
    buffer = io.BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()

# Genera risultati
txt_output = salva_risultati_txt(scored_combinations)
pdf_output = salva_risultati_pdf(txt_output)

# Download link
st.download_button("📄 Scarica risultati in TXT", txt_output, file_name="risultati_esami.txt")
st.download_button("📄 Scarica risultati in PDF", pdf_output, file_name="risultati_esami.pdf")


