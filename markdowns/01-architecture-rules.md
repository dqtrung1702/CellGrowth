# Greenfield Architecture Rules

File nay la bo quy tac kien truc cho du an moi duoc build tu tai lieu BA.

## Nguyen tac cot loi

1. Kien truc phai phuc vu requirement, khong phai phuc vu so thich cong nghe.
2. Uu tien MVP giai quyet dung bai toan truoc, sau do moi toi uu scale.
3. Moi boundary phai ro ownership.
4. External dependency phai co adapter va strategy thay the.
5. Business rule phai song o tang de test va de tien hoa.

## Cach chon hinh thai kien truc

Chon dua tren:

- do phuc tap domain
- luong giao dich
- muc tieu release
- nang luc team
- constraint van hanh

Thong thuong:

- MVP thuong nen bat dau bang modular monolith neu chua co ly do rat manh cho microservice.
- Tach service som chi khi co boundary domain, ownership team, scale, hoac compliance ro rang.

## Boundary bat buoc

1. Presentation layer
2. Application or use-case layer
3. Domain layer
4. Data access layer
5. Integration adapter layer
6. Cross-cutting concerns

## Trach nhiem tung tang

### Presentation

- nhan request
- validate shape co ban
- map request vao use case
- map result thanh response

### Application or use-case

- dieu phoi flow
- ap dung process logic
- khong chua chi tiet storage hay framework

### Domain

- entity
- value object
- business invariant
- domain service

### Data access

- luu tru
- query
- transaction boundary

### Integration adapter

- email
- payment
- cloud storage
- queue
- OCR
- AI
- he thong ngoai

## Rules cho greenfield project

1. Khong de framework chi pho toan bo business rule.
2. Khong cho phep import-time side effect kho test.
3. Khong de contract public va schema bi truot khoi business rule.
4. Auth, authz, audit, validation, cache, va idempotency phai duoc thiet ke co y thuc neu use case can.
5. Log va metric phai du duoc de van hanh MVP trong production.

## Chon data va consistency

1. Chot source of truth cho tung object.
2. Chot pattern tao ID, uniqueness, va referential integrity.
3. Neu co queue hoac async job, phai xac dinh:
   - retry
   - idempotency
   - dead-letter strategy
4. Neu co cache, phai xac dinh owner, TTL, va invalidation.

## Security baseline

1. Secret phai luu qua config an toan.
2. Password, token, credential phai fail fast neu crypto backend loi.
3. Role, permission, va data access phai co model ro rang neu BA co phan quyen.
4. Input validation va output sanitization phai duoc xac dinh tu som.
5. Audit trail phai co neu bai toan lien quan approval, tai chinh, PII, hoac thao tac quan trong.

## Delivery baseline

1. Moi project moi phai co:
   - cach run local
   - cach test
   - cach build
   - cach config
   - cach release
2. Moi thay doi boundary quan trong phai cap nhat doc.
3. Agent phai uu tien scaffold de team co the tiep tuc phat trien, khong chi patch mot diem.
