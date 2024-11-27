from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import  db_helper
import generic_helper
from fastapi.templating import Jinja2Templates
from middleware.cors_middleware import add_cors_middleware



app = FastAPI()

templates = Jinja2Templates(directory="templates")

add_cors_middleware(app)

# Khai báo biến toàn cục cho các đơn hàng đang xử lý
progress_orders = {}

@app.post("/")
async def handle_request(request: Request):
    payload = await request.json()
    intent = payload.get('queryResult', {}).get('intent', {}).get('displayName', '')
    parameters = payload.get('queryResult', {}).get('parameters', {})
    output_contexts = payload.get('queryResult', {}).get('outputContexts', [])
    
    session_id = None
    if output_contexts:
        session_id = generic_helper.extract_session_id(output_contexts[0]['name'])

    if intent == "track.order - context: ongoing-tracking":
        return track_order(parameters, session_id)
    elif intent == "order.add - context: ongoing-order":
        return add_to_order(parameters, session_id)
    elif intent == "order.remove - context: ongoing-order": 
        return remove_from_order(parameters, session_id)
    elif intent == "order.complete - context: ongoing-order":
        return complete_order(parameters, session_id)
    else: 
        return JSONResponse(content={"fulfillmentText": "Intent not recognized"})

    
    
#                          Session_id_1
# ===============================||====================================
# I need 2 seafood Pizza and one coca ==> add_to_order ==>{"seafood Pizza": 2, "coca": 1}

# oh well, add one salad ==>{"seafood Pizza": 2, "coca": 1, "salad": 1}

def add_to_order(parameters: dict, session_id: str):
    # Chuyển đổi keys của parameters thành chữ thường để tránh nhầm lẫn
    normalized_parameters = {k.lower(): v for k, v in parameters.items()}

    # Lấy food_items và quantities từ parameters
    food_items = normalized_parameters.get("food-items", [])
    quantities = normalized_parameters.get("number", [])

    print(f"Food Items: {food_items}, Quantities: {quantities}")  # Log thông tin nhận được

    # Kiểm tra thông tin đầu vào
    if not food_items or not quantities or len(food_items) != len(quantities):
        fulfillment_text = "Sorry, I didn't understand. Can you please specify food items and quantities"
    else:
        new_food_dict = dict(zip(food_items, quantities))
        if session_id in progress_orders:
            current_food_dict = progress_orders[session_id]
            current_food_dict.update(new_food_dict)
            progress_orders[session_id] = current_food_dict
        else:
            progress_orders[session_id] = new_food_dict
        
        # Lấy chuỗi mô tả đơn hàng từ dictionary
        order_str = generic_helper.get_str_from_food_dict(progress_orders[session_id])
        fulfillment_text = f"So far you have {order_str}. Do you need anything else?"
        

    return JSONResponse(content={"fulfillmentText": fulfillment_text, "session_id": session_id})



def remove_from_order(parameters: dict, session_id: str):
    if session_id not in progress_orders:
        return JSONResponse(content={
            "fulfillmentText": "I'm having trouble finding your order. Can you place a new order, please?"
        })
    
    # Lấy thông tin món ăn và số lượng từ parameters
    food_items = parameters.get("food-items", [])
    quantity = parameters.get("number", 0)
    current_order = progress_orders[session_id]

    removed_items = []
    no_such_items = []

    for item in food_items:
        item_lower = item.lower()  # So sánh không phân biệt chữ hoa/thường
        matching_item = next((key for key in current_order.keys() if key.lower() == item_lower), None)

        if matching_item:
            if quantity >= current_order[matching_item]:  # Nếu số lượng cần xóa >= số lượng trong order
                del current_order[matching_item]
                removed_items.append(item)
            else:
                current_order[matching_item] -= quantity  # Giảm số lượng
                removed_items.append(f"{quantity} x {item}")
        else:
            no_such_items.append(item)

    # Tạo phản hồi
    fulfillment_text = ""
    if removed_items:
        fulfillment_text += f"Removed {', '.join(removed_items)} from your order. "

    if no_such_items:
        fulfillment_text += f"Your current order does not include {', '.join(no_such_items)}. "

    if not current_order:  # Nếu đơn hàng trống
        fulfillment_text += "Your order is now empty!"
        del progress_orders[session_id]
    else:
        order_str = generic_helper.get_str_from_food_dict(current_order)
        fulfillment_text += f"Here is what remains in your order: {order_str}."

    return JSONResponse(content={"fulfillmentText": fulfillment_text})


    


def complete_order(parameters: dict, session_id: str):
    # Kiểm tra xem có đơn hàng nào đang được xử lý không
    if session_id not in progress_orders:
        return JSONResponse(content={"fulfillmentText": "No ongoing order found for this session.", "session_id": session_id})

    # Lấy các món ăn và số lượng từ progress_orders
    order_items = progress_orders[session_id]
    
    # Lấy next order_id
    order_id = db_helper.get_next_order_id()

    # Tính tổng tiền cho đơn hàng từ order_items
    total_price = 0
    for item, quantity in order_items.items():
        item_id = db_helper.get_item_id_by_name(item)
        item_price = db_helper.get_item_price(item_id)
        total_price += item_price * quantity

    # Kiểm tra nếu tổng giá trị đơn hàng <= 0
    if total_price <= 0:
        return JSONResponse(content={"fulfillmentText": "Error calculating total price or no items found in the order.", "session_id": session_id})

    # Trả về kết quả với fulfillmentText bao gồm order_id
    fulfillment_text = f"Your order with ID {order_id} has been completed. The total price is {total_price} VND. Thank you for your order!"
    

    # Lưu tổng tiền và các món ăn vào cơ sở dữ liệu
    db_helper.save_to_db(order_id, total_price, order_items)


    # Xóa đơn hàng khỏi bộ nhớ tạm
    del progress_orders[session_id]

    return JSONResponse(content={"fulfillmentText": fulfillment_text})







def track_order(parameters: dict, session_id: str):
    order_id = parameters.get('order_id')
    if not order_id:
        return JSONResponse(content={"fulfillmentText": "No order ID provided", "session_id": session_id})

    try:
        order_id = int(order_id)
    except ValueError:
        return JSONResponse(content={"fulfillmentText": "Invalid order ID format.", "session_id": session_id})

    try:
        order_status = db_helper.get_order_status(order_id)
        if order_status:
            fulfillment_text = f"The status of your order ID {order_id} is: {order_status[0][0]}."
        else:
            fulfillment_text = f"No order found with order ID: {order_id}"
    except Exception as e:
        print(f"Error retrieving order status: {e}")
        fulfillment_text = "An unexpected error occurred while processing your request. Please try again."

    return JSONResponse(content={"fulfillmentText": fulfillment_text, "session_id": session_id})





@app.get("/api/order-tracking/")
async def order_tracking():
    # Gọi hàm fetch_order_details từ db_helper để lấy dữ liệu từ DB
    orders = db_helper.fetch_order_details()
    if orders is None:
        return {"error": "Failed to fetch order details"}
    return {"orders": orders}



