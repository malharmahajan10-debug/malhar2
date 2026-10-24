"""Desktop Graphical User Interface for Flight Booking System.

Built with Python's built-in `tkinter` and `tkinter.ttk` (standard library).
Requires zero external pip packages.
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox

from flight_booking_manager import FlightBookingSystem
from settings import MAX_SEATS, STACK_MAX


class FlightBookingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("✈️ Flight Booking System - Data Structures Project")
        self.root.geometry("1100, 720")
        self.root.minsize(950, 600)

        # Style configuration
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        self.system = FlightBookingSystem()

        self._init_ui()
        self.load_demo_data()
        self.refresh_all()

    def _init_ui(self):
        # Top Banner
        banner = tk.Frame(self.root, bg="#1e3a8a", padx=16, pady=12)
        banner.pack(fill=tk.X)

        title_lbl = tk.Label(
            banner,
            text="✈️ Flight Booking & Seat Management System",
            font=("Helvetica", 18, "bold"),
            fg="#ffffff",
            bg="#1e3a8a",
        )
        title_lbl.pack(side=tk.LEFT)

        subtitle_lbl = tk.Label(
            banner,
            text="DS Project: Doubly Linked List • Queue • Stack • Arrays • Sorting & Searching",
            font=("Helvetica", 10),
            fg="#93c5fd",
            bg="#1e3a8a",
        )
        subtitle_lbl.pack(side=tk.LEFT, padx=16)

        # Main Split Container
        main_pane = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left Frame (Forms & Controls)
        left_frame = tk.Frame(main_pane, padx=8, pady=8, width=380)
        main_pane.add(left_frame, minsize=320)

        # Right Frame (Visual Map & Tables)
        right_frame = tk.Frame(main_pane, padx=8, pady=8)
        main_pane.add(right_frame, minsize=550)

        self._build_booking_form(left_frame)
        self._build_search_box(left_frame)
        self._build_cancellation_box(left_frame)
        self._build_system_actions(left_frame)

        self._build_seat_map(right_frame)
        self._build_tabs(right_frame)

        # Bottom Status Bar
        self.status_bar = tk.Label(
            self.root,
            text="Ready",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=("Helvetica", 9),
            bg="#f1f5f9",
            padx=10,
            pady=4,
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _build_booking_form(self, parent):
        group = ttk.LabelFrame(parent, text=" 📝 Book Flight Ticket ")
        group.pack(fill=tk.X, pady=(0, 10), padx=2)

        f = tk.Frame(group, padx=10, pady=10)
        f.pack(fill=tk.X)

        tk.Label(f, text="Passenger Name:", font=("Helvetica", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=4)
        self.entry_name = ttk.Entry(f, width=24)
        self.entry_name.grid(row=0, column=1, sticky=tk.EW, pady=4, padx=5)

        tk.Label(f, text="Age (1-120):", font=("Helvetica", 9, "bold")).grid(row=1, column=0, sticky=tk.W, pady=4)
        self.entry_age = ttk.Spinbox(f, from_=1, to=120, width=22)
        self.entry_age.set("25")
        self.entry_age.grid(row=1, column=1, sticky=tk.EW, pady=4, padx=5)

        tk.Label(f, text="Choose Seat:", font=("Helvetica", 9, "bold")).grid(row=2, column=0, sticky=tk.W, pady=4)
        self.combo_seat = ttk.Combobox(f, state="readonly", width=22)
        self.combo_seat.grid(row=2, column=1, sticky=tk.EW, pady=4, padx=5)

        tk.Label(f, text="Seat Preference:", font=("Helvetica", 9, "bold")).grid(row=3, column=0, sticky=tk.W, pady=4)
        self.pref_var = tk.StringVar(value="W")
        pref_frame = tk.Frame(f)
        pref_frame.grid(row=3, column=1, sticky=tk.W, pady=4)
        ttk.Radiobutton(pref_frame, text="Window (₹1,200)", variable=self.pref_var, value="W").pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(pref_frame, text="Middle (₹1,000)", variable=self.pref_var, value="M").pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(pref_frame, text="Aisle (₹900)", variable=self.pref_var, value="A").pack(side=tk.LEFT, padx=2)

        btn_book = tk.Button(
            f,
            text="🎫 Book Ticket & Get Boarding Pass",
            bg="#2563eb",
            fg="white",
            font=("Helvetica", 10, "bold"),
            command=self.action_book,
            cursor="hand2",
            padx=10,
            pady=4,
        )
        btn_book.grid(row=4, column=0, columnspan=2, sticky=tk.EW, pady=(8, 2))


    def _build_search_box(self, parent):
        group = ttk.LabelFrame(parent, text=" 🔍 Search Passenger (PNR) ")
        group.pack(fill=tk.X, pady=(0, 10), padx=2)

        f = tk.Frame(group, padx=10, pady=8)
        f.pack(fill=tk.X)

        tk.Label(f, text="PNR Code:").grid(row=0, column=0, sticky=tk.W)
        self.entry_search_pnr = ttk.Entry(f, width=16)
        self.entry_search_pnr.grid(row=0, column=1, sticky=tk.EW, padx=5)

        self.search_mode = tk.StringVar(value="binary")
        mode_frame = tk.Frame(f)
        mode_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=4)
        ttk.Radiobutton(mode_frame, text="⚡ Binary Search", variable=self.search_mode, value="binary").pack(side=tk.LEFT, padx=4)
        ttk.Radiobutton(mode_frame, text="🔎 Linear Search", variable=self.search_mode, value="linear").pack(side=tk.LEFT, padx=4)

        btn_search = ttk.Button(f, text="Search Ticket", command=self.action_search)
        btn_search.grid(row=2, column=0, columnspan=2, sticky=tk.EW, pady=4)

        self.lbl_search_result = tk.Label(f, text="", font=("Helvetica", 8), fg="#1e3a8a", wraplength=280, justify=tk.LEFT)
        self.lbl_search_result.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=2)

    def _build_cancellation_box(self, parent):
        group = ttk.LabelFrame(parent, text=" ❌ Cancel / Undo Ticket ")
        group.pack(fill=tk.X, pady=(0, 10), padx=2)

        f = tk.Frame(group, padx=10, pady=8)
        f.pack(fill=tk.X)

        tk.Label(f, text="PNR to Cancel:").grid(row=0, column=0, sticky=tk.W)
        self.entry_cancel_pnr = ttk.Entry(f, width=16)
        self.entry_cancel_pnr.grid(row=0, column=1, sticky=tk.EW, padx=5)

        btn_cancel = tk.Button(
            f,
            text="Cancel Ticket",
            bg="#dc2626",
            fg="white",
            font=("Helvetica", 9, "bold"),
            command=self.action_cancel,
        )
        btn_cancel.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=6)

        btn_undo = tk.Button(
            f,
            text="↩️ Undo Last Cancellation (Stack Pop)",
            bg="#d97706",
            fg="white",
            font=("Helvetica", 9, "bold"),
            command=self.action_undo,
        )
        btn_undo.grid(row=2, column=0, columnspan=2, sticky=tk.EW, pady=2)

    def _build_system_actions(self, parent):
        group = ttk.LabelFrame(parent, text=" ⚙️ System Controls ")
        group.pack(fill=tk.X, pady=(0, 5), padx=2)

        f = tk.Frame(group, padx=10, pady=8)
        f.pack(fill=tk.X)

        btn_demo = ttk.Button(f, text="📁 Previous Flight Record", command=self.load_previous_records)
        btn_demo.pack(fill=tk.X, pady=2)

        btn_new_flight = ttk.Button(f, text="🛫 New Flight Booking", command=self.action_new_flight)
        btn_new_flight.pack(fill=tk.X, pady=2)

    def _build_seat_map(self, parent):
        group = ttk.LabelFrame(parent, text=" 💺 Aircraft Seat Map (1D Array Allocation) ")
        group.pack(fill=tk.X, pady=(0, 10))

        container = tk.Frame(group, padx=12, pady=10, bg="#f8fafc")
        container.pack(fill=tk.X)

        # Seat Grid: dynamic rows of 3 seats
        self.seat_buttons = {}
        row_frames = {}
        total_seats = self.system.seatmap.n

        for i in range(1, total_seats + 1):
            row_idx = (i - 1) // 3
            if row_idx not in row_frames:
                rf = tk.Frame(container, bg="#f8fafc")
                rf.pack(pady=3)
                row_frames[row_idx] = rf

            parent_row = row_frames[row_idx]
            seat_type = self.system.seatmap.get_seat_type(i)
            type_name = "Win" if seat_type == "W" else ("Mid" if seat_type == "M" else "Aisle")

            btn = tk.Button(
                parent_row,
                text=f"Seat {i} ({type_name})\n[Free]",
                width=12,
                height=2,
                font=("Helvetica", 8, "bold"),
                relief=tk.GROOVE,
                bd=2,
                cursor="hand2",
                command=lambda s=i: self.on_seat_click(s),
            )
            btn.pack(side=tk.LEFT, padx=4)
            self.seat_buttons[i] = btn

        legend_lbl = tk.Label(
            container,
            text="🟢 Green = Available  |  🔴 Red = Booked (Click booked seat to cancel)",
            font=("Helvetica", 8),
            fg="#64748b",
            bg="#f8fafc",
        )
        legend_lbl.pack(pady=(4, 0))

    def _build_tabs(self, parent):
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Confirmed Tickets (Doubly Linked List)
        tab_confirmed = ttk.Frame(self.notebook, padding=6)
        self.notebook.add(tab_confirmed, text=" 📋 Confirmed Tickets (Doubly Linked List) ")

        ctrl_frame = tk.Frame(tab_confirmed)
        ctrl_frame.pack(fill=tk.X, pady=(0, 6))

        tk.Label(ctrl_frame, text="Doubly Linked List:", font=("Helvetica", 9, "bold")).pack(side=tk.LEFT)
        btn_sort_name = ttk.Button(ctrl_frame, text="Sort by Name (Bubble Sort)", command=lambda: self.action_sort("name"))
        btn_sort_name.pack(side=tk.LEFT, padx=6)
        btn_sort_age = ttk.Button(ctrl_frame, text="Sort by Age (Bubble Sort)", command=lambda: self.action_sort("age"))
        btn_sort_age.pack(side=tk.LEFT, padx=4)

        self.tree_confirmed = ttk.Treeview(
            tab_confirmed,
            columns=("no", "name", "age", "pnr", "seat", "pref", "fare"),
            show="headings",
            height=7,
        )
        self.tree_confirmed.heading("no", text="#")
        self.tree_confirmed.heading("name", text="Passenger Name")
        self.tree_confirmed.heading("age", text="Age")
        self.tree_confirmed.heading("pnr", text="PNR")
        self.tree_confirmed.heading("seat", text="Seat No")
        self.tree_confirmed.heading("pref", text="Pref")
        self.tree_confirmed.heading("fare", text="Fare (₹)")

        self.tree_confirmed.column("no", width=30, anchor=tk.CENTER)
        self.tree_confirmed.column("name", width=130)
        self.tree_confirmed.column("age", width=40, anchor=tk.CENTER)
        self.tree_confirmed.column("pnr", width=100, anchor=tk.CENTER)
        self.tree_confirmed.column("seat", width=55, anchor=tk.CENTER)
        self.tree_confirmed.column("pref", width=45, anchor=tk.CENTER)
        self.tree_confirmed.column("fare", width=70, anchor=tk.CENTER)

        scroll_c = ttk.Scrollbar(tab_confirmed, orient=tk.VERTICAL, command=self.tree_confirmed.yview)
        self.tree_confirmed.configure(yscroll=scroll_c.set)
        self.tree_confirmed.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_c.pack(side=tk.RIGHT, fill=tk.Y)

        # Tab 2: Waiting List (Queue)
        tab_waiting = ttk.Frame(self.notebook, padding=6)
        self.notebook.add(tab_waiting, text=" ⏳ Waiting List (Queue - FIFO) ")

        self.tree_waiting = ttk.Treeview(
            tab_waiting,
            columns=("pos", "name", "age", "pnr", "pref", "fare"),
            show="headings",
            height=7,
        )
        self.tree_waiting.heading("pos", text="Queue Pos")
        self.tree_waiting.heading("name", text="Passenger Name")
        self.tree_waiting.heading("age", text="Age")
        self.tree_waiting.heading("pnr", text="PNR")
        self.tree_waiting.heading("pref", text="Pref")
        self.tree_waiting.heading("fare", text="Est. Fare")

        self.tree_waiting.column("pos", width=65, anchor=tk.CENTER)
        self.tree_waiting.column("name", width=135)
        self.tree_waiting.column("age", width=40, anchor=tk.CENTER)
        self.tree_waiting.column("pnr", width=100, anchor=tk.CENTER)
        self.tree_waiting.column("pref", width=45, anchor=tk.CENTER)
        self.tree_waiting.column("fare", width=70, anchor=tk.CENTER)

        scroll_w = ttk.Scrollbar(tab_waiting, orient=tk.VERTICAL, command=self.tree_waiting.yview)
        self.tree_waiting.configure(yscroll=scroll_w.set)
        self.tree_waiting.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_w.pack(side=tk.RIGHT, fill=tk.Y)

        # Tab 3: Cancellation Stack (Undo)
        tab_history = ttk.Frame(self.notebook, padding=6)
        self.notebook.add(tab_history, text=" 🗑️ Cancellation History (Stack - LIFO) ")

        self.tree_history = ttk.Treeview(
            tab_history,
            columns=("lvl", "name", "age", "pnr", "seat"),
            show="headings",
            height=7,
        )
        self.tree_history.heading("lvl", text="Stack Level")
        self.tree_history.heading("name", text="Passenger Name")
        self.tree_history.heading("age", text="Age")
        self.tree_history.heading("pnr", text="PNR")
        self.tree_history.heading("seat", text="Original Seat")

        self.tree_history.column("lvl", width=80, anchor=tk.CENTER)
        self.tree_history.column("name", width=140)
        self.tree_history.column("age", width=45, anchor=tk.CENTER)
        self.tree_history.column("pnr", width=110, anchor=tk.CENTER)
        self.tree_history.column("seat", width=80, anchor=tk.CENTER)

        scroll_h = ttk.Scrollbar(tab_history, orient=tk.VERTICAL, command=self.tree_history.yview)
        self.tree_history.configure(yscroll=scroll_h.set)
        self.tree_history.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_h.pack(side=tk.RIGHT, fill=tk.Y)

    # ------------------ Actions & Event Handlers ------------------

    def action_book(self):
        name = self.entry_name.get().strip()
        age = self.entry_age.get().strip()
        pref = self.pref_var.get()

        if not name:
            messagebox.showwarning("Input Error", "Please enter a passenger name.")
            return

        seat_selection = self.combo_seat.get().strip()
        seat_no = 0
        if ":" in seat_selection:
            try:
                seat_no = int(seat_selection.split(":")[0].strip())
            except ValueError:
                seat_no = 0

        res = self.system.book_ticket(name, age, pref, seat_no=seat_no)
        if res.get("success"):
            p = res.get("passenger")
            st_type = self.system.seatmap.get_seat_type(res['seat']) if res['seat'] > 0 else "N/A"
            fare_val = res.get("fare", getattr(p, "fare", 0))
            boarding_pass = (
                "✈️  BOARDING PASS & TICKET RECEIPT\n"
                "===========================================\n"
                f"  PNR NUMBER     : {res['pnr']}\n"
                f"  PASSENGER NAME : {p.name}\n"
                f"  AGE            : {p.age}\n"
                f"  BOOKING STATUS : {res['status']}\n"
                + (f"  ASSIGNED SEAT  : Seat #{res['seat']} ({st_type})\n" if res['status'] == "CONFIRMED" else f"  WAITING LIST   : Position #{res['position']}\n")
                + f"  TICKET FARE    : ₹{fare_val:,}\n"
                + f"  DATA STRUCTURE : {'Doubly Linked List' if res['status'] == 'CONFIRMED' else 'Linked Queue (FIFO)'}\n"
                "===========================================\n\n"
                f"Details: {res.get('message', '')}"
            )
            messagebox.showinfo("🎫 Ticket Booked - Boarding Pass", boarding_pass)
            self.entry_name.delete(0, tk.END)
            self.refresh_all()
        else:
            messagebox.showerror("Booking Failed", res.get("message", "Error"))

    def action_cancel(self):
        pnr = self.entry_cancel_pnr.get().strip().upper()
        if not pnr:
            messagebox.showwarning("Input Error", "Please enter a PNR code to cancel.")
            return

        res = self.system.cancel_ticket(pnr)
        if res.get("success"):
            messagebox.showinfo("Cancellation Result", res["message"])
            self.entry_cancel_pnr.delete(0, tk.END)
            self.refresh_all()
        else:
            messagebox.showerror("Cancellation Failed", res.get("message", "Error"))

    def action_undo(self):
        res = self.system.undo_cancellation()
        if res.get("success"):
            messagebox.showinfo("Undo Result", res["message"])
            self.refresh_all()
        else:
            messagebox.showwarning("Undo Failed", res.get("message", "History is empty."))

    def action_search(self):
        pnr = self.entry_search_pnr.get().strip().upper()
        if not pnr:
            messagebox.showwarning("Input Error", "Please enter a PNR code to search.")
            return

        mode = self.search_mode.get()
        if mode == "binary":
            res = self.system.fast_search_pnr(pnr)
        else:
            res = self.system.search_pnr(pnr)

        msg = res.get("message", "")
        self.lbl_search_result.config(text=msg)
        if res.get("found"):
            messagebox.showinfo("Search Result", msg)
        else:
            messagebox.showwarning("Search Result", msg)

    def action_sort(self, key):
        sort_name = self.system.sort_tickets(by=key)
        self.refresh_all()
        messagebox.showinfo("Sorted", f"Confirmed tickets sorted by {sort_name} using Bubble Sort on Doubly Linked List.")

    def on_seat_click(self, seat_no):
        confirmed_list = self.system.tickets.to_list()
        occupant = next((p for p in confirmed_list if p.seat_no == seat_no), None)
        if occupant:
            confirm = messagebox.askyesno(
                "Seat Occupied",
                f"Seat {seat_no} is booked by {occupant.name} (PNR: {occupant.pnr}).\n\nDo you want to cancel this ticket?",
            )
            if confirm:
                res = self.system.cancel_ticket(occupant.pnr)
                messagebox.showinfo("Cancelled", res.get("message", ""))
                self.refresh_all()
        else:
            seat_type = self.system.seatmap.get_seat_type(seat_no)
            seat_price = self.system.seatmap.get_seat_price(seat_no)
            type_full = 'Window' if seat_type == 'W' else ('Middle' if seat_type == 'M' else 'Aisle')
            self.combo_seat.set(f"{seat_no}: Seat #{seat_no} ({type_full} - ₹{seat_price:,})")
            self.pref_var.set(seat_type)
            messagebox.showinfo(
                "Seat Selected",
                f"Seat #{seat_no} ({type_full} - ₹{seat_price:,}) is selected in the booking form on the left!",
            )
            self.entry_name.focus()

    def load_previous_records(self):
        self.system = FlightBookingSystem()

        # Confirmed passengers (Name, Age, Seat No) requested by user
        confirmed_passengers = [
            ("Tejas Wable", 21, 1),
            ("Shubham Patil", 32, 2),
            ("Devesh Panchal", 20, 3),
            ("Shubham Dixit", 39, 4),
            ("ishane chikne", 39, 5),
            ("Arnav Chavanke", 52, 6),
            ("Malhar Mahajan", 20, 7),
            ("Atharva Kabra", 27, 8),
            ("Atharva Panchal", 27, 9),
            ("Smit kolhapure", 28, 10),
            ("Shardul Narkar", 23, 11),
            ("Rohit Gondhal", 25, 12),
        ]

        for name, age, seat in confirmed_passengers:
            self.system.book_ticket(name, age, seat_no=seat, prepend=False)

        # Fictional waitlist passengers overflow into Linked Queue (FIFO)
        fictional_waitlist = [
            ("Tony Stark", 45, "W"),
            ("Bruce Wayne", 38, "M"),
            ("Peter Parker", 18, "A"),
            ("Clark Kent", 33, "W"),
        ]

        for name, age, pref in fictional_waitlist:
            self.system.book_ticket(name, age, pref)

        self.refresh_all()

    # Alias for backward compatibility
    load_demo_data = load_previous_records


    def action_new_flight(self):
        if messagebox.askyesno("New Flight Booking", "Are you sure you want to start a New Flight Booking?\n\nAll current seat bookings and passenger records will be cleared for a fresh flight."):
            self.system = FlightBookingSystem()
            self.refresh_all()
            messagebox.showinfo("New Flight Ready", "🛫 New Flight initialized! All 12 seats are now available for booking.")

    # Alias for backward compatibility
    action_reset = action_new_flight

    def refresh_all(self):
        state = self.system.get_system_state()

        # Update Seat Combobox in Booking Form
        current_val = self.combo_seat.get()
        combo_options = ["0: ✨ Auto-assign by preference"] + [
            f"{s['seat_no']}: Seat #{s['seat_no']} ({s['type']} - ₹{s.get('price', 1000):,})"
            for s in state["seat_map"]
            if not s["is_booked"]
        ]
        self.combo_seat["values"] = combo_options
        if current_val in combo_options:
            self.combo_seat.set(current_val)
        else:
            self.combo_seat.set("0: ✨ Auto-assign by preference")

        # Update Seat Map Buttons
        for s in state["seat_map"]:
            seat_no = s["seat_no"]
            is_booked = s["is_booked"]
            seat_type = s["type"]
            price = s.get("price", 1000)
            type_name = "Win" if seat_type == "W" else ("Mid" if seat_type == "M" else "Aisle")
            btn = self.seat_buttons.get(seat_no)

            occupant = next((p for p in state["confirmed_tickets"] if p["seat_no"] == seat_no), None)
            if btn:
                if is_booked:
                    occ_name = occupant["name"] if occupant else "Booked"
                    btn.config(
                        text=f"Seat {seat_no} ({type_name})\n₹{price:,}\n{occ_name[:10]}\n[Booked]",
                        bg="#ef4444",
                        fg="white",
                    )
                else:
                    btn.config(
                        text=f"Seat {seat_no} ({type_name})\n₹{price:,}\n[Available]",
                        bg="#10b981",
                        fg="black",
                    )


        # Update Confirmed Tree
        for item in self.tree_confirmed.get_children():
            self.tree_confirmed.delete(item)
        for i, t in enumerate(state["confirmed_tickets"]):
            fare_str = f"₹{t.get('fare', 0):,}"
            self.tree_confirmed.insert("", tk.END, values=(i + 1, t["name"], t["age"], t["pnr"], t["seat_no"], t["seatpref"], fare_str))

        # Update Waiting Tree
        for item in self.tree_waiting.get_children():
            self.tree_waiting.delete(item)
        for w in state["waiting_list"]:
            fare_str = f"₹{w.get('fare', 0):,}"
            self.tree_waiting.insert("", tk.END, values=(w["position"], w["name"], w["age"], w["pnr"], w["seatpref"], fare_str))

        # Update History Tree
        for item in self.tree_history.get_children():
            self.tree_history.delete(item)
        for i, h in enumerate(state["cancellation_history"]):
            lvl = "TOP" if i == 0 else f"L-{i+1}"
            orig_seat = h["seat_no"] if h["seat_no"] > 0 else "Waiting"
            self.tree_history.insert("", tk.END, values=(lvl, h["name"], h["age"], h["pnr"], orig_seat))

        # Status Bar with Total Revenue
        total_rev = state.get("total_revenue", 0)
        self.status_bar.config(
            text=f"Capacity: {state['max_seats']} | Confirmed: {state['confirmed_count']} | Waiting: {state['waiting_count']} | Stack: {state['history_count']} | Free: {state['available_seats']} | Flight Revenue: ₹{total_rev:,}"
        )


def run_gui():
    root = tk.Tk()
    app = FlightBookingGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
