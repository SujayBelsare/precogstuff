import json
import random
from typing import Any, Dict, List, Tuple, Set, Optional
from chars import letters, numbers, symbols


def biasedCoin(p_head: float) -> int:
    return random.choices([1, 0], weights=[p_head, 1 - p_head])[0]


rules: Dict[str, str] = {}
characters: List[str] = letters


def makerFunction(
    current: str,
    maxSteps: int,
    ruleReuseProbability: float,
    ruleReplaceDifference: int,
) -> str:
    if maxSteps <= 0:
        if current in rules and rules[current] != "":
            makerFunction(current, 1, ruleReuseProbability, ruleReplaceDifference)
            return ""
        else:
            rules[current] = ""
            return ""

    n: int = len(current)
    if n <= 0:
        return ""

    options: list = []
    toss: int = biasedCoin(ruleReuseProbability)

    if toss:
        for src, tgt in rules.items():
            if src in current:
                options.append(src)

        if len(options) != 0:
            choice: int = random.randint(0, len(options) - 1)
            return makerFunction(
                current.replace(options[choice], rules[options[choice]], 1),
                maxSteps - 1,
                ruleReuseProbability,
                ruleReplaceDifference,
            )

    if not toss or len(options) == 0:
        left: int = random.randint(0, n - 1)

        right: int = int(random.gauss(left, 4))

        left, right = sorted((left, right))

        source: str = current[left : right + 1]

        # want to reduce the length by each replacement, but not by too much and not consistently.
        meanLength = max(len(source) - 1, 1)
        stdDev = ruleReplaceDifference

        # new length must be a non negative integer
        newLen = int(random.gauss(meanLength, stdDev))
        newLen = max(2, newLen)

        # randomly generate the target string
        target = "".join(random.choices(characters, k=newLen))

        rules[source] = target

        return makerFunction(
            current.replace(source, target, 1),
            maxSteps - 1,
            ruleReuseProbability,
            ruleReplaceDifference,
        )


def decideParameters(iteration: int) -> Tuple[int, int, float, int]:
    if iteration < 35:
        return 6, 4, 0.4, 1
    if iteration < 70:
        return 9, 8, 0.7, 2
    if iteration < 100:
        global characters
        characters = letters + numbers
        return 9, 12, 0.9, 3


if __name__ == "__main__":
    results = []
    start: int = 70
    end: int = 100

    for i in range(start, end):
        startLen, maxSteps, ruleReuseProbability, ruleReplaceDifference = (
            decideParameters(i)
        )

        # to consistently generate string based on difficulty but with some variation
        length: int = int(random.gauss(startLen + 2, 4))
        length = max(5, length)

        source: str = "".join(random.choices(characters, k=length))

        transitions = makerFunction(
            source, maxSteps, ruleReuseProbability, ruleReplaceDifference
        )

        formattedTransitions = [{"src": src, "tgt": tgt} for src, tgt in rules.items()]

        result = {
            "problem_id": f"{i:03}",
            "initial_string": source,
            "transitions": formattedTransitions,
        }

        rules.clear()
        results.append(result)

    print(json.dumps(results, indent=4))
