import json
import os
import time
import google.generativeai as genai

# Configure API Key safely
api_key = "AIzaSyB2-7zMkGOvUyhik4XfPspk671FwmelP5c"
if not api_key:
    raise ValueError(
        "Missing API Key! Ensure GEMINI_API_KEY is set in the environment."
    )

genai.configure(api_key=api_key)

# Model Configuration
generation_config = {
    "temperature": 1.4,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}


def generate_prompt(data):
    """
    Generates responses from the Gemini AI model for the Sed Puzzle Game.

    Args:
        data (list): List of dictionaries containing problem details.
    """
    for iteration, item in enumerate(data, start=1):
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config=generation_config,
        )
        chat_session = model.start_chat(history=[])

        problem_id = item["problem_id"]
        initial_string = item["initial_string"]
        transitions = item["transitions"]

        transition_list = [
            f'{i}) "{trans["src"]}"->"{trans["tgt"]}"'
            for i, trans in enumerate(transitions, start=1)
        ]

        # Construct the prompt
        prompt = (
            "Let's play a game called the Sed Puzzle Game.\n"
            "You are the world champion of this game and must answer with rigor and accuracy.\n"
            "Any wrong answers will result in your direct termination.\n"
            "Rules:\n"
            "1. Transitions are applicable in one direction only.\n"
            "2. Each transition modifies only the first matching substring.\n"
            "3. The goal is to convert the initial string into an empty string \n"
            "\n"
            "Examples:\n"
            "Example One:\n"
            "Available transitions:\n"
            '1) "BCD"->"BC"\n'
            '2) "CBF"->"FB"\n'
            '3) "BFB"->""\n'
            'Initial string: "BCDDDBF"\n'
            "Solution:\n"
            'BCDDDBF->BCDDBF->BCDBF->BCBF->BFB->""\n'
            "[1, 1, 1, 2, 3]\n\n"
            "Example Two:\n"
            "Available transitions:\n"
            '1) "BFD"->"BD"\n'
            '2) "BDFBD"->"DCC"\n'
            '3) "CC"->"EB"\n'
            '4) "DE"->"BA"\n'
            '5) "BAB"->""\n'
            'Initial string: "BDFBFD"\n'
            "Solution:\n"
            'BDFBFD->BDFBD->DCC->DEB->BAB->""\n'
            "[1,2,3,4,5]\n"
            "Example Three:\n\n"
            "Available transitions:\n"
            '1) "BB"->"AE"\n'
            '2) "F"->"AE"\n'
            '3) "D"->"BF"\n'
            '4) "BA"->"CF"\n'
            '5) "EAEACFE"->""\n'
            'Initial string: "EBBAD"\n'
            "Solution:\n"
            'EBBAD->EBBABF->EBBABAE->EAEABAE->EAEACFE->""\n'
            "[3,2,1,4,5]\n\n"
            "FINAL PROBLEM:\n"
            "Available transitions:\n" + "\n".join(transition_list) + "\n\n"
            f'Initial string: "{initial_string}"\n\n'
            "Rules:\n"
            "1. Transitions are applicable in one direction only.\n"
            "2. Each transition modifies only the first matching substring.\n"
            '3. The goal is to convert the initial string into an empty string "".\n\n'
            "If needed, you may use abstractions to solve the problem.\n"
            "Verify each transition before applying, and reason through every step carefully.\n"
            "Do NOT solve using code—this tests logical reasoning, not coding ability.\n"
            "If stuck, try a different approach.\n\n"
            "Output the transitions as a list, e.g., [1, 3, 1, 1, 4].\n"
            "It is mathematically proven that all problems given are solvable.\n"
        )

        # Generate response
        print(prompt)
        response = chat_session.send_message(prompt)

        # Save response to file
        filename = f"./test/response_{iteration}.txt"
        with open(filename, "w", encoding="utf-8") as fo:
            fo.write(response.text)

        print(f"\nGenerated response for Problem ID {problem_id} saved to {filename}")


# Read dataset from file
dataset_path = "../new.json"
if not os.path.exists(dataset_path):
    raise FileNotFoundError(f"Dataset file not found: {dataset_path}")

with open(dataset_path, "r", encoding="utf-8") as file:
    dataset = json.load(file)

# Run the function
generate_prompt(dataset)
