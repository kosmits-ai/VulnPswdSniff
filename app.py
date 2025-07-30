import math
import re
import sys
import os
from machine_learning_dataset.train import evaluate_new_sample, build_keyboard_graph


import joblib

ENTROPY_THERESHOLD = 80   


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
     


pswd_strength = ['Weak', 'Medium' , 'Strong', 'Very Strong']
#password = str(input("Please insert your code."))

if __name__ == "__main__":
     password = str(input("Please insert your password  =>  "))
     if check_length(password) < 12:
          print(f"\nYour password is {pswd_strength[0]}. Please insert a longer password.")
          exit()
     print("Length checking done.Checking common-passwords database...")

     if(check_common_passwords(password) == True):
          print(f"\nYour password is {pswd_strength[0]}. {password} is a common used password.")
          exit()
          
     print("\nNothing found in well known passwords.Proceeding to check for variety of chars...")
     
     if(check_letters(password) == False):
                    print(f"\nYour password is {pswd_strength[0]}. Be sure that {password} has at least one uppercase, one lowercase, one digit and one symbol.")
                    exit()
     
     
     print("\nVariety of chars done. Let's use or RandomForest Model for a binary classification (Random-Keyboard-walked)")
                    
     graph = build_keyboard_graph()
     model = joblib.load("keyboard_walk_model.pkl")

     
     if (evaluate_new_sample(password, model, graph) == 1):
                    print(f"\nYour password is {pswd_strength[1]}. Model classified {password} as keyboard-walk generated.")
                    exit()
     
     
     print(f"\nML model classifies {password} as random. One last entropy check...")
     
     print(check_entropy(password))
     if(check_entropy(password) < ENTROPY_THERESHOLD):
                    print(f"\nYour password is {pswd_strength[2]}. Your password is solid but it's entropy did not pass the required threshold.")
                    exit()
     
     
     print(f"\nCongratulations. Your password is {pswd_strength[3]}.")                


