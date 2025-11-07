import mysql.connector
from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# ======================================
# DATABASE CONNECTION
# ======================================
def connect_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",            # your MySQL username
            password="password",    # change to your MySQL password
            database="coworking_space"
        )
        return conn
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
        return None


# ======================================
# ADMIN FUNCTIONS
# ======================================
def view_all_bookings(tree):
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                b.BookingID,
                CONCAT(c.FirstName, ' ', c.LastName) AS ClientName,
                w.WorkspaceType, 
                w.Location,
                b.StartTime, 
                b.EndTime, 
                b.TotalCost,
                b.AdminID,
                COALESCE(CONCAT(a.FirstName, ' ', a.LastName), 'Not Assigned') AS AssignedAdmin
            FROM Booking b
            JOIN Client c ON b.ClientID = c.ClientID
            JOIN Workspace w ON b.WorkspaceID = w.WorkspaceID
            LEFT JOIN Admin a ON b.AdminID = a.AdminID
            ORDER BY b.StartTime DESC
        """)
        rows = cur.fetchall()

        tree.delete(*tree.get_children())
        for row in rows:
            tree.insert("", "end", values=row)

        cur.close()
        conn.close()

        if not rows:
            messagebox.showinfo("Info", "No bookings found in the database.")

    except Exception as e:
        messagebox.showerror("Error", str(e))


def update_booking(entry_id, entry_start, entry_end, tree):
    try:
        booking_id = entry_id.get()
        start = entry_start.get()
        end = entry_end.get()

        if booking_id == "" or start == "" or end == "":
            messagebox.showerror("Error", "Please fill all fields.")
            return

        conn = connect_db()
        cur = conn.cursor()

        # Check if booking exists
        cur.execute("SELECT BookingID FROM Booking WHERE BookingID = %s", (booking_id,))
        if not cur.fetchone():
            messagebox.showerror("Error", f"No booking found with ID {booking_id}.")
            cur.close()
            conn.close()
            return

        cur.execute("""
            UPDATE Booking
            SET StartTime = %s, EndTime = %s
            WHERE BookingID = %s
        """, (start, end, booking_id))
        conn.commit()

        messagebox.showinfo("Updated", f"Booking {booking_id} updated successfully.")

        cur.close()
        conn.close()

        view_all_bookings(tree)

    except Exception as e:
        messagebox.showerror("Error", str(e))


def delete_booking(entry_delete, tree):
    try:
        booking_id = entry_delete.get().strip()
        if booking_id == "":
            messagebox.showerror("Error", "Enter Booking ID to delete.")
            return

        conn = connect_db()
        cur = conn.cursor()

        # Check if booking exists
        cur.execute("SELECT BookingID FROM Booking WHERE BookingID = %s", (booking_id,))
        exists = cur.fetchone()
        if not exists:
            messagebox.showerror("Error", f"No booking found with ID {booking_id}.")
            cur.close()
            conn.close()
            return

        cur.execute("DELETE FROM Booking WHERE BookingID = %s", (booking_id,))
        conn.commit()

        messagebox.showinfo("Deleted", f"Booking ID {booking_id} deleted successfully.")

        cur.close()
        conn.close()

        # Refresh admin booking table
        view_all_bookings(tree)

    except Exception as e:
        messagebox.showerror("Error", str(e))


# ======================================
# CLIENT FUNCTIONS
# ======================================
def create_booking(client_id, entry_workspace, entry_start, entry_end):
    try:
        workspace_id = entry_workspace.get()
        start = entry_start.get()
        end = entry_end.get()

        if workspace_id == "" or start == "" or end == "":
            messagebox.showerror("Error", "All fields are required.")
            return

        conn = connect_db()
        cur = conn.cursor()

        # Prevent overlapping bookings
        cur.execute("""
            SELECT * FROM Booking
            WHERE WorkspaceID=%s AND
            ((StartTime <= %s AND EndTime > %s)
            OR (StartTime < %s AND EndTime >= %s))
        """, (workspace_id, start, start, end, end))
        overlap = cur.fetchone()

        if overlap:
            messagebox.showwarning("Warning", "This workspace is already booked for the selected time.")
            cur.close()
            conn.close()
            return

        # Get last assigned admin
        cur.execute("SELECT LastAssignedAdminID FROM AdminAssignmentTracker ORDER BY TrackerID DESC LIMIT 1")
        last_admin = cur.fetchone()[0]
        next_admin = 2 if last_admin == 1 else 1

        # Update tracker
        cur.execute("UPDATE AdminAssignmentTracker SET LastAssignedAdminID = %s WHERE TrackerID = 1", (next_admin,))

        # Insert booking with assigned admin
        cur.execute("""
            INSERT INTO Booking (ClientID, WorkspaceID, StartTime, EndTime, AdminID)
            VALUES (%s, %s, %s, %s, %s)
        """, (client_id, workspace_id, start, end, next_admin))
        conn.commit()

        booking_id = cur.lastrowid

        # Fetch admin details to show client
        cur.execute("SELECT CONCAT(FirstName, ' ', LastName) FROM Admin WHERE AdminID = %s", (next_admin,))
        admin_name = cur.fetchone()[0]

        messagebox.showinfo("Booking Created",
                            f"Booking created successfully!\n\nAssigned Admin:\nID: {next_admin}\nName: {admin_name}\n\nProceeding to payment...")

        cur.close()
        conn.close()

        # Open payment page for this specific booking
        open_payment_page(client_id, booking_id)

    except Exception as e:
        messagebox.showerror("Error", str(e))


def view_available_workspaces(tree):
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT WorkspaceID, WorkspaceType, Capacity, PricePerHour, Location FROM Workspace")
        rows = cur.fetchall()
        tree.delete(*tree.get_children())
        for row in rows:
            tree.insert("", "end", values=row)
        cur.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", str(e))


def view_my_bookings(client_id):
    try:
        win = tk.Toplevel()
        win.title("My Bookings")
        win.geometry("700x400")

        columns = ("BookingID", "WorkspaceType", "Location", "StartTime", "EndTime", "TotalCost")
        tree = ttk.Treeview(win, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=110)
        tree.pack(fill="both", expand=True)

        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT b.BookingID, w.WorkspaceType, w.Location, b.StartTime, b.EndTime, b.TotalCost
            FROM Booking b
            JOIN Workspace w ON b.WorkspaceID = w.WorkspaceID
            WHERE b.ClientID = %s
            ORDER BY b.StartTime DESC
        """, (client_id,))
        rows = cur.fetchall()
        for row in rows:
            tree.insert("", "end", values=row)
        cur.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def show_premium_clients():
    try:
        win = tk.Toplevel()
        win.title("Clients Who Booked Premium Workspaces")
        win.geometry("700x400")
        win.config(bg="#f0f8ff")

        tk.Label(win, text="Clients Who Booked Premium Workspaces",
                 font=("Arial", 16, "bold"), bg="#f0f8ff").pack(pady=15)

        columns = ("ClientID", "FirstName", "LastName", "Email")
        tree = ttk.Treeview(win, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT DISTINCT c.ClientID, c.FirstName, c.LastName, c.Email
            FROM Client c
            JOIN Booking b ON c.ClientID = b.ClientID
            WHERE b.WorkspaceID IN (
                SELECT WorkspaceID FROM Workspace
                WHERE PricePerHour > (SELECT AVG(PricePerHour) FROM Workspace)
            );
        """)
        rows = cur.fetchall()
        for row in rows:
            tree.insert("", "end", values=row)
        cur.close()
        conn.close()

    except Exception as e:
        messagebox.showerror("Error", str(e))

def show_admin_revenue():
    try:
        win = tk.Toplevel()
        win.title("Total Revenue Collected by Each Admin")
        win.geometry("700x400")
        win.config(bg="#f0f8ff")

        tk.Label(win, text="Total Revenue Collected by Each Admin",
                 font=("Arial", 16, "bold"), bg="#f0f8ff").pack(pady=15)

        columns = ("AdminName", "TotalRevenue")
        tree = ttk.Treeview(win, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=200)
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT CONCAT(a.FirstName, ' ', a.LastName) AS AdminName,
                   IFNULL(SUM(p.Amount), 0) AS TotalRevenue
            FROM Admin a
            JOIN Booking b ON a.AdminID = b.AdminID
            JOIN Payment p ON b.BookingID = p.BookingID
            GROUP BY a.AdminID;
        """)
        rows = cur.fetchall()
        for row in rows:
            tree.insert("", "end", values=row)
        cur.close()
        conn.close()

    except Exception as e:
        messagebox.showerror("Error", str(e))

def show_client_bookings_count():
    try:
        win = tk.Toplevel()
        win.title("Total Bookings per Client")
        win.geometry("700x400")
        win.config(bg="#f0f8ff")

        tk.Label(win, text="Total Bookings per Client",
                 font=("Arial", 16, "bold"), bg="#f0f8ff").pack(pady=15)

        columns = ("ClientName", "TotalBookings")
        tree = ttk.Treeview(win, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=250)
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT CONCAT(c.FirstName, ' ', c.LastName) AS ClientName,
                   COUNT(b.BookingID) AS TotalBookings
            FROM Client c
            LEFT JOIN Booking b ON c.ClientID = b.ClientID
            GROUP BY c.ClientID;
        """)
        rows = cur.fetchall()
        for row in rows:
            tree.insert("", "end", values=row)
        cur.close()
        conn.close()

    except Exception as e:
        messagebox.showerror("Error", str(e))

# ======================================
# PAYMENT PAGE FUNCTION
# ======================================
def open_payment_page(client_id, booking_id=None):
    try:
        pay_win = tk.Toplevel()
        pay_win.title("Payment Confirmation")
        pay_win.geometry("500x420")
        pay_win.config(bg="#f0f8ff")

        tk.Label(pay_win, text="Payment Portal", font=("Arial", 16, "bold"), bg="#f0f8ff").pack(pady=15)

        conn = connect_db()
        if not conn:
            return
        cur = conn.cursor()

        # Fetch the booking created
        if booking_id:
            cur.execute("""
                SELECT BookingID, IFNULL(TotalCost, 0)
                FROM Booking
                WHERE ClientID = %s AND BookingID = %s
            """, (client_id, booking_id))
        else:
            cur.execute("""
                SELECT BookingID, IFNULL(TotalCost, 0)
                FROM Booking
                WHERE ClientID = %s
                ORDER BY BookingID DESC LIMIT 1
            """, (client_id,))
        booking = cur.fetchone()

        if not booking:
            tk.Label(pay_win, text="No recent bookings found.", bg="#f0f8ff", font=("Arial", 12)).pack(pady=20)
            cur.close()
            conn.close()
            return

        booking_id_sel, total_cost = booking

        # Fetch the payment record generated by AFTER trigger
        cur.execute("""
            SELECT PaymentID, PaymentDate, Amount, PaymentMethod
            FROM Payment
            WHERE BookingID = %s
            ORDER BY PaymentID DESC LIMIT 1
        """, (booking_id_sel,))
        payment = cur.fetchone()

        if not payment:
            tk.Label(pay_win, text="Payment record not found (trigger may not have executed yet).",
                     bg="#f0f8ff", font=("Arial", 12)).pack(pady=20)
            cur.close()
            conn.close()
            return

        payment_id, payment_date, amount, method = payment
        cur.close()
        conn.close()

        # Display details
        tk.Label(pay_win, text=f"Booking ID: {booking_id_sel}", bg="#f0f8ff", font=("Arial", 12)).pack(pady=5)
        tk.Label(pay_win, text=f"Payment ID: {payment_id}", bg="#f0f8ff", font=("Arial", 12)).pack(pady=5)
        tk.Label(pay_win, text=f"Amount: ₹{amount}", bg="#f0f8ff", font=("Arial", 12)).pack(pady=5)
        tk.Label(pay_win, text=f"Payment Date: {payment_date}", bg="#f0f8ff", font=("Arial", 12)).pack(pady=5)

        # Dropdown for payment method
        tk.Label(pay_win, text="Select/Change Payment Method:", bg="#f0f8ff", font=("Arial", 12)).pack(pady=5)
        payment_var = tk.StringVar(value=method)
        payment_combo = ttk.Combobox(pay_win, textvariable=payment_var, width=25, state="readonly")
        payment_combo["values"] = ["UPI", "Credit Card", "Debit Card", "Net Banking", "Cash"]
        payment_combo.pack(pady=5)

        # Label to show status
        status_label = tk.Label(pay_win, text="", bg="#f0f8ff", font=("Arial", 12))
        status_label.pack(pady=10)

        # Confirm button updates payment method
        def update_payment_method():
            new_method = payment_var.get()
            try:
                conn2 = connect_db()
                cur2 = conn2.cursor()
                cur2.execute("""
                    UPDATE Payment
                    SET PaymentMethod = %s
                    WHERE PaymentID = %s
                """, (new_method, payment_id))
                conn2.commit()
                cur2.close()
                conn2.close()
                status_label.config(text=f"Payment method updated to {new_method}", fg="green")
                messagebox.showinfo("Updated", f"Payment method updated to {new_method} successfully!")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(pay_win, text="Confirm Payment", bg="#4CAF50", fg="white", font=("Arial", 12),
                  width=18, command=update_payment_method).pack(pady=15)

    except Exception as e:
        messagebox.showerror("Error", str(e))

def open_membership_page(client_id):
    try:
        mem_win = tk.Toplevel()
        mem_win.title("Membership Plans")
        mem_win.geometry("650x500")
        mem_win.config(bg="#f0f8ff")

        tk.Label(mem_win, text="Available Membership Plans", font=("Arial", 16, "bold"), bg="#f0f8ff").pack(pady=15)

        # Table for membership plans
        columns = ("MembershipID", "PlanName", "DurationMonths", "Price")
        plan_tree = ttk.Treeview(mem_win, columns=columns, show="headings", height=6)
        for col in columns:
            plan_tree.heading(col, text=col)
            plan_tree.column(col, width=130)
        plan_tree.pack(pady=10, fill="x")

        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT MembershipID, PlanName, DurationMonths, Price FROM membershipplan")
        plans = cur.fetchall()
        for p in plans:
            plan_tree.insert("", "end", values=p)
        conn.close()

        # Benefits list
        tk.Label(mem_win, text="Plan Benefits:", font=("Arial", 12, "bold"), bg="#f0f8ff").pack(pady=5)
        benefit_list = tk.Listbox(mem_win, width=70, height=6)
        benefit_list.pack(pady=5)

        def show_benefits(event):
            selected_item = plan_tree.focus()
            if not selected_item:
                return
            plan_id = plan_tree.item(selected_item)['values'][0]
            conn2 = connect_db()
            cur2 = conn2.cursor()
            cur2.execute("""
                SELECT BenefitDescription FROM membershipbenefit
                WHERE MembershipID = %s
            """, (plan_id,))
            benefits = cur2.fetchall()
            benefit_list.delete(0, tk.END)
            for b in benefits:
                benefit_list.insert(tk.END, f"• {b[0]}")
            cur2.close()
            conn2.close()

        plan_tree.bind("<<TreeviewSelect>>", show_benefits)

        def purchase_membership():
            selected_item = plan_tree.focus()
            if not selected_item:
                messagebox.showerror("Error", "Please select a membership plan.")
                return
            plan_id = plan_tree.item(selected_item)['values'][0]

            try:
                conn3 = connect_db()
                cur3 = conn3.cursor()

                # ✅ Call stored procedure instead of direct UPDATE
                cur3.callproc('PurchaseMembership', (client_id, plan_id))
                conn3.commit()

                cur3.close()
                conn3.close()

                messagebox.showinfo("Success", f"Membership Plan ID {plan_id} purchased successfully!")
                mem_win.destroy()

            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(mem_win, text="Purchase Membership", bg="#4CAF50", fg="white",
                  font=("Arial", 12), width=20, command=purchase_membership).pack(pady=20)

    except Exception as e:
        messagebox.showerror("Error", str(e))


# ======================================
# LOGIN FUNCTION
# ======================================
def login():
    email = entry_email.get()
    password = entry_password.get()

    if email == "" or password == "":
        messagebox.showerror("Error", "All fields required!")
        return

    try:
        conn = connect_db()
        cur = conn.cursor()

        # Admin login
        cur.execute("SELECT AdminID FROM Admin WHERE Email=%s AND Password=%s", (email, password))
        admin = cur.fetchone()

        if admin:
            root.destroy()
            open_admin_dashboard()
            return

        # Client login
        cur.execute("SELECT ClientID FROM Client WHERE Email=%s AND Password=%s", (email, password))
        client = cur.fetchone()

        if client:
            client_id = client[0]
            root.destroy()
            open_client_dashboard(client_id)
        else:
            messagebox.showerror("Error", "Invalid credentials.")

        cur.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", str(e))


# ======================================
# SIGNUP FUNCTION
# ======================================
def open_signup_page():
    signup = tk.Toplevel(root)
    signup.title("Client Sign Up")
    signup.geometry("400x520")
    signup.config(bg="#f5f5f5")

    tk.Label(signup, text="New User Registration", font=("Arial", 16, "bold"), bg="#f5f5f5").pack(pady=15)

    frame = tk.Frame(signup, bg="#f5f5f5")
    frame.pack(pady=10)

    labels = ["First Name", "Last Name", "Email", "Password", "Gender", "Address", "Phone Number"]
    entries = {}

    for i, label in enumerate(labels):
        tk.Label(frame, text=label + ":", font=("Arial", 12), bg="#f5f5f5").grid(row=i, column=0, padx=10, pady=5, sticky="w")

        if label == "Gender":
            gender_var = tk.StringVar()
            gender_combo = ttk.Combobox(frame, textvariable=gender_var, values=["Male", "Female"], state="readonly", width=22)
            gender_combo.grid(row=i, column=1, padx=10, pady=5)
            entries[label] = gender_combo
        else:
            ent = tk.Entry(frame, width=25, show="*" if label == "Password" else "")
            ent.grid(row=i, column=1, padx=10, pady=5)
            entries[label] = ent

    def register_user():
        fname = entries["First Name"].get()
        lname = entries["Last Name"].get()
        email = entries["Email"].get()
        password = entries["Password"].get()
        gender = entries["Gender"].get()
        address = entries["Address"].get()
        phone = entries["Phone Number"].get()

        if not all([fname, lname, email, password, gender, address, phone]):
            messagebox.showerror("Error", "All fields required!")
            return

        try:
            conn = connect_db()
            cur = conn.cursor()

            # Insert into Client table
            cur.execute("""
                INSERT INTO Client (FirstName, LastName, Email, Password, Gender, Address, MembershipID)
                VALUES (%s, %s, %s, %s, %s, %s, 1)
            """, (fname, lname, email, password, gender, address))
            conn.commit()

            # ✅ Retrieve auto-generated ClientID
            client_id = cur.lastrowid

            # ✅ Insert phone number into ClientPhone table
            cur.execute("""
                INSERT INTO ClientPhone (ClientID, PhoneNumber)
                VALUES (%s, %s)
            """, (client_id, phone))
            conn.commit()

            cur.close()
            conn.close()

            messagebox.showinfo("Success", "Registration successful! You can now log in.")
            signup.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Database Error: {e}")

    tk.Button(signup, text="Sign Up", command=register_user,
              bg="#4CAF50", fg="white", width=15, font=("Arial", 12)).pack(pady=20)


# ======================================
# ADMIN DASHBOARD
# ======================================
def open_admin_dashboard():
    dash = tk.Tk()
    dash.title("Admin Dashboard")
    dash.geometry("850x600")

    frame_tree = tk.Frame(dash)
    frame_tree.pack(fill="both", expand=True, padx=10, pady=10)

    columns = ("BookingID", "ClientName", "WorkspaceType", "Location", "StartTime", "EndTime", "TotalCost", "AdminID", "AssignedAdmin")

    tree = ttk.Treeview(frame_tree, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=110)
    tree.pack(fill="both", expand=True)

    tk.Button(dash, text="View All Bookings", bg="#2196F3", fg="white",
              command=lambda: view_all_bookings(tree)).pack(pady=10)
    tk.Button(dash, text="Premium Clients (Nested Query)", bg="#9C27B0", fg="white",
          command=show_premium_clients).pack(pady=5)

    tk.Button(dash, text="Admin Revenue (Aggregate Query)", bg="#009688", fg="white",
          command=show_admin_revenue).pack(pady=5)
    tk.Button(dash, text="Client Booking Count", bg="#3F51B5", fg="white",
          command=show_client_bookings_count).pack(pady=5)
    
    frame_update = tk.LabelFrame(dash, text="Update Booking", padx=10, pady=10)
    frame_update.pack(fill="x", padx=10, pady=10)
    tk.Label(frame_update, text="Booking ID").grid(row=0, column=0)
    entry_id = tk.Entry(frame_update)
    entry_id.grid(row=0, column=1)
    tk.Label(frame_update, text="New Start Time").grid(row=0, column=2)
    entry_start = tk.Entry(frame_update)
    entry_start.grid(row=0, column=3)
    tk.Label(frame_update, text="New End Time").grid(row=0, column=4)
    entry_end = tk.Entry(frame_update)
    entry_end.grid(row=0, column=5)
    tk.Button(frame_update, text="Update", bg="#4CAF50", fg="white",
              command=lambda: update_booking(entry_id, entry_start, entry_end, tree)).grid(row=0, column=6, padx=10)

    frame_delete = tk.LabelFrame(dash, text="Delete Booking", padx=10, pady=10)
    frame_delete.pack(fill="x", padx=10, pady=10)
    tk.Label(frame_delete, text="Booking ID").grid(row=0, column=0)
    entry_delete = tk.Entry(frame_delete)
    entry_delete.grid(row=0, column=1)
    tk.Button(frame_delete, text="Delete", bg="red", fg="white",
              command=lambda: delete_booking(entry_delete, tree)).grid(row=0, column=2, padx=10)
    

    dash.mainloop()


# ======================================
# CLIENT DASHBOARD
# ======================================
def open_client_dashboard(client_id):
    dash = tk.Tk()
    dash.title("Client Dashboard")
    dash.geometry("700x520")
    dash.config(bg="#f5f5f5")

    # Fetch client's current membership plan
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT COALESCE(mp.PlanName, 'No Membership Selected')
            FROM Client c
            LEFT JOIN membershipplan mp ON c.MembershipID = mp.MembershipID
            WHERE c.ClientID = %s
        """, (client_id,))
        result = cur.fetchone()
        current_membership = result[0] if result else "No Membership Selected"
        cur.close()
        conn.close()
    except Exception as e:
        current_membership = "Error fetching membership"

    # Dashboard Header
    tk.Label(dash, text=f"Welcome, Client ID: {client_id}",
             font=("Arial", 13, "bold"), bg="#f5f5f5").pack(pady=5)
    tk.Label(dash, text=f"Current Membership: {current_membership}",
             font=("Arial", 12), fg="green", bg="#f5f5f5").pack(pady=5)

    # Available Workspaces Section
    frame_ws = tk.LabelFrame(dash, text="Available Workspaces", padx=10, pady=10, bg="#f5f5f5")
    frame_ws.pack(fill="both", expand=True, padx=10, pady=10)

    columns = ("WorkspaceID", "WorkspaceType", "Capacity", "PricePerHour", "Location")
    ws_tree = ttk.Treeview(frame_ws, columns=columns, show="headings")
    for col in columns:
        ws_tree.heading(col, text=col)
        ws_tree.column(col, width=120)
    ws_tree.pack(fill="both", expand=True)

    tk.Button(dash, text="View Workspaces", bg="#2196F3", fg="white",
              command=lambda: view_available_workspaces(ws_tree)).pack(pady=10)

    # Booking section
    frame = tk.LabelFrame(dash, text="Create Booking", padx=10, pady=10, bg="#f5f5f5")
    frame.pack(fill="x", padx=10, pady=10)
    tk.Label(frame, text="Workspace ID", bg="#f5f5f5").grid(row=0, column=0)
    entry_workspace = tk.Entry(frame)
    entry_workspace.grid(row=0, column=1)
    tk.Label(frame, text="Start Time (YYYY-MM-DD HH:MM)", bg="#f5f5f5").grid(row=1, column=0)
    entry_start = tk.Entry(frame)
    entry_start.grid(row=1, column=1)
    tk.Label(frame, text="End Time (YYYY-MM-DD HH:MM)", bg="#f5f5f5").grid(row=2, column=0)
    entry_end = tk.Entry(frame)
    entry_end.grid(row=2, column=1)
    tk.Button(frame, text="Create Booking", bg="#4CAF50", fg="white",
              command=lambda: create_booking(client_id, entry_workspace, entry_start, entry_end)).grid(row=3, column=1, pady=10)

    # Additional buttons
    tk.Button(dash, text="View My Bookings", bg="#FF9800", fg="white",
              command=lambda: view_my_bookings(client_id)).pack(pady=10)
    
    tk.Button(dash, text="Membership Plans", bg="#2196F3", fg="white",
              font=("Arial", 12), command=lambda: open_membership_page(client_id)).pack(pady=10)

    dash.mainloop()


# ======================================
# LOGIN UI
# ======================================
root = tk.Tk()
root.title("Coworking Space Login")
root.geometry("400x350")
root.config(bg="#f5f5f5")

tk.Label(root, text="Coworking Space Login", font=("Arial", 16, "bold"), bg="#f5f5f5").pack(pady=20)

frame = tk.Frame(root, bg="#f5f5f5")
frame.pack(pady=10)

tk.Label(frame, text="Email:", font=("Arial", 12), bg="#f5f5f5").grid(row=0, column=0, padx=10, pady=5, sticky="w")
entry_email = tk.Entry(frame, width=30)
entry_email.grid(row=0, column=1, padx=10, pady=5)

tk.Label(frame, text="Password:", font=("Arial", 12), bg="#f5f5f5").grid(row=1, column=0, padx=10, pady=5, sticky="w")
entry_password = tk.Entry(frame, width=30, show="*")
entry_password.grid(row=1, column=1, padx=10, pady=5)

tk.Button(root, text="Login", command=login, bg="#4CAF50", fg="white", font=("Arial", 12), width=15).pack(pady=10)
tk.Button(root, text="Sign Up", command=open_signup_page, bg="#2196F3", fg="white", font=("Arial", 12), width=15).pack(pady=5)

root.mainloop()
