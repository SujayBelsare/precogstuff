import os
import json
import re
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content
import time


def process_files(
    input_folder="./test/",
    output_file="sherlock.json",
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

    final_files = {}

    for filename in os.listdir(input_folder):
        match = re.match(r"response_(\d+)(?:_iter_(\d+))?\.txt", filename)
        if match:
            problem_id = match.group(1)
            iteration = int(match.group(2)) if match.group(2) else 0  # 0 for initial

            # Track the highest iteration for each problem_id
            if problem_id not in final_files or iteration > final_files[problem_id][1]:
                final_files[problem_id] = (filename, iteration)

    results = []

    for problem_id, (final_filename, _) in final_files.items():
        file_path = os.path.join(input_folder, final_filename)

        with open(file_path, "r") as f:
            file_content = f.read()

        prompt = (
            f"Go through the following data and parse it to find the list with final operations. "
            f"Please only find the final operations and not the ones done in between. "
            f"If the file says it's impossible to solve please mark correct field as false. "
            f"Do not try to solve the problem yourself. Only parse it.\n"
            f"Data:\n{file_content}"
        )

        chat_session = model.start_chat(history=[])

        try:
            response = chat_session.send_message(prompt)

            response_json = json.loads(response.text)
            solution = response_json.get("solution", [])

        except (json.JSONDecodeError, AttributeError):
            print(f"Error decoding JSON from response for {final_filename}.")
            solution = []

        results.append({"problem_id": problem_id, "solution": solution})

        print("Processed:", final_filename)
        time.sleep(4)

    with open(output_file, "w") as out_f:
        json.dump(results, out_f, indent=4)

    print(f"Results written to {output_file}")


if __name__ == "__main__":
    process_files()
