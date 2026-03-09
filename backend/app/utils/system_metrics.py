from collections import deque
from statistics import mean
from threading import Lock


_MAX_POINTS = 5000
_METRIC_HISTORY = {}
_LOCK = Lock()


def _percentile(values, percentile):
    if not values:
        return 0.0
    if len(values) == 1:
        return float(values[0])
    idx = (len(values) - 1) * (float(percentile) / 100.0)
    lower = int(idx)
    upper = min(lower + 1, len(values) - 1)
    fraction = idx - lower
    return float(values[lower] + (values[upper] - values[lower]) * fraction)


def record_metric(name, duration_ms):
    if not name:
        return
    try:
        value = float(duration_ms)
    except Exception:
        return
    if value < 0:
        return

    with _LOCK:
        history = _METRIC_HISTORY.get(name)
        if history is None:
            history = deque(maxlen=_MAX_POINTS)
            _METRIC_HISTORY[name] = history
        history.append(value)


def get_metrics_snapshot():
    with _LOCK:
        snapshot = {}
        for name, history in _METRIC_HISTORY.items():
            values = list(history)
            if not values:
                continue
            ordered = sorted(values)
            snapshot[name] = {
                "count": len(values),
                "avg_ms": round(float(mean(values)), 4),
                "min_ms": round(float(ordered[0]), 4),
                "max_ms": round(float(ordered[-1]), 4),
                "p50_ms": round(_percentile(ordered, 50), 4),
                "p95_ms": round(_percentile(ordered, 95), 4),
                "last_ms": round(float(values[-1]), 4),
            }
        return snapshot


def reset_metrics():
    with _LOCK:
        _METRIC_HISTORY.clear()
