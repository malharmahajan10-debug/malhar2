"""Doubly linked list -> confirmed tickets."""


class TicketNode:
    def __init__(self, data):
        self.data = data
        self.next = None
        self.prev = None


class TicketList:
    def __init__(self):
        self.start = None
        self.last = None
        self.count = 0

    def append(self, passenger):
        node = TicketNode(passenger)
        if self.start is None:
            self.start = self.last = node
        else:
            node.prev = self.last
            self.last.next = node
            self.last = node
        self.count += 1

    def prepend(self, passenger):
        """Insert passenger at the HEAD of the Doubly Linked List (O(1)).
        Ensures newly confirmed tickets appear first in the confirmed manifest."""
        node = TicketNode(passenger)
        if self.start is None:
            self.start = self.last = node
        else:
            node.next = self.start
            self.start.prev = node
            self.start = node
        self.count += 1

    def find(self, pnr):                       # linear search
        p = self.start
        pnr_clean = str(pnr).strip().upper()
        while p is not None:
            if p.data.pnr.strip().upper() == pnr_clean:
                return p
            p = p.next
        return None

    def remove(self, node):
        if node is None:
            return
        if node.prev:
            node.prev.next = node.next
        else:
            self.start = node.next

        if node.next:
            node.next.prev = node.prev
        else:
            self.last = node.prev

        node.prev = None
        node.next = None
        self.count -= 1

    def bubble_sort(self, key="name", by_age=False):       # swaps data, not nodes
        if self.start is None:
            return
        if by_age:
            key = "age"

        swapped = True
        while swapped:
            swapped = False
            p = self.start
            while p.next is not None:
                a, b = p.data, p.next.data
                if key == "age":
                    out_of_order = a.age > b.age
                elif key == "seat":
                    out_of_order = a.seat_no > b.seat_no
                elif key == "pnr":
                    out_of_order = a.pnr.upper() > b.pnr.upper()
                else:  # default "name"
                    out_of_order = a.name.lower() > b.name.lower()

                if out_of_order:
                    p.data, p.next.data = b, a
                    swapped = True
                p = p.next

    def pnr_array(self):
        """Copy all PNRs into a plain array (used for binary search)."""
        arr, p = [], self.start
        while p is not None:
            arr.append(p.data.pnr)
            p = p.next
        return arr

    def to_list(self):
        """Return list of confirmed passengers in order."""
        res, p = [], self.start
        while p is not None:
            res.append(p.data)
            p = p.next
        return res


    def display(self):
        if self.start is None:
            print("No confirmed tickets.")
            return
        line = "=" * 74
        print("\n" + line)
        print(f"| {'No':<3} | {'Passenger Name':<20} | {'Age':<4} | {'PNR':<12} | {'Pref':<4} | {'Seat':<4} |")
        print(line)
        p, i = self.start, 1
        while p is not None:
            d = p.data
            print(f"| {i:<3} | {d.name:<20} | {d.age:<4} | {d.pnr:<12} | {d.seatpref:<4} | {d.seat_no:<4} |")
            p, i = p.next, i + 1
        print(line)
