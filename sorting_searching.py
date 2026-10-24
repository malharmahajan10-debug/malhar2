"""Sorting and searching algorithms on arrays."""


def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key


def binary_search(arr, key):
    """arr must be sorted. Returns index or -1."""
    key_str = str(key).strip().upper()
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        mid_val = str(arr[mid]).strip().upper()
        if mid_val == key_str:
            return mid
        if mid_val < key_str:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def binary_search_detailed(arr, key):
    """Educational helper for project viva/UI: returns (index, comparisons, steps_log)."""
    key_str = str(key).strip().upper()
    lo, hi = 0, len(arr) - 1
    comparisons = 0
    steps = []

    while lo <= hi:
        mid = (lo + hi) // 2
        comparisons += 1
        mid_val = str(arr[mid]).strip().upper()
        steps.append({
            "step": comparisons,
            "low": lo,
            "high": hi,
            "mid": mid,
            "value": arr[mid],
            "comparison": "equal" if mid_val == key_str else ("less" if mid_val < key_str else "greater")
        })
        if mid_val == key_str:
            return mid, comparisons, steps
        if mid_val < key_str:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1, comparisons, steps

