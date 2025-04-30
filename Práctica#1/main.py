from functions import insert_patients, search_patient, update_patient, delete_patient, db

ID_1 = 1234567890
ID_2 = 1122334455
ID_3 = 70065456

# Menu de opciones
def main():
    insert_patients(db)
    
    while True:
        try:
            print("\n\n******** Menu ********\n")
            print("1. Buscar paciente")
            print("2. Actualizar informacion de paciente")
            print("3. Eliminar paciente")
            print("4. Salir")
            print("\n************************\n")
            opcion = int(input("\nIngrese una opción >> "))
            
            if opcion == 1:
                while True:
                    id = input("\nIngrese el ID del paciente (o escriba 'm' para volver al menú principal): \n")
                    if id.lower() == 'm':
                        print("\nRegresando al menú principal...\n")
                        break
                    patient = search_patient(id)
                    
                    if not patient:
                        print(f"\nNo se encontró paciente con ID: {id}\n")
                    else:
                        break
            
            elif opcion == 2: # actualizar informacion del paciente
                while True:
                    id = input("Ingrese el ID del paciente a actualizar (o escriba 'm' para volver al menú principal): ")
                    if id.lower() == 'm':
                        print("\nRegresando al menú principal...\n")
                        break
                    if update_patient(id):
                        break
                    else:
                        print(f"\nNo se encontró paciente con ID: {id}\n")
            
            elif opcion == 3:
                while True:
                    id = input("\nIngrese el ID del paciente a eliminar (o escriba 'm' para volver al menú principal): ")
                    if id.lower() == 'm':
                        print("\nRegresando al menú principal...\n")
                        break
                    if delete_patient(id):
                        break
                    else:
                        print(f"\nNo se encontró paciente con ID: {id}\n")
                
            elif opcion == 4:
                print("\n*** Saliendo del programa ***\n")
                break
            else:
                print("\nOpcion no valida!\n")
            
        except ValueError:
            print("Por favor ingrese un caracter válido\n")
        
if __name__ == "__main__":
    main()