# Coworking Space Management System

A database-driven desktop application for managing a coworking space, built as a 5th-semester DBMS mini-project. The system features a simple Tkinter GUI for both clients and administrators, connected to a robust MySQL backend.

<!-- You can add screenshots here if you have them -->
<!-- 
![Login Screen](link_to_your_login_screenshot.png)
![Admin Dashboard](link_to_your_admin_dashboard_screenshot.png) 
-->

## Features

### Client Module
* **User Authentication:** Secure sign-up and login for clients.
* **View Workspaces:** Browse all available workspaces with details on type, capacity, price, and location.
* **Create Bookings:** Book an available workspace for a specific date and time slot.
* **View Bookings:** See a personal history of all past and upcoming bookings.
* **Membership Management:** View and "purchase" membership plans (Basic, Standard, Premium, etc.).

### Admin Module
* **Admin Login:** Separate, secure login for administrators.
* **View All Bookings:** See a comprehensive table of all bookings from all clients.
* **Update Bookings:** Modify the start and end times of any booking.
* **Delete Bookings:** Remove invalid or cancelled bookings from the system.
* **Analytics Dashboard:**
    * **Admin Revenue:** View total revenue collected by each admin (Aggregate Query).
    * **Premium Clients:** See a list of clients who have booked high-value workspaces (Nested Query).
    * **Client Booking Count:** View the total number of bookings made by each client (Aggregate Query).

## Tech Stack
* **Frontend:** Python (Tkinter)
* **Backend:** Python
* **Database:** MySQL

## Database Schema
The database is designed in 3rd Normal Form (3NF) to reduce redundancy and ensure data integrity. The schema includes 9 tables:

* `Client`
* `ClientPhone` (handles multivalued attribute)
* `Admin`
* `Workspace`
* `Booking`
* `Payment`
* `MembershipPlan`
* `MembershipBenefit`
* `AdminAssignmentTracker`

For a visual representation, see the [ER Diagram in the docs folder](./docs/ER_Diagram.png).

## Key SQL Features Implemented
* **Triggers:**
    * `before_booking_insert`: Automatically calculates the `TotalCost` of a booking based on workspace price and duration.
    * `after_booking_insert`: Automatically creates a corresponding 'Pending' entry in the `Payment` table.
* **Stored Procedures:**
    * `PurchaseMembership`: A procedure that takes `ClientID` and `MembershipID` to update a client's membership status.
* **Nested & Correlated Queries:** Used in the admin dashboard to find premium clients.
* **Aggregate Queries:** Used to calculate total revenue per admin and total bookings per client, employing `SUM()`, `COUNT()`, and `GROUP BY`.

## Setup and Installation

Follow these steps to run the project locally:

1.  **Clone the repository:**
    ```sh
    git clone [https://github.com/YOUR_USERNAME/coworking-space-dbms.git](https://github.com/YOUR_USERNAME/coworking-space-dbms.git)
    cd coworking-space-dbms
    ```

2.  **Create a virtual environment and activate it:**
    ```sh
    # Windows
    python -m venv venv
    .\venv\Scripts\activate
    
    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required libraries:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Set up the MySQL Database:**
    * Ensure you have a MySQL server running (e.g., via MySQL Workbench).
    * Open the `sql/setup.sql` file.
    * Run the entire script in your MySQL server to create the `coworking_space` database, all tables, triggers, procedures, and sample data.

5.  **Configure the Application:**
    * Open the `src/DbmsProject.py` file.
    * Go to the `connect_db()` function (line 15).
    * Change the `password` parameter to **your own MySQL root password**.
    ```python
    def connect_db():
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="YOUR_PASSWORD_HERE",  # <-- CHANGE THIS
                database="coworking_space"
            )
    ```

6.  **Run the application:**
    ```sh
    python src/DbmsProject.py
    ```
    You can now log in using the sample client/admin data from the `setup.sql` file.

## Authors
* **Greeshma Dhananjaiah** (PES2UG23CS206)
* **Harshita Mudliar** (PES2UG23CS918)
