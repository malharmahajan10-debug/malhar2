# ✈️ Flight Booking & Seat Management System (Data Structures Project)

A complete **Flight Booking and Seat Management System** developed in Python, demonstrating core Data Structures and Algorithms without relying on any external packages.

---

## 📚 Data Structures & Algorithms Used

| Data Structure / Algorithm | File | Real-world Purpose in Project |
| :--- | :--- | :--- |
| **Doubly Linked List** | `confirmed_tickets.py` | Stores confirmed passenger tickets. Allows forward and backward traversal, constant-time deletion (`remove`) when node is located, and easy swapping for bubble sort. |
| **Singly Linked Queue (FIFO)** | `waiting_queue.py` | Manages the waiting list when flight capacity is reached (`front` and `rear` pointers). When a confirmed ticket is cancelled, the first waiting passenger is automatically promoted (`dequeue`). |
| **Array-based Stack (LIFO)** | `cancellation_stack.py` | Maintains cancellation history (`push`/`pop`). Powers the **Undo Cancellation** functionality by popping the most recently cancelled ticket. |
| **1D Fixed-size Array** | `seat_allocation.py` | Tracks aircraft seat availability and handles preference-based seat allocation (Window, Middle, Aisle) in $O(1)$ to $O(N)$ time. |
| **Bubble Sort** | `confirmed_tickets.py` | Sorts passenger nodes in the doubly linked list by Name ($A \rightarrow Z$) or by Age (ascending) by swapping node data. |
| **Insertion Sort** | `sorting_searching.py` | Sorts the dynamic array of PNR codes into alphabetical order in-place prior to binary search. |
| **Binary Search** | `sorting_searching.py` | Provides fast $O(\log N)$ divide-and-conquer lookup of PNR codes over the sorted PNR array, reporting comparison telemetry. |
| **Linear Search** | `flight_booking_manager.py` | Sequential traversal across linked list nodes to locate passenger details. |

---

## 💵 Seat Layout & Dynamic Pricing

The aircraft has **12 seats** organized into **4 rows $\times$ 3 seats** (3-abreast seating: Window, Middle, Aisle):

| Seat Type | Code | Seats in Aircraft | Price (INR) | Features |
| :--- | :---: | :---: | :---: | :--- |
| **Window** | `W` | Seat #1, #4, #7, #10 | **₹1,200** | Scenic view, exterior window wall |
| **Middle** | `M` | Seat #2, #5, #8, #11 | **₹1,000** | Standard center seat |
| **Aisle** | `A` | Seat #3, #6, #9, #12 | **₹900** | Direct aisle access, easy legroom |

- Fares are automatically computed upon seat assignment and displayed directly on the **Boarding Pass & Ticket Receipt**, table records, and flight revenue summaries.
- When waiting list passengers are automatically promoted into a vacated seat upon a cancellation, their ticket fare is adjusted to match their newly assigned seat type.

---

## 🚀 How to Run

You can choose between **three interfaces**:

### 1. Interactive Web Dashboard (Recommended)
Modern browser-based UI with interactive airplane seat layout, live pointer visualizations for Doubly Linked List, Queue, and Stack, and telemetry comparison between Linear and Binary Search.

```bash
python3 main.py --web
# or
python3 web_app.py
```
Then open your browser at **http://127.0.0.1:5050**.

---

### 2. Desktop GUI (Tkinter Window)
Native desktop application with interactive aircraft seat map, Treeview tables for confirmed, waiting, and cancellation lists, and quick-action buttons. Zero extra packages needed.

```bash
python3 main.py --gui
# or
python3 gui_app.py
```

---

### 3. Console CLI (Terminal Menu)
Classic terminal-based text menu.

```bash
python3 main.py --cli
# or
python3 flight_booking_app.py
```

---

### 4. Interactive Launcher
Running without arguments prompts you to select your preferred interface:

```bash
python3 main.py
```

---

## 🛠️ Key Fixes and Improvements Made

1. **Missing `main.py` Created**:
   - `flight_booking_app.py` originally referenced `python main.py` in its docstring, but the file did not exist. `main.py` is now implemented with support for Web, Desktop GUI, and CLI modes.
2. **Seat Preference Allocation**:
   - Passenger records collected seat preferences (`W`, `M`, `A`), but the original allocation logic ignored them. `SeatMap.allocate(pref)` now prioritizes matching seat preferences (Window / Middle / Aisle) while falling back to available seats when necessary.
3. **Waiting List Ticket Cancellation**:
   - Previously, only confirmed tickets could be cancelled; waiting passengers who tried to cancel received an error ("No such confirmed PNR found"). We implemented node deletion on the linked queue so waiting passengers can cancel their tickets properly.
4. **Binary Search Result Display**:
   - Original fast search only returned the sorted position index without passenger details. It now retrieves and displays the full passenger details along with comparison counts.
5. **Undo Cancellation Edge Cases**:
   - When a cancellation is undone and the flight has since become full, the passenger is safely placed onto the waiting list with seat reset to 0.
6. **Case-Insensitive PNR Lookups**:
   - All searches and cancellations now sanitize and standardize PNR strings (`strip().upper()`).
7. **Complete Separation of Concerns**:
   - Added programmatic methods (`book_ticket`, `cancel_ticket`, `undo_cancellation`, etc.) alongside CLI wrappers, allowing any interface (CLI, GUI, or Web) to interact with the exact same business logic.
