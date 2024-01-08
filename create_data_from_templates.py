import json
import os
import argparse
from jinja2 import Environment, FileSystemLoader

# Parsing command line arguments
parser = argparse.ArgumentParser(description='Create questions from pool of templates.')
parser.add_argument('--path_csv', default='data/csv', help='Path to the directory with json files with the data')
parser.add_argument('--path_questions', default='data/templates/questions_pool.json', help='Path to the file with questions pool')
parser.add_argument('--path_templates', default='data/templates/questions_pool_1_template.j2', help='Path to the file with templates')
parser.add_argument('--output_path', default='data/questions', help='Path to the output directory')
args = parser.parse_args()

def open_json_file(path):
    with open(path, "r") as f:
        data = json.load(f)
    return data

def open_csv(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = f.read()
    return data

def extract_pools_and_questions(json_data):
    pools_dict = {}
    for pool in json_data:
        pool_name = pool.get("name", "")
        questions = pool.get("questions", [])
        pools_dict[pool_name] = questions
    return pools_dict

def get_data_unil(path):
    data = []
    if os.path.isfile(path) and path.endswith(".csv"):
        data.append(open_csv(path))
    elif os.path.isdir(path):
        for filename in os.listdir(path):
                if filename.endswith(".csv"):
                    csv_path = os.path.join(path, filename)
                    data.append(open_csv(csv_path))
    return data

def render_questions(pools_dict, template_path, json_data_path, output_path):
    env = Environment(loader=FileSystemLoader(os.path.dirname(template_path)))
    template = env.get_template(os.path.basename(template_path))

    if not os.path.exists(output_path):
        os.makedirs(output_path)

# Load JSON data
json_data = open_json_file(args.path_questions)
pools_dict = extract_pools_and_questions(json_data)
unil_data = get_data_unil(args.path_csv)

print(unil_data)
