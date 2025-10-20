import streamlit as st
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt

# --- PAGE CONFIG ---
st.set_page_config(page_title="GreenHalal.AI", page_icon="🕌", layout="wide")
st.title("🕌 GreenHalal.AI — Full Compliance Demo")
st.markdown("### Assess your halal and sustainability compliance scores for your products")

# --- SIDEBAR INPUTS ---
st.sidebar.header("Input Company & Product Details")

# Company & Product Info
company_name = st.sidebar.text_input("Company Name", "EcoMeat Ltd")
product_name = st.sidebar.text_input("Product Name / SKU", "Organic Lamb")
country = st.sidebar.text_input("Country", "UAE")
category = st.sidebar.selectbox("Product Category", ["Meat", "Dairy", "Beverages", "Snacks", "Other"])

# Halal Compliance
halal_certified = st.sidebar.checkbox("Halal Certified", True)
zabiha_required = st.sidebar.checkbox("Zabiha Slaughter Required", True)
uses_non_halal_ingredients = st.sidebar.checkbox("Uses Non-Halal Ingredients", False)
halal_cert_body = st.sidebar.text_input("Halal Certification Body", "Emirates Halal Authority")
cross_contamination_risk = st.sidebar.slider("Cross-Contamination Risk (0=low, 1=high)", 0.0, 1.0, 0.2)
ingredient_upload = st.sidebar.file_uploader("Upload Ingredient List (CSV/XLSX)", type=["csv", "xlsx"])

# Sustainability / Green Metrics
energy_source = st.sidebar.selectbox("Primary Energy Source", ["Solar", "Wind", "Hydro", "Gas", "Coal", "Mixed"])
renewable_percentage = st.sidebar.slider("Percentage Renewable Energy", 0, 100, 60)
carbon_emission = st.sidebar.number_input("Carbon Emission (kg CO₂/kg product)", 0.0, 20.0, 2.5)
water_usage = st.sidebar.number_input("Water Usage (litres/kg product)", 0.0, 500.0, 50.0)
waste_management = st.sidebar.selectbox("Waste Management Practice", ["Recycling", "Landfill", "Incineration", "None"])
packaging_type = st.sidebar.selectbox("Packaging Type", ["Plastic", "Biodegradable", "Recycled Paper", "Glass"])
transportation_mode = st.sidebar.selectbox("Transportation Mode", ["Truck", "Rail", "Ship", "Air", "Mixed"])

# Social & Ethical
animal_welfare = st.sidebar.checkbox("Animal Welfare Certified", True)
fair_labour = st.sidebar.checkbox("Fair Labour Certified", True)
csr_initiatives = st.sidebar.text_area("CSR / Community Initiatives")

# Supplier Transparency
supplier_transparency = st.sidebar.slider("Supplier Transparency Score (0-1)", 0.0, 1.0, 0.8)

# --- DATA PACKAGE ---
data = {
    "company_name": company_name,
    "product_name": product_name,
    "category": category,
    "country": country,
    "halal_certified": halal_certified,
    "zabiha_required": zabiha_required,
    "uses_non_halal_ingredients": uses_non_halal_ingredients,
    "halal_cert_body": halal_cert_body,
    "cross_contamination_risk": cross_contamination_risk,
    "ingredient_upload": ingredient_upload,
    "energy_source": energy_source,
    "renewable_percentage": renewable_percentage,
    "carbon_emission": carbon_emission,
    "water_usage": water_usage,
    "waste_management": waste_management,
    "packaging_type": packaging_type,
    "transportation_mode": transportation_mode,
    "animal_welfare": animal_welfare,
    "fair_labour": fair_labour,
    "csr_initiatives": csr_initiatives,
    "supplier_transparency": supplier_transparency
}

# --- SCORING FUNCTIONS ---
def halal_score(d):
    score = 0
    if d["halal_certified"]:
        score += 40
    if d["category"]=="Meat" and d["zabiha_required"]:
        score += 20
    if not d["uses_non_halal_ingredients"]:
        score += 20
    if d["animal_welfare"]:
        score += 20
    score -= d["cross_contamination_risk"] * 20
    return max(0, min(score, 100))

def sustainability_score(d):
    score = 0
    if d["energy_source"] in ["Solar","Wind","Hydro"]:
        score += 20
    score += d["renewable_percentage"] * 0.2
    if d["carbon_emission"] < 5:
        score += 20
    if d["water_usage"] < 100:
        score += 10
    if d["waste_management"] == "Recycling":
        score += 10
    if d["packaging_type"] in ["Biodegradable","Recycled Paper"]:
        score += 10
    score += d["supplier_transparency"] * 10
    return max(0, min(score,100))

def ethical_score(d):
    score = 0
    if d["fair_labour"]:
        score += 20
    if d["csr_initiatives"]:
        score += 10
    return max(0, min(score,100))

def greenhalal_compliance(d):
    h = halal_score(d)
    s = sustainability_score(d)
    e = ethical_score(d)
    combined = 0.5*h + 0.4*s + 0.1*e
    rating = "Excellent" if combined > 80 else ("Good" if combined > 60 else "Needs Improvement")
    return {
        "halal_score": round(h,2),
        "sustainability_score": round(s,2),
        "ethical_score": round(e,2),
        "greenhalal_score": round(combined,2),
        "rating": rating
    }

# --- AI-BASED RECOMMENDATIONS ---
def generate_recommendations(d, result):
    recs = []
    # Halal
    if not d["halal_certified"]:
        recs.append("Consider obtaining a verified Halal certification.")
    if d["category"]=="Meat" and d["zabiha_required"] and not d["halal_certified"]:
        recs.append("Ensure Zabiha compliance for all meat products.")
    if d["cross_contamination_risk"] > 0.3:
        recs.append("Reduce cross-contamination risk in production lines.")
    if d["uses_non_halal_ingredients"]:
        recs.append("Replace non-halal ingredients with halal alternatives.")
    # Sustainability
    if d["renewable_percentage"] < 50:
        recs.append("Increase the percentage of renewable energy used.")
    if d["carbon_emission"] > 5:
        recs.append("Reduce carbon emissions per unit by optimising processes or sourcing low-carbon suppliers.")
    if d["water_usage"] > 100:
        recs.append("Reduce water usage per unit through efficient processes.")
    if d["packaging_type"] not in ["Biodegradable","Recycled Paper"]:
        recs.append("Consider switching to biodegradable or recycled packaging.")
    if d["waste_management"] != "Recycling":
        recs.append("Implement recycling programs to improve sustainability score.")
    # Ethical
    if not d["fair_labour"]:
        recs.append("Obtain fair labour certification for social compliance.")
    if not d["csr_initiatives"]:
        recs.append("Publish CSR initiatives to improve ethical score.")
    return recs

# --- CERTIFICATE FUNCTION ---
def generate_certificate(result, company, product):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(width/2, height-100, "GreenHalal.AI Certificate")
    c.setFont("Helvetica", 14)
    c.drawCentredString(width/2, height-150, f"{company} — {product}")
    c.drawCentredString(width/2, height-180, f"has achieved a Green Halal Compliance Score.")
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2, height-220, f"Score: {result['greenhalal_score']}%")
    c.drawCentredString(width/2, height-250, f"Rating: {result['rating']}")
    if data["zabiha_required"] and data["category"]=="Meat":
        c.setFont("Helvetica-Oblique", 12)
        c.drawCentredString(width/2, height-280, "Zabiha compliance verified.")
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# --- MAIN APP ---
if st.button("Calculate Compliance"):
    result = greenhalal_compliance(data)
    recommendations = generate_recommendations(data, result)

    tabs = st.tabs(["Summary", "Details", "Visuals", "Certificate", "Recommendations"])

    with tabs[0]:
        st.subheader("Summary")
        st.metric("GreenHalal Compliance Score", f"{result['greenhalal_score']}%")
        if result["rating"]=="Excellent":
            st.success("Excellent Compliance")
        elif result["rating"]=="Good":
            st.info("Good Compliance")
        else:
            st.warning("Needs Improvement")

    with tabs[1]:
        st.subheader("Score Breakdown")
        st.write(f"Halal Score: {result['halal_score']}%")
        st.write(f"Sustainability Score: {result['sustainability_score']}%")
        st.write(f"Ethical Score: {result['ethical_score']}%")
        st.write(f"Rating: {result['rating']}")

    with tabs[2]:
        st.subheader("Visual Representation")
        fig, ax = plt.subplots()
        categories = ['Halal','Sustainability','Ethical']
        scores = [result['halal_score'], result['sustainability_score'], result['ethical_score']]
        ax.bar(categories, scores, color=['green','lightgreen','darkgreen'])
        ax.set_ylim(0,100)
        ax.set_ylabel("Score (%)")
        st.pyplot(fig)

    with tabs[3]:
        st.subheader("Certificate")
        if result["rating"]=="Excellent":
            st.success("Eligible for GreenHalal Certificate")
            pdf = generate_certificate(result, company_name, product_name)
            st.download_button("📄 Download Certificate (PDF)", pdf,
                               file_name=f"{company_name}_{product_name}_GreenHalal.pdf",
                               mime="application/pdf")
        else:
            st.info("Improve scores to receive certificate.")

    with tabs[4]:
        st.subheader("AI-Based Recommendations")
        if recommendations:
            for rec in recommendations:
                st.info(rec)
        else:
            st.success("No recommendations! Your product already meets excellent compliance standards.")
