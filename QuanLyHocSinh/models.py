import random
from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship
from flask_login import UserMixin, LoginManager
from QuanLyHocSinh import db, app

from werkzeug.security import generate_password_hash, check_password_hash
class User(db.Model,UserMixin):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    gender = Column(String(10))
    DOB = Column(DateTime)
    email = Column(String(50),unique=True)
    phoneNumber = Column(String(11),unique=True)
    userName = Column(String(50), unique=True)
    password = Column(String(500))
    verification_code = Column(String(10), nullable=True)
    type = Column(String(50))  # Phân biệt loại người dùng
    staffs = relationship('Staff', backref='user', cascade="all, delete-orphan", lazy=True, passive_deletes=True)
    teachers = relationship('Teacher', backref='user', cascade="all, delete-orphan", lazy=True, passive_deletes=True)
    admins = relationship('Administrator', backref='user', cascade="all, delete-orphan", lazy=True, passive_deletes=True)

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': type
    }

class Administrator(User):
    __tablename__ = 'administrator'
    id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)  # ForeignKey với ondelete
    adminRole = Column(String(20))
    __mapper_args__ = {
        'polymorphic_identity': 'administrator',
        'inherit_condition': id == User.id
    }


class Staff(User):
    __tablename__ = 'staff'
    id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    staffRole = Column(String(20))
    __mapper_args__ = {
        'polymorphic_identity': 'staff',
        'inherit_condition': id == User.id
    }


class Teacher(User):
    __tablename__ = 'teacher'
    id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    yearExperience = Column(Integer)
    subjectID = Column(Integer, ForeignKey('subject.id'), nullable=True)  # Đặt nullable tại đây
    teaches = relationship('Teach', backref='teacher_teach', lazy=True, cascade="all, delete")
    __mapper_args__ = {
        'polymorphic_identity': 'teacher',
        'inherit_condition': id == User.id
    }



class Grade(db.Model):
    __tablename__ = 'grade'
    id = Column(Integer, primary_key=True, autoincrement=True)
    gradeName = Column(String(20), nullable=False)
    classes = relationship('Class', backref='grade_class', lazy=True, cascade="all, delete")


class ClassRule(db.Model):
    __tablename__ = 'classRule'
    id = Column(Integer, primary_key=True, autoincrement=True)
    maxNoStudent = Column(Integer, nullable=False)
    classes = relationship('Class', backref='classRule_class', lazy=True, cascade="all, delete")


class Class(db.Model):
    __tablename__ = 'class'
    id = Column(Integer, primary_key=True, autoincrement=True)
    className = Column(String(20), nullable=False)
    classRuleID = Column(Integer, ForeignKey(ClassRule.id), nullable=False)
    gradeID = Column(Integer, ForeignKey(Grade.id,ondelete='CASCADE'), nullable=False)
    teaches = relationship('Teach', backref='class_teach', lazy=False, cascade="all, delete")

    # Quan hệ nhiều-nhiều với Student
    students = relationship('StudentClass', backref='classes_students', lazy=True,cascade="all, delete")


class StudentClass(db.Model):
    __tablename__ = 'student_class'
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('student.id'), nullable=False)
    class_id = Column(Integer, ForeignKey('class.id'), nullable=False)
    semester_id = Column(Integer, ForeignKey('semester.id'),nullable=False)
    # Đảm bảo rằng mỗi học sinh chỉ có thể tham gia một lớp một lần
    __table_args__ = (db.UniqueConstraint('student_id','semester_id', name='unique_student_class'),)


class Teach(db.Model):
    __tablename__ = 'teach'
    id = Column(Integer, primary_key=True, autoincrement=True)
    teacherID = Column(Integer, ForeignKey(Teacher.id, ondelete='CASCADE'), nullable=False)
    classID = Column(Integer, ForeignKey(Class.id, ondelete='CASCADE'), nullable=False)


class StudentRule(db.Model):
    __tablename__ = 'studentRule'
    id = Column(Integer, primary_key=True, autoincrement=True)
    maxAge = Column(Integer, nullable=False)
    minAge = Column(Integer, nullable=False)
    students = relationship('Student', backref='studentRule_student', lazy=True, cascade="all, delete")


class Student(db.Model):
    __tablename__ = 'student'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    gender = Column(String(10))
    DOB = Column(DateTime)
    address = Column(String(200))
    phone = Column(String(11),unique=True)
    email = Column(String(70),unique=True)
    stuRuleID = Column(Integer, ForeignKey(StudentRule.id,ondelete='CASCADE'), nullable=False)
    points = relationship('Point', backref='student_point', lazy=True, cascade="all, delete")

    # Quan hệ nhiều-nhiều với Class
    classes = relationship('StudentClass', backref='students_classes', lazy=True,cascade="all, delete")



class Subject(db.Model):
    __tablename__ = 'subject'
    id = Column(Integer, primary_key=True, autoincrement=True)
    subjectName = Column(String(50), nullable=False)
    subjectRequirement = Column(String(1000))
    subjectDescription = Column(String(1500))
    teachers = relationship('Teacher', backref='subject_teacher', lazy=True, cascade="all, delete")
    points = relationship('Point', backref='subject_point', lazy=True, cascade="all, delete")


class Semester(db.Model):
    __tablename__ = 'semester'
    id = Column(Integer, primary_key=True, autoincrement=True)
    semesterName = Column(String(15), nullable=False)
    year = Column(String(30), nullable=False)
    points = relationship('Point', backref='semester_point', lazy=True, cascade="all, delete")
    # Quan hệ 1-n với StudentClass
    student_classes = relationship('StudentClass', backref='semester_stuClass', lazy=True, cascade="all, delete")

class PointType(db.Model):
    __tablename__ = 'pointtype'
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(30), nullable=False)
    points = relationship('Point', backref='pointType_point', lazy=True, cascade="all, delete")


class Point(db.Model):
    __tablename__ = 'point'
    id = Column(Integer, primary_key=True, autoincrement=True)
    pointValue = Column(Float, nullable=False)
    pointTypeID = Column(Integer, ForeignKey(PointType.id), nullable=False)
    semesterID = Column(Integer, ForeignKey(Semester.id,ondelete='CASCADE'), nullable=False)
    subjectID = Column(Integer, ForeignKey(Subject.id,ondelete='CASCADE'), nullable=False)
    studentID = Column(Integer, ForeignKey(Student.id,ondelete='CASCADE'), nullable=False)


def delete_user_by_id(user_id):
    try:
        # Tạo session
        session = db.session()

        # Lấy người dùng theo ID
        user = session.query(User).get(user_id)

        if not user:
            return None  # Người dùng không tồn tại

        # Xóa người dùng
        session.delete(user)
        session.commit()
        return user  # Trả về người dùng đã xóa
    except Exception as e:
        session.rollback()  # Rollback nếu có lỗi
        raise e
    finally:
        session.close()  # Đảm bảo đóng session sau khi xóa


# =================================Hàm thêm dữ liệu mẫu vào bảng=============================================
def seed_data():
    # Xóa dữ liệu cũ
    db.drop_all()
    db.create_all()

    # Thêm Grade mẫu
    grades = [Grade(gradeName=f"Lớp {i}") for i in range(10, 13)]
    db.session.add_all(grades)

    # Thêm ClassRule mẫu
    class_rules = [
        ClassRule(maxNoStudent=40),
    ]
    db.session.add_all(class_rules)

    # Thêm Class mẫu
    classes = [
        Class(className="10A", classRuleID=1, gradeID=1),
        Class(className="10B", classRuleID=1, gradeID=1),
        Class(className="10C", classRuleID=1, gradeID=1),
        Class(className="11A", classRuleID=1, gradeID=2),
        Class(className="11B", classRuleID=1, gradeID=2),
        Class(className="11C", classRuleID=1, gradeID=2),
        Class(className="12A", classRuleID=1, gradeID=3),
        Class(className="12B", classRuleID=1, gradeID=3),
        Class(className="12C", classRuleID=1, gradeID=3),

    ]
    db.session.add_all(classes)

    # Thêm StudentRule mẫu
    student_rules = [
        StudentRule(minAge=16, maxAge=20),
    ]
    db.session.add_all(student_rules)



    # Thêm Subject mẫu
    subjects = [
        Subject(subjectName="Toán"),
        Subject(subjectName="Vật lý"),
        Subject(subjectName="Hóa học"),
        Subject(subjectName="Sinh học"),
        Subject(subjectName="Tiếng Anh"),
        Subject(subjectName="Ngữ văn"),
        Subject(subjectName="Địa lý"),
        Subject(subjectName="Lịch sử"),
        Subject(subjectName="Giáo dục công dân"),
        Subject(subjectName="Thể dục"),

    ]
    db.session.add_all(subjects)

    # Thêm Semester mẫu
    semesters = [
        Semester(semesterName="Học kỳ 1", year="2022-2023"),
        Semester(semesterName="Học kỳ 2", year="2022-2023"),
        Semester(semesterName="Học kỳ 1", year="2023-2024"),
        Semester(semesterName="Học kỳ 2", year="2023-2024"),

    ]
    db.session.add_all(semesters)
    db.session.commit()

    # Danh sách tên mẫu
    names = [
        "Nguyễn Văn A", "Trần Thị B", "Lê Văn C", "Phạm Thị D",
        "Hoàng Văn E", "Vũ Thị F", "Đặng Văn G", "Ngô Thị H",
        "Bùi Văn I", "Đinh Thị J"
    ]

    # Danh sách giới tính
    genders = ["Nam", "Nữ"]

    # Thêm dữ liệu mẫu cho bảng Student
    students = []
    for i in range(1, 121):  # Tạo 120 học sinh (tối đa 15 học sinh * 9 lớp)
        name = random.choice(names) + f" {i}"  # Tạo tên duy nhất
        gender = random.choice(genders)
        dob = datetime(2010, 1, 1) + timedelta(days=random.randint(0, 365 * 18))  # Sinh từ 2005-2010
        address = f"Địa chỉ số {i}"
        phone = f"091{random.randint(1000000, 9999999)}"
        email = f"student{i}@gmail.com"
        stu_rule_id = 1

        student = Student(
            name=name,
            gender=gender,
            DOB=dob,
            address=address,
            phone=phone,
            email=email,
            stuRuleID=stu_rule_id
        )
        db.session.add(student)
        students.append(student)
    db.session.commit()

    # Thêm dữ liệu mẫu cho bảng StudentClass
    for semester_id in range(1, 5):  # 4 học kỳ
        for class_id in range(1, 10):  # 9 lớp
            student_count = random.randint(10, 15)  # Mỗi lớp có từ 10 đến 15 học sinh
            selected_students = random.sample(students, student_count)  # Chọn ngẫu nhiên học sinh cho lớp
            for student in selected_students:
                # Kiểm tra xem bản ghi đã tồn tại chưa
                existing_record = db.session.query(StudentClass).filter_by(
                    student_id=student.id,
                    semester_id=semester_id
                ).first()

                if not existing_record:  # Nếu chưa tồn tại thì thêm mới
                    student_class = StudentClass(
                        student_id=student.id,
                        class_id=class_id,
                        semester_id=semester_id
                    )
                    db.session.add(student_class)
    db.session.commit()
    # Thêm PointType mẫu
    point_types = [
        PointType(type="15 phút"),
        PointType(type="1 tiết"),
        PointType(type="Cuối kỳ"),
    ]
    db.session.add_all(point_types)

    # Thêm Point mẫu
    points_data = generate_points()

    # Lưu vào cơ sở dữ liệu
    db.session.add_all(points_data)

    try:
        db.session.commit()
        print("Data seeding successful!")
    except IntegrityError as e:
        db.session.rollback()
        print(f"Data seeding failed: {e}")


# ===================================Hàm chứa các thao tác thêm sửa xóa một phần tử trong bảng=============================


# Hàm tạo dữ liệu điểm cho học sinh
def generate_points():
    points = []
    for student_id in range(1, 121):  # Tổng cộng 90 học sinh
        for semester_id in range(1, 5):  # 2 học kỳ
            for subject_id in range(1, 11):  # 10 môn học
                # Số lượng bài kiểm tra 15 phút (từ 1 đến 5 bài)
                num_15min = random.randint(1, 5)
                # Tạo điểm cho các bài kiểm tra 15 phút
                for _ in range(num_15min):
                    # Tạo điểm với xác suất cao hơn cho điểm >= 5
                    if random.random() < 0.7:  # 70% xác suất điểm >= 5
                        point_15min = round(random.uniform(5, 10), 1)  # Sinh điểm từ 5 đến 10
                    else:
                        point_15min = round(random.uniform(1, 4), 1)  # Sinh điểm dưới 5
                    points.append(
                        Point(pointValue=point_15min, pointTypeID=1, semesterID=semester_id, subjectID=subject_id,
                              studentID=student_id))

                # Số lượng bài kiểm tra 1 tiết (từ 1 đến 3 bài)
                num_45min = random.randint(1, 3)
                # Tạo điểm cho các bài kiểm tra 1 tiết
                for _ in range(num_45min):
                    # Tạo điểm với xác suất cao hơn cho điểm >= 5
                    if random.random() < 0.7:  # 70% xác suất điểm >= 5
                        point_45min = round(random.uniform(5, 10), 1)  # Sinh điểm từ 5 đến 10
                    else:
                        point_45min = round(random.uniform(1, 4), 1)  # Sinh điểm dưới 5
                    points.append(
                        Point(pointValue=point_45min, pointTypeID=2, semesterID=semester_id, subjectID=subject_id,
                              studentID=student_id))

                # Điểm cuối kỳ (1 bài duy nhất, từ 1 đến 10 điểm)
                # Tạo điểm với xác suất cao hơn cho điểm >= 5
                if random.random() < 0.7:  # 70% xác suất điểm >= 5
                    point_final = round(random.uniform(5, 10), 1)  # Sinh điểm từ 5 đến 10
                else:
                    point_final = round(random.uniform(1, 4), 1)  # Sinh điểm dưới 5
                points.append(Point(pointValue=point_final, pointTypeID=3, semesterID=semester_id, subjectID=subject_id,
                                    studentID=student_id))

    return points






def create_admin():
    # Mã hóa thông tin
    username = "admin"  # Mã hóa tên đăng nhập "admin"
    hashed_password = generate_password_hash("123")  # Mã hóa mật khẩu

    # Tạo đối tượng User và Administrator
    admin_user = Administrator(
        name="Administrator",
        gender="Nam",
        DOB="1980-01-01",  # Ví dụ ngày sinh
        email="admin@example.com",
        phoneNumber="1234567890",
        userName=username,
        password=hashed_password,
        type="administrator",
        adminRole="Super Admin"  # Ví dụ vai trò admin
    )

    # Thêm vào cơ sở dữ liệu
    db.session.add(admin_user)
    db.session.commit()
    print("Admin user created successfully")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data()
        create_admin()