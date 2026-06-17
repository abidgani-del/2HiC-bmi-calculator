import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="2HiC BMI Calculator",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# File to store historical data
HISTORY_FILE = "bmi_history.csv"

# Ensure the history file exists
if not os.path.exists(HISTORY_FILE):
    df_empty = pd.DataFrame(columns=[
        "Timestamp", "Name", "Gender", "Age", 
        "Height_Ft_In", "Weight_Kg", "BMI", "Category"
    ])
    df_empty.to_csv(HISTORY_FILE, index=False)

# CSS for vibrant medical-facility look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Overall Font Settings */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Header Style */
    .header-container {
        background: linear-gradient(135deg, #0A5C5A 0%, #149390 50%, #20C2BE 100%);
        padding: 2.5rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(20, 147, 144, 0.2);
    }
    .header-title {
        font-size: 2.8rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: 1px;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
    }
    .header-subtitle {
        font-size: 1.1rem;
        font-weight: 300;
        margin-top: 0.5rem;
        opacity: 0.9;
    }
    
    /* Card design */
    .result-card {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(20, 147, 144, 0.1);
        text-align: center;
        height: 100%;
    }
    
    /* Category styles */
    .category-box {
        font-size: 1.8rem;
        font-weight: 700;
        padding: 0.8rem 1.5rem;
        border-radius: 12px;
        display: inline-block;
        margin-top: 1rem;
        color: white;
    }
    .cat-underweight {
        background: linear-gradient(135deg, #3A86C8 0%, #2A6CA6 100%);
        box-shadow: 0 4px 15px rgba(58, 134, 200, 0.3);
    }
    .cat-healthy {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
    }
    .cat-overweight {
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
    }
    .cat-obese {
        background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
    }
    
    /* Stat grid */
    .stat-val {
        font-size: 3.5rem;
        font-weight: 800;
        color: #111827;
        margin: 0.5rem 0;
    }
    .stat-label {
        font-size: 0.95rem;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 500;
    }
    
    /* Custom Recommendations */
    .rec-box {
        background: #F3F4F6;
        border-left: 4px solid #149390;
        padding: 1.2rem;
        border-radius: 8px;
        text-align: left;
        margin-top: 1.5rem;
        font-size: 0.95rem;
        color: #374151;
        line-height: 1.5;
    }
    
    /* Section dividers */
    .section-title {
        font-size: 1.6rem;
        font-weight: 600;
        color: #0A5C5A;
        border-left: 5px solid #20C2BE;
        padding-left: 10px;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Application Header
st.markdown("""
<div class="header-container">
    <div class="header-title">🏥 2HiC BMI Calculator</div>
    <div class="header-subtitle">Professional Grade Clinical BMI Dashboard & Health Tracker</div>
</div>
""", unsafe_allow_html=True)

# Helper function to compute BMI and get category/color
def calculate_bmi(weight_kg, height_meters):
    if height_meters <= 0:
        return 0, "Unknown", "grey"
    bmi = weight_kg / (height_meters ** 2)
    bmi = round(bmi, 2)
    
    if bmi < 18.5:
        return bmi, "Underweight", "cat-underweight"
    elif 18.5 <= bmi < 25.0:
        return bmi, "Healthy", "cat-healthy"
    elif 25.0 <= bmi < 30.0:
        return bmi, "Overweight", "cat-overweight"
    else:
        return bmi, "Obese", "cat-obese"

# Helper to provide recommendations
def get_recommendations(category, age, gender):
    recs = {
        "Underweight": [
            "Focus on nutrient-dense foods (nuts, seeds, lean protein, healthy fats).",
            "Consider strength training exercises to build muscle mass safely.",
            "Consult with a nutritionist to design a healthy weight-gain plan."
        ],
        "Healthy": [
            "Maintain your current lifestyle with a balanced diet rich in vegetables, fruits, and lean protein.",
            "Aim for at least 150 minutes of moderate aerobic exercise weekly.",
            "Continue regular hydration and high-quality sleep (7-9 hours)."
        ],
        "Overweight": [
            "Incorporate more fiber-rich foods and reduce processed sugars/carbs.",
            "Engage in daily physical activities such as brisk walking, cycling, or swimming.",
            "Track your daily caloric intake and look for healthy, sustainable deficit options."
        ],
        "Obese": [
            "Work alongside a clinical healthcare provider to establish a safe, long-term weight management plan.",
            "Begin with low-impact exercises (like walking or water aerobics) to protect joints.",
            "Focus on portion control and eliminating sugary drinks/refined foods."
        ]
    }
    
    gender_txt = "Mr." if gender == "Male" else "Ms./Mrs." if gender == "Female" else "Patient"
    age_notes = ""
    if age > 60:
        age_notes = " Note: For individuals over 60, maintaining muscle mass and bone density is vital; avoid rapid weight changes without medical supervision."
    elif age < 18:
        age_notes = " Note: Standard BMI is calibrated for adults. Pediatric clinical charts should be consulted for comprehensive growth tracking."

    list_items = "".join([f"<li>{item}</li>" for item in recs.get(category, [])])
    
    return f"""
    <strong>Clinical Recommendations for {gender_txt} (Age {age}):</strong>
    <ul style='margin-top: 5px; padding-left: 20px;'>
        {list_items}
    </ul>
    <p style='margin-top: 5px; font-size: 0.85rem; font-style: italic;'>{age_notes}</p>
    """

# Sidebar for patient inputs
st.sidebar.markdown("""
<h2 style='color: #0A5C5A; margin-top: 0;'>📋 Patient Registration</h2>
""", unsafe_allow_html=True)

name = st.sidebar.text_input("Patient Name/ID", value="Guest Patient", placeholder="Enter name or patient ID")
gender = st.sidebar.radio("Gender", ["Male", "Female", "Other"])
age = st.sidebar.number_input("Age (Years)", min_value=1, max_value=120, value=30, step=1)

st.sidebar.markdown("---")
st.sidebar.markdown("<h3 style='color: #0A5C5A;'>📏 Height & Weight</h3>", unsafe_allow_html=True)

# Select height format
height_unit = st.sidebar.selectbox("Height Format", ["Feet & Inches", "Centimeters"])
if height_unit == "Feet & Inches":
    ft = st.sidebar.number_input("Feet", min_value=1, max_value=8, value=5, step=1)
    inch = st.sidebar.number_input("Inches", min_value=0, max_value=11, value=7, step=1)
    # Convert to meters
    total_inches = (ft * 12) + inch
    height_m = total_inches * 0.0254
    height_display = f"{ft}' {inch}\""
else:
    cm = st.sidebar.number_input("Height (cm)", min_value=30.0, max_value=250.0, value=170.0, step=0.5)
    height_m = cm / 100.0
    # Convert to ft & inch representation for table
    total_inches = height_m / 0.0254
    ft = int(total_inches // 12)
    inch = round(total_inches % 12, 1)
    height_display = f"{ft}' {inch}\""

# Weight input
weight_kg = st.sidebar.number_input("Weight (Kilograms)", min_value=1.0, max_value=500.0, value=70.0, step=0.5)

# Calculate button
save_btn = st.sidebar.button("🏥 Calculate & Record BMI", use_container_width=True)

# Load History Data
try:
    history_df = pd.read_csv(HISTORY_FILE)
except Exception:
    history_df = pd.DataFrame(columns=["Timestamp", "Name", "Gender", "Age", "Height_Ft_In", "Weight_Kg", "BMI", "Category"])

# Process current inputs or button press
current_bmi, category, cat_class = calculate_bmi(weight_kg, height_m)

if save_btn:
    # Append to CSV
    new_record = pd.DataFrame([{
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Name": name,
        "Gender": gender,
        "Age": int(age),
        "Height_Ft_In": height_display,
        "Weight_Kg": float(weight_kg),
        "BMI": float(current_bmi),
        "Category": category
    }])
    history_df = pd.concat([history_df, new_record], ignore_index=True)
    history_df.to_csv(HISTORY_FILE, index=False)
    st.sidebar.success(f"✓ Calculation recorded for {name}!")

# LAYOUT: Main Content
col_metric, col_gauge = st.columns([1, 1])

# Column 1: BMI Metric Card and Details
with col_metric:
    st.markdown(f"""
    <div class="result-card">
        <span class="stat-label">Current Analysis</span>
        <div class="stat-val">{current_bmi}</div>
        <span class="stat-label">Body Mass Index (BMI)</span>
        <div>
            <span class="category-box {cat_class}">{category}</span>
        </div>
        <div class="rec-box">
            {get_recommendations(category, age, gender)}
        </div>
    </div>
    """, unsafe_allow_html=True)

# Column 2: Plotly Gauge Indicator
with col_gauge:
    # Build a vibrant Speedometer Gauge Chart
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=current_bmi,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "BMI Health Classification Gauge", 'font': {'size': 20, 'color': '#0A5C5A', 'family': 'Outfit'}},
        gauge={
            'axis': {'range': [10, 40], 'tickwidth': 1, 'tickcolor': "#4B5563"},
            'bar': {'color': "#111827", 'thickness': 0.25}, # Dark needle/bar
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#E5E7EB",
            'steps': [
                {'range': [10, 18.5], 'color': '#DCEEFC'},   # Soft Blue
                {'range': [18.5, 25.0], 'color': '#D1FAE5'}, # Soft Green
                {'range': [25.0, 30.0], 'color': '#FEF3C7'}, # Soft Yellow/Orange
                {'range': [30.0, 40.0], 'color': '#FEE2E2'}  # Soft Red
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': current_bmi
            }
        }
    ))
    fig_gauge.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=50, b=20),
        height=320,
        font={'family': "Outfit"}
    )
    # Add annotations representing categories
    fig_gauge.add_annotation(x=0.15, y=0.15, text="Underweight<br>(<18.5)", showarrow=False, font=dict(color="#2A6CA6", size=10))
    fig_gauge.add_annotation(x=0.38, y=0.75, text="Healthy<br>(18.5-25)", showarrow=False, font=dict(color="#059669", size=10))
    fig_gauge.add_annotation(x=0.62, y=0.75, text="Overweight<br>(25-30)", showarrow=False, font=dict(color="#D97706", size=10))
    fig_gauge.add_annotation(x=0.85, y=0.15, text="Obese<br>(>=30)", showarrow=False, font=dict(color="#DC2626", size=10))
    
    st.plotly_chart(fig_gauge, use_container_width=True)

# SECTION: HISTORY & CLINICAL DASHBOARD
st.markdown('<div class="section-title">📊 Clinical History & Trend Dashboard</div>', unsafe_allow_html=True)

if not history_df.empty:
    # Filters
    patient_names = ["All Patients"] + sorted(history_df["Name"].unique().tolist())
    selected_patient = st.selectbox("Select Patient to Filter Dashboard & Trends", patient_names)
    
    # Filtered dataframe
    if selected_patient == "All Patients":
        filtered_df = history_df
    else:
        filtered_df = history_df[history_df["Name"] == selected_patient]
    
    # Dashboard Grid
    col_chart, col_table = st.columns([3, 2])
    
    with col_chart:
        st.subheader("BMI Progress Trend")
        if len(filtered_df) > 0:
            # Generate line chart
            # Ensure Timestamp is sorted
            trend_df = filtered_df.copy()
            trend_df['Timestamp'] = pd.to_datetime(trend_df['Timestamp'])
            trend_df = trend_df.sort_values('Timestamp')
            
            fig_trend = px.line(
                trend_df,
                x='Timestamp',
                y='BMI',
                color='Name' if selected_patient == "All Patients" else None,
                markers=True,
                title=f"BMI History for {selected_patient}",
                labels={'Timestamp': 'Check-in Date & Time', 'BMI': 'Body Mass Index'},
                color_discrete_sequence=['#149390', '#3A86C8', '#EF4444', '#F59E0B']
            )
            
            # Customizing line markers and grid
            fig_trend.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='#F9FAFB',
                margin=dict(l=20, r=20, t=50, b=20),
                height=350,
                font={'family': "Outfit"},
                xaxis=dict(showgrid=True, gridcolor='#E5E7EB'),
                yaxis=dict(showgrid=True, gridcolor='#E5E7EB')
            )
            # Add range highlights for healthy zone
            fig_trend.add_hrect(y0=18.5, y1=25.0, line_width=0, fillcolor="rgba(16, 185, 129, 0.1)", annotation_text="Healthy Range", annotation_position="top left")
            
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("No trend data available for the selection.")
            
    with col_table:
        st.subheader("Recent Patient Logs")
        
        # Sort recent first
        display_df = filtered_df.copy()
        display_df = display_df.iloc[::-1] # Reverse order
        
        # Display styled table
        st.dataframe(
            display_df,
            column_config={
                "Timestamp": "Date/Time",
                "Name": "Patient Name",
                "Age": st.column_config.NumberColumn("Age", format="%d"),
                "Height_Ft_In": "Height",
                "Weight_Kg": "Weight (Kg)",
                "BMI": st.column_config.NumberColumn("BMI", format="%.2f"),
                "Category": "Status"
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Clear logs button
        if st.button("🗑 Clear Log History", type="secondary"):
            if os.path.exists(HISTORY_FILE):
                os.remove(HISTORY_FILE)
                # Re-create empty file
                df_empty = pd.DataFrame(columns=[
                    "Timestamp", "Name", "Gender", "Age", 
                    "Height_Ft_In", "Weight_Kg", "BMI", "Category"
                ])
                df_empty.to_csv(HISTORY_FILE, index=False)
                st.toast("Logs cleared successfully!")
                st.rerun()

else:
    st.info("No health logs recorded yet. Register a patient and click 'Calculate & Record BMI' to start tracking.")
