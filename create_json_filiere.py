import json
import os
import argparse
import sys

parser = argparse.ArgumentParser(description='Convert CSV files to JSON.')
parser.add_argument('--path', default='data/csv', help='Path to the CSV file or directory containing CSV files')
parser.add_argument('--output_name', default='data/json', help='Name of the output JSON file')
parser.add_argument('--tag', default='#students', help='Tag of the assistant')
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

def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)



if __name__ == '__main__':
    path = args.path
    proxy_assistant_data_path = os.path.join(args.output_name, 'proxy.json')
    data_for_proxy_assistant = []
    if os.path.isfile(path) and path.endswith(".csv"):
        filiere = get_filiere(path)
        data = open_csv(path)
        json_data = save_to_json(data, filiere)
        context = "Ce document retrace les statistiques du nombres d'étudiant(nationalité, sexe, nationalité) inscrit au semestre d'automne en {} depuis 2012 a l'université de Lausanne.".format(filiere)
        json_data = {
            "context": context, 
            "data": json_data,
            'tag': args.tag + ' #' + filiere
		}
        save_json(json_data, os.path.join(args.output_name, filiere + '.json'))
    elif os.path.isdir(path):
        found_csv = False
        for filename in os.listdir(path):
            if filename.endswith(".csv"):
                found_csv = True
                csv_path = os.path.join(path, filename)
                filiere = get_filiere(csv_path)
                data = open_csv(csv_path)
                json_data = save_to_json(data, filiere)
                context = "Ce document retrace les statistiques du nombres d'étudiant(nationalité, sexe, nationalité) inscrit au semestre d'automne en {} depuis 2012 a l'université de Lausanne.".format(filiere)
                json_data = {"context": context, "data": json_data}
                save_json(json_data, os.path.join(args.output_name, filename.split('.')[0] + '.json'))
                data_for_proxy_assistant.append({
                    'name': filename.split('.')[0] + '.json',
                    'context': context,
                    'tag': args.tag + ' #' + filiere
                })
        if not found_csv:
            print("No CSV files found in the directory.")
            sys.exit(1)
    else:
        print("The provided path is neither a CSV file nor a directory.")
        sys.exit(1)

    save_json(data_for_proxy_assistant, proxy_assistant_data_path)