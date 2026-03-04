# Mongo Stack (infra/mongo)

## Thành phần
- `docker-compose.yml`: chạy MongoDB 7.0 trên `localhost:27017`.
  - Biến môi trường (có giá trị mặc định):
    - `MONGO_ROOT_USERNAME` (admin)
    - `MONGO_ROOT_PASSWORD` (admin)
    - `MONGO_APP_DB` (dev) — DB ứng dụng và cũng là DB seed.
- `init/01_seed_person.sh`: script seed chạy tự động khi container khởi tạo lần đầu
  - Tạo index unique `Code_Idx` trên collection `person`
  - Seed danh mục tỉnh/thành (64 tỉnh/thành VN) vào collection `provinces` (upsert theo `Code`)
  - Seed danh mục loại điện thoại (Mobile/Home/Work) vào collection `phonetype` (upsert theo `Code`)

## Khởi chạy nhanh
```bash
cd infra/mongo
docker compose up -d
```

> Lưu ý: file `.env` trong thư mục này đã khai sẵn:
> ```
> MONGO_ROOT_USERNAME=admin
> MONGO_ROOT_PASSWORD=admin
> MONGO_APP_DB=dev
> ```
> Sửa trực tiếp file `.env` nếu muốn đổi thông số, không cần `export` thủ công.

## Tùy chỉnh cấu hình
```bash
export MONGO_ROOT_USERNAME=your_admin
export MONGO_ROOT_PASSWORD=your_password
export MONGO_APP_DB=your_db
docker compose up -d
```

## Dừng / xóa
```bash
docker compose down         # dừng
docker compose down -v      # dừng và xóa volume dữ liệu
```

## Kết nối thử
```bash
mongosh "mongodb://admin:admin@localhost:27017/dev?authSource=admin"
```

## Ghi chú
- Script seed chỉ chạy lần đầu khi volume dữ liệu trống. Muốn chạy lại, xóa volume hoặc xóa các collection liên quan rồi khởi động lại.
