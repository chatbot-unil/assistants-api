import json
import os
import argparse
import sys

parser = argparse.ArgumentParser(description='Convert CSV files to JSON.')
parser.add_argument('--path', default='data/csv', help='Path to the CSV file or directory containing CSV files')
parser.add_argument('--output_name', default='students_data.json', help='Name of the output JSON file')
args = parser.parse_args()

def save_to_json(data, filiere):
    lines = data.strip().split('\n')
    header = lines[0].split('; ')
    result = {}
    for line in lines[1:]:
        values = line.split('; ')
        year_data = dict(zip(header[1:], map(int, values[1:])))
        if values[0] not in result:
            result[values[0]] = {}
        result[values[0]][filiere] = year_data
    return result

def open_csv(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = f.read()
    return data

def get_filiere(path):
    filename_with_extension = path.split('/')[-1]
    filiere = filename_with_extension.split('.')[0]
    return filiere

def merge_json_data(json_data_list):
    unified_json = {}
    for json_data in json_data_list:
        for year, data in json_data.items():
            if year not in unified_json:
                unified_json[year] = {}
            unified_json[year].update(data)
    return unified_json

def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    json_data_list = []
    path = args.path
    if os.path.isfile(path) and path.endswith(".csv"):
        filiere = get_filiere(path)
        data = open_csv(path)
        json_data = save_to_json(data, filiere)
        json_data_list.append(json_data)
    elif os.path.isdir(path):
        found_csv = False
        for filename in os.listdir(path):
            if filename.endswith(".csv"):
                found_csv = True
                csv_path = os.path.join(path, filename)
                filiere = get_filiere(csv_path)
                data = open_csv(csv_path)
                json_data = save_to_json(data, filiere)
                json_data_list.append(json_data)
        if not found_csv:
            print("No CSV files found in the directory.")
            sys.exit(1)
    else:
        print("The provided path is neither a CSV file nor a directory.")
        sys.exit(1)

    # Merge the JSON data and save it
    unified_json = merge_json_data(json_data_list)
    unified_json_with_context = {
        "contexte": "Ce document retrace les statistiques du nombre d'étudiants (sexe, nationalité) inscrits au semestre d'automne depuis 2011 à l'Université de Lausanne.",
        "data": unified_json
    }
    output_name = f"data/json/{args.output_name}"
    save_json(unified_json_with_context, output_name)
