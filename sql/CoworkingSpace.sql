-- ==============================================
-- DATABASE: coworking_spaces
-- ==============================================
CREATE DATABASE IF NOT EXISTS coworking_spaces;
USE coworking_spaces;

-- ==============================================
-- 1. ADMIN TABLE
-- ==============================================
CREATE TABLE Admin (
    AdminID INT AUTO_INCREMENT PRIMARY KEY,
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    Email VARCHAR(100) UNIQUE,
    Password VARCHAR(50),
    PhoneNumber VARCHAR(15)
);

-- ==============================================
-- 2. MEMBERSHIP PLAN
-- ==============================================
CREATE TABLE MembershipPlan (
    MembershipID INT AUTO_INCREMENT PRIMARY KEY,
    PlanName VARCHAR(50),
    DurationMonths INT,
    Price DECIMAL(10,2)
);

-- ==============================================
-- 3. CLIENT TABLE
-- ==============================================
CREATE TABLE Client (
    ClientID INT AUTO_INCREMENT PRIMARY KEY,
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    Email VARCHAR(100) UNIQUE,
    Password VARCHAR(50),
    Gender ENUM('Male', 'Female'),
    Address VARCHAR(200),
    MembershipID INT DEFAULT 1,
    FOREIGN KEY (MembershipID) REFERENCES MembershipPlan(MembershipID)
        ON DELETE SET NULL
);

-- ==============================================
-- 4. CLIENT PHONE (MULTI-VALUE ATTRIBUTE)
-- ==============================================
CREATE TABLE ClientPhone (
    PhoneNumber VARCHAR(15) PRIMARY KEY,
    ClientID INT,
    FOREIGN KEY (ClientID) REFERENCES Client(ClientID)
        ON DELETE CASCADE
);

-- ==============================================
-- 5. MEMBERSHIP BENEFIT
-- ==============================================
CREATE TABLE MembershipBenefit (
    BenefitID INT AUTO_INCREMENT PRIMARY KEY,
    MembershipID INT,
    BenefitDescription VARCHAR(255),
    FOREIGN KEY (MembershipID) REFERENCES MembershipPlan(MembershipID)
        ON DELETE CASCADE
);

-- ==============================================
-- 6. WORKSPACE
-- ==============================================
CREATE TABLE Workspace (
    WorkspaceID INT AUTO_INCREMENT PRIMARY KEY,
    WorkspaceType VARCHAR(50),
    Capacity INT,
    PricePerHour DECIMAL(10,2),
    Location VARCHAR(100)
);

-- ==============================================
-- 7. BOOKING
-- ==============================================
CREATE TABLE Booking (
    BookingID INT AUTO_INCREMENT PRIMARY KEY,
    ClientID INT,
    WorkspaceID INT,
    StartTime DATETIME,
    EndTime DATETIME,
    TotalCost DECIMAL(10,2),
    AdminID INT,
    FOREIGN KEY (ClientID) REFERENCES Client(ClientID)
        ON DELETE CASCADE,
    FOREIGN KEY (WorkspaceID) REFERENCES Workspace(WorkspaceID),
    FOREIGN KEY (AdminID) REFERENCES Admin(AdminID)
);

-- ==============================================
-- 8. PAYMENT
-- ==============================================
CREATE TABLE Payment (
    PaymentID INT AUTO_INCREMENT PRIMARY KEY,
    BookingID INT,
    PaymentDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    Amount DECIMAL(10,2),
    PaymentMethod VARCHAR(50) DEFAULT 'Pending',
    FOREIGN KEY (BookingID) REFERENCES Booking(BookingID)
        ON DELETE CASCADE
);

-- ==============================================
-- 9. ADMIN ASSIGNMENT TRACKER
-- ==============================================
CREATE TABLE AdminAssignmentTracker (
    TrackerID INT AUTO_INCREMENT PRIMARY KEY,
    LastAssignedAdminID INT
);
	

-- ============================================
-- SAMPLE DATA FOR COWORKING SPACES DATABASE
-- ============================================

USE coworking_spaces;

-- ==============================
-- 1. MEMBERSHIP PLAN
-- ==============================
INSERT INTO MembershipPlan (PlanName, DurationMonths, Price) VALUES
('Basic', 1, 2000.00),
('Standard', 3, 5000.00),
('Premium', 6, 9000.00),
('Enterprise', 12, 15000.00);

-- ==============================
-- 2. CLIENT
-- (Password added to match your app’s login)
-- ==============================
INSERT INTO Client (FirstName, LastName, Email, Password, Gender, Address, MembershipID) VALUES
('Riya', 'Sharma', 'riya@example.com', 'riya123', 'Female', 'Indiranagar, Bangalore', 1),
('Arjun', 'Patel', 'arjun@example.com', 'arjun123', 'Male', 'Koramangala, Bangalore', 2),
('Sneha', 'Menon', 'sneha@example.com', 'sneha123', 'Female', 'Whitefield, Bangalore', 3),
('Karan', 'Singh', 'karan@example.com', 'karan123', 'Male', 'HSR Layout, Bangalore', 4);

-- ==============================
-- 3. CLIENT PHONE (Multi-Valued Attribute)
-- ==============================
INSERT INTO ClientPhone (PhoneNumber, ClientID) VALUES
('9876543210', 1),
('9123456780', 1),
('9822012345', 2),
('9811122233', 3),
('9000011122', 4);

-- ==============================
-- 4. MEMBERSHIP BENEFIT
-- ==============================
INSERT INTO MembershipBenefit (MembershipID, BenefitDescription) VALUES
(1, 'Access to open spaces'),
(2, 'Access to open spaces and meeting rooms'),
(3, 'Priority booking and free beverages'),
(4, '24x7 access with dedicated locker and parking');

-- ==============================
-- 5. WORKSPACE
-- ==============================
INSERT INTO Workspace (WorkspaceType, Capacity, PricePerHour, Location) VALUES
('Private Office', 4, 800.00, 'Koramangala'),
('Shared Desk', 10, 300.00, 'Indiranagar'),
('Meeting Room', 6, 500.00, 'Whitefield'),
('Open Space', 20, 200.00, 'HSR Layout');

-- ==============================
-- 6. ADMIN
-- (Added Password and Phone to match your Python code)
-- ==============================
INSERT INTO Admin (FirstName, LastName, Email, Password, PhoneNumber) VALUES
('Aditi', 'Verma', 'aditi.admin@example.com', 'admin1', '9876500011'),
('Rohit', 'Kumar', 'rohit.admin@example.com', 'admin2', '9876500022');

-- ==============================
-- 7. ADMIN ASSIGNMENT TRACKER
-- ==============================
INSERT INTO AdminAssignmentTracker (LastAssignedAdminID) VALUES (1);

-- ==============================
-- 8. BOOKING
-- (Triggers will auto-calculate TotalCost)
-- ==============================
INSERT INTO Booking (ClientID, WorkspaceID, AdminID, StartTime, EndTime)
VALUES
(1, 2, 1, '2025-10-21 10:00:00', '2025-10-21 14:00:00'),
(2, 1, 2, '2025-10-22 09:00:00', '2025-10-22 17:00:00'),
(3, 3, 1, '2025-10-23 11:00:00', '2025-10-23 13:00:00'),
(4, 4, 2, '2025-10-24 08:00:00', '2025-10-24 12:00:00');

-- ==============================
-- 9. PAYMENT
-- (In case triggers didn’t auto-fire, manual insert included)
-- ==============================
INSERT INTO Payment (BookingID, PaymentDate, Amount, PaymentMethod) VALUES
(1, '2025-10-21 14:10:00', 1200.00, 'UPI'),
(2, '2025-10-22 17:15:00', 6400.00, 'Credit Card'),
(3, '2025-10-23 13:05:00', 1000.00, 'Net Banking'),
(4, '2025-10-24 12:05:00', 800.00, 'Cash');

-- ==============================================
-- TRIGGER 1: BEFORE INSERT ON BOOKING
-- Automatically calculates TotalCost
-- ==============================================
DELIMITER $$

CREATE TRIGGER before_booking_insert
BEFORE INSERT ON Booking
FOR EACH ROW
BEGIN
    DECLARE rate DECIMAL(10,2);
    DECLARE total_hours INT;

    -- Fetch hourly rate for selected workspace
    SELECT PricePerHour INTO rate
    FROM Workspace
    WHERE WorkspaceID = NEW.WorkspaceID;

    -- Calculate duration in hours
    SET total_hours = TIMESTAMPDIFF(HOUR, NEW.StartTime, NEW.EndTime);

    -- Compute total cost
    SET NEW.TotalCost = total_hours * rate;
END $$

DELIMITER ;

-- ==============================================
-- TRIGGER 2: AFTER INSERT ON BOOKING
-- Automatically creates payment record
-- ==============================================
DELIMITER $$

CREATE TRIGGER after_booking_insert
AFTER INSERT ON Booking
FOR EACH ROW
BEGIN
    DECLARE total_hours INT;
    DECLARE rate DECIMAL(10,2);
    DECLARE total_amount DECIMAL(10,2);

    -- Fetch hourly rate from Workspace
    SELECT PricePerHour INTO rate
    FROM Workspace
    WHERE WorkspaceID = NEW.WorkspaceID;

    -- Calculate total cost again for safety
    SET total_hours = TIMESTAMPDIFF(HOUR, NEW.StartTime, NEW.EndTime);
    SET total_amount = total_hours * rate;

    -- Insert corresponding payment record
    INSERT INTO Payment (BookingID, PaymentDate, Amount, PaymentMethod)
    VALUES (NEW.BookingID, NOW(), total_amount, 'UPI');
END $$

DELIMITER ;

-- ==============================================
-- STORED PROCEDURE: PurchaseMembership
-- Used when client buys or upgrades membership
-- ==============================================
DELIMITER $$

CREATE PROCEDURE PurchaseMembership(IN client_id INT, IN plan_id INT)
BEGIN
    -- Update client's membership
    UPDATE Client
    SET MembershipID = plan_id
    WHERE ClientID = client_id;
END $$

DELIMITER ;

-- ==============================================
-- FUNCTION: GetClientTotalSpent
-- Returns total payment amount for a given client
-- ==============================================
DELIMITER $$

CREATE FUNCTION GetClientTotalSpent(client_id INT)
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE total DECIMAL(10,2);

    SELECT IFNULL(SUM(p.Amount), 0) INTO total
    FROM Payment p
    JOIN Booking b ON p.BookingID = b.BookingID
    WHERE b.ClientID = client_id;

    RETURN total;
END $$

DELIMITER ;