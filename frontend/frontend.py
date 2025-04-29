import requests
import streamlit as st
import pandas as pd
import numpy as np
import json

from extract_email import get_emails,move_to_spam

url_predict = "http://localhost:6000/predict"
url_retrain = "http://localhost:6000/train"

if "bodies" not in st.session_state:
    st.session_state.bodies = None
if "mail_ids" not in st.session_state:
    st.session_state.mail_ids = None
if "my_mail" not in st.session_state:
    st.session_state.my_mail = None
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "has_spam" not in st.session_state:
    st.session_state.has_spam = False
if "spam_mail_ids" not in st.session_state:
    st.session_state.spam_mail_ids = None
if "predictions" not in st.session_state:
    st.session_state.preictions = None
if "feedback" not in st.session_state:
    st.session_state.feedback = None
if "feedback_data" not in st.session_state:
    st.session_state.feedback_data = None
if "feedback_labels" not in st.session_state:
    st.session_state.feedback_labels = None
# ------------------- Page Config -------------------
st.set_page_config(
    page_title="Spam Shield",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------- Sidebar -------------------
with st.sidebar:
    st.title("Navigation")
    page = st.radio("Go to", ["Home", "Paste Email", "Upload CSV file", "Integrate with Gmail","User Manual","Pipelines","About"])

# ------------------- Home Page -------------------
if page == "Home":
    st.title("🛡️ Welcome to Spam Shield")
    st.markdown("""
    ### 📬 Your Personal Email Spam Filter, Powered by AI

    Spam Shield helps you:
    - 📧 **Scan your Gmail inbox** for spam
    - 🧠 **Give feedback** and improve predictions
    - 📄 **Upload CSV files** of emails for batch processing
    - 🛠️ **Retrain the model** with your feedback
    - 🧪 **Test individual emails** in real time

    ---
    👉 Use the sidebar to explore different features.
    
    💡 Start with **"Integrate with Gmail"** to try it on your real inbox!
    """)

# ------------------- Upload Page -------------------
elif page == "Upload CSV file":
    st.title("📤 Upload Your File")

    st.markdown("""
    Please make sure that the csv has a column called 'Message' which has the bodies of all the emails
    """)
    
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

        if "Message" not in df.columns:
            st.error("CSV must contain a 'Message' column.")
        else:
            st.success("File uploaded successfully!")
            st.write("Preview of data:")
            st.dataframe(df.head())
        
            if st.button("Predict Spam"):
                df["Message"] = df["Message"].astype("str")
                email_texts = df["Message"].tolist()
                res = requests.post(url_predict, json={"emails": email_texts})

                if res.status_code == 200:
                    predictions = res.json()["predictions"]
                    df["Spam/Ham"] = predictions  # Adding predictions to DataFrame

                    st.success("Predictions completed ✅")
                    st.dataframe(df)

                    # Converting to downloadable CSV
                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="📥 Download CSV with Predictions",
                        data=csv,
                        file_name="predicted_emails.csv",
                        mime="text/csv",
                    )
                else:
                    st.error(f"Prediction failed: {res.text}")
        



elif page == "Integrate with Gmail":
    st.title("📧 Login to Gmail")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            my_mail, mail_ids, bodies = get_emails(username, password)
            st.success("Login successful ✅")
            st.session_state.bodies = bodies  # Save bodies
            st.session_state.mail_ids = mail_ids
            st.session_state.my_mail = my_mail
            st.session_state.logged_in = True  # Mark login successful
            st.write("Fetched New Emails:", bodies)


        except Exception as e:
            st.error(f"Login failed: {e}")

    
    if st.session_state.logged_in:
        if st.session_state.bodies:
            if st.button("Check for Spam"):
                bodies = st.session_state.bodies
                mail_ids = st.session_state.mail_ids 
                my_mail = st.session_state.my_mail 
                res = requests.post(url_predict, json={"emails":bodies})    
                predictions = res.json()["predictions"]
                
                st.session_state.predictions = predictions
                
                
            if "predictions" in st.session_state:
                predictions = st.session_state.predictions
                bodies = st.session_state.bodies
                mail_ids = st.session_state.mail_ids 
                my_mail = st.session_state.my_mail 

                feedback_data = []
                feedback_labels = []

                for i in range(len(bodies)):

                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(bodies[i])
                    with col2:
                        st.write(predictions[i])
                    
                    
                    feedback = st.radio(
                            f"Was prediction for Email {i+1} correct?",
                            ("Yes", "No"),
                            key=f"feedback_{i}"
                        )

                    if feedback == "No":
                        st.session_state.feedback = True
                        correct_label = st.radio(
                            f"Correct label for Email {i+1}?",
                            ("Spam", "Not Spam"),
                            key=f"correct_{i}"
                        )
                        if correct_label == "Spam":
                            predictions[i] = "spam"
                        else:
                            predictions[i] = "ham"
                        feedback_data.append(bodies[i])
                        feedback_labels.append(predictions[i])
                    st.markdown("---")
                
                st.session_state.feedback_data = feedback_data
                st.session_state.feedback_labels = feedback_labels

                spam_mail_ids = []
                for i in range(len(predictions)):
                    if predictions[i] == "spam":
                        spam_mail_ids.append(mail_ids[i])

                st.session_state.spam_mail_ids = spam_mail_ids
                
                if spam_mail_ids is not None:
                    st.session_state.has_spam = True

                if st.session_state.has_spam:
                    if st.button(f"Move spam emails to spam folder"):
                        spam_mail_ids = st.session_state.spam_mail_ids
                        my_mail = st.session_state.my_mail
                        move_to_spam(my_mail,spam_mail_ids)
                        st.success(f"Moved to spam")
                
                if st.session_state.feedback:
                    if st.button("Retrain Model with Feedback"):
                        feedback_data = st.session_state.feedback_data 
                        feedback_labels = st.session_state.feedback_labels 
                        res = requests.post(url_retrain, json={"feedback_data":feedback_data,"feedback_labels":feedback_labels}) 
                        msg = res.json()["message"]
                        st.success(msg)
                        st.session_state.feedback = None

        else:
            st.success(f"No new mails received")

        if st.button(f"Logout"):
            st.session_state.clear()

            

# ------------------- Predict Page -------------------
elif page == "Paste Email":

    email_input = st.text_area("Paste your email content here")
    if st.button("Check for Spam"):
        try:
            res = requests.post(url_predict, json={"emails": [email_input]})
            if res.status_code == 200:      
                st.write("Prediction:", res.json()["predictions"][0])
            else:
                st.error("Error with the prediction service. Please try again later.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

# ------------------- Pipeline -------------------
elif page == "Pipelines":

    st.markdown("""
                📨 Checking a Single Email
                """)
    st.graphviz_chart('''
    digraph G {
        rankdir=LR;
        node [shape=box];
        "User pastes Input" -> "Text Preprocessing" -> "ML Model Prediction" -> "Spam / Not Spam Decision";
    }
    ''')
    st.markdown("---")
                
    st.markdown("""
                📤 Predicting for a CSV
                """)
    st.graphviz_chart('''
    digraph G {
        rankdir=LR;
        node [shape=box];
        "Upload CSV" -> "Extract Data from CSV" -> "Text Preprocessing" -> "ML Model Prediction" -> "Spam / Not Spam Decisions" -> "Output CSV with predictions";
    }
    ''')
    st.markdown("---")

    st.markdown("""
                📧 Integrating with Gmail
                """)
    st.graphviz_chart('''
    digraph G {
        rankdir=LR;
        node [shape=box];
        "Login to Gmail" -> "Fetch unread emails" -> "Create Dataset" -> "Text Preprocessing" -> "ML Model Prediction" -> "Spam / Not Spam Decision" -> "User Feedback" -> "Reorganize emails" -> "Model Retraining based on feedback";
    }
    ''')
    st.markdown("---")
    
elif page == "User Manual":
    st.title("📘 User Manual - Spam Shield")

    st.markdown("""
    Follow this guide to use the application smoothly:
    ---

    ## 🧭 1. Navigation Overview
    | Page | Purpose |
    |:-----|:--------|
    | Home | Welcome and basic info |
    | Paste Email | Check a single email manually |
    | Upload CSV file | Upload dataset to detect spam |
    | Integrate with Gmail | Connect directly to Gmail to detect spam |
    | User Manual | User instructions and help |
    | Pipelines | ML - pipeline visualizaiton |
    | About | App and author info |
    
    ## 📨 2. Checking a Single Email
    - Paste an email manually under **Paste Email**.
    - Click **Check for Spam** to instantly predict.
                
    ## 📤 3. Uploading Your Email Dataset
    - Navigate to **Upload CSV file**.
    - Upload a `.csv` file with email texts under a column named 'Message'.
    - Preview your uploaded data in the app.
    - Get Predictions for every datapoint in the csv.
    - You can download the csv with predictions.

    ## 📧 4. Integrating with Gmail
    1. Go to **Integrate with Gmail**.
    2. Enter Gmail **username** and **password**.
    3. Click **Login** to fetch new unread mails from your inbox.
    4. Click **Check for Spam** to scan emails.
    5. Review predictions and give feedback if needed.
    6. Move detected spam to your Spam folder.
    7. Retrain the model with your feedback for better accuracy.

    """, unsafe_allow_html=True)

# ------------------- About Page -------------------
elif page == "About":
    st.title("📖 About")
    st.write("""
    - **App**: Spam Shield
    - **Made by**: C.S.Akharan (CH21B009)
    - **GitHub**: [Link](https://github.com/yourprofile)
    """)

# ------------------- Footer -------------------
st.markdown(
    """
    <hr style="border:1px solid gray">
    <center>
    Made by CH21B009 using Streamlit.
    </center>
    """, unsafe_allow_html=True
)