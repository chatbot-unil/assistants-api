import os
import argparse
from dotenv import load_dotenv
from openai import OpenAI
import time
import json
import re

parser = argparse.ArgumentParser(description='Create assistants on OpenAI.')
parser.add_argument('--data_path', default='data/', help='Path to the JSON file or directory containing JSON files')
parser.add_argument('--model', default='gpt-4-1106-preview', help='Name of the model to use')
parser.add_argument('--instructions', default="Étant donné la liste JSON suivante, qui contient des informations sur différents fichiers de statistiques étudiantes, votre tâche est de simplement identifier les fichiers pertinents et d'extraire leurs IDs. Il n'est pas nécessaire de chercher ou de fournir une réponse à une question spécifique. Veuillez simplement fournir les IDs des fichiers pertinents au format JSON.", help='Instructions to send to the assistant')
parser.add_argument('--name', default='unil_assistant', help='Name of the assistant')
parser.add_argument('--init_message', default='Bonjour', help='Initial message to send to the assistant')
parser.add_argument('--output', default='output_images', help='Output directory')
args = parser.parse_args()

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
instructions = args.instructions
thread_id = None

# Load the model
client = OpenAI()

def send_files_to_openAI(data):
	file = client.files.create(
		purpose='assistants',
		file=open(data, 'rb')
	)
	return file

def send_all_files(dir):
	# Send CSV files in the directory, excluding the proxy file
	files = []
	for file in os.listdir(dir):
		if file.endswith(".json") and "proxy" not in file:
			file_path = os.path.join(dir, file)
			files.append(send_files_to_openAI(file_path))
	return files

def add_ids_to_proxy_file(proxy_file, files):
	# Lire le fichier proxy
	with open(proxy_file, 'r', encoding='utf-8') as file:
		proxy_data = json.load(file)

	# Associer les IDs aux objets JSON
	for item in proxy_data:
		# Utiliser le nom du fichier pour trouver l'ID correspondant
		file_name = item['name']
		for file in files:
			if file.filename == file_name:
				item['id'] = file.id
				break

	# Écrire les modifications dans le fichier proxy
	with open(proxy_file, 'w', encoding='utf-8') as file:
		json.dump(proxy_data, file, indent=4, ensure_ascii=False)
		
def create_assistants_with_code_interpreter_and_retrieval(name, files, instructions):
	files_ids = [file.id for file in files]
	assistant = client.beta.assistants.create(
		name=name,
		instructions=instructions,
		model=args.model,
		tools=[{"type": "code_interpreter"}, {"type": "retrieval"}],
		file_ids=files_ids,
	)
	return assistant

def chat_create_thread(content):
	thread = client.beta.threads.create(
		messages=[
			{
				"role": "user",
				"content": content,
			}
		],
	)
	return thread

def chat_send_message(thread_id, content):
	message = client.beta.threads.messages.create(
		thread_id=thread_id,
		role="user",
		content=content,
	)
	return message

def add_file_to_the_assistant(assistant_id, file_id):
	assistant = client.beta.assistants.update(
		assistant_id=assistant_id,
		file_ids=file_id,
	)
	return assistant.id

def get_assistant_files(assistant_id):
	assistant = client.beta.assistants.retrieve(
		assistant_id=assistant_id,
	)
	return assistant.file_ids

def update_assistant(assistant_id, instructions, file_ids):
	assistant_files = get_assistant_files(assistant_id)
	assistant_files = assistant_files + file_ids
	print(assistant_files)
	assistant = client.beta.assistants.update(
		assistant_id=assistant_id,
		instructions=instructions,
		file_ids=assistant_files,
	)
	return assistant.id

def run_assistant(assistant_id, thread_id):
	run = client.beta.threads.runs.create(
		thread_id=thread_id,
		assistant_id=assistant_id,
	)
	return run

def get_run_status(run_id, thread_id):
	run = client.beta.threads.runs.retrieve(
		run_id=run_id,
		thread_id=thread_id,
	)
	return run

def get_messages(thread_id):
	messages = client.beta.threads.messages.list(
		thread_id=thread_id,
	)
	return messages

def get_last_assistant_message_id(thread_id):
	messages = get_messages(thread_id)
	for message in messages:
		if message.role == "assistant":
			return message.id

def retrive_message(message_id, thread_id):
	message = client.beta.threads.messages.retrieve(
		message_id=message_id,
		thread_id=thread_id,
	)
	return message

def print_all_contents(message):
	for content in message.content:
		type = test_type_content(content)
		if type == "text":
			print(content)
			print(type)
		elif type == "image_file":
			print(content.image_file)
			get_image(content.image_file.file_id)

def get_image(image_file_id):
	image_file = client.files.content(image_file_id)
	file_path = os.path.join(args.output, image_file_id + ".png")
	with open(file_path, "wb") as f:
		f.write(image_file.content)

def test_type_content(content):
	return content.type

def get_image_url_from_file_id(file_id):
	file = client.files.retrieve(file_id)
	return file.url

def chat_with_assistant(assistant_id, thread_id, question):
	# Send the question and receive the response
	chat_send_message(thread_id, question)
	run = run_assistant(assistant_id, thread_id)
	while get_run_status(run.id, thread_id).status == "in_progress":
		time.sleep(10)
	message_id = get_last_assistant_message_id(thread_id)
	message = retrive_message(message_id, thread_id)
	print_all_contents(message)

	# Extract file IDs from plain text
	file_ids = extract_file_ids_from_text(message)

	print("File IDs found: ", file_ids)
	
	procces_second_question(assistant_id, thread_id, file_ids)
	
def procces_second_question(assistant_id, thread_id, file_ids):
	instructions = "Maintenant que vous avez identifié les fichiers pertinents, veuillez les ajouter à l'assistant en utilisant leur ID. Vous pouvez ajouter plusieurs IDs en les séparant par des virgules."
	# If file IDs are found, load and query a sub-assistant
	if file_ids:
		# Update the assistant with the new instructions
		assistant_id = update_assistant(assistant_id, instructions, file_ids)
		run = run_assistant(assistant_id, thread_id)
		while get_run_status(run.id, thread_id).status == "in_progress":
			time.sleep(10)
		message_id = get_last_assistant_message_id(thread_id)
		message = retrive_message(message_id, thread_id)
		print_all_contents(message)
	else:
		print("No relevant files found for the asked question.")

def extract_file_ids_from_text(message):
	file_ids = []
	for content in message.content:
		if content.type == 'text':
			text_content = content.text.value
			extracted_ids = re.findall(r'file-\w+', text_content)
			file_ids.extend([str(file_id) for file_id in extracted_ids if isinstance(file_id, str)])
	return file_ids


# Utiliser cette fonction dans votre programme principal
if __name__ == '__main__':
	data_path = args.data_path
	data_path = os.path.join(data_path, 'json')
	proxy_file_path = os.path.join(data_path, 'proxy.json') # Assurez-vous que ce chemin est correct
	files = []

	if os.path.isfile(data_path) and data_path.endswith(".json"):
		file = send_files_to_openAI(data_path)
		files.append(file)
	elif os.path.isdir(data_path):
		files = send_all_files(data_path)

	# Ajouter les IDs au fichier proxy
	add_ids_to_proxy_file(proxy_file_path, files)

	# uploader le fichier proxy
	proxy_file = send_files_to_openAI(proxy_file_path)

	# Créer l'assistant
	assistant = create_assistants_with_code_interpreter_and_retrieval(args.name, [proxy_file], instructions)
	assistant_id = assistant.id

	thread = chat_create_thread(args.init_message)

	print("Assistant created with ID: " + assistant.id)
	print("Thread created with ID: " + thread.id)
	print("Files sent to OpenAI: " + str([f"ID: {file.id}, Name: {file.filename}" for file in files]))

	while True:
		message = input("You: ")
		if message == "exit":
			break
		chat_with_assistant(assistant.id, thread.id, message)
	
	# Supprimer l'assistant
	client.beta.assistants.delete(assistant_id=assistant_id)
	print("Assistant deleted with ID: " + assistant_id)

	# Supprimer les fichiers
	for file in files:
		client.files.delete(file_id=file.id)
		print("File deleted with ID: " + file.id)

	# Supprimer le fichier proxy
	client.files.delete(file_id=proxy_file.id)

