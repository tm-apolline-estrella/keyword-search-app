# Import standard library modules
from typing import Dict, List, Tuple


def _sum_of_ranges(ranges):
    return sum(end - start for start, end in ranges)


def _union_ranges(ranges):
    # Sort ranges based on the starting index
    sorted_ranges = sorted(ranges, key=lambda x: x[0])

    # Initialize with the first range
    merged_ranges = [sorted_ranges[0]]

    for current_start, current_end in sorted_ranges[1:]:
        last_start, last_end = merged_ranges[-1]

        # Check if the current range overlaps or is contiguous with the last range in the merged list
        if current_start <= last_end:
            # Merge the two ranges
            merged_ranges[-1] = (last_start, max(last_end, current_end))
        else:
            # No overlap, add the current range as new
            merged_ranges.append((current_start, current_end))

    return merged_ranges


def _intersect_two_ranges(range1, range2):
    # Unpack the ranges
    start1, end1 = range1
    start2, end2 = range2

    # Calculate the maximum of the starting indices and the minimum of the ending indices
    intersect_start = max(start1, start2)
    intersect_end = min(end1, end2)

    # Check if the intersection is valid (the start is less than or equal to the end)
    if intersect_start <= intersect_end:
        return (intersect_start, intersect_end)
    else:
        return None  # Return an None if there is no intersection


def _difference(ranges, target):
    """
    Takes a set of ranges and a target range, and returns the difference.

    Args:
    - ranges (list of tuples): A list of tuples representing ranges. Each tuple is (a, b) where a <= b.
    - target (tuple): A tuple representing a target range (c, d) where c <= d.

    Returns:
    - List of tuples representing ranges after removing the segments that overlap with the target range.
    """
    result = []
    target_start, target_end = target

    for start, end in ranges:
        if end < target_start or start > target_end:
            # No overlap
            result.append((start, end))
        elif start < target_start and end > target_end:
            # Target is a subset of this range, split it into two ranges
            result.append((start, target_start))
            result.append((target_end, end))
        elif start < target_start:
            # Overlap at the start
            result.append((start, target_start))
        elif end > target_end:
            # Overlap at the end
            result.append((target_end, end))
        # Else, this range is fully contained by the target, and is thus removed

    return result


def get_context_scores(groundtruth: Dict, retrieved_chunks: List[Dict]) -> Dict:
    # question = groundtruth["question"]
    references = groundtruth["references"]
    source = groundtruth["source"]

    numerator_sets = []
    denominator_chunks_sets = []
    unused_highlights = [(x["start_index"], x["end_index"]) for x in references]

    for metadata in retrieved_chunks:
        # Unpack chunk start and end indices
        chunk_start, chunk_end, chunk_corpus_id = (
            metadata["start_index"],
            metadata["end_index"],
            metadata["source"],
        )

        if chunk_corpus_id != source:
            continue

        # for reference, ref_start, ref_end in references:
        for ref_obj in references:
            # reference = ref_obj["content"]
            ref_start, ref_end = int(ref_obj["start_index"]), int(ref_obj["end_index"])

            # Calculate intersection between chunk and reference
            intersection = _intersect_two_ranges(
                (chunk_start, chunk_end), (ref_start, ref_end)
            )

            if intersection is not None:
                # Remove intersection from unused highlights
                unused_highlights = _difference(unused_highlights, intersection)

                # Add intersection to numerator sets
                numerator_sets = _union_ranges([intersection] + numerator_sets)

                # Add chunk to denominator sets
                denominator_chunks_sets = _union_ranges(
                    [(chunk_start, chunk_end)] + denominator_chunks_sets
                )

    if numerator_sets:
        numerator_value = _sum_of_ranges(numerator_sets)
    else:
        numerator_value = 0

    recall_denominator = _sum_of_ranges(
        [(x["start_index"], x["end_index"]) for x in references]
    )
    precision_denominator = _sum_of_ranges(
        [(x["start_index"], x["end_index"]) for x in retrieved_chunks]
    )
    # iou_denominator = precision_denominator + _sum_of_ranges(unused_highlights)

    recall_score = numerator_value / recall_denominator
    precision_score = numerator_value / precision_denominator
    # iou_score = numerator_value / iou_denominator

    return {"recall": recall_score, "precision": precision_score}
