import sys
import base64
import json

d = {
    "user": [
        {
            "id": 2,
            "SetId": 1,
            "PersonId": None,
            "Password": "$2b$12$vDzOZFbZcVcUXsaeBZKTPex6BPL.eNqLzaoLFz0d.6OaakN8vhVSa",
            "NameDisplay": "administrator",
            "LastUpdateUserName": "numone",
            "DataPermission": 7,
            "UserName": "admin",
            "UserLocked": False,
            "LastSignOnDateTime": "2021-07-08,20:20:27",
            "LastUpdateDateTime": "2021-07-08,22:35:56"
        },
        {
            "id": 3,
            "SetId": 1,
            "PersonId": None,
            "Password": "$2b$12$86wig14c0c.CdbkpYAcMdeoTi6I.YObT5.fSMHLkoZWmbtqUfthIu",
            "NameDisplay": "Đặng Quang Trung",
            "LastUpdateUserName": "numone",
            "DataPermission": 7,
            "UserName": "trung.dang",
            "UserLocked": False,
            "LastSignOnDateTime": "2021-07-08,20:38:59",
            "LastUpdateDateTime": "2021-07-08,22:35:56"
        },
        {
            "id": 4,
            "SetId": 1,
            "PersonId": None,
            "Password": "$2b$12$NC29P52jRUuAuJ.dupaGSu5tgntsqTLMWVL1reLkNvPRKpDPwL1m.",
            "NameDisplay": "Nguyễn Thị Hường",
            "LastUpdateUserName": "numone",
            "DataPermission": 7,
            "UserName": "huong.nguyen",
            "UserLocked": False,
            "LastSignOnDateTime": "2021-07-08,20:38:59",
            "LastUpdateDateTime": "2021-07-08,22:35:56"
        },
        {
            "id": 5,
            "SetId": 1,
            "PersonId": None,
            "Password": "$2b$12$yVQONdB8Yp9YvcQLgYh/D.U7OXpZpvYFXH86fS0gTcNXUz2OC0VS2",
            "NameDisplay": "Cường Pháo",
            "LastUpdateUserName": "numone",
            "DataPermission": 7,
            "UserName": "phao",
            "UserLocked": False,
            "LastSignOnDateTime": "2021-07-08,20:39:02",
            "LastUpdateDateTime": "2021-07-08,22:35:57"
        },
        {
            "id": 1,
            "SetId": 1,
            "PersonId": None,
            "Password": "$2b$12$gzzGvT4VpBqL8LemRoaoVOCbx2hgyuV9jJ07HOcfSYubTvdmb4LR2",
            "NameDisplay": "hand of GOD",
            "LastUpdateUserName": "numone",
            "DataPermission": 0,
            "UserName": "numone",
            "UserLocked": False,
            "LastSignOnDateTime": "2021-07-09,05:37:08",
            "LastUpdateDateTime": "2021-07-08,07:06:39"
        }
    ],
    "status": "OK"
}
st = str(d)
enc = str(d).encode() 
s = json.dumps(d)
b = base64.encodestring(enc)
print(sys.getsizeof(d))
print(sys.getsizeof(st))
print(sys.getsizeof(enc))
print(sys.getsizeof(s))
print(sys.getsizeof(b))