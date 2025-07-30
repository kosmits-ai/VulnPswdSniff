from .keyboard_walk_passwords import store_passwords as store_keyboard_passwords
from .keyboard_walk_passwords import create_keyboard_walk_passwords 
from .random_pswds import store_passwords as store_random_passwords
from .random_pswds import generate_random_passwords 
import pandas as pd
import string
import math
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, precision_score
from sklearn.ensemble import RandomForestClassifier
import os
import joblib
import networkx as nx


keyboard_rows = [
    ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '='],
    ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\'],
    ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', "'"],
    ['z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/']
]


def build_keyboard_graph():
    G = nx.Graph()
    for row_idx, row in enumerate(keyboard_rows):
        for col_idx, key in enumerate(row):
            G.add_node(key)
            if col_idx > 0 :
                G.add_edge(key, row[col_idx - 1])
            if col_idx < len(row) - 1:
                G.add_edge(key, row[col_idx + 1])
            if row_idx > 0 and col_idx < len(keyboard_rows[row_idx - 1]):
                G.add_edge(key, keyboard_rows[row_idx - 1][col_idx])  # above
                if col_idx > 0:
                    G.add_edge(key, keyboard_rows[row_idx - 1][col_idx - 1])  # top-left
                if col_idx + 1 < len(keyboard_rows[row_idx - 1]):
                    G.add_edge(key, keyboard_rows[row_idx - 1][col_idx + 1])  # top-right
            if row_idx + 1 < len(keyboard_rows) and col_idx < len(keyboard_rows[row_idx + 1]):
                G.add_edge(key, keyboard_rows[row_idx + 1][col_idx])  # below
                if col_idx > 0:
                    G.add_edge(key, keyboard_rows[row_idx + 1][col_idx - 1])  # bottom-left
                if col_idx + 1 < len(keyboard_rows[row_idx + 1]):
                    G.add_edge(key, keyboard_rows[row_idx + 1][col_idx + 1])  # bottom-right

    
    return G

def contains_keyboard_walk(password):
    keyboard_patterns = [
        "qwerty", "asdfgh", "zxcvbn", "qwer", "asdf", "zxcv",
        "werty", "sdfgh", "xcvbn", "erty", "dfgh", "cvbnm",
        "1234", "2345", "3456", "4567", "5678", "6789", "7890",
        "1qaz", "2wsx", "3edc", "4rfv", "5tgb", "6yhn", "7ujm", "8ik,", "9ol.", "0p;/",
        "qaz", "wsx", "edc", "rfv", "tgb", "yhn", "ujm", "ik,", "ol.", "p;/",
        "QWERTY", "ASDFGH", "ZXCVBN", "QAZ", "WSX", "EDC"
    ]
    pswd_lower = password.lower()
    return int(any(pattern.lower() in pswd_lower for pattern in keyboard_patterns))



def count_neighbor_parts(password, graph):
    password = password.lower()
    count = 0
    for i in range(len(password) - 1):
        c1,c2 = password[i], password[i+1]
        if c1 in graph and c2 in graph:
            if graph.has_edge(c1,c2):
                count += 1
    return count 
                    
def extract_features(password, graph):
    length = len(password)
    uppercase_count = sum(1 for c in password if c.isupper())
    lowercase_count = sum(1 for c in password if c.islower())
    digit_count = sum(1 for c in password if c.isdigit())
    special_count = sum(1 for c in password if c in string.punctuation)
    unique_chars = len(set(password))
    prob = [password.count(c) / len(password) for c in set(password)]
    entropy_char = -sum(p * math.log2(p) for p in prob)
    entropy = entropy_char * len(password)
    pattern = contains_keyboard_walk(password)
    neighbors = count_neighbor_parts(password, graph)
    return [length, uppercase_count, lowercase_count, digit_count, special_count, unique_chars,entropy, pattern, neighbors]

def prepare_dataset(csv_path = "model_password_dataset.csv", regenerate = False):
    if os.path.exists(csv_path) and not regenerate:
        df = pd.read_csv(csv_path)
        print("Dataset from CSV loaded.")
    else:
        print("Generating new dataset")
        keyboard_passwords = create_keyboard_walk_passwords(1000)
        random_passwords = generate_random_passwords(1000)

        keyboard_labeled = store_keyboard_passwords(keyboard_passwords)  # label 0
        random_labeled = store_random_passwords(random_passwords)      # label 1

        # Combine both lists
        full_dataset = keyboard_labeled + random_labeled
        df = pd.DataFrame(full_dataset, columns =['Name', 'Label'])

        df.to_csv(csv_path, index=False)
        #extract features from string password
        features = df['Name'].apply(lambda pw: extract_features(pw, graph))
        features_df = pd.DataFrame(features.tolist(), columns = ['length', 'uppercase', 'lowercase', 'digits', 'special', 'unique_chars', 'entropy', 'pattern', 'neighbors'])

        #combine features with Label for final dataframe
        final_df = pd.concat([features_df, df['Label']], axis = 1)
        print(final_df.head())


        #split X and Y features
        X = final_df.drop('Label', axis = 1)
        Y = final_df['Label']
        
        return X, Y



def evaluate_new_sample(password, model, graph):
    metrics = extract_features(password, graph)
    new_features_df = pd.DataFrame([metrics], columns=[
        'length', 'uppercase', 'lowercase', 'digits', 'special', 'unique_chars', 'entropy', 'pattern', 'neighbors'
    ])
    
    prediction = model.predict(new_features_df)[0]  
    return prediction


def train_model(X,Y):

    #split train and test dataset
    X_train, X_test, y_train, y_test = train_test_split(
        X, Y, test_size=0.2, random_state=42
    )

    # clf = LogisticRegression(max_iter = 500, random_state= 42)
    # clf.fit(X_train, y_train)

    # y_probs = clf.predict_proba(X_test)[:, 1]
    # threshold = 0.6
    # y_pred_custom = (y_probs >= threshold).astype(int)


    # roc_auc = roc_auc_score(y_test, y_pred_custom)
    # print(f"ROC AUC Score: {roc_auc:.3f}")

    # acc = accuracy_score(y_test, y_pred_custom) * 100
    # print(f"Logistic Regression model accuracy: {acc:.2f}%")

    # precision = precision_score(y_test,y_pred_custom)
    # print(f"Logistic Regression model precision: {precision:.2f}%")

    clf = RandomForestClassifier(n_estimators=800, random_state = 42)
    clf.fit(X_train, y_train)

    y_train_pred = clf.predict(X_train)
    y_test_pred = clf.predict(X_test)

    train_acc = accuracy_score(y_train, y_train_pred)
    print(f"Training acc is {train_acc:.3f}")


    roc_auc = roc_auc_score(y_test, y_test_pred)
    print(f"ROC AUC Score: {roc_auc:.3f}")

    acc = accuracy_score(y_test, y_test_pred) * 100
    print(f"Random forest accuracy: {acc:.2f}%")

    precision = precision_score(y_test,y_test_pred)
    print(f"Random forest precision: {precision:.2f}%") #I want high precision because i don't want false positives (keyboard-walked passwords marked as safe)

    test_acc = accuracy_score(y_test, y_test_pred)
    print(f"Testing acc is {test_acc:.3f}")

    joblib.dump(clf, "keyboard_walk_model.pkl")

    print("Model saved.")


if __name__ == '__main__':
    graph = build_keyboard_graph()
    X, Y = prepare_dataset("model_password_dataset.csv", True)
    train_model(X,Y)




