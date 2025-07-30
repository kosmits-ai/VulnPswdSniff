import random
import string

def generate_random_passwords(number):
    random_string_pass = []
    for _ in range(number):
        pass_sizes = [8,9,10,11,12,13,14,15]
        pass_length = random.choice(pass_sizes)
        random_string =  ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=pass_length))
        random_string_pass.append(random_string)
    return random_string_pass



def store_passwords(passwords):
    label_data = []
    with open("random_pswds.txt" , 'w') as file:
        for pswd in passwords:
            file.write(pswd + '\n')
            label_data.append((pswd,0))
    print(f"{len(passwords)} passwords stored in random_pswds.txt")
    return label_data

