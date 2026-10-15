# PTIT CareerHub Frontend

## Chạy frontend

```powershell
npm install
Copy-Item .env.example .env
npm run dev
```

Từ thư mục gốc dự án, có thể chạy cả frontend và backend LAN bằng:

```powershell
.\start-lan.ps1
```

Frontend hiện được cấu hình gọi Backend tại `VITE_API_BASE_URL`. File `.env` đang dùng:

```env
VITE_API_BASE_URL=http://192.168.1.93:8000/api/v1
```

Sau khi sửa `.env`, cần dừng và chạy lại Vite vì biến môi trường được nạp lúc khởi động.

## Chạy Backend Django

Lỗi `net::ERR_CONNECTION_REFUSED` nghĩa là trình duyệt không kết nối được tới `localhost:8000`; đây là lỗi tiến trình Backend chưa chạy hoặc đang chạy ở cổng khác, không phải lỗi route React. Trong thư mục Backend Django, chạy lệnh tương đương:

```powershell
python manage.py runserver 0.0.0.0:8000
```

Trên máy chạy dự án, mở `http://192.168.1.93:5173`. Các laptop cùng mạng mở cùng địa chỉ này; API nằm tại `http://192.168.1.93:8000/api/v1/`.

Nếu Django chạy ở máy/LAN khác, đổi `.env` thành đúng địa chỉ đó, ví dụ `http://192.168.1.93:8000/api/v1`, rồi restart Vite. Backend cũng phải cho phép origin frontend (`http://localhost:5173`) trong CORS.

Kiểm tra nhanh endpoint:

```powershell
Invoke-WebRequest http://192.168.1.93:8000/api/v1/health/
```

Nếu lệnh này vẫn báo không kết nối được, hãy khởi động Backend hoặc sửa port/base URL trước khi mở `/jobs/1`.

## Build

```powershell
npm run build
```

API mapping và các phần chưa xác minh được ghi trong `docs/API_INTEGRATION.md` và `docs/API_GAPS.md`.

## Cấu trúc repository

Mở frontend trên máy chạy dự án tại `http://192.168.1.93:5173`; các laptop cùng mạng có thể dùng cùng địa chỉ này. API chạy tại `http://192.168.1.93:8000/api/v1/`.
