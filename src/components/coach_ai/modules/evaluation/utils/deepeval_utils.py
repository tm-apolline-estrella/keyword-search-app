# Import standard library modules
import re
from typing import Any, List


def _get_average_score(test_results: List[Any]):
    scores = [test_result.metrics_data[0].score for test_result in test_results]
    return sum(scores) / len(scores)


def extract_words(input_string):
    pattern = r"\[(.*?)\]"
    match = re.findall(pattern, input_string)
    if match:
        content = match[0]
        words = [word.strip() for word in content.split(",")]
        return words
    else:
        return []
