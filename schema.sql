DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS sub_categories;
DROP TABLE IF EXISTS cards;
DROP TABLE IF EXISTS degrees;
DROP TABLE IF EXISTS spending;

CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE sub_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    c_id INTEGER NOT NULL,
    default_card INTEGER,
    default_degree INTEGER,
    FOREIGN KEY (c_id) REFERENCES categories (id),
    FOREIGN KEY (default_card) REFERENCES cards (id),
    FOREIGN KEY (default_degree) REFERENCES degrees (id)
);

CREATE TABLE cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bank TEXT NOT NULL,
    name TEXT UNIQUE NOT NULL,
    cur_balance REAL,
    pay_date INTEGER,
    last_statement TEXT
);

CREATE TABLE degrees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE spending (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    amount REAL NOT NULL,
    category INTEGER NOT NULL,
    sub_category INTEGER NOT NULL,
    yr INTEGER NOT NULL,
    mon INTEGER NOT NULL,
    daynum INTEGER NOT NULL,
    card INTEGER NOT NULL,
    degree INTEGER NOT NULL,
    comments TEXT,
    FOREIGN KEY (category) REFERENCES categories (id),
    FOREIGN KEY (sub_category) REFERENCES sub_categories (id),
    FOREIGN KEY (card) REFERENCES cards (id),
    FOREIGN KEY (degree) REFERENCES degrees (id)
);