import sqlite3



# Đường dẫn tới cơ sở dữ liệu SQLite
db_path = r'F:\PYTHON CODE\AIProject\database\FastFoodAI.db'


def get_order_status(order_id: int):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print(f"Querying for order ID: {order_id}")  # Log truy vấn

        # Thực hiện truy vấn
        cursor.execute("""
            SELECT ot.status, oi.item_id, oi.quantity, oi.total_price, fi.name
            FROM order_tracking ot
            LEFT JOIN order_items oi ON ot.order_id = oi.order_id
            LEFT JOIN food_items fi ON oi.item_id = fi.item_id
            WHERE ot.order_id = ?;
        """, (order_id,))

        order_status = cursor.fetchall()
        conn.close()

        print(f"Fetched data: {order_status}")  # Log kết quả trả về
        return order_status
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None

def get_next_order_id():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT MAX(order_id) FROM order_tracking")
        result = cursor.fetchone()[0]

        next_order_id = 1 if result is None else result + 1
        cursor.close()
        return next_order_id
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return -1

# Lấy ID món ăn theo tên
def get_item_id_by_name(food_item: str):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT item_id FROM food_items WHERE name = ?", (food_item,))
        result = cursor.fetchone()

        item_id = result[0] if result else None
        cursor.close()
        return item_id
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None

# Lấy giá của món ăn theo item_id
def get_item_price(item_id: int):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT price FROM food_items WHERE item_id = ?", (item_id,))
        result = cursor.fetchone()

        price = result[0] if result else 0
        cursor.close()
        return price
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return 0



def get_total_order_price(order_id: int):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT SUM(oi.quantity * fi.price) FROM order_items oi
            LEFT JOIN food_items fi ON oi.item_id = fi.item_id
            WHERE oi.order_id = ?
        """, (order_id,))
        
        result = cursor.fetchone()
        total_price = result[0] if result and result[0] is not None else 0.0

        cursor.close()
        return total_price
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return 0



def save_to_db(order_id: int, total_price: float, order_items: dict):
  """
  Saves order information to the database.

  Args:
      order_id (int): The unique identifier for the order.
      total_price (float): The total price of the order.
      order_items (dict): A dictionary containing food items and their quantities.

  Returns:
      bool: True if successful, False otherwise.
  """

  try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Insert order tracking information
    cursor.execute("INSERT INTO order_tracking (order_id, status) VALUES (?, ?)",
                   (order_id, "in progress"))

    # Insert each order item
    for food_item, quantity in order_items.items():
      item_id = get_item_id_by_name(food_item)
      if not item_id:
        # Handle error: Food item not found in database
        return False

      total_item_price = get_item_price(item_id) * quantity
      cursor.execute("INSERT INTO order_items (order_id, item_id, quantity, total_price) VALUES (?, ?, ?, ?)",
                     (order_id, item_id, quantity, total_item_price))

    # Commit changes and close connection
    conn.commit()
    conn.close()
    return True

  except sqlite3.Error as e:
    print(f"Database error: {e}")
    conn.rollback()  # Rollback changes in case of errors
    conn.close()
    return False


