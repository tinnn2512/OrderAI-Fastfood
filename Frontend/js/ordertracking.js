// Ẩn bảng và hiển thị loading spinner khi đang tải dữ liệu
document.getElementById('loading').style.display = 'block';
document.querySelector('table').style.display = 'none';

// Fetch data from FastAPI backend
fetch('http://localhost:8000/api/order-tracking/')
    .then(response => response.json())
    .then(data => {
        const orders = data.orders;  // Dữ liệu đơn hàng từ API
        const tableBody = document.getElementById('order-table-body');
        const loadingSpinner = document.getElementById('loading');

        // Ẩn spinner và hiển thị bảng sau khi có dữ liệu
        loadingSpinner.style.display = 'none';
        document.querySelector('table').style.display = 'table';

        // Lặp qua từng đơn hàng và tạo các dòng trong bảng
        orders.forEach(order => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${order[0]}</td>    <!-- Order ID -->
                <td>${order[1]}</td>    <!-- Status -->
                <td>${order[2]}</td>    <!-- Item -->
                <td>${order[3]}</td>    <!-- Quantity -->
                <td>${order[4]}</td>    <!-- Total Price -->
            `;
            tableBody.appendChild(row);
        });

        // Hiển thị thông báo khi fetch dữ liệu thành công
        if (data.fulfillmentText) {
            const fulfillmentText = data.fulfillmentText;
            const notification = document.createElement('div');
            notification.innerHTML = `<p style="color: green; font-weight: bold;">${fulfillmentText}</p>`;
            document.getElementById('loading').appendChild(notification);
        }
    })
    .catch(error => {
        console.error('Error fetching data:', error);
        document.getElementById('loading').innerHTML = "Failed to load data";
    });
