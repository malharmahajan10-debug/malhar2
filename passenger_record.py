"""Passenger record stored inside every data structure."""


class Passenger:
    def __init__(self, pnr, name, age, seatpref, seat_no=0, fare=0):
        self.pnr = pnr
        self.name = name
        self.age = age
        self.seatpref = seatpref    # W / A / M
        self.seat_no = seat_no      # 0 = not assigned (waiting)
        self.fare = fare            # Ticket fare in INR (₹)

    def to_dict(self):
        return {
            "pnr": self.pnr,
            "name": self.name,
            "age": self.age,
            "seatpref": self.seatpref,
            "seat_no": self.seat_no,
            "fare": self.fare,
        }

    def __repr__(self):
        return f"Passenger(pnr='{self.pnr}', name='{self.name}', age={self.age}, pref='{self.seatpref}', seat={self.seat_no}, fare={self.fare})"

    def __str__(self):
        status = f"Seat {self.seat_no} (₹{self.fare:,})" if self.seat_no > 0 else f"Waiting (Est. ₹{self.fare:,})"
        return f"[{self.pnr}] {self.name} (Age: {self.age}, Pref: {self.seatpref}, {status})"

