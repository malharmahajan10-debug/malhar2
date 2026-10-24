"""Project-wide settings."""

MAX_SEATS = 12     # flight capacity (4 rows x 3 seats = 12 seats)
STACK_MAX = 50     # max cancelled tickets remembered

# Seat Pricing in INR (₹)
SEAT_PRICE_WINDOW = 1200   # Window seat: ₹1,200
SEAT_PRICE_MIDDLE = 1000   # Middle seat: ₹1,000
SEAT_PRICE_AISLE = 900     # Aisle seat: ₹900

SEAT_PRICES = {
    "W": SEAT_PRICE_WINDOW,
    "M": SEAT_PRICE_MIDDLE,
    "A": SEAT_PRICE_AISLE,
    "Window": SEAT_PRICE_WINDOW,
    "Middle": SEAT_PRICE_MIDDLE,
    "Aisle": SEAT_PRICE_AISLE,
}



