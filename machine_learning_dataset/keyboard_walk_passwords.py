import random

keyboard_walks = [
    "qwerty", "asdfgh", "zxcvbn", "123456", "1qaz2wsx", "qazwsx", 
    "poiuy", "lkjhg", "mnbvc", "098765", "0p9o8i", "qweasd", 
    "qwerasdf", "wsxedc", "plmokn", "ujmnhy", "1q2w3e", "3edc", 
    "qaz", "wsx", "edc", "rfv", "tgb", "yhn", "ujm", "ik,", "ol.", 
    "p;/", "l;'k", "a;s'd", "sdfghj", "zxcvbnm"
]

patterns = [
    "duplicate",       # Repeat part of the walk (e.g., qwertyqwerty)
    "remain",          # Use the pattern as-is
    "reverse",         # e.g., "qwerty" → "ytrewq"
    "capitalize",      # Capitalize first letter or all
    "leet",            # Substitute letters with similar-looking numbers/symbols (e.g., "a"→"@", "e"→"3")
    "append_number",   # Add digits to the end (e.g., qwerty123)
    "prepend_number",  # Add digits to the beginning
    "sandwich",        # Add a number or symbol at both ends
    "symbol_insert",   # Insert a symbol in the middle
    "uppercase_mix",   # Randomly capitalize some letters
    "shift_keys",      # Replace with shifted versions of keys (e.g., q → Q, 1 → !)
    "mirror",          # e.g., qwe → qweewq
    "insert_year",     # Add common years like "2020", "2023" at the end
]

def leet_replace(s):
    leet_dict = {'a':'@', 'e':'3', 'i':'1', 'o':'0', 's':'$', 't':'7'}
    return ''.join(leet_dict.get(c.lower(), c) for c in s)

def symbol_insert(s):
    if len(s) < 2:
        return s
    symbols = "!@#$%^&*"
    index = random.randint(1, len(s) - 1)
    return s[:index] + random.choice(symbols) + s[index:]

def random_uppercase_mix(s):
    num = random.randint(1, len(s) - 1)
    final_password = s
    for _ in range(num):
        index = random.randint(0, len(final_password) - 1)
        password =  final_password[:index] + final_password[index].upper() + final_password[(index+1):]
        final_password = password
    return final_password

def shift_keys(s):
    result = []
    shift_map = {
    '1': '!', '2': '@', '3': '#', '4': '$', '5': '%',
    '6': '^', '7': '&', '8': '*', '9': '(', '0': ')'
    }
    for c in s:
        if c.isdigit() and c in shift_map:
            result.append(shift_map[c])
        elif c.isalpha() :
            result.append(c.upper())
        else:
            result.append(c)
    return ''.join(result)

def create_keyboard_walk_passwords(number, min_length = 8, max_length = 15):
    passwords = []
    counter = 0
    years = ["2020", "2021", "2022", "2023", "2024", "2025"]
    symbols = "!@#$%^&*"
    while (counter < number):
        pattern_selection = random.choice(patterns)
        while True:
            combo = random.choice(keyboard_walks) + random.choice(keyboard_walks)
            if len(combo) >= 8:
                keyboard_walk = combo
                break

        if (pattern_selection == "duplicate"):
            password = keyboard_walk + keyboard_walk
            
        elif (pattern_selection == "remain"):
            password = keyboard_walk

        elif (pattern_selection == "reverse"):
            password = keyboard_walk[::-1]
            
        elif (pattern_selection == "capitalize"):
            password = keyboard_walk.capitalize()

        elif (pattern_selection == "leet"):
            password = leet_replace(keyboard_walk)

        elif (pattern_selection == "append_number"):
            password = keyboard_walk + str(random.randint(10, 999))
            
        elif pattern_selection == "prepend_number":
            password = str(random.randint(10, 999)) + keyboard_walk
            
        elif pattern_selection == "sandwich":
            password = random.choice(symbols) + keyboard_walk + random.choice(symbols)
            
        elif pattern_selection == "symbol_insert":
            password = symbol_insert(keyboard_walk)
            
        elif pattern_selection == "uppercase_mix":
            password = random_uppercase_mix(keyboard_walk)
            

        elif pattern_selection == "shift_keys":
            password = shift_keys(keyboard_walk)
            

        elif pattern_selection == "mirror":
            password = keyboard_walk + keyboard_walk[::-1]
            

        elif pattern_selection == "insert_year":
            password = keyboard_walk + random.choice(years)
            
        else:
            password = keyboard_walk  # fallback
            


        if min_length <= len(password) <= max_length:
            passwords.append(password)
            counter += 1

    return passwords

def store_passwords(passwords):
    label_data = []
    with open("keyboard_walk_pswds.txt" , 'w') as file:
        for pswd in passwords:
            file.write(pswd + '\n')
            label_data.append((pswd, 1))
    print(f"{len(passwords)} passwords stored in keyboard_walk_pswds.txt")
    return label_data

