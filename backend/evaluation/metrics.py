def safe_div(numerator, denominator):
    denominator = float(denominator)
    if denominator <= 0:
        return 0.0
    return float(numerator) / denominator


def precision_recall(predicted, truth):
    predicted_set = set(predicted or [])
    truth_set = set(truth or [])
    intersection = predicted_set.intersection(truth_set)
    precision = safe_div(len(intersection), len(predicted_set))
    recall = safe_div(len(intersection), len(truth_set))
    return precision, recall


def top_k_hit(predicted_ids, truth_ids, k):
    if not truth_ids:
        return 0.0
    top_k = set((predicted_ids or [])[: max(1, int(k))])
    truth = set(truth_ids)
    return 1.0 if top_k.intersection(truth) else 0.0


def recall_at_k(predicted_ids, truth_ids, k):
    if not truth_ids:
        return 0.0
    top_k = set((predicted_ids or [])[: max(1, int(k))])
    truth = set(truth_ids)
    return safe_div(len(top_k.intersection(truth)), len(truth))
