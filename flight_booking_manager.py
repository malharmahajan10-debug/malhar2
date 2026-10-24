"""Business logic: ties all data structures together."""

import random
import string

from passenger_record import Passenger
from confirmed_tickets import TicketList
from waiting_queue import Queue
from cancellation_stack import Stack
from seat_allocation import SeatMap
from sorting_searching import insertion_sort, binary_search

class FlightBookingSystem:
    def __init__(self):
        self.tickets = TicketList()    # doubly linked list
        self.waiting = Queue()         # queue
        self.history = Stack()         # stack
        self.seatmap = SeatMap()       # array

    def _unique_pnr(self):
        chars = string.digits + string.ascii_uppercase
        while True:
            pnr = "".join(random.choice(chars) for _ in range(10))
            if self.tickets.find(pnr) is None and not self.waiting.find(pnr):
                return pnr

    # ------------------ Core Business Logic Methods ------------------

    def book_ticket(self, name, age, pref="W", seat_no=None, prepend=True):
        """Book a ticket programmatically (used by GUI, Web API, and CLI).
        Allows choosing a specific seat number, or auto-assigning by preference.
        Newly booked seats are prepended to the Doubly Linked List to show first."""
        name = str(name).strip()
        if not name:
            return {"success": False, "message": "Name cannot be empty."}

        try:
            age = int(age)
        except (ValueError, TypeError):
            return {"success": False, "message": "Invalid age. Must be a number."}

        if not 0 < age <= 120:
            return {"success": False, "message": "Invalid age. Must be between 1 and 120."}

        pref = str(pref).strip().upper()
        if pref not in ("W", "A", "M"):
            pref = "W"

        pnr = self._unique_pnr()

        # Check if user requested a specific seat number
        specific_seat = None
        if seat_no is not None:
            try:
                s_int = int(seat_no)
                if s_int > 0:
                    specific_seat = s_int
            except (ValueError, TypeError):
                specific_seat = None

        if specific_seat is not None:
            if not 1 <= specific_seat <= self.seatmap.n:
                return {
                    "success": False,
                    "message": f"Invalid seat number #{specific_seat}. Flight has seats 1 to {self.seatmap.n}."
                }
            if not self.seatmap.is_seat_available(specific_seat):
                return {
                    "success": False,
                    "message": f"Seat #{specific_seat} is already booked! Please select an available seat or choose Auto-assign."
                }

            allocated_seat = self.seatmap.allocate_specific(specific_seat)
            actual_pref = self.seatmap.get_seat_type(allocated_seat)
            fare = self.seatmap.get_seat_price(allocated_seat)
            p = Passenger(pnr, name, age, actual_pref, seat_no=allocated_seat, fare=fare)
            if prepend:
                self.tickets.prepend(p)
            else:
                self.tickets.append(p)
            msg = f"Ticket CONFIRMED. PNR: {pnr} | Seat No: {allocated_seat} ({actual_pref}) | Fare: ₹{fare:,}"
            return {
                "success": True,
                "status": "CONFIRMED",
                "passenger": p,
                "seat": allocated_seat,
                "fare": fare,
                "pnr": pnr,
                "message": msg
            }

        # Auto-assignment by preference
        seat = self.seatmap.allocate(pref)
        if seat > 0:
            seat_type = self.seatmap.get_seat_type(seat)
            fare = self.seatmap.get_seat_price(seat)
            p = Passenger(pnr, name, age, seat_type, seat_no=seat, fare=fare)
            if prepend:
                self.tickets.prepend(p)
            else:
                self.tickets.append(p)
            msg = f"Ticket CONFIRMED. PNR: {p.pnr} | Seat No: {seat} ({seat_type}) | Fare: ₹{fare:,}"
            return {
                "success": True,
                "status": "CONFIRMED",
                "passenger": p,
                "seat": seat,
                "fare": fare,
                "pnr": pnr,
                "message": msg
            }
        else:
            from settings import SEAT_PRICES
            est_fare = SEAT_PRICES.get(pref, 1000)
            p = Passenger(pnr, name, age, pref, seat_no=0, fare=est_fare)
            self.waiting.enqueue(p)
            pos = self.waiting.size
            msg = f"Flight full! Added to WAITING LIST (position {pos}). PNR: {p.pnr} | Est. Fare: ₹{est_fare:,}"
            return {
                "success": True,
                "status": "WAITING",
                "passenger": p,
                "seat": 0,
                "fare": est_fare,
                "pnr": pnr,
                "position": pos,
                "message": msg
            }


    def cancel_ticket(self, pnr):
        """Cancel a ticket by PNR (handles both confirmed tickets and waiting list)."""
        pnr_clean = str(pnr).strip().upper()
        if not pnr_clean:
            return {"success": False, "message": "Please enter a valid PNR."}

        # 1. Check confirmed tickets (doubly linked list)
        node = self.tickets.find(pnr_clean)
        if node is not None:
            cancelled = node.data
            if not self.history.push(cancelled):
                print("(History stack full, cannot record undo for this cancellation.)")

            self.tickets.remove(node)
            self.seatmap.free(cancelled.seat_no)

            # Promote first waiting passenger (Queue FIFO)
            nxt = self.waiting.dequeue()
            promoted_msg = ""
            if nxt is not None:
                nxt.seat_no = self.seatmap.allocate(nxt.seatpref)
                nxt.seatpref = self.seatmap.get_seat_type(nxt.seat_no)
                nxt.fare = self.seatmap.get_seat_price(nxt.seat_no)
                self.tickets.prepend(nxt)
                promoted_msg = f" Waiting passenger {nxt.name} (PNR {nxt.pnr}) is now CONFIRMED on Seat {nxt.seat_no} ({nxt.seatpref}, Fare ₹{nxt.fare:,})."

            msg = f"Confirmed ticket for {cancelled.name} (PNR {cancelled.pnr}, Seat {cancelled.seat_no}) cancelled successfully.{promoted_msg}"
            return {
                "success": True,
                "type": "confirmed",
                "cancelled": cancelled,
                "promoted": nxt,
                "message": msg
            }

        # 2. Check waiting list (queue)
        waiting_p = self.waiting.remove(pnr_clean)
        if waiting_p is not None:
            msg = f"Waiting list ticket for {waiting_p.name} (PNR {waiting_p.pnr}) cancelled successfully."
            return {
                "success": True,
                "type": "waiting",
                "cancelled": waiting_p,
                "promoted": None,
                "message": msg
            }

        return {"success": False, "message": f"No passenger found with PNR '{pnr_clean}'."}

    def undo_cancellation(self):
        """Undo last cancellation using the LIFO Stack."""
        p = self.history.pop()
        if p is None:
            return {"success": False, "message": "Nothing to undo. Cancellation history stack is empty."}

        seat = self.seatmap.allocate(p.seatpref)
        if seat > 0:
            p.seat_no = seat
            p.seatpref = self.seatmap.get_seat_type(seat)
            p.fare = self.seatmap.get_seat_price(seat)
            self.tickets.prepend(p)
            msg = f"Cancellation undone. {p.name} restored with Seat {seat} ({p.seatpref}, Fare ₹{p.fare:,}) (PNR {p.pnr})."
            return {
                "success": True,
                "status": "CONFIRMED",
                "passenger": p,
                "seat": seat,
                "fare": p.fare,
                "message": msg
            }
        else:
            p.seat_no = 0
            self.waiting.enqueue(p)
            pos = self.waiting.size
            msg = f"Flight is currently full. {p.name} (PNR {p.pnr}) restored to WAITING LIST at position {pos}."
            return {
                "success": True,
                "status": "WAITING",
                "passenger": p,
                "seat": 0,
                "position": pos,
                "message": msg
            }

    def search_pnr(self, pnr):
        """Linear search across confirmed tickets (linked list) and waiting list (queue)."""
        pnr_clean = str(pnr).strip().upper()
        if not pnr_clean:
            return {"found": False, "message": "Please enter a valid PNR."}

        node = self.tickets.find(pnr_clean)
        if node is not None:
            d = node.data
            return {
                "found": True,
                "status": "CONFIRMED",
                "passenger": d,
                "message": f"CONFIRMED -> {d.name}, Age {d.age}, Seat {d.seat_no} (Pref {d.seatpref})"
            }

        wait_p, pos = self.waiting.find_passenger(pnr_clean)
        if wait_p is not None:
            return {
                "found": True,
                "status": "WAITING",
                "passenger": wait_p,
                "position": pos,
                "message": f"WAITING LIST (Position {pos}) -> {wait_p.name}, Age {wait_p.age}, Pref {wait_p.seatpref}"
            }

        return {"found": False, "status": "NOT_FOUND", "message": f"PNR '{pnr_clean}' not found."}

    def fast_search_pnr(self, pnr):
        """Fast binary search using sorted array of PNRs."""
        pnr_clean = str(pnr).strip().upper()
        arr = self.tickets.pnr_array()
        if not arr:
            # Check waiting list if no confirmed tickets
            wait_p, pos = self.waiting.find_passenger(pnr_clean)
            if wait_p:
                return {
                    "found": True,
                    "status": "WAITING",
                    "passenger": wait_p,
                    "position": pos,
                    "comparisons": 0,
                    "message": f"PNR '{pnr_clean}' is on the WAITING LIST at position {pos}."
                }
            return {
                "found": False,
                "status": "EMPTY",
                "message": "No confirmed tickets available to search."
            }

        insertion_sort(arr)
        from sorting_searching import binary_search_detailed
        idx, comparisons, steps = binary_search_detailed(arr, pnr_clean)

        if idx >= 0:
            found_pnr = arr[idx]
            node = self.tickets.find(found_pnr)
            d = node.data if node else None
            msg = f"PNR found via Binary Search in {comparisons} comparison(s) (sorted position {idx + 1}): "
            if d:
                msg += f"CONFIRMED -> {d.name}, Age {d.age}, Seat {d.seat_no} (Pref {d.seatpref})"
            return {
                "found": True,
                "status": "CONFIRMED",
                "passenger": d,
                "sorted_position": idx + 1,
                "comparisons": comparisons,
                "steps": steps,
                "message": msg
            }

        # Check waiting queue as fallback
        wait_p, pos = self.waiting.find_passenger(pnr_clean)
        if wait_p is not None:
            return {
                "found": True,
                "status": "WAITING",
                "passenger": wait_p,
                "position": pos,
                "comparisons": comparisons,
                "steps": steps,
                "message": f"PNR not in confirmed list, but found on WAITING LIST at position {pos}."
            }

        return {
            "found": False,
            "status": "NOT_FOUND",
            "comparisons": comparisons,
            "steps": steps,
            "message": f"PNR '{pnr_clean}' not found after {comparisons} binary search comparisons."
        }

    def sort_tickets(self, by="name"):
        """Sort confirmed tickets doubly linked list using Bubble Sort."""
        by_age = str(by).lower() in ("2", "age")
        self.tickets.bubble_sort(by_age=by_age)
        return "age" if by_age else "name"

    def get_system_state(self):
        """Return a complete dictionary of current system state for UI/Web."""
        confirmed_list = [p.to_dict() for p in self.tickets.to_list()]
        total_revenue = sum(p.fare for p in self.tickets.to_list())
        return {
            "max_seats": self.seatmap.n,
            "available_seats": self.seatmap.available_count(),
            "booked_seats": self.seatmap.booked_count(),
            "confirmed_count": self.tickets.count,
            "waiting_count": self.waiting.size,
            "history_count": self.history.size(),
            "total_revenue": total_revenue,
            "seat_prices": {"Window": 1200, "Middle": 1000, "Aisle": 900},
            "seat_map": self.seatmap.get_map_list(),
            "confirmed_tickets": confirmed_list,
            "waiting_list": [
                {**p.to_dict(), "position": i + 1}
                for i, p in enumerate(self.waiting.to_list())
            ],
            "cancellation_history": [p.to_dict() for p in self.history.to_list()],
        }

    # ------------------ Console / CLI Wrapper Methods ------------------

    def book(self):
        name = input("Enter passenger name: ").strip()
        if not name:
            print("Name cannot be empty.")
            return

        try:
            age = int(input("Enter age: "))
        except ValueError:
            print("Invalid age.")
            return

        if not 0 < age <= 120:
            print("Invalid age. Must be between 1 and 120.")
            return

        # Show available seats with pricing so user can choose specific seat
        available_seats = [s for s in range(1, self.seatmap.n + 1) if self.seatmap.is_seat_available(s)]
        seat_no = 0
        if available_seats:
            print("\nAircraft Seats & Pricing (X = Booked):")
            for s in range(1, self.seatmap.n + 1):
                st = self.seatmap.get_seat_type(s)
                pr = self.seatmap.get_seat_price(s)
                if self.seatmap.is_seat_available(s):
                    print(f"[{s}:{st}:₹{pr}]", end=" ")
                else:
                    print("[ X ]", end=" ")
                if s % 3 == 0:
                    print()
            print()
            seat_input = input("Enter specific seat number (or press Enter / 0 for auto-assign): ").strip()
            seat_no = int(seat_input) if seat_input.isdigit() else 0
        else:
            print("\nNotice: All seats are currently occupied. Booking will place passenger on the Waiting List.")

        pref = "W"
        if seat_no == 0:
            print("\nSeat Pricing: Window = ₹1,200 | Middle = ₹1,000 | Aisle = ₹900")
            pref = input("Enter seat preference (W=Window ₹1200 / M=Middle ₹1000 / A=Aisle ₹900) [Default W]: ").strip().upper()
            if pref not in ("W", "A", "M"):
                pref = "W"

        res = self.book_ticket(name, age, pref, seat_no=seat_no)

        # Print ticket info first!
        if res.get("success"):
            p = res.get("passenger")
            st_type = self.seatmap.get_seat_type(res['seat']) if res['seat'] > 0 else "N/A"
            fare_val = res.get('fare', getattr(p, 'fare', 0))
            print("\n" + "=" * 52)
            print("✈️   BOARDING PASS / TICKET CONFIRMATION")
            print("=" * 52)
            print(f"  PNR NUMBER     : {res['pnr']}")
            print(f"  PASSENGER NAME : {p.name}")
            print(f"  AGE            : {p.age}")
            print(f"  STATUS         : {res['status']}")
            if res['status'] == "CONFIRMED":
                print(f"  ASSIGNED SEAT  : Seat {res['seat']} ({st_type})")
                print(f"  FARE PAID      : ₹{fare_val:,}")
            else:
                print(f"  WAITING LIST   : Position #{res['position']}")
                print(f"  ESTIMATED FARE : ₹{fare_val:,}")
            print(f"  DATA STRUCTURE : {'Doubly Linked List' if res['status'] == 'CONFIRMED' else 'Linked Queue (FIFO)'}")
            print("=" * 52)
            print(f"Details: {res.get('message', '')}\n")
        else:
            print(f"\n❌ Booking Failed: {res.get('message', '')}\n")


    def cancel(self):
        pnr = input("Enter PNR to cancel: ").strip().upper()
        res = self.cancel_ticket(pnr)
        print(res.get("message", ""))

    def undo_cancel(self):
        res = self.undo_cancellation()
        print(res.get("message", ""))

    def search(self):
        pnr = input("Enter PNR to search: ").strip().upper()
        res = self.search_pnr(pnr)
        print(res.get("message", ""))

    def fast_search(self):
        pnr = input("Enter PNR to search: ").strip().upper()
        res = self.fast_search_pnr(pnr)
        print(res.get("message", ""))

    def sort_tickets_cli(self):
        choice = input("Sort by: 1) Name  2) Age : ").strip()
        sort_key = self.sort_tickets(by=choice)
        print(f"Sorted by {sort_key}.")
        self.tickets.display()

