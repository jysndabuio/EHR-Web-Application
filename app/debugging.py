# app/debugging.py
from app import routes  # Absolute import

if __name__ == '__main__':
    print(dir(routes))  # Debugging: Print the attributes of 'routes' module
