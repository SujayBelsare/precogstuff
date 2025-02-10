import json
import collections
import sys


def find_solution(initial_string, transitions):
    # Each queue element is a tuple: (current_string, depth, path)
    # where path is a list of transition indices applied.
    queue = collections.deque([(initial_string, 0, [])])
    visited = set()

    while queue:
        current_string, depth, path = queue.popleft()

        if depth > 10:
            continue  # Skip states that exceed our depth limit

        if current_string == "":
            return path  # Found a solution

        if current_string in visited:
            continue
        visited.add(current_string)

        for i, transition in enumerate(transitions):
            src, tgt = transition["src"], transition["tgt"]

            # If src is empty, we define the replacement as prepending tgt to the string.
            # (Be careful: with empty src, every string contains it; our depth limit guards against infinite loops.)
            if src == "":
                new_string = tgt + current_string
            else:
                if src in current_string:
                    new_string = current_string.replace(src, tgt, 1)
                else:
                    continue

            new_path = path + [i]
            if new_string not in visited:
                queue.append((new_string, depth + 1, new_path))
    return None  # No solution found within depth limit


def check_all_problems(filename):
    with open(filename, "r") as file:
        data = json.load(file)

    results = []
    for problem in data:
        problem_id = problem["problem_id"]
        initial_string = problem["initial_string"]
        transitions = problem["transitions"]

        solution = find_solution(initial_string, transitions)
        if solution is None:
            solution = []  # If no solution is found, return an empty list

        results.append({"problem_id": problem_id, "solution": solution})

    return results


if __name__ == "__main__":
    filename = "../dataset/combined.json"
    results = check_all_problems(filename)

    # Print the results as a JSON array with indenting.
    print(json.dumps(results, indent=4))
    sys.stdout.flush()
