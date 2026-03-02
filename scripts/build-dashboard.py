import os
import pandas as pd
import matplotlib.pyplot as plt
from google import genai
from dotenv import load_dotenv

# ---------------------------------
# 1. Resolve project root dynamically
# ---------------------------------
# Ensures it works on your ThinkPad, in GitHub Actions, or from the scripts folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
DATA_PATH = os.path.join(BASE_DIR, "data", "processed_logbook.csv")

# Ensure the /docs directory exists before saving files
os.makedirs(DOCS_DIR, exist_ok=True)

OUTPUT_MD = os.path.join(DOCS_DIR, "dashboard.md")
OUTPUT_IMG = os.path.join(DOCS_DIR, "pain_trend.png")

# ---------------------------------
# 2. Gemini setup
# ---------------------------------
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("❌ MISSING API KEY: Check your .env file or GitHub Secrets.")

client = genai.Client(api_key=api_key)

# ---------------------------------
# 3. Chart Optimization (Dual-Axis & Dark Mode)
# ---------------------------------
def generate_visuals(df):
    # Ensure Date is datetime and sort for a chronological chart
    df["Date"] = pd.to_datetime(df["Date"])
    plot_df = df.sort_values("Date").tail(14)

    plt.style.use('dark_background')
    fig, ax1 = plt.subplots(figsize=(10, 5), facecolor="#121212")
    ax1.set_facecolor("#121212")

    # Primary Axis: Pain Score (The "Durability" Line)
    color_pain = '#ff5722' # Deep Orange
    ax1.set_ylabel('Pain (0-10)', color=color_pain, fontweight='bold')
    ax1.plot(plot_df["Date"], plot_df["Pain_Score"], color=color_pain, marker="o", linewidth=3, label="Pain Score")
    ax1.tick_params(axis='y', labelcolor=color_pain)
    ax1.set_ylim(-0.5, 10.5) # Extra padding for visibility

    # Secondary Axis: Distance (The "Volume" Bars)
    ax2 = ax1.twinx()
    color_dist = '#4caf50' # Marathon Green
    ax2.set_ylabel('Distance (km)', color=color_dist, fontweight='bold')
    # Match CSV column 'Distance'
    ax2.bar(plot_df["Date"], plot_df["Distance"], color=color_dist, alpha=0.2, label="Volume (km)")
    ax2.tick_params(axis='y', labelcolor=color_dist)

    plt.title('DURABILITY AUDIT: PAIN vs VOLUME', pad=20, fontweight='bold', color='white')
    
    # Clean up X-axis dates
    plt.xticks(rotation=45)
    fig.tight_layout()
    
    plt.savefig(OUTPUT_IMG, dpi=150)
    plt.close()

# ---------------------------------
# 4. AI Analysis (Prompt Optimization)
# ---------------------------------
def generate_analysis(df):
    # Sort for the coach to see the most recent status first
    recent_data = df.sort_values("Date", ascending=False).head(10).to_string()

    prompt = f"""
    ROLE: Ruthless Elite Endurance Coach.
    CONTEXT: Athlete 45+, targeting sub-3:15 marathon and sub-1:30 half-marathon. 
    CURRENT STATE: -10kg weight loss achieved. 
    TRAINING SPLIT: Wed/Thu, Sat, Sun training only. Other days are Soleus/Core/Glute isometrics.
    
    CRITERIA: Target Pain_Score = 0.
    
    TRAINING DATA (Last 10 sessions):
    {recent_data}
    
    TASK: Write a brutal, data-driven 200-word status update.
    - If Pain_Score > 2, highlight the correlation with Distance or Pace and call out the athlete's ego.
    - Evaluate Pace vs HR efficiency.
    - Use the metric system (km).
    - No sugarcoating. Be the coach that wins races.
    """

    try:
        # Using Gemini 2.5 Flash as requested
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"⚠️ Coach is offline. Analysis failed: {str(e)}"

# ---------------------------------
# 5. Build Dashboard Page
# ---------------------------------
def build_dashboard():
    if not os.path.exists(DATA_PATH):
        print(f"❌ ERROR: CSV not found at {DATA_PATH}")
        return

    df = pd.read_csv(DATA_PATH)
    
    # --- ROBUST DATA CLEANING ---
    # Standardize headers: Strip spaces and replace with underscores
    df.columns = df.columns.str.strip().str.replace(' ', '_')
    
    # Ensure columns exist, or create them to prevent crashes
    if 'Pain_Score' not in df.columns:
        df['Pain_Score'] = 0
    if 'Distance' not in df.columns:
        # Fallback if column is named Distance_km
        if 'Distance_km' in df.columns:
            df.rename(columns={'Distance_km': 'Distance'}, inplace=True)
        else:
            df['Distance'] = 0

    df['Pain_Score'] = df['Pain_Score'].fillna(0)
    # ----------------------------

    print("📊 Generating visuals (Pain vs Volume)...")
    generate_visuals(df)
    
    print("🧠 Consulting Gemini 2.5 Flash...")
    analysis = generate_analysis(df)

    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write("# 🏃 Performance Dashboard\n\n")
        f.write("![Pain Trend](pain_trend.png)\n\n")
        f.write("## 🧠 Gemini Resilience Audit\n\n")
        f.write(analysis)

    print(f"✅ Dashboard successfully updated at {OUTPUT_MD}")

if __name__ == "__main__":
    build_dashboard()