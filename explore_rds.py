import rpy2.robjects as robjects
from rpy2.robjects import pandas2ri
import json
from rpy2.robjects.vectors import ListVector, ListSexpVector, IntVector
import numpy as np
import argparse

parser = argparse.ArgumentParser(description='Convert RDS to JSON')
parser.add_argument('--rds_path', default='data/LOL/RDS/data.rds', help='Path to the RDS file')
parser.add_argument('--json_path', default='data/LOL/json/data.json', help='Path to the JSON file')
args = parser.parse_args()

def convert_listvector(lv):
    result = {}
    for name in lv.names:
        item = lv.rx2(str(name))
        if isinstance(item, robjects.vectors.DataFrame):
            result[str(name)] = pandas2ri.ri2py(item).to_dict(orient='records')
        else:
            result[str(name)] = item
    return result

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, robjects.vectors.DataFrame):
            return pandas2ri.rpy2py(obj).to_dict(orient='records')
        elif isinstance(obj, (ListVector, ListSexpVector)):
            return {str(key): self.default(value) for key, value in obj.items()}
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, IntVector):
            return list(obj)
        elif hasattr(obj, 'rclass'):
            return str(obj)
        return super().default(obj)

def read_and_convert_rds_to_json(rds_path, json_path):
    pandas2ri.activate()
    readRDS = robjects.r['readRDS']
    lv = readRDS(rds_path)
    data_dict = convert_listvector(lv)
    
    with open(json_path, 'w') as json_file:
        json.dump(data_dict, json_file, cls=CustomEncoder, indent=4, ensure_ascii=False)

# Read the RDS file and save it as a JSON file
read_and_convert_rds_to_json(args.rds_path, args.json_path)

print("Data successfully written to", args.json_path)
