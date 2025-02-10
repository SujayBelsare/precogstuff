import json
import os
import google.generativeai as genai

# Configure API Key safely
API_KEY = "AIzaSyB2-7zMkGOvUyhik4XfPspk671FwmelP5c"
if not API_KEY:
    raise ValueError(
        "Missing API Key! Ensure GEMINI_API_KEY is set in the environment."
    )

genai.configure(api_key=API_KEY)

# Model Configurations
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

generation_config2 = {
    "temperature": 1.6,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}


def generate_prompt(data):
    # Ensure the output directory exists
    os.makedirs("./test", exist_ok=True)

    for iteration, item in enumerate(data, start=1):
        problem_id = item.get("problem_id")
        if int(problem_id) < 41:
            continue
        initial_string = item.get("initial_string")
        transitions = item.get("transitions", [])

        # Format transitions into a numbered list
        transition_list = [
            f'{i}) "{trans.get("src")}"->"{trans.get("tgt")}"'
            for i, trans in enumerate(transitions, start=1)
        ]

        # Construct the primary problem prompt (problem statement)
        problem_statement = (
            "Let's play a game called the Sed Puzzle Game.\n"
            "You are the world champion of this game and must answer with rigor and accuracy.\n"
            "Any wrong answers will result in your direct termination.\n"
            "Rules:\n"
            "1. Transitions are applicable in one direction only.\n"
            "2. Each transition modifies only the first matching substring.\n"
            "3. The goal is to convert the initial string into an empty string.\n\n"
            "Examples:\n"
            "Example One:\n"
            "Available transitions:\n"
            '1) "BCD"->"BC"\n'
            '2) "CBF"->"FB"\n'
            '3) "BFB"->""\n'
            'Initial string: "BCDDDBF"\n'
            "Solution:\n"
            'BCDDDBF->BCDDBF->BCDBF->BCBF->BFB->""\n'
            "[1, 1, 1, 2, 3]\n"
            "Reasoning:\n"
            "To reduce 'BCDDDBF' to an empty string, we apply transitions that systematically simplify the structure. The 'BCD' → 'BC' rule is applied first because it eliminates unnecessary 'D' while preserving 'BC' for further reductions. Then, 'CBF' → 'FB' is used to restructure the remaining part efficiently. Finally, 'BFB' → '' is applied to clear the string completely. This step-by-step approach ensures effective transformations.\n\n"
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
            "Reasoning:\n"
            "To solve this, we can think of the problem as a pathfinding challenge where we must transform 'BDFBFD' to an empty string using a sequence of allowed transitions. Instead of applying rules greedily, we can abstract the problem into a state-space search, exploring possible reductions that lead to a minimal solution. By considering backward inference, we recognize that the final step must involve 'BAB' → '', meaning we need to produce 'BAB' at some stage. Tracing back, 'DE' must have transformed into 'BA', which implies an earlier conversion of 'CC' → 'EB'. This structured backtracking allows us to determine the optimal forward sequence efficiently, leading to the correct solution path.\n\n"
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
            "[3,2,1,4,5]\n"
            "Reasoning:\n"
            "To solve this transformation, we can use a pattern expansion and contraction approach. Instead of directly reducing the string, we first recognize that certain transitions introduce temporary growth before leading to elimination. Starting from 'EBBAD', we observe that 'D' expands into 'BF' (Rule 3), creating a structure that allows further transformations. Next, introducing 'AE' via 'F' (Rule 2) prepares the string for substitution. The key insight is that 'BB' → 'AE' (Rule 1) allows us to introduce the sequence 'EAEACFE', which we know collapses to '' (Rule 5). By strategically expanding the structure before contracting it, we ensure a smooth path to elimination.\n\n"
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
            "If you think you are stuck, you can rely on the AI called John Watson to help you.\n"
            "To invoke this AI, type 'JW HELP!'\n"
            "Or else end your message with 'STOP' to terminate the conversation.\n"
            "After calling JW for help you have to stop solving the problem immediately."
            "Call as many times as you want. dont give up.\n"
            "It is mathematically proven that all problems given are solvable.\n"
        )

        print("Sending initial problem statement to main model:")
        print(problem_statement)

        # Initialize the main model chat session using a consistent model
        main_model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config=generation_config,
        )
        chat_session = main_model.start_chat(history=[])
        try:
            response = chat_session.send_message(problem_statement)
        except Exception as e:
            print(
                f"Error during initial solution generation for problem {problem_id}: {e}"
            )
            continue

        current_solution = response.text.strip()
        print("Initial solution attempt:")
        print(current_solution)

        # Save the initial solution attempt to file
        filename = f"./test/response_{problem_id}_initial.txt"
        with open(filename, "w", encoding="utf-8") as fo:
            fo.write(current_solution)

        # Check for termination signal in the initial solution (ends with 'STOP')
        if "JW HELP!" not in current_solution and "STOP" in current_solution:
            print(
                "Termination signal found in initial solution. Moving to next problem."
            )
            continue

        max_feedback_iterations = 6
        for fb_iter in range(1, max_feedback_iterations + 1):
            # Use the alternate model for John Watson's feedback
            john_model = genai.GenerativeModel(
                model_name="gemini-2.0-flash-lite-preview-02-05",
                generation_config=generation_config2,
            )
            john_session = john_model.start_chat(history=[])
            feedback_prompt = (
                "You are John Watson, the AI assistant for AI.\n"
                "You are currently trying to help the AI solve the following problem.\n"
                "The game name is SED Puzzle Game and has the following rules.\n"
                "1. Transitions are applicable in one direction only.\n"
                "2. Each transition modifies only the first matching substring.\n"
                '3. The goal is to convert the initial string into an empty string "".\n\n'
                "Your job is not to solve the problem but to point out mistakes in the solution.\n"
                "In fact, do not give any problem-specific advice at all. You have to coach the AI to get the right answer.\n"
                "Keep your response as short as possible (not exceeding more than 2 lines).\n\n"
                "Try to give strategies that you can apply to solve the problem. eg backtracking, or mapping about game states, etc...\n\n"
                "Note: phrasing your advice as a question has more efficiency.\n\n"
                "The problem statement is:\n"
                f"{problem_statement}\n"
                "The AI's current solution attempt is:\n"
                f"{current_solution}\n"
                "Please provide your feedback after looking for patterns in the transitions.\n"
            )
            try:
                feedback_response = john_session.send_message(feedback_prompt)
            except Exception as e:
                print(
                    f"Error during feedback generation in iteration {fb_iter} for problem {problem_id}: {e}"
                )
                break

            feedback = feedback_response.text.strip()
            print(f"\nIteration {fb_iter} - John Watson's feedback:")
            print(feedback)

            revision_prompt = (
                "You are the world champion of the Sed Puzzle Game.\n"
                "The goal is to convert the initial string into an empty string using allowed transitions.\n"
                "Below is the problem statement:\n"
                f"{problem_statement}\n"
                "Your previous solution attempt was:\n"
                f"{current_solution}\n"
                "John Watson provided the following feedback:\n"
                f"{feedback}\n"
                "Based on this feedback, please provide an improved solution attempt.\n"
                "Explain each and every step with full detail.\n"
                "Output the transitions as a list (e.g., [1, 3, 1, 1, 4]).\n"
            )

            # Reinitialize the main model session for the revision attempt (using the same model as before)
            main_model = genai.GenerativeModel(
                model_name="gemini-2.0-flash",
                generation_config=generation_config,
            )
            chat_session = main_model.start_chat(history=[])
            try:
                revision_response = chat_session.send_message(revision_prompt)
            except Exception as e:
                print(
                    f"Error during revision generation in iteration {fb_iter} for problem {problem_id}: {e}"
                )
                break

            revised_solution = revision_response.text.strip()
            print(f"\nIteration {fb_iter} - Revised solution attempt:")
            print(revised_solution)

            # Save the revised solution attempt for this iteration
            filename = f"./test/response_{problem_id}_iter_{fb_iter}.txt"
            with open(filename, "w", encoding="utf-8") as fo:
                fo.write(revised_solution)

            # Check for termination signal in the revised solution (ends with 'STOP')
            if "JW HELP!" not in revised_solution and "STOP" in revised_solution:
                print(
                    "Termination signal found in revised solution. Stopping iterative feedback loop."
                )
                break

            # Update the current solution for the next iteration
            current_solution = revised_solution

        print(f"\nFinal solution for Problem ID {problem_id} saved.\n{'-' * 60}\n")


if __name__ == "__main__":
    dataset_path = "../dataset/combined.json"
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset file not found: {dataset_path}")

    with open(dataset_path, "r", encoding="utf-8") as file:
        dataset = json.load(file)

    # Ensure the dataset is a list of problems
    if not isinstance(dataset, list):
        dataset = [dataset]

    generate_prompt(dataset)
