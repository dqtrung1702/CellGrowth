import pymongo
MONGO_URI = 'mongodb://10.14.119.40:27017/test'
person = pymongo.MongoClient(MONGO_URI).test

data = [
    {
        "Name": "An Giang",
        "Code": "AG"
    },
    {
        "Name": "Bà Rịa – Vũng Tàu",
        "Code": "BV"
    },
    {
        "Name": "Bạc Liêu",
        "Code": "BL"
    },
    {
        "Name": "Bắc Kạn",
        "Code": "BK"
    },
    {
        "Name": "Bắc Giang",
        "Code": "BG"
    },
    {
        "Name": "Bắc Ninh",
        "Code": "BN"
    },
    {
        "Name": "Bến Tre",
        "Code": "BT"
    },
    {
        "Name": "Bình Dương",
        "Code": "BD"
    },
    {
        "Name": "Bình Định",
        "Code": "BĐ"
    },
    {
        "Name": "Bình Phước",
        "Code": "BP"
    },
    {
        "Name": "Bình Thuận",
        "Code": "BTh"
    },
    {
        "Name": "Cà Mau",
        "Code": "CM"
    },
    {
        "Name": "Cao Bằng",
        "Code": "CB"
    },
    {
        "Name": "Cần Thơ",
        "Code": "CT"
    },
    {
        "Name": "Đà Nẵng",
        "Code": "ĐNa"
    },
    {
        "Name": "Đắk Lắk",
        "Code": "ĐL"
    },
    {
        "Name": "Đắk Nông",
        "Code": "ĐNo"
    },
    {
        "Name": "Điện Biên",
        "Code": "ĐB"
    },
    {
        "Name": "Đồng Nai",
        "Code": "ĐN"
    },
    {
        "Name": "Đồng Tháp",
        "Code": "ĐT"
    },
    {
        "Name": "Gia Lai",
        "Code": "GL"
    },
    {
        "Name": "Hà Giang",
        "Code": "HG"
    },
    {
        "Name": "Hà Nam",
        "Code": "HNa"
    },
    {
        "Name": "Hà Nội",
        "Code": "HN"
    },
    {
        "Name": "Hà Tĩnh",
        "Code": "HT"
    },
    {
        "Name": "Hải Dương",
        "Code": "HD"
    },
    {
        "Name": "Hải Phòng",
        "Code": "HP"
    },
    {
        "Name": "Hậu Giang",
        "Code": "HGi"
    },
    {
        "Name": "Hòa Bình",
        "Code": "HB"
    },
    {
        "Name": "Thành phố Hồ Chí Minh (tên cũ Sài Gòn)",
        "Code": "SG"
    },
    {
        "Name": "Hưng Yên",
        "Code": "HY"
    },
    {
        "Name": "Khánh Hòa",
        "Code": "KH"
    },
    {
        "Name": "Kiên Giang",
        "Code": "KG"
    },
    {
        "Name": "Kon Tum",
        "Code": "KT"
    },
    {
        "Name": "Lai Châu",
        "Code": "LC"
    },
    {
        "Name": "Lạng Sơn",
        "Code": "LS"
    },
    {
        "Name": "Lào Cai",
        "Code": "LCa"
    },
    {
        "Name": "Lâm Đồng",
        "Code": "LĐ"
    },
    {
        "Name": "Long An",
        "Code": "LA"
    },
    {
        "Name": "Nam Định",
        "Code": "NĐ"
    },
    {
        "Name": "Nghệ An",
        "Code": "NA"
    },
    {
        "Name": "Ninh Bình",
        "Code": "NB"
    },
    {
        "Name": "Ninh Thuận",
        "Code": "NT"
    },
    {
        "Name": "Phú Thọ",
        "Code": "PT"
    },
    {
        "Name": "Phú Yên",
        "Code": "PY"
    },
    {
        "Name": "Quảng Bình",
        "Code": "QB"
    },
    {
        "Name": "Quảng Nam",
        "Code": "QNa"
    },
    {
        "Name": "Quảng Ngãi",
        "Code": "QNg"
    },
    {
        "Name": "Quảng Ninh",
        "Code": "QN"
    },
    {
        "Name": "Quảng Trị",
        "Code": "QT"
    },
    {
        "Name": "Sóc Trăng",
        "Code": "ST"
    },
    {
        "Name": "Sơn La",
        "Code": "SL"
    },
    {
        "Name": "Tây Ninh",
        "Code": "TN"
    },
    {
        "Name": "Thái Bình",
        "Code": "TB"
    },
    {
        "Name": "Thái Nguyên",
        "Code": "TNg"
    },
    {
        "Name": "Thanh Hóa",
        "Code": "TH"
    },
    {
        "Name": "Thừa Thiên Huế",
        "Code": "TTH"
    },
    {
        "Name": "Tiền Giang",
        "Code": "TG"
    },
    {
        "Name": "Trà Vinh",
        "Code": "TV"
    },
    {
        "Name": "Tuyên Quang",
        "Code": "TQ"
    },
    {
        "Name": "Vĩnh Long",
        "Code": "VL"
    },
    {
        "Name": "Vĩnh Phúc",
        "Code": "VP"
    },
    {
        "Name": "Yên Bái",
        "Code": "YB"
    }
]
person.db.province.insert_many(data)
