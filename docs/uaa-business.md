# UAA service – mô tả nghiệp vụ (business view)

## Mục đích
UAA (User Authentication & Authorization) cung cấp:
- Xác thực người dùng (JWT).
- Phân quyền theo vai trò (Role/Permission) cho URL và trang UI.
- Phân quyền dữ liệu (Data Permission) ở mức bộ dữ liệu/điều kiện hàng.

## Thực thể chính
- User: thông tin đăng nhập, trạng thái khóa, tên hiển thị, tham chiếu DataPermissionId.
- Role: nhóm quyền chức năng.
- Permission:
  - ROLE: quyền truy cập URL hoặc trang.
  - DATA: quyền truy cập phạm vi dữ liệu.
- RolePermission: gán permission vào role.
- UserRole: gán role cho user.
- URLPermissions: ánh xạ permission (ROLE) -> URL + method (+ wildcard %).
- PagePermissions: ánh xạ permission (ROLE) -> đường dẫn trang (hiển thị menu).
- Set: tập định nghĩa phạm vi dữ liệu (Services, SetCode, SetName).
- Dataset: điều kiện chi tiết (Table, Column, Value) thuộc một Set.
- DataPermissions: gán Permission (DATA) với Set.

## Luồng nghiệp vụ
1) Đăng nhập / đăng ký:
   - `/login` tạo JWT chứa UserId, Role; lưu ở cookie `app_token`.
   - `/register` tạo user mới (không gán role mặc định).
2) Kiểm tra quyền URL:
   - Mọi request (trừ public `/login`,`/register`,`/status`,`/health`,`/ping`,`/static`) đi qua middleware `enforce_url_permission`.
   - Kiểm tra User -> UserRole -> RolePermission -> URLPermissions (method, pattern).
3) Hiển thị menu trang:
   - Frontend gọi `/getPageByUser`, nhận danh sách page từ PagePermissions để bật/tắt menu.
4) Kiểm soát dữ liệu:
   - User có `data_permission_id` (từ Permission type DATA).
   - API `_data_scope_filters` (RolePermission.py) lấy Set/Dataset để dựng điều kiện WHERE hoặc quyết định full/deny.
   - Frontend User list/detail cũng áp dụng lọc local theo scopes.
5) Quản trị:
   - Quản lý User/Role/Permission/Set/Dataset qua các endpoint tương ứng (CRUD).
   - Gán role cho user (`/updateUserRole`), gán permission cho role (`/updateRolePermission`), gán Set vào permission DATA (`/updateDataPermission`).

## Phân quyền chức năng (ROLE)
- Chỉ định qua URLPermissions (method + url, có hỗ trợ wildcard %).
- Menu hiển thị dựa vào PagePermissions.

## Phân quyền dữ liệu (DATA)
- Set = (Services, SetCode, SetName) là đơn vị scope.
- Dataset = (Table, Column, Value) chi tiết điều kiện (có thể dùng `*` để mở rộng).
- DataPermission = Permission(DATA) + Set -> gắn cho user qua `data_permission_id`.
- Wildcard `*` ở Column/Value cho phép full-access trên table; `*` toàn bộ cho phép full-access mọi dữ liệu.

## Seed mặc định
- `scripts/initadmin.sql`: user `admin` với role `Admin`, permission `ALL_ROLE` (ROLE), `FULL_DATA` (DATA) và scope `ALL/*/*/*`.
- `scripts/inituaa.sql`: user `uaa` (monitor), role `UAA_MONITOR`, quyền URL chỉ `/status|/health|/ping|/static/%`, scope hẹp (`UAA_DATA`) giới hạn vào dữ liệu UAA.

## Cấu hình chính
- JWT: `Config.JWT_SECRET`, `Config.JWT_ALGORITHM`.
- DB: PostgreSQL (xem `config.py`).
- Session: Redis (bắt buộc sống, kiểm tra khi start).

## Lỗi/điều kiện từ chối
- 401 khi thiếu/invalid token hoặc không có user id.
- 403 khi không khớp URLPermissions hoặc CSRF sai (frontend server).

## Frontend integration
- Cookie `app_token` gửi kèm mọi request.
- CSRF token được cài ở frontend server; UAA không yêu cầu CSRF.
- Menu và DataScope được load ở trang Home để cache vào session frontend.

## Phạm vi bảo trì
- Khi thêm API mới: cần seed URLPermissions (ROLE) tương ứng; nếu hiển thị trang mới, thêm PagePermissions.
- Khi bổ sung phân tầng dữ liệu: thêm Set/Dataset, gán vào Permission(DATA), cập nhật `data_permission_id` cho user cần truy cập.
