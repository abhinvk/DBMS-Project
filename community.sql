
-- Create Resident table
CREATE TABLE Resident (
    ResidentID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100),
    ContactInfo bigint,
    Email VARCHAR(100),
    Password VARCHAR(255),
    Location VARCHAR(100)
);

-- Create Event table
CREATE TABLE Event (
    EventID INT auto_increment PRIMARY KEY,
    Title VARCHAR(50),
    Date1 date,
    Location VARCHAR(50),
    Details VARCHAR(100),
    ResidentID INT,
    foreign key(ResidentID) references Resident(ResidentID)
);

-- Create MaintenanceRequest table
CREATE TABLE MaintenanceRequest (
    RequestID INT auto_increment PRIMARY KEY,
    ResidentID INT,
    Description VARCHAR(300),
    Date DATE,
    Location VARCHAR(30),
    Status VARCHAR(50),
    FOREIGN KEY (ResidentID) REFERENCES Resident(ResidentID)
);

-- Create Transportation table
CREATE TABLE lost_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    item_name VARCHAR(100) NOT NULL,
    image_data MEDIUMBLOB NOT NULL,
    location VARCHAR(255) NOT NULL,
    description TEXT,
    FOREIGN KEY (user_id) REFERENCES Resident(ResidentID)
);


CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    destination VARCHAR(255) NOT NULL,
    departure_time DATETIME NOT NULL,
    seats_available INT NOT NULL,
    user_id INT,
    FOREIGN KEY (user_id) references Resident(ResidentID)
    );
    
CREATE TABLE seat_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    notification_id INT,
    name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    stop VARCHAR(100) NOT NULL,
    FOREIGN KEY (notification_id) REFERENCES notifications(id)
);
