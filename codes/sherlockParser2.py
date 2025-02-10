import os
import json
import re
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content
import time


def process_selected_initial_files(
    input_folder="./test/",
    output_file="reasoning_selected_initial.json",
):
    genai.configure(api_key="AIzaSyB2-7zMkGOvUyhik4XfPspk671FwmelP5c")

    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_schema": content.Schema(
            type=content.Type.OBJECT,
            properties={
                "solution": content.Schema(
                    type=content.Type.ARRAY,
                    items=content.Schema(
                        type=content.Type.INTEGER,
                    ),
                ),
                "correct": content.Schema(
                    type=content.Type.BOOLEAN,
                ),
            },
        ),
        "response_mime_type": "application/json",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )

    selected_filenames = {
        "response_001_initial.txt",
        "response_004_initial.txt",
        "response_011_initial.txt",
        "response_013_initial.txt",
        "response_017_initial.txt",
        "response_018_initial.txt",
        "response_021_initial.txt",
        "response_022_initial.txt",
        "response_024_initial.txt",
        "response_025_initial.txt",
        "response_028_initial.txt",
        "response_031_initial.txt",
        "response_032_initial.txt",
        "response_043_initial.txt",
        "response_049_initial.txt",
        "response_055_initial.txt",
        "response_078_initial.txt",
        "response_087_initial.txt",
        "response_089_initial.txt",
        "response_091_initial.txt",
        "response_094_initial.txt",
        "response_095_initial.txt",
    }

    results = []

    for filename in selected_filenames:
        file_path = os.path.join(input_folder, filename)
        if not os.path.exists(file_path):
            print(f"Skipping {filename}, file not found.")
            continue

        problem_id_match = re.search(r"response_(\d+)_initial\.txt", filename)
        if not problem_id_match:
            continue
        problem_id = problem_id_match.group(1)

        with open(file_path, "r") as f:
            file_content = f.read()

        prompt = (
            f"Go through the following data and parse it to find the list with final operations. "
            f"Please only find the final operations and not the ones done in between. "
            f"If the file says it's impossible to solve, please mark the correct field as false. "
            f"Do not try to solve the problem yourself. Only parse it.\n"
            f"Data:\n{file_content}"
        )

        print(prompt)
        chat_session = model.start_chat(history=[])

        try:
            response = chat_session.send_message(prompt)

            response_json = json.loads(response.text)
            solution = response_json.get("solution", [])

        except (json.JSONDecodeError, AttributeError):
            print(f"Error decoding JSON from response for {filename}.")
            solution = []

        results.append({"problem_id": problem_id, "solution": solution})

        print("Processed:", filename)
        time.sleep(4)

    with open(output_file, "w") as out_f:
        json.dump(results, out_f, indent=4)

    print(f"Results written to {output_file}")


if __name__ == "__main__":
    process_selected_initial_files()
