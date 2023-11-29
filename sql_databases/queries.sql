eschedule.db shema

CREATE TABLE members (
    member_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    email TEXT NOT NULL
);

CREATE TABLE contacts (
    contacts_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    email TEXT NOT NULL,
    address TEXT NOT NULL,
    work_type TEXT NOT NULL,
    member_id INTEGER,
    FOREIGN KEY (member_id) REFERENCES members(member_id)
);

CREATE TABLE schedule (
    month INTEGER NOT NULL,
    day INTEGER NOT NULL,
    year INTEGER NOT NULL,
    contacts_id INTEGER,
    FOREIGN KEY (contacts_id) REFERENCES contacts(contacts_id)
);

CREATE TABLE proposals (
    price INTEGER,
    description TEXT,
    contacts_id INTEGER,
    FOREIGN KEY (contacts_id) REFERENCES contacts(contacts_id)
);