import json
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io
import matplotlib.pyplot as plt

# --- GREENHALAL.AI POC WEB DEMO v2 ---
# Polished layout with tabs, charts, and certificate download

st.set_page_config(page_title="GreenHalal.AI", page_icon="🕌", layout="wide")
st.title("🕌 GreenHalal.AI — Compliance Scoring Demo")
st.markdown("### Assess your sustainability and halal compliance score for your products")

# --- Sidebar Inputs ---
st.sidebar.header("Input Company & Product Details")
company_name = st.sidebar.text_input("Company Name", "EcoMeat Ltd")
country = st.sidebar.text_input("Country", "UAE")
energy_source = st.sidebar.selectbox("Primary Energy Source", ["solar", "wind", "hydro", "gas", "coal", "mixed"])
waste_management = st.sidebar.selectbox("Waste Management Practice", ["recycling", "landfill", "incineration", "none"])
animal_welfare_certified = st.sidebar.checkbox("Animal Welfare Certified", True)
halal_certified = st.sidebar.checkbox("Halal Certified", True)
uses_non_halal_ingredients = st.sidebar.checkbox("Uses Non-Halal Ingredients", False)
carbon_emission_per_unit = st.sidebar.number_input("Carbon Emission (kg CO₂/kg product)", 0.0, 20.0, 2.5)
water_usage_per_unit = st.sidebar.number_input("Water Usage (litres/kg product)", 0.0, 500.0, 50.0)
supplier_transparency_score = st.sidebar.slider("Supplier Transparency (0-1)", 0.0, 1.0, 0.8)

# --- Package Data ---
data = {
    "company_name": company_name,
    "country": country,
    "energy_source": energy_source,
    "waste_management": waste_management,
    "animal_welfare_certified": animal_welfare_certified,
    "halal_certified": halal_certified,
    "uses_non_halal_ingredients": uses_non_halal_ingredients,
    "carbon_emission_per_unit": carbon_emission_per_unit,
    "water_usage_per_unit": water_usage_per_unit,
    "supplier_transparency_score": supplier_transparency_score
}

# --- Scoring Functions ---
def halal_score(data):
    score = 0
    if data["halal_certified"]: score += 50
    if not data["uses_non_halal_ingredients"]: score += 30
    if data["animal_welfare_certified"]: score += 20
    return min(score, 100)

def sustainability_score(data):
    score = 0
    if data["energy_source"] in ["solar", "wind", "hydro"]: score += 30
    if data["waste_management"] == "recycling": score += 20
    if data["carbon_emission_per_unit"] < 5: score += 30
    if data["water_usage_per_unit"] < 100: score += 10
    score += data["supplier_transparency_score"] * 10
    return min(score, 100)

def greenhalal_score(data):
    weights = {"halal": 0.5, "sustainability": 0.5}
    h_score = halal_score(data)
    s_score = sustainability_score(data)
    combined = (h_score * weights["halal"] + s_score * weights["sustainability"])
    return {
        "company_name": data["company_name"],
        "halal_score": round(h_score, 2),
        "sustainability_score": round(s_score, 2),
        "greenhalal_compliance": round(combined, 2),
        "rating": "Excellent" if combined > 80 else ("Good" if combined > 60 else "Needs Improvement")
    }

# --- Simulated Public Database ---
public_database = {
    "EcoMeat Ltd": {"emission_data": 2.5, "verified_halal": True, "certification_id": "H12345"},
    "PureFoods Co": {"emission_data": 4.0, "verified_halal": True, "certification_id": "H98765"}
}

def enrich_with_public_data(data):
    company = data["company_name"]
    if company in public_database:
        db_data = public_database[company]
        data["carbon_emission_per_unit"] = db_data.get("emission_data", data["carbon_emission_per_unit"])
        data["halal_certified"] = db_data.get("verified_halal", data["halal_certified"])
    return data

# --- Generate Certificate PDF ---
def generate_certificate(result):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(width / 2, height - 100, "GreenHalal.AI Certificate")

    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2, height - 150, f"This certifies that {result['company_name']}")
    c.drawCentredString(width / 2, height - 180, "has achieved an Excellent Green Halal Compliance Score.")

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 230, f"Compliance Score: {result['greenhalal_compliance']}%")

    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 280, "Awarded by GreenHalal.AI — Promoting Ethical and Sustainable Halal Practices")

    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(width / 2, 100, "© 2025 GreenHalal.AI | Prototype Demo")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# --- Main App Logic ---
if st.button("Calculate Compliance Score"):
    enriched_data = enrich_with_public_data(data)
    result = greenhalal_score(enriched_data)

    # --- Tabs for Layout ---
    tabs = st.tabs(["Summary", "Details", "Visuals", "Certificate"])

    with tabs[0]:  # Summary
        st.subheader("Summary")
        st.metric(label="Green Halal Compliance Score", value=f"{result['greenhalal_compliance']}%")
        if result["rating"] == "Excellent": st.success("Excellent compliance")
        elif result["rating"] == "Good": st.info("Good compliance")
        else: st.warning("Needs improvement")

    with tabs[1]:  # Details
        st.subheader("Score Breakdown")
        st.write(f"Halal Score: {result['halal_score']}%")
        st.write(f"Sustainability Score: {result['sustainability_score']}%")
        st.write(f"Rating: {result['rating']}")

    with tabs[2]:  # Visuals
        st.subheader("Visual Representation")
        fig, ax = plt.subplots()
        categories = ['Halal', 'Sustainability']
        scores = [result['halal_score'], result['sustainability_score']]
        ax.bar(categories, scores, color=['green', 'lightgreen'])
        ax.set_ylim(0, 100)
        ax.set_ylabel('Score %')
        st.pyplot(fig)

    with tabs[3]:  # Certificate
        if result["rating"] == "Excellent":
            st.success("You are eligible for the GreenHalal Certificate.")
            pdf_buffer = generate_certificate(result)
            st.download_button(label="📜 Download Certificate (PDF)", data=pdf_buffer,
                               file_name=f"{result['company_name']}_GreenHalal_Certificate.pdf",
                               mime="application/pdf")
        else:
            st.info("Improve your scores to obtain the certificate.")

