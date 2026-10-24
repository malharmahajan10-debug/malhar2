"""Linked queue (FIFO) -> waiting list when the flight is full.

Named queue_ds.py so it does not clash with Python's built-in `queue` module.
"""


class QNode:
    def __init__(self, data):
        self.data = data
        self.next = None


class Queue:
    def __init__(self):
        self.front = None
        self.rear = None
        self.size = 0

    def is_empty(self):
        return self.front is None

    def enqueue(self, passenger):
        node = QNode(passenger)
        if self.rear is None:
            self.front = self.rear = node
        else:
            self.rear.next = node
            self.rear = node
        self.size += 1

    def dequeue(self):
        if self.is_empty():
            return None
        node = self.front
        self.front = node.next
        if self.front is None:
            self.rear = None
        self.size -= 1
        return node.data

    def peek(self):
        if self.is_empty():
            return None
        return self.front.data

    def find(self, pnr):
        p = self.front
        pnr_clean = str(pnr).strip().upper()
        while p is not None:
            if p.data.pnr.strip().upper() == pnr_clean:
                return True
            p = p.next
        return False

    def find_passenger(self, pnr):
        """Find a passenger in queue. Returns (Passenger, position_1_indexed) or (None, -1)."""
        p, pos = self.front, 1
        pnr_clean = str(pnr).strip().upper()
        while p is not None:
            if p.data.pnr.strip().upper() == pnr_clean:
                return p.data, pos
            p, pos = p.next, pos + 1
        return None, -1

    def remove(self, pnr):
        """Remove a passenger by PNR from the queue (for waiting list cancellation)."""
        if self.is_empty():
            return None

        pnr_clean = str(pnr).strip().upper()

        # If front node matches
        if self.front.data.pnr.strip().upper() == pnr_clean:
            return self.dequeue()

        prev = self.front
        curr = self.front.next
        while curr is not None:
            if curr.data.pnr.strip().upper() == pnr_clean:
                prev.next = curr.next
                if curr == self.rear:
                    self.rear = prev
                self.size -= 1
                return curr.data
            prev = curr
            curr = curr.next
        return None

    def to_list(self):
        """Return list of waiting passengers in FIFO order."""
        result = []
        p = self.front
        while p is not None:
            result.append(p.data)
            p = p.next
        return result

    def display(self):
        if self.is_empty():
            print("Waiting list is empty.")
            return
        print("\n------------ WAITING LIST (front -> rear) ------------")
        p, i = self.front, 1
        while p is not None:
            d = p.data
            print(f"{i}. {d.name:<20} Age:{d.age:<3} PNR:{d.pnr} Pref:{d.seatpref}")
            p, i = p.next, i + 1

