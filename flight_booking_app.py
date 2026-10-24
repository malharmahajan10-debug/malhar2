"""FLIGHT BOOKING SYSTEM - entry point.

Run with:  python main.py
"""

from flight_booking_manager import FlightBookingSystem

MENU = """
=========== FLIGHT BOOKING MENU ===========
 1. Book Ticket
 2. Cancel Ticket
 3. Search by PNR (linear search)
 4. Display Confirmed Tickets (Doubly Linked List)
 5. Display Waiting List (Queue - FIFO)
 6. Undo Last Cancellation (Stack - LIFO)
 7. Show Cancellation History (Stack)
 8. Sort Tickets (by name / age - Bubble Sort)
 9. Fast Search by PNR (binary search)
10. Show Seat Map (1D Array)
11. Launch Web Dashboard (Browser GUI)
12. Launch Desktop GUI (Tkinter Window)
13. New Flight Booking (Clear all seats for a fresh flight)
 0. Exit
==========================================="""


def main():
    system = FlightBookingSystem()

    def launch_web():
        try:
            import web_app
            web_app.run_web_server(port=5050, open_browser=True)
        except Exception as e:
            print(f"Could not start Web GUI: {e}")

    def launch_desktop():
        try:
            import gui_app
            gui_app.run_gui()
        except Exception as e:
            print(f"Could not start Desktop GUI: {e}")

    def new_flight():
        nonlocal system
        confirm = input("Are you sure you want to start a New Flight Booking? All seats will be cleared (y/n): ").strip().lower()
        if confirm == 'y':
            system = FlightBookingSystem()
            print("🛫 New flight initialized! All 12 seats are available.")

    actions = {
        "1": system.book,
        "2": system.cancel,
        "3": system.search,
        "4": system.tickets.display,
        "5": system.waiting.display,
        "6": system.undo_cancel,
        "7": system.history.display,
        "8": system.sort_tickets_cli,
        "9": system.fast_search,
        "10": system.seatmap.show,
        "11": launch_web,
        "12": launch_desktop,
        "13": new_flight,
    }

    while True:
        print(MENU)
        choice = input("Enter choice: ").strip()
        if choice == "0":
            print("Thank you for using the Flight Booking System!")
            break
        action = actions.get(choice)
        if action:
            action()
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()

