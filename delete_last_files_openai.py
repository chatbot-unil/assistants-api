from openai import OpenAI
import os
import dotenv as dt
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--nb', default=3, help='Number of files to delete')
args = parser.parse_args()

dt.load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

client = OpenAI()

tab_not_to_delete = ["AnnuaireStatistique.json", "UNIL_Annuaire_Statistique_22022-23.pdf", "AnnuaireStatistique.csv"]

def get_last_files(nb):
	files = client.files.list()
	files = files.data
	files.sort(key=lambda x: x.created_at, reverse=True)
	return files[:nb]

def print_files(files):
	for file in files:
		print(file.filename)

def delete_files(files):
	for i in range(len(files)):
		if files[i].filename not in tab_not_to_delete:
			print(f"Deleting {files[i].filename}... ({i+1}/{len(files)})")
			client.files.delete(files[i].id)

def get_all_files_length():
	files = client.files.list()
	return len(files.data)

if __name__ == "__main__":
	files = get_last_files(int(args.nb))
	print("Files length:", get_all_files_length())
	print_files(files)
	input("Are you sure you want to delete these files? Press Enter to continue...")
	delete_files(files)
	print("Files deleted")
