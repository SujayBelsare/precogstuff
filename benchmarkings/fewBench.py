import json


def load_data():
    with open("../dataset/combined.json", "r") as f:
        input_data = json.load(f)
    with open("../outputs/fewshot/fewshot.json", "r") as f:
        output_data = json.load(f)
    return input_data, output_data


def apply_transition(current_str, transition):
    src = transition["src"]
    tgt = transition["tgt"]
    pos = current_str.find(src)
    if pos == -1:
        return None
    # Replace only the first occurrence.
    new_str = current_str.replace(src, tgt, 1)
    return new_str


def validate_problem(problem, solution_moves):
    s = problem["initial_string"]
    transitions = problem["transitions"]

    for move in solution_moves:
        if move < 1 or move > len(transitions):
            print(
                f"Invalid move {move} in problem {problem['problem_id']}: no such transition."
            )
            return False
        transition = transitions[move - 1]
        new_s = apply_transition(s, transition)
        if new_s is None:
            print(
                f"Transition {move} (src='{transition['src']}') cannot be applied to '{s}' in problem {problem['problem_id']}"
            )
            return False
        # print(f"Problem {problem['problem_id']}: applying move {move} on '{s}' -> '{new_s}'")
        s = new_s

    if s == "":
        return True
    else:
        print(
            f"After applying all moves, problem {problem['problem_id']} did not reduce to empty string: '{s}'"
        )
        return False


def find_problem(problem_id, dataset):
    for prob in dataset:
        if int(prob["problem_id"]) == int(problem_id) - 1:
            return prob
    return None


def main():
    input_data, output_data = load_data()

    rightCount = 0
    all_valid = True
    for out_entry in output_data:
        pid = out_entry["problem_id"]
        solution_moves = out_entry["solution"]
        prob = find_problem(pid, input_data)
        if prob is None:
            print(f"Problem {pid} not found in input dataset.")
            all_valid = False
            continue
        if validate_problem(prob, solution_moves):
            print(f"Problem {pid} is VALID.")
            rightCount += 1
        else:
            print(f"Problem {pid} is INVALID.")
            all_valid = False

    if all_valid:
        print("All output solutions are valid!")
    else:
        print("Some output solutions are invalid.")

    print(f"Total correct solutions: {rightCount}")


if __name__ == "__main__":
    main()
