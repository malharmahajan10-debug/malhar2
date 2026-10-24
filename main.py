"""Main entry point for the Flight Booking System.

Usage:
  python3 main.py          # Interactive launcher
  python3 main.py --web    # Launch Web Dashboard in browser
  python3 main.py --gui    # Launch Desktop Tkinter GUI
  python3 main.py --cli    # Launch Console CLI
"""

import sys


def main():
    args = sys.argv[1:]

    if "--web" in args or "-w" in args:
        import web_app
        web_app.run_web_server(port=5050, open_browser=True)
        return

    if "--gui" in args or "-g" in args:
        import gui_app
        gui_app.run_gui()
        return

    if "--cli" in args or "-c" in args:
        import flight_booking_app
        flight_booking_app.main()
        return

    # Interactive choice if no flag provided
    print("\n" + "=" * 50)
    print("✈️   FLIGHT BOOKING SYSTEM (DS PROJECT)")
    print("=" * 50)
    print("Choose your preferred interface:")
    print("  1. 🌐 Web Dashboard (Recommended - Browser UI)")
    print("  2. 🖥️  Desktop GUI (Tkinter Window)")
    print("  3. ⌨️  Console CLI (Terminal Menu)")
    print("  0. ❌ Exit")
    print("=" * 50)

    try:
        choice = input("Enter choice (1/2/3/0) [Default: 1]: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nExiting...")
        return

    if choice == "" or choice == "1":
        import web_app
        web_app.run_web_server(port=5050, open_browser=True)
    elif choice == "2":
        import gui_app
        gui_app.run_gui()
    elif choice == "3":
        import flight_booking_app
        flight_booking_app.main()
    elif choice == "0":
        print("Goodbye!")
    else:
        print("Invalid choice. Defaulting to Web Dashboard...")
        import web_app
        web_app.run_web_server(port=5050, open_browser=True)


if __name__ == "__main__":
    main()
