import streamlit as st
import pandas as pd
import os
import subprocess
from datetime import datetime

# --- CONFIGURATION ---
DATA_FILE = "gpu_log.csv"

# --- DATA HANDLING ---
def load_data():
    # Check if file exists AND is not empty (size > 0)
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        # Create empty dataframe if file doesn't exist or is empty
        df = pd.DataFrame(columns=["User", "Activity", "Start Time", "End Time", "Status"])
        df.to_csv(DATA_FILE, index=False)
        return df
    
    try:
        return pd.read_csv(DATA_FILE)
    except pd.errors.EmptyDataError:
        # Failsafe: If pandas still thinks it's empty, reset it
        df = pd.DataFrame(columns=["User", "Activity", "Start Time", "End Time", "Status"])
        df.to_csv(DATA_FILE, index=False)
        return df

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# --- PAGE CONFIG ---
st.set_page_config(page_title="GPU Server Manager", layout="wide")

# --- TOAST LOGIC (Must run at the start of the script) ---
if 'show_reminder' in st.session_state and st.session_state['show_reminder']:
    st.toast("✅ Session Started! Please remember to click **'Stop'** when you are done.", icon="🔔")
    st.session_state['show_reminder'] = False 

st.title("🚦 GPU Server Manager")

# Load data
df = load_data()

# --- SIDEBAR: SERVER HEALTH & CONTROLS ---
with st.sidebar:
    st.header("Server Status")
    
    # Refresh Button
    if st.button("🔄 Refresh Data"):
        st.rerun()
    
    st.divider()
    
    # GPU Real-time Stats
    st.subheader("Live Hardware Stats")
    try:
        cmd_output = subprocess.getoutput("gpustat -cp") 
        st.code(cmd_output, language="bash")
    except:
        st.error("Could not fetch GPU stats")

    st.divider()
    
    # RESTART CONTROLS
    st.header("⚠️ Admin Controls")
    st.warning("Restarting affects ALL users.")
    restart_confirm = st.checkbox("I confirm restart")
    if st.button("🚨 RESTART SERVER"):
        if restart_confirm:
            st.error("Restarting...")
            os.system("sudo shutdown -r now")
        else:
            st.error("Check the box to confirm.")

# --- MAIN AREA: NEW SESSION (FORM) ---
st.subheader("1. Start a New Task")

# clear_on_submit=True wipes the text boxes after the button is clicked
with st.form("entry_form", clear_on_submit=True):
    c1, c2, c3 = st.columns([2, 3, 1])
    with c1:
        # user_name input
        user_name = st.text_input("Your Name", placeholder="e.g. Alice")
    with c2:
        # activity input
        activity = st.text_input("Activity/Model", placeholder="e.g. Training Llama-3 (12 hours)")
    with c3:
        st.write("") # Vertical spacer to align button
        st.write("") 
        # Form Submit Button (Triggers on Enter key inside inputs)
        submitted = st.form_submit_button("🚀 Start Using GPU")

    # LOGIC: What happens when they submit
    if submitted:
        if user_name and activity:
            new_entry = pd.DataFrame([{
                "User": user_name, 
                "Activity": activity, 
                "Start Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                "End Time": None,
                "Status": "Active"
            }])
            df = pd.concat([df, new_entry], ignore_index=True)
            save_data(df)
            
            # Set flag for toast
            st.session_state['show_reminder'] = True
            st.rerun()
        else:
            st.warning("Please fill in both Name and Activity.")

st.divider()

# --- MAIN AREA: ACTIVE SESSIONS ---
st.subheader("2. Currently Active Users")

active_df = df[df["Status"] == "Active"]

if active_df.empty:
    st.info("No one is manually reporting usage right now.")
else:
    for index, row in active_df.iterrows():
        col1, col2, col3, col4 = st.columns([2, 3, 2, 1])
        col1.write(f"**👤 {row['User']}**")
        col2.write(f"📝 {row['Activity']}")
        col3.write(f"⏰ Started: {row['Start Time']}")
        
        # Stop button (Outside the form, so it works independently)
        if col4.button("🏁 Stop", key=f"stop_{index}"):
            df.at[index, "End Time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df.at[index, "Status"] = "Finished"
            save_data(df)
            st.rerun()

st.divider()

# --- MAIN AREA: HISTORY ---
with st.expander("📜 View Usage History"):
    history_df = df[df["Status"] == "Finished"].sort_index(ascending=False)
    st.dataframe(history_df, use_container_width=True)