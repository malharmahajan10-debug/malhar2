"""Array-based stack (LIFO) -> cancellation history / undo."""

from settings import STACK_MAX


class Stack:
    def __init__(self, capacity=STACK_MAX):
        self.items = [None] * capacity       # fixed-size array
        self.top = -1
        self.capacity = capacity

    def is_empty(self):
        return self.top == -1

    def is_full(self):
        return self.top == self.capacity - 1

    def push(self, passenger):
        if self.is_full():
            return False
        self.top += 1
        self.items[self.top] = passenger
        return True

    def pop(self):
        if self.is_empty():
            return None
        item = self.items[self.top]
        self.items[self.top] = None
        self.top -= 1
        return item

    def peek(self):
        if self.is_empty():
            return None
        return self.items[self.top]

    def size(self):
        return self.top + 1

    def to_list(self):
        """Return list of cancelled passengers, latest (top) first."""
        return [self.items[i] for i in range(self.top, -1, -1) if self.items[i] is not None]

    def display(self):
        if self.is_empty():
            print("No cancellation history.")
            return
        print("\n---- CANCELLATION HISTORY (latest first) ----")
        for i in range(self.top, -1, -1):
            d = self.items[i]
            if d is not None:
                print(f"{d.pnr}  ({d.name}, age {d.age})")

