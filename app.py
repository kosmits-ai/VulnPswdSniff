import math
import re
import requests
from machine_learning_dataset.train import evaluate_new_sample, build_keyboard_graph
import streamlit as st
import joblib
from zxcvbn import zxcvbn
from streamlit_lottie import st_lottie
import pandas as pd

ENTROPY_THERESHOLD = 80   
pswd_strength = ['Weak', 'Medium' , 'Strong', 'Very Strong']

def load_model_and_graph():
       model = joblib.load("keyboard_walk_model.pkl")
       graph = build_keyboard_graph()
       return model, graph

def check_length(pswd):
    return len(pswd)

def check_common_passwords(pswd):
    common_passwords = set()        #set is faster data structure than a list for checking existance of pswd
    with open("common_passwords.txt", encoding = 'utf-8') as file:
        for item in file:
            common_passwords.add(item.strip())
    if pswd in common_passwords:
            return True
    return False

def check_entropy(pswd):
    # Calculate probability of each unique character
    prob = [pswd.count(c) / len(pswd) for c in set(pswd)]
    
    # Apply Shannon entropy formula
    entropy_char = -sum(p * math.log2(p) for p in prob)         #Shannon bits for whole password string. If H = total_entropy a brute force attackers would need 2^H guesses.
    return (entropy_char * len(pswd))

def check_letters(pswd):                    #ensure that a password has at least one lowercase, one uppercase, one digit, one symbol
      digit = any(char.isdigit() for char in pswd)
      uppercase = any(char.isupper() for char in pswd)
      lowercase = any(char.islower() for char in pswd)
      regex = re.compile('[@_!#$%^&*()<>?/\\|}{~:]')
      if(regex.search(pswd) == None):
          symbol = False
      else:
          symbol = True   
      if (digit and uppercase and lowercase and symbol):
           return True
      else:
           return False

def evaluate_password(password):
    score = 0
    negative_feedback = []
    positive_feedback = []
    if check_length(password) < 12:
        negative_feedback.append(f"Please insert a longer password.")
        score = 1
        result = pswd_strength[0]
        return score, positive_feedback, negative_feedback, result
    
    positive_feedback.append("Length checking passed successfully.")

    if(check_common_passwords(password) == True):
        negative_feedback.append(f"Password is a common used one, found in common_pswds database.")
        score = 1
        result = pswd_strength[0]
        return score, positive_feedback, negative_feedback, result
    
    positive_feedback.append("Nothing found in common_passwords database.")

    if(check_letters(password) == False):
        negative_feedback.append(f"Be sure that password has at least one uppercase, one lowercase, one digit and one symbol.")
        model, graph = load_model_and_graph()
        if (evaluate_new_sample(password, model, graph) == 1):
            negative_feedback.append("Model classified password as keyboard-walk generated.")
            score = 1
            result = pswd_strength[0]
            return score, positive_feedback, negative_feedback, result

        positive_feedback.append(f"ML model classifies password as random.")

        if(check_entropy(password) < ENTROPY_THERESHOLD):
            negative_feedback.append(f"Password entropy did not pass the required threshold.")
            score = 2
            result = pswd_strength[1]
            return score, positive_feedback, negative_feedback, result
        
        result = pswd_strength[2] 
        positive_feedback.append(f"Password's entropy is bigger than the required threshold.")  
        score = 3
        return score, positive_feedback, negative_feedback, result
    

    positive_feedback.append("Password has at least one upperace, lowercase, digit, symbol.")

                
    model, graph = load_model_and_graph()

    if (evaluate_new_sample(password, model, graph) == 1):
        negative_feedback.append("Model classified password as keyboard-walk generated.")
        score = 2
        result = pswd_strength[1]       
        return score, positive_feedback, negative_feedback, result

    positive_feedback.append(f"ML model classifies password as random.")


    if(check_entropy(password) < ENTROPY_THERESHOLD):
        negative_feedback.append(f"Password entropy did not pass the required threshold.")
        score = 3
        result = pswd_strength[2]
        return score, positive_feedback, negative_feedback, result

    result = pswd_strength[3] 
    positive_feedback.append(f"Password's entropy is bigger than the required threshold.")  
    score = 4

    st.session_state["Submitted"] = False

    return score, positive_feedback, negative_feedback, result

def set_bar(score):
    score_color = {
          1 : 'red',
          2 : 'yellow',
          3 : 'lightgreen',
          4 : 'green'
     }
       
    st.markdown(f"""
    <div style="background-color: lightgray; border-radius: 5px; padding: 3px;">
        <div style="width: {(score / 4) * 100}%; background-color: {score_color[score]}; height: 20px; border-radius: 5px;"></div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("\n")


def get_crack_time(password):
    result = zxcvbn(password)
    return result

def load_lottie_url():
    r = requests.get("https://lottie.host/60d84093-9040-425c-b27e-fcc085ae0eb7/PJpfeaxksO.json")
    if r.status_code != 200:
        return None
    else:
        return r.json()

def create_results_table(positive_feedback: list, negative_feedback: list):
    
    max_len = max(len(positive_feedback), len(negative_feedback))
    positive_feedback += [""] * (max_len - len(positive_feedback))
    negative_feedback += [""] * (max_len - len(negative_feedback))

    # Create the DataFrame
    df = pd.DataFrame({
        'Positive': positive_feedback,
        'Negative': negative_feedback
    })

    return df


def highlight_column(col, color):
    return [f'color: {color}; font-size: 16px;' for _ in col]


st.set_page_config(page_title="VulnerablePasswordSniff", layout="centered")
lottie_animation = load_lottie_url()

if lottie_animation:
    st_lottie(lottie_animation, speed=1, height=300, key="password_animation")
else:
    st.warning("⚠️ Could not load Lottie animation.")

    
st.subheader("Welcome to VulnPswdSniff", divider = "orange")

if "Submitted" not in st.session_state:
     st.session_state["Submitted"] = False

with st.form("password_form"):
    password = st.text_input("Enter your password", type="password")
    submitted = st.form_submit_button("Evaluate")

if submitted:
     st.session_state["Submitted"] = True
     st.session_state["password"] = password

if st.session_state["Submitted"]:
    password = st.session_state["password"]

if st.session_state.get("Submitted"):
    password = st.session_state["password"]
    score, positive_feedback, negative_feedback, result = evaluate_password(password)
    
    result = get_crack_time(password)
    crack_time = result['crack_times_display']['offline_fast_hashing_1e10_per_second']

    strength_results = {
         1: "❌ Weak",
         2: "⚠️ Medium",
         3: "✅ Strong",
         4: "🏆 Very Strong"
    }
    st.subheader(f"Strength bar: {strength_results[score]}")          

    set_bar(score)
    
    st.markdown("---")

    
    col1, col2, col3 = st.columns([12, 0.5, 4])

    with col1:
        df = create_results_table(positive_feedback, negative_feedback)
        df.index = range(1, len(df) + 1)
        styled_df = (
            df.style
            .apply(highlight_column, color="lime", subset=["Positive"])
            .apply(highlight_column, color="red", subset=["Negative"])
            .set_properties(**{
                'background-color': '#1c1c1c',
                'text-align': 'left',
                'padding': '10px',
                'border': '1px solid #444'
            })
        )

        # ✅ Render styled DataFrame in Streamlit
        st.markdown(styled_df.to_html(), unsafe_allow_html=True)
    
    with col2:
        st.markdown(
            """
            <div style='display: flex; justify-content: center; align-items: center; height: 100%;'>
                <div style='border-left: 4px solid gray; height: 100%;'></div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
        f"""
        <div style='
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100%;
            padding-top: 80px;
        '>
            <div style='
                width: 300px;
                height: 200px;
                background-color: transparent;
                border-radius: 50%;
                border: 3px solid yellow;
                display: flex;
                justify-content: center;
                align-items: center;
                color: yellow;
                font-weight: bold;
                font-size: 14px;
                text-align: center;
                padding: 10px;
            '>
                Can be<br>cracked in<br>{crack_time}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

       
    
    


   


