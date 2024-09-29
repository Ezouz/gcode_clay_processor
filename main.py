import os
from src.menu import menu_principal

def main():
    os.makedirs("Ressources/", exist_ok=True) 
    menu_principal()

if __name__=="__main__":
	main()
        