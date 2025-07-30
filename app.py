import math
import re
import sys
import os
from machine_learning_dataset.train import evaluate_new_sample, build_keyboard_graph
import streamlit as st
import joblib

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
     
st.set_page_config(page_title="VulnerablePasswordSniff", layout="centered")

st.title("🔐 Password Strength Evaluator")

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

def evaluate_password(password):
    if check_length(password) < 12:
        st.error(f"Your password is {pswd_strength[0]}. Please insert a longer password.")
        st.session_state["Submitted"] = False
        return
    
    st.info("Length checking done.Checking common-passwords database...")

    if(check_common_passwords(password) == True):
        st.error(f"Your password is {pswd_strength[0]}. Password is a common used one.")
        st.session_state["Submitted"] = False
        return
    
    st.info("Nothing found in well known passwords.Proceeding to check for variety of chars...")

    if(check_letters(password) == False):
        st.error(f"Your password is {pswd_strength[0]}. Be sure that password has at least one uppercase, one lowercase, one digit and one symbol.")
        st.session_state["Submitted"] = False              
        return

    st.info("Variety of chars done. Let's use or RandomForest Model for a binary classification (Random-Keyboard-walked)")
                
    model, graph = load_model_and_graph()


    if (evaluate_new_sample(password, model, graph) == 1):
        st.error(f"Your password is {pswd_strength[1]}. Model classified password as keyboard-walk generated.")
        st.session_state["Submitted"] = False           
        return

    st.info(f"ML model classifies password as random. One last entropy check...")


    if(check_entropy(password) < ENTROPY_THERESHOLD):
        st.error(f"Your password is {pswd_strength[2]}. Your password is solid but it's entropy did not pass the required threshold.")
        st.session_state["Submitted"] = False           
        return

    st.success(f"Congratulations. Your password is {pswd_strength[3]}.")                
    st.session_state["Submitted"] = False

if st.session_state.get("Submitted"):
    password = st.session_state["password"]
    evaluate_password(password)