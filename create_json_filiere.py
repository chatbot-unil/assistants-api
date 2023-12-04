import json
import os
import argparse
import sys

parser = argparse.ArgumentParser(description='Update proxy.json with CSV file references.')
parser.add_argument('--path', default='data/csv', help='Path to the CSV file or directory containing CSV files')
parser.add_argument('--output_name', default='data/', help='Name of the output JSON file')
parser.add_argument('--tag', default='#students', help='Tag to use for the assistant')
args = parser.parse_args()

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
        context = "Ce document contient les statistiques des étudiants (nationalité, sexe, nationalité) inscrits au semestre d'automne en {} depuis 2012 à l'université de Lausanne.".format(filiere)
        data_for_proxy_assistant.append({
            'name': os.path.basename(path),
            'context': context,
            'tag': args.tag + ' #' + filiere
        })
    elif os.path.isdir(path):
        found_csv = False
        for filename in os.listdir(path):
            if filename.endswith(".csv"):
                found_csv = True
                filiere = get_filiere(filename)
                context = "Ce document contient les statistiques des étudiants (nationalité, sexe, nationalité) inscrits au semestre d'automne en {} depuis 2012 à l'université de Lausanne.".format(filiere)
                data_for_proxy_assistant.append({
                    'name': filename,
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
