import re

# Trích xuất session_id từ session string
def extract_session_id(session_str: str):
    match = re.search(r"/sessions/(.*?)/contexts/", session_str)
    if match:
        extracted_string = match.group(1)
        return extracted_string
    return ""

# Chuyển đổi food_dict thành chuỗi dễ đọc
def get_str_from_food_dict(food_dict: dict):
    if not food_dict:  # Kiểm tra nếu food_dict rỗng
        return "No items in the order"
    return ", ".join([f"{int(value)} {key}" for key, value in food_dict.items()])


if __name__ == "__main__":
    print(get_str_from_food_dict({"Seafood pizza": 2, "salad": 1}))
    # print(extract_session_id("projects/tinnn-chatbot-for-food-de-oucm/agent/sessions/123/contexts/ongoing-order"))
