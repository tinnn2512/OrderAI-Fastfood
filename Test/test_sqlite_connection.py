import sqlite3

# Đường dẫn tới cơ sở dữ liệu SQLite của bạn
db_path = r'F:\PYTHON CODE\AIProject\database\FastFoodAI.db'

# Hàm kết nối và tính tổng giá trị đơn hàng
def get_total_order_price(order_id: int):
    try:
        # Kết nối tới cơ sở dữ liệu
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Truy vấn tổng giá trị đơn hàng
        cursor.execute('''
            SELECT SUM(total_price) FROM order_items WHERE order_id = ?
        ''', (order_id,))
        result = cursor.fetchone()[0]
        
        # Nếu không có giá trị nào (không có món trong đơn hàng), trả về 0
        total_price = result if result else 0.0

        # Đảm bảo đóng kết nối
        conn.close()

        return total_price

    except sqlite3.Error as e:
        print(f"Lỗi khi truy vấn cơ sở dữ liệu: {e}")
        return 0.0

# Test hàm với order_id = 43
order_id = 43
total_price = get_total_order_price(order_id)
print(f"Tổng giá trị đơn hàng với order_id = {order_id} là: {total_price} VND")
