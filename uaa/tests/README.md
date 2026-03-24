# Test Guide (pytest)

## Cấu trúc
- `tests/` chứa các unit test hiện có:
  - `test_auth_service.py`
  - `test_access_request_service.py`
  - `test_middleware.py`

## Chuẩn bị môi trường
1. Kích hoạt venv (nếu có):
   ```bash
   cd /home/CellGrowth
   source venv/bin/activate
   ```
2. Cài pytest (nếu chưa có):
   ```bash
   pip install pytest
   ```
3. Biến môi trường để bỏ qua healthcheck DB/Redis khi chạy test:
   ```bash
   export UAA_SKIP_REDIS_HEALTHCHECK=1
   export UAA_SKIP_DB_INIT=1
   ```

## Chạy test
Từ thư mục `uaa/`:
```bash
cd /home/CellGrowth/uaa
PYTHONPATH=. pytest -q
```

## Lưu ý
- Các test hiện tại không cần DB/Redis thực, nhờ các biến `UAA_SKIP_REDIS_HEALTHCHECK` và `UAA_SKIP_DB_INIT`.
- Nếu thêm test yêu cầu DB, hãy dùng fixture riêng hoặc docker compose để khởi tạo dữ liệu, tránh phụ thuộc state thật.
- Với middleware test, có thể cần thêm `CONFIG_MODE=Testing` nếu bạn thay đổi cấu hình sau này.
