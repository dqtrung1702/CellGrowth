# Kiến trúc tổng quan

```mermaid
flowchart LR
    Browser[[Client Browser]]
    FE[Frontend Server\nFlask @5003]
    UAA[UAA Service\nFlask @8082]
    Redis[(Redis TLS @6380\nDocker Compose)]
    PG[(PostgreSQL @5432)]

    Browser -->|HTTP (views/api)| FE
    FE -->|JWT login/refresh| UAA
    UAA -->|RBAC/Auth APIs| FE
    UAA -->|Sessions| Redis
    UAA -->|SQL queries| PG
```

## Diễn giải
- **Frontend Server** (Flask) cung cấp UI/API cho người dùng, gọi UAA để xác thực & nhận JWT.
- **UAA** xử lý đăng nhập, session server-side (Redis) và kiểm tra quyền truy cập trước khi trả dữ liệu.
- **Redis** chạy trong container qua `infra/redis/docker-compose.yml`, dùng TLS và mật khẩu `123456@`.
- **PostgreSQL** phục vụ dữ liệu ứng dụng/UAA (mặc định `localhost:5432`, DB `dev`, user/pass `admin`).
- Script **`run.sh`** tại repo root khởi động lần lượt Redis → UAA → Frontend; log lưu trong `logs/`.

## Đường dẫn liên quan
- `run.sh` — orchestration script.
- `infra/redis/` — cấu hình Redis, TLS certs, docker-compose.
- `uaa/` — dịch vụ UAA (Flask).
- `frontend/server/` — backend frontend (Flask).
