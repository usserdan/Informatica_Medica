import os
import json
import csv
from pymongo import MongoClient

# se inserta el string de conexion con el cluster
uri = "mongodb+srv://danielbarreram:987654321@infomedica.m9fbrpf.mongodb.net/?retryWrites=true&w=majority&appName=InfoMedica"
client = MongoClient(uri)

# base de datos a usar
db = client['Practica1']

# funcion para leer el archivo json
def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# funcion para leer el archivo csv
def read_csv(file_path):
    with open(file_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        data = []
        for row in reader:
            # hay que limpiar los espacios en blanco de las claves
            clean_row = {k.strip(): v.strip() for k, v in row.items()}
            data.append(clean_row)
        return data

# funcion para leer el archivo txt
def read_txt(file_path):
    data = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('3O|'):
                parts = line.split('|')
                data['id'] = parts[2]  # ID del paciente
                data['name'] = f"{parts[12]} {parts[13]} {parts[14]}".strip()  # Nombre completo
            elif line.startswith('1H|'):
                data['date'] = line.split('|')[-1]  # Fecha del informe
            elif line.startswith(('4R|','5R|','6R|','7R|','0R|','1R|','2R|','3R|')):
                parts = line.split('|')
                test_info = parts[2].split('^^^')  # Información de la prueba
                if len(test_info) > 1:
                    test_name = test_info[1].replace('^', ' ')  # Nombre de la prueba
                    test_value = parts[3]  # Valor de la prueba
                    # Solo leer tests que contienen 'AREA', pero no 'TOTAL AREA', sí 'WINDOW AREA'
                    if 'AREA' in test_name.upper() and 'TOTAL AREA' not in test_name.upper():
                        if 'tests' not in data:
                            data['tests'] = {}
                        data['tests'][test_name] = test_value
    return data

# funcion para leer los archivos de los pacientes y guardarlos en la base de datos
def insert_patients(db):
    folder = 'patients'
    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)
        pacientes = []

        if file.endswith('.json'):
            pacientes = read_json(file_path)
        elif file.endswith('.csv'):
            pacientes = read_csv(file_path)
        elif file.endswith('.txt'):
            data = read_txt(file_path)
            if data:
                pacientes = [data]

        for paciente in pacientes:
            # Normaliza la clave 'id'
            paciente_id = paciente.get('id') or paciente.get('id ')
            if not paciente_id:
                continue

            documento = dict(paciente)
            # Elimina la clave 'id ' si existe
            if 'id ' in documento:
                del documento['id ']
            documento['_id'] = str(paciente_id)
            documento['id'] = str(paciente_id)

            if not db.Patients.find_one({'_id': documento['_id']}):
                try:
                    db.Patients.insert_one(documento)
                    print(f"Paciente {documento['id']} ingresado correctamente")
                except Exception as e:
                    print(f"Error ingresando paciente {documento['id']}: {e}")
            else:
                print(f"Paciente {documento['id']} ya existe en la base de datos")   

# funcion para bucar e imprimir la informacion de un paciente           
def search_patient(id_paciente):
    id_paciente = str(id_paciente)
    paciente = db.Patients.find_one({"id": id_paciente})
    if paciente:
        print("******** Información del Paciente ********\n")
        for key, value in paciente.items():
            if key == "_id":
                continue
            if isinstance(value, dict):
                print(f"{key}:")
                for subkey, subvalue in value.items():
                    print(f"  {subkey}: {subvalue}")
            elif isinstance(value, list):
                print(f"{key}:")
                for idx, item in enumerate(value, 1):
                    print(f" {item}")
            else:
                print(f"{key}: {value}")
        return True
    else:
        return False
    
# funcion para actualizar un paciente
def update_patient(id_paciente):
    id_paciente = str(id_paciente)
    paciente = db.Patients.find_one({"id": id_paciente})
    if not paciente:
        return False

    # no se puede editar el id y el _id
    atributos = [k for k in paciente.keys() if k not in ['_id', 'id']]
    if not atributos:
        print("No hay informacion que se pueda actualizar para este paciente.")
        return False

    while True:
        print("\n******** Información del Paciente ********")
        for idx, attr in enumerate(atributos, 1):
            print(f"{idx}. {attr}: {paciente[attr]}")
        print(f"\n\n{len(atributos)+1}. Salir")
        try:
            opcion = int(input(f"\nSeleccione el número del campo a modificar o ingrese {len(atributos)+1} para salir >> "))
            if opcion == len(atributos) + 1:
                print("\n--- Volviendo al menú principal ---.")
                return True
            if 1 <= opcion <= len(atributos):
                atributo = atributos[opcion - 1]
                valor_actual = paciente[atributo]
                # Si es dict, permitir actualizar subcampos
                if isinstance(valor_actual, dict):
                    subkeys = list(valor_actual.keys())
                    while True:
                        print(f"\nCampos de '{atributo}':")
                        for i, subk in enumerate(subkeys, 1):
                            print(f"{i}. {subk}: {valor_actual[subk]}")
                        print(f"{len(subkeys)+1}. Salir")
                        try:
                            subop = int(input(f"\nSeleccione el número del subcampo a modificar o ingrese {len(subkeys)+1} para salir >> "))
                            if subop == len(subkeys) + 1:
                                break
                            if 1 <= subop <= len(subkeys):
                                subattr = subkeys[subop - 1]
                                nuevo_valor = input(f"\nIngrese el nuevo valor para '{subattr}': ")
                                db.Patients.update_one(
                                    {"id": id_paciente},
                                    {"$set": {f"{atributo}.{subattr}": nuevo_valor}}
                                )
                                paciente[atributo][subattr] = nuevo_valor
                            else:
                                print("\nOpción no válida.")
                        except ValueError:
                            print("\nPor favor, ingrese un número válido.")
                # Si es lista, permitir actualizar elementos individuales
                elif isinstance(valor_actual, list):
                    if not valor_actual:
                        print(f"La lista '{atributo}' está vacía.")
                        continue
                    while True:
                        print(f"\nCampos de '{atributo}':")
                        for i, item in enumerate(valor_actual, 1):
                            print(f"{i}. {item}")
                        print(f"\n{len(valor_actual)+1}. Salir")
                        try:
                            idx_elem = int(input(f"\nSeleccione el número del campo a modificar o ingrese {len(valor_actual)+1} para salir >> "))
                            if idx_elem == len(valor_actual) + 1:
                                break
                            if 1 <= idx_elem <= len(valor_actual):
                                nuevo_valor = input(f"Ingrese el nuevo valor para el campo {idx_elem}: ")
                                db.Patients.update_one(
                                    {"id": id_paciente},
                                    {"$set": {f"{atributo}.{idx_elem-1}": nuevo_valor}}
                                )
                                paciente[atributo][idx_elem-1] = nuevo_valor
                            else:
                                print("\nOpción no válida.")
                        except ValueError:
                            print("\nPor favor, ingrese un número válido.")
                else:
                    nuevo_valor = input(f"\nIngrese el nuevo valor para '{atributo}': ")
                    db.Patients.update_one(
                        {"id": id_paciente},
                        {"$set": {atributo: nuevo_valor}}
                    )
                    paciente[atributo] = nuevo_valor 
            else:
                print("\nOpción no válida.")
        except ValueError:
            print("\nPor favor, ingrese un número válido.")
            
# funcion para eliminar un paciente
def delete_patient(id_paciente):
    id_paciente = str(id_paciente)
    paciente = db.Patients.find_one({"id": id_paciente})
    if paciente:
        db.Patients.delete_one({"id": id_paciente})
        print(f"Paciente con ID {id_paciente} eliminado correctamente.")
        return True
    else:
        return False

     