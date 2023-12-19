from typing import *
import json
import time
import os
import argparse
from dotenv import load_dotenv
from openai import OpenAI
import time
import json

parser = argparse.ArgumentParser(description='Create assistants on OpenAI.')
parser.add_argument('--data_path', default='data/', help='Path to the JSON file or directory containing JSON files')
parser.add_argument('--model', default='gpt-4-1106-preview', help='Name of the model to use')
parser.add_argument('--name', default='unil_assistant', help='Name of the assistant')
parser.add_argument('--init_message', default='Bonjour', help='Initial message to send to the assistant')
parser.add_argument('--output', default='output_images', help='Output directory')
args = parser.parse_args()

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
thread_id = None

client = OpenAI()

def add_file_to_the_assistant(file_ids, assistant_id):
    print("Adding file to the assistant {}".format(assistant_id))
    _ = client.beta.assistants.update(
        assistant_id=assistant_id,
        file_ids=file_ids,
    )
    for file_id in file_ids:
        print(f"File ID: {file_id}")
    print("File added to the assistant {}".format(assistant_id))
    return json.dumps({"file_ids": file_ids})

FUNCTIONS_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_file_to_the_assistant",
            "description": "Use this function to add a file to the assistant",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_ids": {
                        "type": "array",
                        "items": {
                            "type": "string",
                        },
                        "description": "List of file IDs to add to the assistant",
                    },
                },
                "required": ["file_ids"],
            },
        },
    }
]

TOOLS = [
    {"type": "code_interpreter"},
    {"type": "retrieval"},
] 

# Inclure les fonctions dans les outils

TOOLS.extend(FUNCTIONS_TOOLS)

# Instructions pour l'assistant
INSTRUCTIONS = """
Étant donné la liste JSON suivante, qui contient des informations sur différents fichiers de statistiques étudiantes, votre tâche est de simplement identifier les fichiers pertinents et d'extraire leurs IDs. 
Il n'est pas nécessaire de chercher ou de fournir une réponse à une question spécifique dans un premier temps.

Utilisez la fonction suivante pour ajouter un fichier à l'assistant:

add_file_to_the_assistant(file_ids=["file_id_1", "file_id_2", "file_id_3"])

Dans un second temps, vous pourrez répondre à la question quand vous aurez identifié les fichiers pertinents.

La réponse doit être structurée comme suit uniquement :

{
    'answer': 'la réponse complète à la question',
    'valeurs': ['valeur1', 'valeur2', 'valeur3'] # Liste des valeurs numériques à extraire
}

Si vous ne trouvez pas de réponse, veuillez utiliser le format suivant pour indiquer qu'aucune réponse n'a été trouvée :

{
    'answer': 'None',
    'valeurs': []
}

Merci pour votre assistance !
"""

# Fonctions associées aux outils
FUNCTIONS_TO_HANLDE = {
    "add_file_to_the_assistant": add_file_to_the_assistant,
}

def send_files_to_openAI(data):
    file = client.files.create(
        purpose='assistants',
        file=open(data, 'rb')
    )
    return file

def send_all_files(dir):
    # Envoyer tous les fichiers JSON dans le dossier spécifié à OpenAI
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

def setup_assistant(client, answer, files_ids=[]):
    # Création de l'assistant avec les outils et les instructions
    assistant = client.beta.assistants.create(
        name=args.name,
        instructions=INSTRUCTIONS,
        tools=TOOLS,
        file_ids=files_ids,
        model=args.model,
    )

    # Création d'un nouveau thread
    thread = client.beta.threads.create()

    # Création d'un message dans le thread
    _ = client.beta.threads.messages.create(
        thread.id,
        role="user",
        content=answer,
    )

    return assistant.id, thread.id


def run_assistant(client, assistant_id, thread_id):
    # Création d'un nouveau appel d'un thread avec l'assistant spécifié
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )

    # Attendre que le run soit terminé ou qu'il nécessite une action
    while run.status == "in_progress" or run.status == "queued":
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )

        # Si le run est terminé, récupérer les messages
        if run.status == "completed":
            return client.beta.threads.messages.list(
                thread_id=thread_id
            )
        # Si le run nécessite une action, exécuter la fonction associée
        if run.status == "requires_action":
            function_name = run.required_action.submit_tool_outputs.tool_calls[0].function.name
            function_to_handle = FUNCTIONS_TO_HANLDE[function_name]
            if function_to_handle == add_file_to_the_assistant:
                result = function_to_handle(
                    file_ids=json.loads(run.required_action.submit_tool_outputs.tool_calls[0].function.arguments)['file_ids'],
                    assistant_id=run.assistant_id,
                )
            else:
                print(f"Function {function_name} not found")
                result = json.dumps({"file_ids": []})
            run = client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run.id,
                tool_outputs=[
                    {
                        "tool_call_id": run.required_action.submit_tool_outputs.tool_calls[0].id,
                        "output": result,
                    },
                ]
            )

if __name__ == "__main__":
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

    print("Files sent to OpenAI: " + str([f"ID: {file.id}, Name: {file.filename}" for file in files]))

    # uploader le fichier proxy
    proxy_file = send_files_to_openAI(proxy_file_path)
    
    # calcul time execution
    messages = input("Type your message: ")
    if messages != "":
        start_time = time.time()
        assistant_id, thread_id = setup_assistant(client, messages, [proxy_file.id])
        print(f"Debugging: Useful for checking the generated agent in the playground. https://platform.openai.com/playground?mode=assistant&assistant={assistant_id}")
        print(f"Debugging: Useful for checking logs. https://platform.openai.com/playground?thread={thread_id}")

        messages = run_assistant(client, assistant_id, thread_id)

        message_dict = json.loads(messages.model_dump_json())
        print(message_dict['data'][0]['content'][0]["text"]["value"])
        print("--- %s seconds ---" % (time.time() - start_time))
        # Supprimer l'assistant
        client.beta.assistants.delete(assistant_id=assistant_id)
        print("Assistant deleted with ID: " + assistant_id)

    # Supprimer les fichiers
    for file in files:
        client.files.delete(file_id=file.id)
    print("Files deleted with ID: " + str([file.id for file in files]))

    # Supprimer le fichier proxy
    client.files.delete(file_id=proxy_file.id)
    print("Proxy file deleted with ID: " + proxy_file.id)