import random
import string

def get_random_string():
    # choose from all lowercase letter
    # letters = string.ascii_uppercase
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for i in range(8))
    # print(password)
    return(password)



if __name__ == '__main__':
    get_random_string()