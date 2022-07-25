from flask_sqlalchemy import SQLAlchemy
from datetime import date
db = SQLAlchemy()
class sqlexec:
    '''func json() để trả ra dữ liệu cho query select./ update, delete bằng sql chưa có'''    
    def __init__(self, sql):
        self.sql = sql
    def json(self):
        record = db.engine.execute(self.sql).mappings().all()
        result = []
        for row in record:
            line = {}
            for key,val in row.items():
                value = val.strftime('%Y-%m-%d,%H:%M:%S') if isinstance(val, date) else str(val,'utf-8') if isinstance(val, bytes) else val                
                line.update({key:value}) 
            result.append(line)
        return result
class BaseModel(db.Model):
    """Base data model for all objects"""
    """Các hàm json, add, remove, update chỉ action trên từng bản ghi """
    """
    Các object không sử dụng foreign-key vì hệ thống viết theo kiến trúc microservice rất nhiều bảng chứa ID của bảng nằm trên service khác.
    Không có  foreign-key nên khi query cần join nhiều bảng thì viết câu query và chạy qua class sqlexec
    Mỗi lần deploy mà đồng bộ dữ liệu cũ xong cần cover lại đống seq sinh id của các bảng.
    """
    __abstract__ = True
    # def __init__(self, sql):
    #     self.sql = sql
    
    # def xquery(self):
    #     record = db.engine.execute(self.sql).mappings().all()
    #     result = []
    #     for row in record:
    #         line = {}
    #         for key,val in row.items():
    #             value = val.strftime('%Y-%m-%d,%H:%M:%S') if isinstance(val, date) else str(val,'utf-8') if isinstance(val, bytes) else val                
    #             line.update({key:value}) 
    #         result.append(line)
    #     return result

    def json(self):
        """Define a base way to jsonify models, dealing with datetime objects"""
        r = {}
        for item in self.__dict__:
            if item != '_sa_instance_state':
                column = item
                value = self.__dict__[item].strftime('%Y-%m-%d,%H:%M:%S') if isinstance(self.__dict__[item], date) else str(self.__dict__[item],'utf-8') if isinstance(self.__dict__[item], bytes) else self.__dict__[item]
                r.update({column:value})        
        return r
    def add(self):
        db.session.add(self)
        db.session.commit()
        return self.id

    def remove(self):
        db.session.delete(self)
        db.session.commit()
        return self.id

    def update(self, dict: dict):
        for key, value in dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()
        return self.id
class UserDefine(BaseModel, db.Model):
    """Model for the UserDefine table"""
    
    """
    User - Role - Permission -> phân quyền chức năng
        ex: 
            1.Trung - Admin, Employee -> Monitor UAA, Common Setup, Self Service
            2.Phao - Recruitment Management, Recruitment Operation, Employee -> Recruitment Setup, Monitor Recruitment, Self Service
            3.Vân - Person Management, Person Operation, Manager, Employee -> Department Setup, Profile Setup, JobData Setup, Labour Protection Setup, PayRoll Setup, Peron Service, Self Service
            4.Hường - PayRoll Management, Manager, Employee  -> PayRoll Setup, Employee Service, Self Service
            5.Trang - Accouting Management, Employee -> Accouting Setup, Self Service
            6.Thảo - Accouting Operation -> Monitor Accouting
    User - DataPermission -> phân quyền dữ liệu
        1 user - 1 data permission -< data permission quyết định user được access tới những dữ liệu nào
    """
    # Tạo bảng UserDefine 
    __tablename__ = 'UserDefine'
    __table_args__ = {"schema": "uaa"}

    id = db.Column(db.Integer, primary_key = True, nullable=False)
    UserName = db.Column(db.String(50), nullable=False, unique=True,default='False')
    PersonId = db.Column(db.Integer)
    Password = db.Column(db.LargeBinary(500), nullable=False)
    UserLocked = db.Column(db.Boolean,default=False)
    NameDisplay = db.Column(db.String(100))
    LastSignOnDateTime = db.Column(db.DateTime)
    LastUpdateUserName = db.Column(db.String(50))
    LastUpdateDateTime = db.Column(db.DateTime)
    # def __init__(self, id, UserName, PersonId, DataPermission, Password, UserLocked, NameDisplay, LastSignOnDateTime, LastUpdateUserName, LastUpdateDateTime):
        # self.id = id
        # self.UserName = UserName
        # self.PersonId = PersonId
        # self.DataPermission = DataPermission
        # self.Password = Password
        # self.UserLocked = UserLocked
        # self.NameDisplay = NameDisplay
        # self.LastSignOnDateTime = LastSignOnDateTime
        # self.LastUpdateUserName = LastUpdateUserName
        # self.LastUpdateDateTime = LastUpdateDateTime       
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        # return f"<UserName {self.UserName}, Password {self.Password}>"
        r = ''
        for item in self.__dict__:
            column = item
            value = self.__dict__[item] if not isinstance(self.__dict__[item], date) else self.__dict__[item].strftime('%Y-%m-%d,%H:%M:%S')
            r += f'\n{column} = {value}'
        return r

class RoleDefine(BaseModel, db.Model):
    """Model for the RoleDefine table"""
    # Tạo bảng RoleDefine 
    __tablename__ = 'RoleDefine'
    __table_args__ = {"schema": "uaa"}

    id = db.Column(db.Integer, primary_key = True, nullable=False)
    Code = db.Column(db.String(50), nullable=False, unique=True)    
    Description = db.Column(db.String(150))
    LastUpdateUserName = db.Column(db.String(50))
    LastUpdateDateTime = db.Column(db.DateTime)    
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        r = ''
        for item in self.__dict__:
            column = item
            value = self.__dict__[item] if not isinstance(self.__dict__[item], date) else self.__dict__[item].strftime('%Y-%m-%d,%H:%M:%S')
            r += f'\n{column} = {value}'
        return r
class PermissionDefine(BaseModel, db.Model):
    """Model for the PermissionDefine table"""
    # Tạo bảng PermissionDefine 
    __tablename__ = 'PermissionDefine'
    __table_args__ = {"schema": "uaa"}

    id = db.Column(db.Integer, primary_key = True, nullable=False)
    Code = db.Column(db.String(50), nullable=False, unique=True)
    PermissionType = db.Column(db.String(50), nullable=False)
    Description = db.Column(db.String(150))
    LastUpdateUserName = db.Column(db.String(50))
    LastUpdateDateTime = db.Column(db.DateTime)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        r = ''
        for item in self.__dict__:
            column = item
            value = self.__dict__[item] if not isinstance(self.__dict__[item], date) else self.__dict__[item].strftime('%Y-%m-%d,%H:%M:%S')
            r += f'\n{column} = {value}'
        return r
class UserRole(BaseModel, db.Model):
    """Model for the UserRole table"""
    # Tạo bảng UserRole 
    __tablename__ = 'UserRole'
    __table_args__ = {"schema": "uaa"}

    id = db.Column(db.Integer, primary_key = True, nullable=False)
    UserId = db.Column(db.Integer, nullable=False)  
    RoleId = db.Column(db.Integer, nullable=False)
    Description = db.Column(db.String(100))
    LastUpdateUserName = db.Column(db.String(50))
    LastUpdateDateTime = db.Column(db.DateTime)    
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        r = ''
        for item in self.__dict__:
            column = item
            value = self.__dict__[item] if not isinstance(self.__dict__[item], date) else self.__dict__[item].strftime('%Y-%m-%d,%H:%M:%S')
            r += f'\n{column} = {value}'
        return r
class RolePermission(BaseModel, db.Model):
    """Model for the RolePermission table"""
    # Tạo bảng RolePermission 
    __tablename__ = 'RolePermission'
    __table_args__ = {"schema": "uaa"}

    id = db.Column(db.Integer, primary_key = True, nullable=False)
    RoleId = db.Column(db.Integer, nullable=False)
    PermissionId = db.Column(db.Integer, nullable=False)
    Description = db.Column(db.String(100))
    LastUpdateUserName = db.Column(db.String(50))
    LastUpdateDateTime = db.Column(db.DateTime)    
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        r = ''
        for item in self.__dict__:
            column = item
            value = self.__dict__[item] if not isinstance(self.__dict__[item], date) else self.__dict__[item].strftime('%Y-%m-%d,%H:%M:%S')
            r += f'\n{column} = {value}'
        return r
class SetTbl(BaseModel, db.Model):
    """Model for the SetTbl table"""
    """
    Những dữ liệu masterdata cần giới hạn truy xuất của user sẽ tạo các bộ dữ liệu(set) các Set này có thể dùng chung hoặc riêng bằng cách gán vào các DataPermission
    """
    # Tạo bảng SetTbl 
    __tablename__ = 'SetTbl'
    __table_args__ = {"schema": "uaa"}

    id = db.Column(db.Integer, primary_key = True, nullable=False)
    EFFFDate = db.Column(db.Date,default=date.today())
    EFFTDate = db.Column(db.Date)
    BUId = db.Column(db.Integer)
    Type = db.Column(db.String(10))
    Code = db.Column(db.String(50), nullable=False, unique=True)
    Description = db.Column(db.String(150))
    LastUpdateUserName = db.Column(db.String(50))
    LastUpdateDateTime = db.Column(db.DateTime)    
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        r = ''
        for item in self.__dict__:
            column = item
            value = self.__dict__[item] if not isinstance(self.__dict__[item], date) else self.__dict__[item].strftime('%Y-%m-%d,%H:%M:%S')
            r += f'\n{column} = {value}'
        return r
class BU(BaseModel, db.Model):
    """Model for the BU table"""
    """
    BU chỉ ra cách tổ chức cấu trúc của công ty, doanh nghiệp một cách logic, dữ liệu được phân chia theo cấu trúc BU.
    """
    # Tạo bảng BU 
    __tablename__ = 'BU'
    __table_args__ = {"schema": "uaa"}

    id = db.Column(db.Integer, primary_key = True, nullable=False)
    xCode = db.Column(db.String(50), nullable=False, unique=True)
    Description = db.Column(db.String(150))
    LastUpdateUserName = db.Column(db.String(50))
    LastUpdateDateTime = db.Column(db.DateTime)    
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        r = ''
        for item in self.__dict__:
            column = item
            value = self.__dict__[item] if not isinstance(self.__dict__[item], date) else self.__dict__[item].strftime('%Y-%m-%d,%H:%M:%S')
            r += f'\n{column} = {value}'
        return r
class URLPermission(BaseModel, db.Model):
    """Model for the URLPermission table"""
    # Tạo bảng RolePermission 
    __tablename__ = 'URLPermission'
    __table_args__ = {"schema": "uaa"}

    id = db.Column(db.Integer, primary_key = True, nullable=False)
    PermissionId = db.Column(db.Integer, nullable=False)
    url = db.Column(db.String(150), nullable=False)
    EFFFDate = db.Column(db.Date,default=date.today())
    EFFTDate = db.Column(db.Date)
    Method = db.Column(db.String(10))
    Description = db.Column(db.String(100))
    Type = db.Column(db.String(10))
    LastUpdateUserName = db.Column(db.String(50))
    LastUpdateDateTime = db.Column(db.DateTime)    
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        r = ''
        for item in self.__dict__:
            column = item
            value = self.__dict__[item] if not isinstance(self.__dict__[item], date) else self.__dict__[item].strftime('%Y-%m-%d,%H:%M:%S')
            r += f'\n{column} = {value}'
        return r
class DataPermission(BaseModel, db.Model):
    """Model for the DataPermission table"""
    # Tạo bảng DataPermission 
    __tablename__ = 'DataPermission'
    __table_args__ = {"schema": "uaa"}

    id = db.Column(db.Integer, primary_key = True, nullable=False)
    UserId = db.Column(db.Integer, nullable=False)
    PermissionId = db.Column(db.Integer, nullable=False)
    Description = db.Column(db.String(100))
    LastUpdateUserName = db.Column(db.String(50))
    LastUpdateDateTime = db.Column(db.DateTime)    
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        r = ''
        for item in self.__dict__:
            column = item
            value = self.__dict__[item] if not isinstance(self.__dict__[item], date) else self.__dict__[item].strftime('%Y-%m-%d,%H:%M:%S')
            r += f'\n{column} = {value}'
        return r
class DataSet(BaseModel, db.Model):
    """Model for the DataPermission table"""
    # Tạo bảng DataSet 
    __tablename__ = 'DataSet'
    __table_args__ = {"schema": "uaa"}

    id = db.Column(db.Integer, primary_key = True, nullable=False)
    DataPermissionId = db.Column(db.Integer, nullable=False)
    SetId = db.Column(db.Integer, nullable=False)
    Description = db.Column(db.String(100))
    LastUpdateUserName = db.Column(db.String(50))
    LastUpdateDateTime = db.Column(db.DateTime)    
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        r = ''
        for item in self.__dict__:
            column = item
            value = self.__dict__[item] if not isinstance(self.__dict__[item], date) else self.__dict__[item].strftime('%Y-%m-%d,%H:%M:%S')
            r += f'\n{column} = {value}'
        return r
"""Note:
    Query sample:
        peter = User.query.filter_by(username='peter').first()
        missing = User.query.filter_by(username='missing').first()
        User.query.filter(User.email.endswith('@example.com')).all()
        User.query.order_by(User.username).all()
        User.query.order_by(User.id).limit(10).offset(0)
        User.query.limit(1).all()
        User.query.get(1)
        @app.route('/user/<username>')
        def show_user(username):
            user = User.query.filter_by(username=username).first_or_404()
            return render_template('show_user.html', user=user)
        User.query.filter_by(username=username).first_or_404(description='There is no data with {}'.format(username))
"""