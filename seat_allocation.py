"""Fixed-size array -> seat map."""

from settings import MAX_SEATS, SEAT_PRICES


class SeatMap:
    def __init__(self, n=MAX_SEATS):
        self.n = n
        self.seats = [0] * (n + 1)           # index 0 unused; 0 = free, 1 = booked

    def get_seat_type(self, seat_no):
        """Return seat type: W (Window), M (Middle), A (Aisle) based on 3-abreast seating."""
        rem = (seat_no - 1) % 3
        if rem == 0:
            return "W"
        elif rem == 1:
            return "M"
        else:
            return "A"

    def get_seat_price(self, seat_no):
        """Return seat price in INR: Window=1200, Middle=1000, Aisle=900."""
        st = self.get_seat_type(seat_no)
        return SEAT_PRICES.get(st, 1000)

    def allocate(self, pref=None):
        """Allocate a seat. If pref (W/A/M) is given, try matching preference first."""
        if pref in ("W", "A", "M"):
            # First pass: try to satisfy preference
            for i in range(1, self.n + 1):
                if self.seats[i] == 0 and self.get_seat_type(i) == pref:
                    self.seats[i] = 1
                    return i

        # Second pass (or if no pref): allocate first available seat
        for i in range(1, self.n + 1):
            if self.seats[i] == 0:
                self.seats[i] = 1
                return i
        return 0                              # flight full

    def allocate_specific(self, seat_no):
        """Allocate a specific chosen seat by seat number (O(1) array access).
        Returns seat_no if allocated, 0 if invalid or already booked."""
        try:
            seat_no = int(seat_no)
        except (ValueError, TypeError):
            return 0

        if 1 <= seat_no <= self.n:
            if self.seats[seat_no] == 0:
                self.seats[seat_no] = 1
                return seat_no
        return 0

    def is_seat_available(self, seat_no):
        """Check if a specific seat is free (O(1) array lookup)."""
        try:
            seat_no = int(seat_no)
        except (ValueError, TypeError):
            return False

        if 1 <= seat_no <= self.n:
            return self.seats[seat_no] == 0
        return False

    def free(self, seat_no):
        if 1 <= seat_no <= self.n:
            self.seats[seat_no] = 0


    def is_full(self):
        return all(self.seats[i] == 1 for i in range(1, self.n + 1))

    def available_count(self):
        return self.seats[1:self.n + 1].count(0)

    def booked_count(self):
        return self.seats[1:self.n + 1].count(1)

    def get_map_list(self):
        """Return structured seat list with pricing for GUI/Web interface."""
        return [
            {
                "seat_no": i,
                "is_booked": bool(self.seats[i]),
                "type": self.get_seat_type(i),
                "price": self.get_seat_price(i),
            }
            for i in range(1, self.n + 1)
        ]

    def show(self):
        print("\n--- Aircraft Seat Map (X = booked, number = free, W=₹1200, M=₹1000, A=₹900) ---")
        for i in range(1, self.n + 1):
            pref_tag = self.get_seat_type(i)
            price = self.get_seat_price(i)
            print("[ X ]" if self.seats[i] else f"[{i}:{pref_tag}:₹{price}]", end=" ")
            if i % 3 == 0:
                print()
        print()

