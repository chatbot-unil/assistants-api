import os
import argparse
from dotenv import load_dotenv
from openai import OpenAI

parser = argparse.ArgumentParser(description='Create assistants on OpenAI.')
parser.add_argument('--data_path', default='data/json', help='Path to the JSON file or directory containing JSON files')
parser.add_argument('--model', default='gpt-4-1106-preview', help='Name of the model to use')
parser.add_argument('--init_message', default='Bonjour', help='Initial message to send to the assistant')
parser.add_argument('--output', default='output_images', help='Output directory')
args = parser.parse_args()

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
instructions = os.getenv("INSTRUCTIONS")
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
	files = []
	for filename in os.listdir(dir):
		if filename.endswith(".json"):
			file = send_files_to_openAI(os.path.join(dir, filename))
			files.append(file)
	return files

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

if __name__ == '__main__':
	data_path = args.data_path
	if os.path.isfile(data_path) and data_path.endswith(".json"):
		file = send_files_to_openAI(data_path)
	elif os.path.isdir(data_path):
		files = send_all_files(data_path)

	assistant = create_assistants_with_code_interpreter_and_retrieval("test", files, instructions)

	thread = chat_create_thread(args.init_message)

	print("Assistant created with ID: " + assistant.id)
	print("Thread created with ID: " + thread.id)
	print("Files sent to OpenAI: " + str([file.id for file in files]))

	while True:
		message = input("You: ")
		if message == "exit":
			break
		message = chat_send_message(thread.id, message)
		print("Message sent with ID: " + message.id)
		run = run_assistant(assistant.id, thread.id)
		run_status = get_run_status(run.id, thread.id)
		while run_status.status != "completed":
			run_status = get_run_status(run.id, thread.id)
		messages = get_messages(thread.id)
		message_id = get_last_assistant_message_id(thread.id)
		assistant_response = retrive_message(message_id, thread.id)
		print_all_contents(assistant_response)