import os
import json
import re
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content
import time


def process_files(
    input_folder="../outputs/reasoning/reasoning_hard", output_file="reasoning2.json"
):
    # Configure Gemini API key (make sure GEMINI_API_KEY is set in your environment)
    genai.configure(api_key="AIzaSyB2-7zMkGOvUyhik4XfPspk671FwmelP5c")

    # Set up the generation configuration using the provided schema
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

    # Create the Gemini model instance
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )

    # Start a chat session

    # List to store output for each file
    results = []

    # Loop over all files matching the pattern response_*.txt in the input folder
    for filename in os.listdir(input_folder):
        chat_session = model.start_chat(history=[])
        if filename.startswith("response_") and filename.endswith(".txt"):
            file_path = os.path.join(input_folder, filename)
            with open(file_path, "r") as f:
                file_content = f.read()

            # Extract the numeric part from the filename to use as problem_id (padded to three digits)
            match = re.search(r"response_(\d+)\.txt", filename)
            problem_id = str(int(match.group(1)) + 70).zfill(3) if match else "070"
            # Construct a prompt. Adjust this string to instruct the model as desired.
            prompt = (
                f"Go through the following data and parse it to find the list with final operations. Please only find the final operations and not the ones done in between. If the file says it's impossible to solve please mark correct field as false. Do not try to solve the problem yourself. Only parse it.\n"
                f"Data:\n{file_content}"
            )

            # Send the prompt to the Gemini model
            response = chat_session.send_message(prompt)

            # Parse the JSON response from the AI
            try:
                response_json = json.loads(response.text)
                solution = response_json.get("solution", [])
            except json.JSONDecodeError:
                print(f"Error decoding JSON from response for {filename}.")
                solution = []

            # Append the result in the desired format
            results.append({"problem_id": problem_id, "solution": solution})

            print("done with", filename)
            time.sleep(4)

    # Write all results to the output file in JSON format
    with open(output_file, "w") as out_f:
        json.dump(results, out_f, indent=4)
    print(f"Results written to {output_file}")


# To run the processing function
if __name__ == "__main__":
    process_files()
