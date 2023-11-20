import json
import sys
import os
import argparse

parser = argparse.ArgumentParser(description='Convert CSV files to JSON.')
parser.add_argument('--path', default='data/csv', help='Path to the CSV file or directory containing CSV files')
args = parser.parse_args()

def save_to_json(data, filiere):
    # Split the input data into lines
    lines = data.strip().split('\n')
    
    # Parse the header
    header = lines[0].split('; ')
    
    # Initialize the result dictionary
    conexte = f"Ce document retrace les statistiques du nombres d'étudiant(nationalité, sexe, nationalité) inscrit au semestre d'automne en {filiere} depuis 2012 a l'université de Lausanne."
    result = {"contexte": conexte}

    # Process each data line
    for line in lines[1:]:
        values = line.split('; ')
        year_data = dict(zip(header[1:], map(int, values[1:])))
        result[values[0]] = year_data

    return result

def open_csv(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = f.read()
    return data

def get_filiere(path):
    """Retourne le nom de la filière depuis le chemin du fichier CSV"""
    filename_with_extension = path.split('/')[-1]
    filiere = filename_with_extension.split('.')[0]
    return filiere

def save_json(data, filiere):
    """Sauvegarde les données dans un fichier JSON"""
    path = f'data/json/{filiere}.json'
    os.makedirs(os.path.dirname(path), exist_ok=True)  # Ensure the directory exists
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    filto_append_allthejson = []
    path = args.path
    if os.path.isfile(path) and path.endswith(".csv"):
        filiere = get_filiere(path)
        data = open_csv(path)
        json_data = save_to_json(data, filiere)
        save_json(json_data, filiere)
    elif os.path.isdir(path):
        found_csv = False
        for filename in os.listdir(path):
            if filename.endswith(".csv"):
                filiere = get_filiere(filename)
                found_csv = True
                csv_path = os.path.join(path, filename)
                data = open_csv(csv_path)
                json_data = save_to_json(data, filiere)
                save_json(json_data, filiere)
        if not found_csv:
            print("No CSV files found in the directory.")
            sys.exit(1)
    else:
        print("The provided path is neither a CSV file nor a directory.")
        sys.exit(1)