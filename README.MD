# Hướng dẫn chạy nhanh

`run.sh` ở thư mục gốc giúp khởi động trọn bộ:
- Redis dùng TLS qua Docker Compose (`infra/redis/docker-compose.yml`)
- UAA (Flask) tại port 8082
- Frontend server tại port 5003

## Yêu cầu
- Docker và Docker Compose plugin (`docker compose`)
- Python 3; nếu có `venv/bin/python` sẽ được ưu tiên.

## Khởi động
```bash
./run.sh
```
Script sẽ:
1. Sinh chứng chỉ TLS trong `infra/redis/certs` nếu chưa có.
2. `docker compose up -d redis`.
3. Chạy `uaa/main.py` và `frontend/server/main.py`, ghi log vào `logs/uaa.log` và `logs/frontend-server.log`.

## Kiểm tra nhanh
- Redis: `redis-cli -h 127.0.0.1 -p 6380 --tls --cacert infra/redis/certs/ca.crt -a '123456@' PING`
- UAA: mở `http://localhost:8082/status` (hoặc `ping/health` tùy route).
- Frontend server: `http://localhost:5003/`

## Dừng dịch vụ
```bash
docker compose -f infra/redis/docker-compose.yml down
kill $(cat logs/uaa.pid) $(cat logs/frontend-server.pid)
```

## Nhật ký
- `logs/uaa.log`
- `logs/frontend-server.log`

## Ghi chú
- Certs chỉ sinh lần đầu; xóa `infra/redis/certs` nếu muốn tạo lại.
- Mặc định cấu hình Redis TLS: host `127.0.0.1`, port `6380`, password `123456@`.
