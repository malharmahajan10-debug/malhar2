"""Web-based Graphical Interface for Flight Booking System.

Uses Python's standard library `http.server` - zero external pip dependencies needed.
Provides an interactive real-time dashboard visualizing:
- 1D Fixed-size Array (Seat Map with Specific Seat Selection)
- Doubly Linked List (Confirmed Tickets)
- Singly Linked Queue (Waiting List - FIFO)
- Fixed-size Stack (Cancellation History / Undo - LIFO)
- Bubble Sort & Insertion Sort
- Linear Search vs Binary Search with comparison telemetry
- Instant Boarding Pass & Ticket Confirmation Display with PNR
"""

import json
import os
import sys
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from flight_booking_manager import FlightBookingSystem
from settings import MAX_SEATS, STACK_MAX

# Global system instance shared across HTTP requests
system = FlightBookingSystem()


def reset_system_state():
    """Reset the global system to a fresh empty state."""
    global system
    system = FlightBookingSystem()


def load_previous_records():
    """Load Previous Flight Record: user-specified database manifest + fictional waitlist."""
    reset_system_state()

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
        system.book_ticket(name, age, seat_no=seat, prepend=False)

    # Fictional waitlist passengers overflow into Linked Queue (FIFO)
    fictional_waitlist = [
        ("Tony Stark", 45, "W"),
        ("Bruce Wayne", 38, "M"),
        ("Peter Parker", 18, "A"),
        ("Clark Kent", 33, "W"),
    ]

    for name, age, pref in fictional_waitlist:
        system.book_ticket(name, age, pref)


# Alias for backward compatibility
load_demo_data = load_previous_records

# Initial load of previous flight records
load_previous_records()



HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Flight Booking System | Data Structures Dashboard</title>
  <style>
    :root {
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --card-border: #e2e8f0;
      --primary: #2563eb;
      --primary-hover: #1d4ed8;
      --accent: #0284c7;
      --success: #059669;
      --danger: #e11d48;
      --warning: #d97706;
      --text: #0f172a;
      --text-muted: #64748b;
      --seat-free-bg: #ecfdf5;
      --seat-free-border: #10b981;
      --seat-free-text: #047857;
      --seat-booked-bg: #fff1f2;
      --seat-booked-border: #f43f5e;
      --seat-booked-text: #9f1239;
      --seat-selected-bg: #eff6ff;
      --seat-selected-border: #2563eb;
      --seat-selected-text: #1d4ed8;
      --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      background: radial-gradient(circle at 50% 0%, #ffffff 0%, #f1f5f9 100%);
      color: var(--text);
      font-family: var(--font-family);
      line-height: 1.5;
      padding: 24px;
      min-height: 100vh;
    }

    .container {
      max-width: 1320px;
      margin: 0 auto;
    }

    /* Header */
    header {
      background: #ffffff;
      border: 1px solid var(--card-border);
      border-top: 4px solid var(--primary);
      border-radius: 16px;
      padding: 24px 32px;
      margin-bottom: 24px;
      box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05), 0 2px 6px -1px rgba(15, 23, 42, 0.03);
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
    }

    .title-group h1 {
      font-size: 1.85rem;
      font-weight: 700;
      color: #0f172a;
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .title-group p {
      color: #4f46e5;
      font-size: 0.95rem;
      font-weight: 600;
      margin-top: 4px;
    }

    .header-actions {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }

    /* Badges */
    .stats-bar {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }

    .stat-card {
      background: #ffffff;
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 16px 20px;
      display: flex;
      flex-direction: column;
      gap: 4px;
      box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04);
    }

    .stat-card .label {
      font-size: 0.8rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      font-weight: 600;
    }

    .stat-card .val {
      font-size: 1.6rem;
      font-weight: 700;
      color: #0f172a;
    }

    .stat-card .ds-tag {
      font-size: 0.72rem;
      color: #2563eb;
      background: #eff6ff;
      border: 1px solid #dbeafe;
      padding: 2px 8px;
      border-radius: 6px;
      display: inline-block;
      width: fit-content;
      margin-top: 4px;
      font-weight: 600;
    }

    /* Main Grid */
    .grid-2 {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
      margin-bottom: 24px;
    }

    @media (max-width: 900px) {
      .grid-2 { grid-template-columns: 1fr; }
    }

    /* Cards */
    .card {
      background: #ffffff;
      border: 1px solid var(--card-border);
      border-radius: 16px;
      padding: 24px;
      box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05), 0 2px 6px -1px rgba(15, 23, 42, 0.03);
      margin-bottom: 24px;
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 18px;
      border-bottom: 1px solid #f1f5f9;
      padding-bottom: 12px;
    }

    .card-title {
      font-size: 1.2rem;
      font-weight: 600;
      color: #0f172a;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .ds-badge {
      font-size: 0.75rem;
      background: #eff6ff;
      border: 1px solid #bfdbfe;
      color: #1d4ed8;
      padding: 4px 10px;
      border-radius: 12px;
      font-weight: 600;
    }

    /* Cabin Seat Map */
    .cabin {
      background: #f1f5f9;
      border: 2px solid #cbd5e1;
      border-radius: 24px;
      padding: 20px 16px;
      max-width: 520px;
      margin: 0 auto;
      box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.04);
    }

    .cabin-nose {
      width: 90px;
      height: 38px;
      background: #e2e8f0;
      border: 1px solid #cbd5e1;
      border-radius: 40px 40px 0 0;
      margin: 0 auto 16px auto;
      text-align: center;
      font-size: 0.72rem;
      color: #475569;
      font-weight: 700;
      line-height: 36px;
      letter-spacing: 1.5px;
    }

    .seat-grid {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 10px;
      margin-bottom: 16px;
    }

    .seat {
      background: #ffffff;
      border: 2px solid #e2e8f0;
      border-radius: 10px;
      padding: 10px 6px;
      text-align: center;
      cursor: pointer;
      transition: all 0.2s ease;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }

    .seat.free {
      background: var(--seat-free-bg);
      border-color: var(--seat-free-border);
      color: var(--seat-free-text);
    }

    .seat.free:hover {
      background: #d1fae5;
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
    }

    .seat.booked {
      background: var(--seat-booked-bg);
      border-color: var(--seat-booked-border);
      color: var(--seat-booked-text);
    }

    .seat.booked:hover {
      background: #ffe4e6;
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(244, 63, 94, 0.25);
    }

    .seat.selected {
      background: var(--seat-selected-bg) !important;
      border-color: var(--seat-selected-border) !important;
      color: var(--seat-selected-text) !important;
      transform: translateY(-3px) scale(1.02);
      box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.3) !important;
    }

    .seat-number {
      font-size: 1.1rem;
      font-weight: 700;
    }

    .seat-type {
      font-size: 0.68rem;
      text-transform: uppercase;
      font-weight: 600;
      margin-top: 1px;
    }

    .seat-price {
      font-size: 0.72rem;
      font-weight: 700;
      color: #0284c7;
      margin-top: 1px;
    }

    .seat-occupant {
      font-size: 0.72rem;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 100%;
      margin-top: 3px;
      font-weight: 600;
    }

    .fare-banner {
      background: #f0fdf4;
      border: 1px solid #bbf7d0;
      border-radius: 10px;
      padding: 10px 14px;
      margin-top: 14px;
      margin-bottom: 6px;
    }

    .seat-legend {
      display: flex;
      justify-content: center;
      gap: 20px;
      font-size: 0.8rem;
      margin-top: 14px;
      color: var(--text-muted);
    }

    .legend-item {
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .legend-box {
      width: 14px;
      height: 14px;
      border-radius: 4px;
    }

    /* Forms & Inputs */
    .form-group {
      margin-bottom: 16px;
    }

    label {
      display: block;
      font-size: 0.85rem;
      color: var(--text-muted);
      margin-bottom: 6px;
      font-weight: 600;
    }

    input, select {
      width: 100%;
      background: #ffffff;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      padding: 10px 14px;
      color: #0f172a;
      font-size: 0.95rem;
      outline: none;
      transition: border-color 0.2s, box-shadow 0.2s;
    }

    input:focus, select:focus {
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
    }

    .radio-group {
      display: flex;
      gap: 12px;
    }

    .radio-pill {
      flex: 1;
      position: relative;
    }

    .radio-pill input {
      position: absolute;
      opacity: 0;
      cursor: pointer;
    }

    .radio-pill label {
      display: block;
      text-align: center;
      padding: 10px 8px;
      background: #f8fafc;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      cursor: pointer;
      font-size: 0.85rem;
      transition: all 0.2s;
      margin-bottom: 0;
      color: #334155;
      font-weight: 500;
    }

    .radio-pill input:checked + label {
      background: var(--primary);
      border-color: var(--primary);
      color: #ffffff;
      font-weight: 600;
      box-shadow: 0 2px 8px rgba(37, 99, 235, 0.25);
    }

    /* Buttons */
    .btn {
      background: var(--primary);
      color: #fff;
      border: none;
      border-radius: 8px;
      padding: 10px 18px;
      font-size: 0.9rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }

    .btn:hover {
      background: var(--primary-hover);
      transform: translateY(-1px);
    }

    .btn-block { width: 100%; }

    .btn-secondary {
      background: #eff6ff;
      border: 1px solid #bfdbfe;
      color: #1d4ed8;
    }
    .btn-secondary:hover {
      background: #dbeafe;
      transform: translateY(-1px);
    }

    .btn-warning {
      background: #fffbeb;
      border: 1px solid #fde68a;
      color: #b45309;
    }
    .btn-warning:hover {
      background: #fef3c7;
      border-color: #f59e0b;
      transform: translateY(-1px);
    }

    .btn-danger {
      background: #fef2f2;
      border: 1px solid #fecaca;
      color: #b91c1c;
    }
    .btn-danger:hover {
      background: #fee2e2;
      border-color: #ef4444;
      transform: translateY(-1px);
    }

    .btn-sm {
      padding: 5px 10px;
      font-size: 0.78rem;
      border-radius: 6px;
    }

    /* Notification Banner */
    #notification {
      display: none;
      padding: 12px 18px;
      border-radius: 10px;
      margin-bottom: 20px;
      font-size: 0.9rem;
      font-weight: 500;
      box-shadow: 0 4px 12px rgba(0,0,0,0.06);
      animation: fadeIn 0.3s ease;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(-5px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .notify-success { background: #ecfdf5; border: 1px solid #10b981; color: #065f46; }
    .notify-error { background: #fef2f2; border: 1px solid #ef4444; color: #991b1b; }
    .notify-info { background: #eff6ff; border: 1px solid #3b82f6; color: #1e40af; }
    .notify-warning { background: #fffbeb; border: 1px solid #f59e0b; color: #92400e; }

    /* Tables */
    .table-responsive {
      overflow-x: auto;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 0.88rem;
    }

    th {
      background: #f8fafc;
      color: #475569;
      font-weight: 700;
      padding: 12px 16px;
      border-bottom: 1px solid #e2e8f0;
      font-size: 0.78rem;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    td {
      padding: 12px 16px;
      border-bottom: 1px solid #f1f5f9;
      color: #1e293b;
    }

    tr:hover td {
      background: #f8fafc;
    }

    .pnr-tag {
      font-family: monospace;
      font-size: 0.85rem;
      background: #eff6ff;
      border: 1px solid #bfdbfe;
      padding: 2px 6px;
      border-radius: 4px;
      color: #1d4ed8;
      font-weight: 600;
    }

    /* DS Diagram Visualizers */
    .ds-pointer-viz {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 12px 16px;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      font-family: monospace;
      font-size: 0.82rem;
      color: #475569;
      margin-bottom: 14px;
      overflow-x: auto;
    }

    .node-pill {
      background: #ffffff;
      border: 1px solid #3b82f6;
      border-radius: 6px;
      padding: 4px 10px;
      color: #1d4ed8;
      display: inline-block;
      white-space: nowrap;
      font-weight: 600;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }

    .search-telemetry {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 14px;
      font-size: 0.85rem;
      margin-top: 14px;
      color: #0f172a;
    }

    .search-step {
      font-family: monospace;
      padding: 5px 0;
      color: #334155;
      border-bottom: 1px dashed #cbd5e1;
    }

    .empty-state {
      text-align: center;
      padding: 24px;
      color: var(--text-muted);
      font-size: 0.9rem;
    }

    /* Boarding Pass Modal */
    .modal-overlay {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: rgba(15, 23, 42, 0.6);
      backdrop-filter: blur(4px);
      display: flex;
      justify-content: center;
      align-items: center;
      z-index: 1000;
      animation: fadeIn 0.2s ease;
    }

    .modal-card {
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 20px;
      width: 90%;
      max-width: 540px;
      box-shadow: 0 25px 50px -12px rgba(15, 23, 42, 0.25);
      overflow: hidden;
      animation: scaleUp 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }

    @keyframes scaleUp {
      from { transform: scale(0.92); opacity: 0; }
      to { transform: scale(1); opacity: 1; }
    }

    .ticket-header {
      background: #f8fafc;
      padding: 18px 24px;
      border-bottom: 2px dashed #cbd5e1;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .modal-close-btn {
      background: transparent;
      border: none;
      font-size: 1.3rem;
      cursor: pointer;
      color: #64748b;
      padding: 4px;
      line-height: 1;
    }
    .modal-close-btn:hover { color: #0f172a; }

    .ticket-body {
      padding: 24px;
    }

    .ticket-pnr-banner {
      background: #eff6ff;
      border: 1px solid #bfdbfe;
      border-radius: 12px;
      padding: 16px 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
    }

    .pnr-label {
      font-size: 0.72rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: #2563eb;
    }

    .pnr-code {
      font-family: monospace;
      font-size: 1.7rem;
      font-weight: 800;
      color: #1e3a8a;
      letter-spacing: 2px;
    }

    .ticket-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
    }

    .ticket-item {
      display: flex;
      flex-direction: column;
      gap: 2px;
    }

    .ticket-item-label {
      font-size: 0.72rem;
      font-weight: 700;
      color: #64748b;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .ticket-item-val {
      font-size: 1.05rem;
      font-weight: 600;
      color: #0f172a;
    }

    .badge-status {
      display: inline-block;
      padding: 3px 10px;
      border-radius: 20px;
      font-size: 0.8rem;
      font-weight: 700;
    }
    .badge-status.confirmed { background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; }
    .badge-status.waiting { background: #fffbeb; color: #b45309; border: 1px solid #fde68a; }

    .ticket-footer {
      padding: 16px 24px 24px;
      border-top: 1px solid #f1f5f9;
      display: flex;
      gap: 12px;
    }
  </style>
</head>
<body>
  <div class="container">
    <!-- Header -->
    <header>
      <div class="title-group">
        <h1>✈️ Flight Booking & Seat Management System</h1>
        <p>Interactive Data Structures Project • Doubly Linked List • Queue • Stack • Arrays • Sorting & Searching</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-warning" onclick="undoCancel()">↩️ Undo Cancellation (Stack Pop)</button>
        <button class="btn btn-secondary" onclick="loadPreviousRecords()">📁 Previous Flight Record</button>
        <button class="btn btn-danger" onclick="newFlightBooking()">🛫 New Flight Booking</button>
      </div>
    </header>

    <!-- Notification Banner -->
    <div id="notification"></div>

    <!-- Live Telemetry Stats -->
    <div class="stats-bar">
      <div class="stat-card">
        <span class="label">Flight Capacity</span>
        <span class="val" id="stat-capacity">12</span>
        <span class="ds-tag">1D Fixed Array (12 Seats)</span>
      </div>
      <div class="stat-card">
        <span class="label">Confirmed Tickets</span>
        <span class="val" id="stat-confirmed" style="color: #2563eb;">0</span>
        <span class="ds-tag">Doubly Linked List</span>
      </div>
      <div class="stat-card">
        <span class="label">Waiting List</span>
        <span class="val" id="stat-waiting" style="color: #d97706;">0</span>
        <span class="ds-tag">Linked Queue (FIFO)</span>
      </div>
      <div class="stat-card">
        <span class="label">Flight Revenue</span>
        <span class="val" id="stat-revenue" style="color: #059669;">₹0</span>
        <span class="ds-tag">Sum of Ticket Fares</span>
      </div>
      <div class="stat-card">
        <span class="label">Undo Stack</span>
        <span class="val" id="stat-history" style="color: #7c3aed;">0</span>
        <span class="ds-tag">Array Stack (LIFO)</span>
      </div>
    </div>

    <!-- Cabin & Booking Form Grid -->
    <div class="grid-2">
      <!-- Seat Map Card -->
      <div class="card">
        <div class="card-header">
          <span class="card-title">💺 Aircraft Seat Map</span>
          <span class="ds-badge">1D Array Allocation (4 Rows x 3 Seats)</span>
        </div>
        <div class="cabin">
          <div class="cabin-nose">COCKPIT</div>
          <div class="seat-grid" id="seat-grid">
            <!-- Rendered dynamically -->
          </div>
        </div>
        <div class="seat-legend">
          <div class="legend-item">
            <div class="legend-box" style="background: var(--seat-free-bg); border: 2px solid var(--seat-free-border);"></div>
            <span style="font-weight: 500;">Available (Click to select)</span>
          </div>
          <div class="legend-item">
            <div class="legend-box" style="background: var(--seat-booked-bg); border: 2px solid var(--seat-booked-border);"></div>
            <span style="font-weight: 500;">Booked (Click to cancel)</span>
          </div>
        </div>
      </div>

      <!-- Booking Form Card -->
      <div class="card">
        <div class="card-header">
          <span class="card-title">📝 Book a Ticket</span>
          <span class="ds-badge">Choose Specific Seat or Auto-Assign</span>
        </div>
        <form id="book-form" onsubmit="handleBook(event)">
          <div class="form-group">
            <label for="pass-name">Passenger Full Name</label>
            <input type="text" id="pass-name" placeholder="e.g. John Doe" required />
          </div>
          <div class="form-group">
            <label for="pass-age">Passenger Age (1 - 120)</label>
            <input type="number" id="pass-age" min="1" max="120" placeholder="e.g. 28" required />
          </div>
          <div class="form-group">
            <label for="seat-select">Choose Seat Number (or click green seat on map)</label>
            <select id="seat-select" onchange="handleSeatSelectChange()">
              <option value="0">✨ Auto-Assign by Preference</option>
              <!-- Populated dynamically -->
            </select>
          </div>
          <div class="form-group" id="pref-container">
            <label>Seat Preference & Rate</label>
            <div class="radio-group">
              <div class="radio-pill">
                <input type="radio" id="pref-w" name="seatpref" value="W" checked onchange="updateFareEstimate()" />
                <label for="pref-w">Window (₹1,200)</label>
              </div>
              <div class="radio-pill">
                <input type="radio" id="pref-m" name="seatpref" value="M" onchange="updateFareEstimate()" />
                <label for="pref-m">Middle (₹1,000)</label>
              </div>
              <div class="radio-pill">
                <input type="radio" id="pref-a" name="seatpref" value="A" onchange="updateFareEstimate()" />
                <label for="pref-a">Aisle (₹900)</label>
              </div>
            </div>
          </div>

          <!-- Dynamic Live Fare Banner -->
          <div class="fare-banner" id="fare-banner">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-size: 0.85rem; font-weight: 600; color: #334155;">Applicable Ticket Fare:</span>
              <span style="font-size: 1.25rem; font-weight: 800; color: #059669;" id="fare-amount-display">₹1,200</span>
            </div>
            <span style="font-size: 0.72rem; color: #64748b;" id="fare-desc-display">Window seat rate applied</span>
          </div>

          <button type="submit" class="btn btn-block" style="margin-top: 10px;">
            🎫 Book Ticket & Get Boarding Pass
          </button>
        </form>
      </div>

    </div>

    <!-- Boarding Pass / Ticket Confirmation Modal -->
    <div id="ticket-modal" class="modal-overlay" style="display: none;">
      <div class="modal-card">
        <div class="ticket-header">
          <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 1.6rem;">✈️</span>
            <div>
              <h3 style="margin: 0; font-size: 1.15rem; font-weight: 700; color: #0f172a;">BOARDING PASS & TICKET RECEIPT</h3>
              <p style="margin: 0; font-size: 0.78rem; color: #64748b;">Flight DS-101 • Flight Booking System</p>
            </div>
          </div>
          <button class="modal-close-btn" onclick="closeTicketModal()" title="Close">✕</button>
        </div>

        <div class="ticket-body">
          <div class="ticket-pnr-banner">
            <div>
              <span class="pnr-label">YOUR PNR NUMBER</span>
              <div class="pnr-code" id="modal-pnr">ABC123XYZ0</div>
            </div>
            <button class="btn btn-secondary btn-sm" onclick="copyModalPNR()">📋 Copy PNR</button>
          </div>

          <div class="ticket-grid">
            <div class="ticket-item">
              <span class="ticket-item-label">Passenger Name</span>
              <span class="ticket-item-val" id="modal-name">John Doe</span>
            </div>
            <div class="ticket-item">
              <span class="ticket-item-label">Age</span>
              <span class="ticket-item-val" id="modal-age">28</span>
            </div>
            <div class="ticket-item">
              <span class="ticket-item-label">Assigned Seat</span>
              <span class="ticket-item-val" id="modal-seat" style="color: #2563eb; font-weight: 700;">Seat #4 (Window)</span>
            </div>
            <div class="ticket-item">
              <span class="ticket-item-label">Ticket Fare / Amount</span>
              <span class="ticket-item-val" id="modal-fare" style="color: #059669; font-weight: 800; font-size: 1.25rem;">₹1,200</span>
            </div>
            <div class="ticket-item">
              <span class="ticket-item-label">Booking Status</span>
              <span class="ticket-item-val" id="modal-status"><span class="badge-status confirmed">CONFIRMED</span></span>
            </div>
            <div class="ticket-item">
              <span class="ticket-item-label">Data Structure Operation</span>
              <span class="ticket-item-val" id="modal-ds" style="font-size: 0.82rem; color: #334155; font-family: monospace;">Appended to Doubly Linked List</span>
            </div>
          </div>
        </div>

        <div class="ticket-footer">
          <button class="btn btn-block" onclick="closeTicketModal()">✓ Done & View Dashboard</button>
        </div>
      </div>
    </div>

    <!-- Search & Algorithm Explorer Card -->
    <div class="card">
      <div class="card-header">
        <span class="card-title">🔍 Search Passenger by PNR</span>
        <span class="ds-badge">Algorithm Comparison: Linear vs Binary Search</span>
      </div>
      <div style="display: flex; gap: 12px; flex-wrap: wrap;">
        <input type="text" id="search-pnr" placeholder="Enter 10-character PNR code..." style="flex: 2; min-width: 200px;" />
        <select id="search-mode" style="flex: 1; min-width: 180px;">
          <option value="binary">⚡ Binary Search (O(log N))</option>
          <option value="linear">🔎 Linear Search (O(N))</option>
        </select>
        <button class="btn" onclick="handleSearch()">Search</button>
      </div>
      <div id="search-results" style="display: none;"></div>
    </div>

    <!-- Confirmed Tickets (Doubly Linked List) -->
    <div class="card">
      <div class="card-header">
        <span class="card-title">📋 Confirmed Passengers</span>
        <div style="display: flex; gap: 8px; align-items: center;">
          <span class="ds-badge">Doubly Linked List (Swapping Bubble Sort)</span>
          <button class="btn btn-secondary btn-sm" onclick="sortTickets('name')">Sort by Name</button>
          <button class="btn btn-secondary btn-sm" onclick="sortTickets('age')">Sort by Age</button>
        </div>
      </div>
      <div class="ds-pointer-viz" id="dll-viz">
        HEAD [start] ↔ Empty ↔ TAIL [last]
      </div>
      <div class="table-responsive">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Name</th>
              <th>Age</th>
              <th>PNR</th>
              <th>Seat No</th>
              <th>Type</th>
              <th>Fare</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody id="confirmed-tbody">
            <!-- Dynamically populated -->
          </tbody>
        </table>
      </div>
    </div>

    <!-- Waiting List (Queue - FIFO) & Cancellation Stack (LIFO) Grid -->
    <div class="grid-2">
      <!-- Waiting List Queue -->
      <div class="card">
        <div class="card-header">
          <span class="card-title">⏳ Waiting List</span>
          <span class="ds-badge">Linked Queue (FIFO)</span>
        </div>
        <div class="ds-pointer-viz" id="queue-viz">
          FRONT [Next in Line] → Empty → REAR
        </div>
        <div class="table-responsive">
          <table>
            <thead>
              <tr>
                <th>Queue Pos</th>
                <th>Name</th>
                <th>Age</th>
                <th>PNR</th>
                <th>Pref</th>
                <th>Est. Fare</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody id="waiting-tbody">
              <!-- Dynamically populated -->
            </tbody>
          </table>
        </div>
      </div>


      <!-- Cancellation Stack -->
      <div class="card">
        <div class="card-header">
          <span class="card-title">🗑️ Cancellation History</span>
          <span class="ds-badge">Fixed Array Stack (LIFO Undo)</span>
        </div>
        <div class="ds-pointer-viz" id="stack-viz">
          TOP [Latest Cancelled] → Empty → BOTTOM
        </div>
        <div class="table-responsive">
          <table>
            <thead>
              <tr>
                <th>Level</th>
                <th>Name</th>
                <th>Age</th>
                <th>PNR</th>
                <th>Original Seat</th>
              </tr>
            </thead>
            <tbody id="history-tbody">
              <!-- Dynamically populated -->
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>

  <script>
    let globalState = null;

    // Fetch and render initial system state
    async function fetchState() {
      try {
        const res = await fetch('/api/state');
        const data = await res.json();
        globalState = data;
        renderDashboard(data);
      } catch (err) {
        console.error('Error fetching state:', err);
      }
    }

    function showNotification(msg, type = 'info') {
      const el = document.getElementById('notification');
      el.className = 'notify-' + type;
      el.textContent = msg;
      el.style.display = 'block';
      setTimeout(() => {
        el.style.display = 'none';
      }, 5000);
    }

    function renderDashboard(data) {
      // Badges
      document.getElementById('stat-capacity').textContent = data.max_seats;
      document.getElementById('stat-confirmed').textContent = `${data.confirmed_count} / ${data.max_seats}`;
      document.getElementById('stat-waiting').textContent = data.waiting_count;
      document.getElementById('stat-history').textContent = data.history_count;
      const revEl = document.getElementById('stat-revenue');
      if (revEl) revEl.textContent = `₹${(data.total_revenue || 0).toLocaleString()}`;

      // Update Seat Selection Dropdown
      const seatSelect = document.getElementById('seat-select');
      const currentSelected = seatSelect.value;
      seatSelect.innerHTML = '<option value="0">✨ Auto-Assign by Preference</option>';

      data.seat_map.forEach(s => {
        const typeName = s.type === 'W' ? 'Window' : (s.type === 'M' ? 'Middle' : 'Aisle');
        const price = s.price || (s.type === 'W' ? 1200 : (s.type === 'M' ? 1000 : 900));
        const opt = document.createElement('option');
        opt.value = s.seat_no;
        if (s.is_booked) {
          const occ = data.confirmed_tickets.find(t => t.seat_no === s.seat_no);
          opt.textContent = `Seat ${s.seat_no} (${typeName} - ₹${price.toLocaleString()}) - Occupied (${occ ? occ.name : 'Booked'})`;
          opt.disabled = true;
        } else {
          opt.textContent = `Seat ${s.seat_no} (${typeName} - ₹${price.toLocaleString()}) - Available`;
        }
        seatSelect.appendChild(opt);
      });

      // Restore previously chosen seat if still valid
      if (currentSelected && seatSelect.querySelector(`option[value="${currentSelected}"]:not(:disabled)`)) {
        seatSelect.value = currentSelected;
      }

      // Cabin Seat Map
      const seatGrid = document.getElementById('seat-grid');
      seatGrid.innerHTML = '';
      data.seat_map.forEach(s => {
        const occupant = data.confirmed_tickets.find(t => t.seat_no === s.seat_no);
        const seatDiv = document.createElement('div');
        const isSelected = seatSelect.value == s.seat_no;
        const typeName = s.type === 'W' ? 'Window' : (s.type === 'M' ? 'Middle' : 'Aisle');
        const price = s.price || (s.type === 'W' ? 1200 : (s.type === 'M' ? 1000 : 900));

        seatDiv.className = 'seat ' + (s.is_booked ? 'booked' : 'free') + (isSelected ? ' selected' : '');
        seatDiv.id = `seat-box-${s.seat_no}`;
        seatDiv.innerHTML = `
          <div class="seat-number">Seat ${s.seat_no}</div>
          <div class="seat-type">${typeName} • <span class="seat-price">₹${price.toLocaleString()}</span></div>
          <div class="seat-occupant">${occupant ? occupant.name : (isSelected ? '✓ Selected' : 'Available')}</div>
        `;

        if (occupant) {
          const occFare = occupant.fare || price;
          seatDiv.title = `Booked by ${occupant.name} (Age: ${occupant.age}, PNR: ${occupant.pnr}, Fare: ₹${occFare.toLocaleString()}). Click to cancel ticket.`;
          seatDiv.onclick = () => cancelTicket(occupant.pnr);
        } else {
          seatDiv.title = `Seat ${s.seat_no} (${typeName}) is Available for ₹${price.toLocaleString()}. Click to choose this seat for booking.`;
          seatDiv.onclick = () => selectSeatFromMap(s.seat_no, s.type);
        }
        seatGrid.appendChild(seatDiv);
      });

      // Update Live Fare Banner
      updateFareEstimate();

      // Confirmed Doubly Linked List Visualizer
      const dllViz = document.getElementById('dll-viz');
      if (data.confirmed_tickets.length === 0) {
        dllViz.innerHTML = 'HEAD [start] ↔ Empty ↔ TAIL [last]';
      } else {
        const nodes = data.confirmed_tickets.map(t => `<span class="node-pill">${t.name} (Seat ${t.seat_no} • ₹${(t.fare || 0).toLocaleString()})</span>`).join(' ↔ ');
        dllViz.innerHTML = `HEAD [start] ↔ ${nodes} ↔ TAIL [last]`;
      }

      // Confirmed Table
      const confirmedTbody = document.getElementById('confirmed-tbody');
      confirmedTbody.innerHTML = '';
      if (data.confirmed_tickets.length === 0) {
        confirmedTbody.innerHTML = '<tr><td colspan="8" class="empty-state">No confirmed tickets. Book a ticket above!</td></tr>';
      } else {
        data.confirmed_tickets.forEach((t, i) => {
          const tr = document.createElement('tr');
          const typeName = t.seatpref === 'W' ? 'Window' : (t.seatpref === 'M' ? 'Middle' : 'Aisle');
          tr.innerHTML = `
            <td>${i + 1}</td>
            <td><strong>${t.name}</strong></td>
            <td>${t.age}</td>
            <td><span class="pnr-tag">${t.pnr}</span></td>
            <td><strong style="color:#2563eb;">#${t.seat_no}</strong></td>
            <td>${typeName} (${t.seatpref})</td>
            <td><strong style="color:#059669;">₹${(t.fare || 0).toLocaleString()}</strong></td>
            <td><button class="btn btn-danger btn-sm" onclick="cancelTicket('${t.pnr}')">Cancel</button></td>
          `;
          confirmedTbody.appendChild(tr);
        });
      }

      // Waiting Queue Visualizer
      const queueViz = document.getElementById('queue-viz');
      if (data.waiting_list.length === 0) {
        queueViz.innerHTML = 'FRONT [Next in Line] → Empty → REAR';
      } else {
        const qNodes = data.waiting_list.map(w => `<span class="node-pill">#${w.position} ${w.name} (Est. ₹${(w.fare || 0).toLocaleString()})</span>`).join(' → ');
        queueViz.innerHTML = `FRONT → ${qNodes} → REAR`;
      }

      // Waiting Table
      const waitingTbody = document.getElementById('waiting-tbody');
      waitingTbody.innerHTML = '';
      if (data.waiting_list.length === 0) {
        waitingTbody.innerHTML = '<tr><td colspan="7" class="empty-state">Waiting queue is empty.</td></tr>';
      } else {
        data.waiting_list.forEach(w => {
          const tr = document.createElement('tr');
          const typeName = w.seatpref === 'W' ? 'Window' : (w.seatpref === 'M' ? 'Middle' : 'Aisle');
          tr.innerHTML = `
            <td><span class="pnr-tag">#${w.position}</span></td>
            <td><strong>${w.name}</strong></td>
            <td>${w.age}</td>
            <td><span class="pnr-tag">${w.pnr}</span></td>
            <td>${typeName} (${w.seatpref})</td>
            <td><span style="color:#d97706; font-weight: 600;">₹${(w.fare || 0).toLocaleString()}</span></td>
            <td><button class="btn btn-danger btn-sm" onclick="cancelTicket('${w.pnr}')">Cancel</button></td>
          `;
          waitingTbody.appendChild(tr);
        });
      }


      // Stack Visualizer
      const stackViz = document.getElementById('stack-viz');
      if (data.cancellation_history.length === 0) {
        stackViz.innerHTML = 'TOP [Latest Cancelled] → Empty → BOTTOM';
      } else {
        const stackNodes = data.cancellation_history.map((h, i) => `<span class="node-pill">${i === 0 ? 'TOP: ' : ''}${h.name}</span>`).join(' → ');
        stackViz.innerHTML = `${stackNodes} → BOTTOM`;
      }

      // History Table
      const historyTbody = document.getElementById('history-tbody');
      historyTbody.innerHTML = '';
      if (data.cancellation_history.length === 0) {
        historyTbody.innerHTML = '<tr><td colspan="5" class="empty-state">No cancellation history recorded in stack.</td></tr>';
      } else {
        data.cancellation_history.forEach((h, i) => {
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td><span class="pnr-tag">${i === 0 ? 'TOP' : 'L-' + (i + 1)}</span></td>
            <td><strong>${h.name}</strong></td>
            <td>${h.age}</td>
            <td><span class="pnr-tag">${h.pnr}</span></td>
            <td>${h.seat_no > 0 ? '#' + h.seat_no : 'Waiting'}</td>
          `;
          historyTbody.appendChild(tr);
        });
      }
    }

    function updateFareEstimate() {
      const seatSelect = document.getElementById('seat-select');
      const selVal = parseInt(seatSelect ? seatSelect.value : 0) || 0;
      const fareAmountEl = document.getElementById('fare-amount-display');
      const fareDescEl = document.getElementById('fare-desc-display');
      if (!fareAmountEl || !fareDescEl) return;

      if (selVal > 0 && globalState && globalState.seat_map) {
        const s = globalState.seat_map.find(item => item.seat_no === selVal);
        if (s) {
          const typeName = s.type === 'W' ? 'Window' : (s.type === 'M' ? 'Middle' : 'Aisle');
          const price = s.price || (s.type === 'W' ? 1200 : (s.type === 'M' ? 1000 : 900));
          fareAmountEl.textContent = `₹${price.toLocaleString()}`;
          fareDescEl.textContent = `Seat #${selVal} (${typeName}) fixed rate applied`;
          return;
        }
      }

      // Auto-assign: based on selected preference radio button
      const checkedRadio = document.querySelector('input[name="seatpref"]:checked');
      const pref = checkedRadio ? checkedRadio.value : 'W';
      let price = 1200;
      let label = 'Window seat rate';
      if (pref === 'M') {
        price = 1000;
        label = 'Middle seat rate';
      } else if (pref === 'A') {
        price = 900;
        label = 'Aisle seat rate';
      }
      fareAmountEl.textContent = `₹${price.toLocaleString()}`;
      fareDescEl.textContent = `Auto-assign estimate (${label})`;
    }

    function selectSeatFromMap(seatNo, seatType) {
      const sel = document.getElementById('seat-select');
      sel.value = seatNo;
      // Match preference radio button
      const radio = document.querySelector(`input[name="seatpref"][value="${seatType}"]`);
      if (radio) radio.checked = true;

      const price = (seatType === 'W' ? 1200 : (seatType === 'M' ? 1000 : 900));
      showNotification(`Selected Seat #${seatNo} (${seatType === 'W' ? 'Window' : seatType === 'M' ? 'Middle' : 'Aisle'} - ₹${price.toLocaleString()}) from map.`, 'info');
      // Highlight on map
      document.querySelectorAll('.seat').forEach(el => el.classList.remove('selected'));
      const activeBox = document.getElementById(`seat-box-${seatNo}`);
      if (activeBox) activeBox.classList.add('selected');
      updateFareEstimate();
      document.getElementById('pass-name').focus();
    }

    function handleSeatSelectChange() {
      const selVal = document.getElementById('seat-select').value;
      document.querySelectorAll('.seat').forEach(el => el.classList.remove('selected'));
      if (selVal != 0) {
        const activeBox = document.getElementById(`seat-box-${selVal}`);
        if (activeBox) activeBox.classList.add('selected');
        if (globalState && globalState.seat_map) {
          const s = globalState.seat_map.find(item => item.seat_no == selVal);
          if (s) {
            const radio = document.querySelector(`input[name="seatpref"][value="${s.type}"]`);
            if (radio) radio.checked = true;
          }
        }
      }
      updateFareEstimate();
    }

    // Open Boarding Pass Modal displaying PNR & all ticket info first
    function showTicketModal(data) {
      document.getElementById('modal-pnr').textContent = data.pnr;
      document.getElementById('modal-name').textContent = data.passenger ? data.passenger.name : '';
      document.getElementById('modal-age').textContent = data.passenger ? data.passenger.age : '';

      const seatEl = document.getElementById('modal-seat');
      const statusEl = document.getElementById('modal-status');
      const fareEl = document.getElementById('modal-fare');
      const dsEl = document.getElementById('modal-ds');

      const fareVal = data.fare || (data.passenger ? data.passenger.fare : 0);
      if (fareEl) fareEl.textContent = `₹${fareVal.toLocaleString()}`;

      if (data.status === 'CONFIRMED') {
        const typeName = data.passenger ? (data.passenger.seatpref === 'W' ? 'Window' : data.passenger.seatpref === 'M' ? 'Middle' : 'Aisle') : '';
        seatEl.textContent = `Seat #${data.seat} (${typeName} Seat)`;
        seatEl.style.color = '#2563eb';
        statusEl.innerHTML = '<span class="badge-status confirmed">✓ CONFIRMED</span>';
        dsEl.textContent = `Allocated via 1D Array (Index ${data.seat}) • Prepended to Head of Doubly Linked List (Shown First)`;
      } else {
        seatEl.textContent = `Waiting List Position #${data.position || 1}`;
        seatEl.style.color = '#d97706';
        statusEl.innerHTML = '<span class="badge-status waiting">⏳ WAITING LIST</span>';
        dsEl.textContent = `Flight Full (All 12 Seats Occupied) • Enqueued to Singly Linked Queue (FIFO)`;
      }

      document.getElementById('ticket-modal').style.display = 'flex';
    }


    function closeTicketModal() {
      document.getElementById('ticket-modal').style.display = 'none';
      fetchState();
    }

    function copyModalPNR() {
      const pnr = document.getElementById('modal-pnr').textContent;
      navigator.clipboard.writeText(pnr).then(() => {
        showNotification(`PNR code ${pnr} copied to clipboard!`, 'success');
      }).catch(() => {
        prompt('Copy your PNR:', pnr);
      });
    }

    async function handleBook(e) {
      e.preventDefault();
      const name = document.getElementById('pass-name').value.trim();
      const age = document.getElementById('pass-age').value;
      const pref = document.querySelector('input[name="seatpref"]:checked').value;
      const seat_no = parseInt(document.getElementById('seat-select').value) || 0;

      try {
        const res = await fetch('/api/book', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, age, seatpref: pref, seat_no: seat_no })
        });
        const data = await res.json();

        if (data.success) {
          // Reset form fields
          document.getElementById('pass-name').value = '';
          document.getElementById('pass-age').value = '';
          document.getElementById('seat-select').value = '0';
          document.querySelectorAll('.seat').forEach(el => el.classList.remove('selected'));

          // Display the Boarding Pass ticket info with PNR FIRST!
          showTicketModal(data);
          fetchState();
        } else {
          showNotification(data.message, 'error');
        }
      } catch (err) {
        showNotification('Failed to book ticket.', 'error');
      }
    }

    async function cancelTicket(pnr) {
      if (!confirm(`Are you sure you want to cancel ticket for PNR ${pnr}?`)) return;
      try {
        const res = await fetch('/api/cancel', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ pnr })
        });
        const data = await res.json();
        showNotification(data.message, data.success ? 'warning' : 'error');
        fetchState();
      } catch (err) {
        showNotification('Failed to cancel ticket.', 'error');
      }
    }

    async function undoCancel() {
      try {
        const res = await fetch('/api/undo', { method: 'POST' });
        const data = await res.json();
        showNotification(data.message, data.success ? 'success' : 'info');
        fetchState();
      } catch (err) {
        showNotification('Failed to undo cancellation.', 'error');
      }
    }

    async function sortTickets(by) {
      try {
        const res = await fetch('/api/sort', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ by })
        });
        const data = await res.json();
        showNotification(`Confirmed tickets sorted by ${data.sorted_by} using Bubble Sort on Doubly Linked List!`, 'info');
        fetchState();
      } catch (err) {
        showNotification('Failed to sort tickets.', 'error');
      }
    }

    async function handleSearch() {
      const pnr = document.getElementById('search-pnr').value.trim();
      const mode = document.getElementById('search-mode').value;
      if (!pnr) {
        alert('Please enter a PNR code.');
        return;
      }

      try {
        const res = await fetch('/api/search', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ pnr, mode })
        });
        const data = await res.json();
        const container = document.getElementById('search-results');
        container.style.display = 'block';

        let html = `
          <div class="search-telemetry">
            <h4 style="margin-bottom: 8px; color: ${data.found ? '#059669' : '#dc2626'};">
              ${data.found ? '✅ Match Found' : '❌ Not Found'} • ${data.message}
            </h4>
        `;

        if (data.passenger) {
          const typeName = data.passenger.seatpref === 'W' ? 'Window' : (data.passenger.seatpref === 'M' ? 'Middle' : 'Aisle');
          html += `
            <p><strong>Passenger:</strong> ${data.passenger.name} (Age: ${data.passenger.age}, Pref: ${typeName} [${data.passenger.seatpref}])</p>
            <p><strong>Status:</strong> ${data.status} ${data.passenger.seat_no > 0 ? '• Seat #' + data.passenger.seat_no : '• Position #' + (data.position || 1)} • <strong>Fare:</strong> ₹${(data.passenger.fare || 0).toLocaleString()}</p>
          `;
        }

        if (data.steps && data.steps.length > 0) {
          html += `<div style="margin-top: 10px;"><strong>Binary Search Step-by-Step Telemetry:</strong>`;
          data.steps.forEach(s => {
            html += `<div class="search-step">Step ${s.step}: Subarray [${s.low} .. ${s.high}], checked mid index ${s.mid} (PNR: ${s.value}) → Comparison: ${s.comparison}</div>`;
          });
          html += `</div>`;
        }

        html += `</div>`;
        container.innerHTML = html;
      } catch (err) {
        showNotification('Search request failed.', 'error');
      }
    }

    async function loadPreviousRecords() {
      try {
        const res = await fetch('/api/demo', { method: 'POST' });
        const data = await res.json();
        showNotification('Loaded Previous Flight Records successfully!', 'success');
        fetchState();
      } catch (err) {
        showNotification('Failed to load previous flight records.', 'error');
      }
    }

    // Alias for compatibility
    const loadDemo = loadPreviousRecords;


    async function newFlightBooking() {
      if (!confirm("Are you sure you want to start a New Flight Booking? All current seat bookings and passenger records will be cleared for a fresh flight.")) return;
      try {
        const res = await fetch('/api/reset', { method: 'POST' });
        const data = await res.json();
        showNotification('🛫 New Flight Booking started! All 12 seats are available for booking.', 'success');
        fetchState();
      } catch (err) {
        showNotification('Failed to initialize new flight booking.', 'error');
      }
    }

    // Alias for backward compatibility
    const resetSystem = newFlightBooking;

    // Initial load
    fetchState();
  </script>
</body>
</html>
"""


class FlightBookingHTTPHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html):
        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/" or parsed.path == "/index.html":
            self._send_html(HTML_TEMPLATE)
        elif parsed.path == "/api/state":
            self._send_json(system.get_system_state())
        else:
            self.send_error(404, "Endpoint Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        content_len = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_len) if content_len > 0 else b"{}"

        try:
            payload = json.loads(post_body.decode("utf-8")) if post_body else {}
        except json.JSONDecodeError:
            payload = {}

        if parsed.path == "/api/book":
            name = payload.get("name", "")
            age = payload.get("age", 0)
            pref = payload.get("seatpref", "W")
            seat_no = payload.get("seat_no", None)
            res = system.book_ticket(name, age, pref, seat_no=seat_no)
            if "passenger" in res and res["passenger"]:
                res["passenger"] = res["passenger"].to_dict()
            self._send_json(res)

        elif parsed.path == "/api/cancel":
            pnr = payload.get("pnr", "")
            res = system.cancel_ticket(pnr)
            if "cancelled" in res and res["cancelled"]:
                res["cancelled"] = res["cancelled"].to_dict()
            if "promoted" in res and res["promoted"]:
                res["promoted"] = res["promoted"].to_dict()
            self._send_json(res)

        elif parsed.path == "/api/undo":
            res = system.undo_cancellation()
            if "passenger" in res and res["passenger"]:
                res["passenger"] = res["passenger"].to_dict()
            self._send_json(res)

        elif parsed.path == "/api/sort":
            by = payload.get("by", "name")
            sorted_by = system.sort_tickets(by=by)
            self._send_json({"success": True, "sorted_by": sorted_by})

        elif parsed.path == "/api/search":
            pnr = payload.get("pnr", "")
            mode = payload.get("mode", "binary")
            if mode == "binary":
                res = system.fast_search_pnr(pnr)
            else:
                res = system.search_pnr(pnr)
            if "passenger" in res and res["passenger"]:
                res["passenger"] = res["passenger"].to_dict()
            self._send_json(res)

        elif parsed.path == "/api/demo":
            load_demo_data()
            self._send_json({"success": True, "message": "Demo data loaded."})

        elif parsed.path in ("/api/reset", "/api/new-flight"):
            reset_system_state()
            self._send_json({"success": True, "message": "New flight initialized. All seats are free."})

        else:
            self.send_error(404, "Endpoint Not Found")

    def log_message(self, format, *args):
        # Suppress noisy HTTP request logging to console
        pass


def run_web_server(port=5050, open_browser=True):
    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, FlightBookingHTTPHandler)
    url = f"http://127.0.0.1:{port}"
    print("=" * 65)
    print(f"✈️  Flight Booking Web Interface is running at:")
    print(f"    {url}")
    print("=" * 65)
    print("Press Ctrl+C to stop the server.")

    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()


if __name__ == "__main__":
    port = 5050
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    run_web_server(port=port)
