import sqlite3

# Đường dẫn đến SQLite database
db_path = r'F:\PYTHON CODE\OrderAI-Fastfood\OrderAI-Fastfood\database\FastFoodAI.db'

def get_order_status(order_id: int):
    """Lấy trạng thái đơn hàng."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ot.status, oi.item_id, oi.quantity, oi.total_price, fi.name
            FROM order_tracking ot
            LEFT JOIN order_items oi ON ot.order_id = oi.order_id
            LEFT JOIN food_items fi ON oi.item_id = fi.item_id
            WHERE ot.order_id = ?;
        """, (order_id,))
        result = cursor.fetchall()
        conn.close()
        return result
    except sqlite3.Error as e:
        print(f"DB error: {e}")
        return None

def get_next_order_id():
    """Lấy ID đơn hàng tiếp theo."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(order_id) FROM order_tracking")
        result = cursor.fetchone()[0]
        conn.close()
        return 1 if result is None else result + 1
    except sqlite3.Error as e:
        print(f"DB error: {e}")
        return -1

def get_item_id_by_name(food_item: str):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT item_id FROM food_items WHERE LOWER(name) = ?", (food_item.lower(),))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    except sqlite3.Error as e:
        print(f"DB error: {e}")
        return None

def get_item_price(item_id: int):
    """Lấy giá món ăn theo ID."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT price FROM food_items WHERE item_id = ?", (item_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0
    except sqlite3.Error as e:
        print(f"DB error: {e}")
        return 0

def get_total_order_price(order_id: int):
    """Tính tổng tiền đơn hàng."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT SUM(oi.quantity * fi.price) FROM order_items oi
            LEFT JOIN food_items fi ON oi.item_id = fi.item_id
            WHERE oi.order_id = ?;
        """, (order_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result and result[0] is not None else 0.0
    except sqlite3.Error as e:
        print(f"DB error: {e}")
        return 0

def save_to_db(order_id: int, total_price: float, order_items: dict):
    """Lưu đơn hàng vào DB."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO order_tracking (order_id, status) VALUES (?, ?)", (order_id, "in progress"))
        for food_item, quantity in order_items.items():
            item_id = get_item_id_by_name(food_item)
            if not item_id:
                return False
            total_item_price = get_item_price(item_id) * quantity
            cursor.execute("INSERT INTO order_items (order_id, item_id, quantity, total_price) VALUES (?, ?, ?, ?)",
                           (order_id, item_id, quantity, total_item_price))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"DB error: {e}")
        conn.rollback()
        conn.close()
        return False

def fetch_order_details():
    """Lấy thông tin chi tiết các đơn hàng."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ot.order_id, ot.status, fi.name AS item, oi.quantity, oi.total_price
            FROM order_tracking ot
            LEFT JOIN order_items oi ON ot.order_id = oi.order_id
            LEFT JOIN food_items fi ON oi.item_id = fi.item_id
            ORDER BY ot.order_id, oi.item_id;
        """)
        result = cursor.fetchall()
        conn.close()
        return result
    except sqlite3.Error as e:
        print(f"DB error: {e}")
        return None
