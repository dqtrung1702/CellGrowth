# Greenfield Build Prompt Pack

Bo file nay duoc thiet ke de ket hop voi tai lieu BA va build mot du an phan mem moi.

## Muc tieu

- Chuyen BA doc thanh blueprint ky thuat co the thi cong.
- Giu requirement, kien truc, convention, va acceptance criteria lien mach.
- Ho tro nhieu agent phoi hop thay vi chi sua mot codebase co san.

## Workflow de xuat

1. Doc `00-ba-intake.md`
   - muc dich: chuan hoa BA requirement, actor, use case, business rule, NFR, MVP
2. Doc `01-architecture-rules.md`
   - muc dich: chot nguyen tac kien truc cho du an moi
3. Doc `06-code-conventions.md`
   - muc dich: chot quy tac code chung ngay tu dau
4. Chon agent theo vai tro:
   - `02-system-architect-agent.md`
   - `03-backend-agent.md`
   - `04-frontend-agent.md`
   - `05-qa-acceptance-agent.md`
5. Neu can cat pha delivery, doc `07-delivery-planning-agent.md`

## Cach dung bo file nay voi BA doc

1. Nap BA doc va trich requirement theo `00-ba-intake.md`
2. Tao solution blueprint bang `02-system-architect-agent.md`
3. Tao backlog ky thuat theo module va use case
4. Giao implementation cho backend va frontend agents
5. Dung QA acceptance agent de doi chieu voi acceptance criteria

## Nguyen tac

1. Khong nhay thang vao code khi BA doc chua du ro cho MVP.
2. Khong over-engineer o pha dau.
3. Khong bo qua auth, permission, audit, va NFR neu BA da nhac toi.
4. Moi output cua agent phai co the giao tiep duoc cho agent ke tiep.
