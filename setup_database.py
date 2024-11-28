import sqlite3

# Kết nối hoặc tạo cơ sở dữ liệu

conn = sqlite3.connect('/database/FastFoodAI.db')
cursor = conn.cursor()

# Tạo bảng food_items
cursor.execute('''
CREATE TABLE IF NOT EXISTS food_items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price DECIMAL(10, 2) NOT NULL
)
''')

# Tạo bảng order_tracking
cursor.execute('''
CREATE TABLE IF NOT EXISTS order_tracking (
    order_id INTEGER PRIMARY KEY,
    status TEXT NOT NULL
)
''')

# Tạo bảng order_items (thay "order" thành "order_items")
cursor.execute('''
CREATE TABLE IF NOT EXISTS order_items ( 
    order_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (order_id, item_id),
    FOREIGN KEY (order_id) REFERENCES order_tracking(order_id),
    FOREIGN KEY (item_id) REFERENCES food_items(item_id)
)
''')

# Thêm dữ liệu vào bảng food_items
food_items = [
    ('Traditional Pizza', 150000),
    ('Seafood Pizza', 180000),
    ('Special Pizza', 200000),
    ('Fried Chicken Wings', 50000),
    ('French Fries', 30000),
    ('Salad', 40000),
    ('Pasta', 70000),
    ('Coca-Cola', 20000),
    ('Juice', 25000)
]

cursor.executemany('''
INSERT INTO food_items (name, price) VALUES (?, ?)
''', food_items)

# Thêm dữ liệu vào bảng order_tracking
order_tracking = [
    (40, 'Delivered'),
    (41, 'In Transit'),
    (42, 'In Progress')
]

cursor.executemany('''
INSERT INTO order_tracking (order_id, status) VALUES (?, ?)
''', order_tracking)

# Thêm dữ liệu vào bảng order_items
orders = [
    (40, 1, 2, 100000),
    (40, 3, 1, 80000),
    (41, 4, 3, 150000),
    (41, 6, 2, 70000)
]

cursor.executemany('''
INSERT INTO order_items (order_id, item_id, quantity, total_price) VALUES (?, ?, ?, ?)
''', orders)

# Lưu thay đổi và đóng kết nối
conn.commit()
conn.close()

print("Cơ sở dữ liệu đã được tạo và dữ liệu đã được thêm vào thành công!")
