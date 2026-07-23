# Code Conventions For New Projects

File nay la bo quy tac code chung khi khoi tao du an moi. Neu sau nay repo co style guide rieng duoc phe duyet, style guide cua repo se ghi de mot phan file nay.

## Nguyen tac

1. Scaffold de doi ngu co the phat trien tiep.
2. Uu tien ro nghia hon meo ky thuat.
3. Business term phai thong nhat tu BA doc den code.
4. Moi module phai co trach nhiem ro.
5. Testability la yeu cau mac dinh, khong phai phan thu them.

## Naming

1. Dat ten theo domain va use case.
2. Khong dat ten mo ho nhu `temp`, `misc`, `helper_new`, `final2`.
3. API, command, event, entity, DTO, form model nen dat ten phan biet ro.
4. Boolean nen doc duoc thanh menh de.

## Structure

1. Moi feature nen co boundary ro hon la chi chia theo loai file.
2. Neu du an nho, co the dung modular monolith va chia module theo domain.
3. Neu du an lon, van phai giu ownership ro rang, tranh cross-import tuy tien.
4. Constructor va module init khong nen co side effect kho test.

## Error handling

1. Error model phai nhat quan.
2. Khong swallow exception ma khong co xu ly ro.
3. User-facing message va operator-facing detail nen tach ro.
4. Retry chi duoc dung cho loi phu hop va phai co gioi han.

## Contract

1. BA term, API field, database concept, va UI label quan trong nen dong bo y nghia.
2. Neu co mapping ten khac nhau giua cac tang, phai co ly do ro.
3. Contract public phai duoc tai lieu hoa va test.

## Test

1. Moi module quan trong phai co test happy path va error path.
2. Test ten theo hanh vi.
3. Fixture, fake, va mock phai don gian va de hieu.
4. Test command phai on dinh va tai lieu hoa ngay tu luc scaffold.

## Documentation

1. Project moi phai co:
   - run guide
   - config guide
   - test guide
   - architecture overview
2. Moi boundary quan trong phai co note ngan.
3. Doc phai cap nhat cung luc voi contract.
