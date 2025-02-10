import json
from collections import deque


def load_data():
    with open("../dataset/combined.json", "r") as f:
        input_data = json.load(f)
    with open("../outputs/fewshot/fewshot_08.json", "r") as f:
        output_data = json.load(f)
    return input_data, output_data


def apply_transition(current_str, transition):
    src = transition["src"]
    tgt = transition["tgt"]
    pos = current_str.find(src)
    if pos == -1:
        return None
    new_str = current_str.replace(src, tgt, 1)
    return new_str


def bfs_distance_to_empty(s, transitions, max_depth=10):
    if s == "":
        return 0

    queue = deque([(s, 0)])
    visited = set([s])
    while queue:
        current, depth = queue.popleft()
        if current == "":
            return depth
        if depth >= max_depth:
            continue
        for transition in transitions:
            new_s = apply_transition(current, transition)
            if new_s is not None and new_s not in visited:
                visited.add(new_s)
                queue.append((new_s, depth + 1))
    return None


def validate_problem(problem, solution_moves, output_entry=None):
    metrics = {}
    s = problem["initial_string"]
    metrics["initial_string"] = s
    metrics["initial_length"] = len(s)
    metrics["steps"] = []
    transitions = problem["transitions"]
    correct_moves_count = 0

    for move in solution_moves:
        step_info = {"current_string": s, "move": move}
        if move < 1 or move > len(transitions):
            step_info["error"] = f"Invalid move {move}: no such transition."
            metrics["steps"].append(step_info)
            break
        transition = transitions[move - 1]
        new_s = apply_transition(s, transition)
        if new_s is None:
            step_info["error"] = (
                f"Transition {move} (src='{transition['src']}') cannot be applied to '{s}'."
            )
            metrics["steps"].append(step_info)
            break
        step_info["applied_transition"] = transition
        step_info["result_string"] = new_s
        metrics["steps"].append(step_info)
        s = new_s
        correct_moves_count += 1

    metrics["final_string"] = s
    metrics["final_length"] = len(s)
    metrics["reduction"] = metrics["initial_length"] - metrics["final_length"]
    metrics["correct_moves_count"] = correct_moves_count
    metrics["total_moves"] = len(solution_moves)
    metrics["valid"] = s == ""

    metrics["bfs_distance"] = bfs_distance_to_empty(s, transitions, max_depth=10)

    return metrics


def find_problem(problem_id, dataset):
    for prob in dataset:
        if int(prob["problem_id"]) == int(problem_id) - 1:
            return prob
    return None


def main():
    input_data, output_data = load_data()
    aggregated_metrics = []
    rightCount = 0
    all_valid = True

    for out_entry in output_data:
        pid = out_entry["problem_id"]
        if False and (int(pid) > 100 and int(pid) > 70):
            continue

        solution_moves = out_entry["solution"]
        prob = find_problem(pid, input_data)
        if prob is None:
            print(f"Problem {pid} not found in input dataset.")
            continue

        metrics = validate_problem(prob, solution_moves, output_entry=out_entry)
        metrics["problem_id"] = pid
        aggregated_metrics.append(metrics)

        if metrics["valid"]:
            print(f"Problem {pid} is VALID.")
            rightCount += 1
        else:
            print(f"Problem {pid} is INVALID.")
            all_valid = False

        print(f"Problem {pid} metrics:")
        print(f"  Initial length: {metrics['initial_length']}")
        print(f"  Final length: {metrics['final_length']}")
        print(f"  Reduction: {metrics['reduction']}")
        print(
            f"  Correct moves: {metrics['correct_moves_count']} / {metrics['total_moves']}"
        )
        print(f"  BFS distance (additional moves needed): {metrics['bfs_distance']}")
        print("-" * 50)

    if all_valid:
        print("All output solutions are valid!")
    else:
        print("Some output solutions are invalid.")
    print(f"Total correct solutions: {rightCount}")

    with open("../outputs/fewshot/metrics.json", "w") as f:
        json.dump(aggregated_metrics, f, indent=4)


if __name__ == "__main__":
    main()
