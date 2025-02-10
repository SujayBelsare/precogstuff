import json
import collections
import sys


def can_reduce_to_empty(initial_string, transitions):
    queue = collections.deque([(initial_string, 0)])  # Store string and depth
    visited = set()

    while queue:
        current_string, depth = queue.popleft()

        if depth > 10:
            return False  # Depth limit exceeded

        if current_string == "":
            return True  # Successfully reduced to empty

        if current_string in visited:
            continue
        visited.add(current_string)

        for transition in transitions:
            src, tgt = transition["src"], transition["tgt"]

            if src in current_string:
                new_string = current_string.replace(src, tgt, 1)
                if new_string not in visited:
                    queue.append((new_string, depth + 1))

    return False  # Could not reduce to empty within depth limit


def check_all_problems(filename):
    with open(filename, "r") as file:
        data = json.load(file)

    results = {}
    for problem in data:
        problem_id = problem["problem_id"]
        initial_string = problem["initial_string"]
        transitions = problem["transitions"]

        results[problem_id] = can_reduce_to_empty(initial_string, transitions)

    return results


if __name__ == "__main__":
    filename = "../dataset/3-hard.json"
    results = check_all_problems(filename)

    for problem_id, result in results.items():
        print(
            f"Problem {problem_id}: {'Can be reduced to empty' if result else 'Cannot be reduced to empty'}"
        )
        # flush
        sys.stdout.flush()
