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
        return list(csv.DictReader(f, delimiter=';'))

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
                if len(test_info) > 1:  # Verificar que exista el índice
                    test_name = test_info[1].replace('^', ' ')  # Nombre de la prueba
                    test_value = parts[3]  # Valor de la prueba
                    if 'tests' not in data:
                        data['tests'] = {}
                    data['tests'][test_name] = test_value
    return data

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
            if data:  # Si hay datos válidos
                pacientes = [data]

        for paciente in pacientes:
            # id del paciente como _id en MongoDB
            paciente_id = paciente.get('id') or paciente.get('id ')
            if not paciente_id:
                continue  # salta si no hay id

            # documento para la colección de la base de datos
            documento = dict(paciente)
            documento['_id'] = str(paciente_id)
            documento['id'] = str(paciente_id)

            # Insertar solo si no existe
            if not db.Patients.find_one({'_id': documento['_id']}):
                try:
                    db.Patients.insert_one(documento)
                    print(f"Paciente {documento['id']} ingresado correctamente")
                except Exception as e:
                    print(f"Error ingresando paciente {documento['id']}: {e}")
            else:
                print(f"Paciente {documento['id']} ya existe en la base de datos")      
                
def search_patient(id_paciente):
    id_paciente = str(id_paciente)
    paciente = db.Patients.find_one({"id": id_paciente})
    if paciente:
        print("******** Información del Paciente ********\n")
        for key, value in paciente.items():
            if key != "_id": # se excluye el campo _id
                print(f"{key}: {value}")
        return True
    else:
        return False
     