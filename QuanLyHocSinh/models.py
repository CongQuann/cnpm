
from sqlalchemy import Column, Integer, String, Double, DateTime, Float, Boolean, ForeignKey, column,Enum
import enum
import random
from wtforms.fields.numeric import IntegerField
from sqlalchemy.exc import IntegrityError
from QuanLyHocSinh import db, app
from sqlalchemy.orm import relationship, backref
from datetime import datetime

class User(db.Model):
    __tablename__ = 'user'

    id = Column(Integer,primary_key=True,autoincrement=True)
    name = Column(String(50),nullable=False)
    gender = Column(String(10))
    DOB = Column(DateTime)
    email = Column(String(50))
    phoneNumber = Column(String(11))
    userName = Column(String(30))
    password = Column(String(30))
    admins = relationship('Administrator',backref='user_administrator',lazy=True,cascade="all, delete")
    staffs = relationship('Staff',backref='user_staff',lazy = True,cascade="all, delete")
    teachers = relationship('Teacher',backref='user_teacher',lazy=True,cascade="all, delete")

class Administrator(db.Model):
    __tablename__ = 'administrator'
    id = Column(Integer,primary_key=True,autoincrement=True)
    adminRole = Column(String(20))
    userID = Column(Integer, ForeignKey(User.id),nullable=False)

class Staff(db.Model):
    __tablename__ = 'staff'
    id = Column(Integer,primary_key=True,autoincrement=True)
    staffRole = Column(String(20))
    userID = Column(Integer, ForeignKey(User.id),nullable=False)

class Teacher(db.Model):
    __tablename__ = 'teacher'
    id = Column(Integer, primary_key=True, autoincrement=True)
    yearExperience = Column(Integer)
    userID = Column(Integer, ForeignKey(User.id),nullable=False)
    subjectID = Column(Integer,ForeignKey('subject.id'),nullable=True)
    teaches = relationship('Teach',backref='teacher_teach',lazy=True,cascade="all, delete")

class Grade(db.Model):
    __tablename__ = 'grade'
    id = Column(Integer, primary_key=True, autoincrement=True)
    gradeName = Column(String(20),nullable=False)
    classes = relationship('Class',backref='grade_class',lazy=True,cascade="all, delete")

class ClassRule(db.Model):
    __tablename__ = 'classRule'
    id = Column(Integer, primary_key=True, autoincrement=True)
    maxNoStudent = Column(Integer,nullable=False)
    classes = relationship('Class',backref='classRule_class',lazy=True,cascade="all, delete")


class Class(db.Model):
    __tablename__ = 'class'
    id = Column(Integer, primary_key=True, autoincrement=True)
    className = Column(String(20),nullable=False)
    classRuleID = Column(Integer, ForeignKey(ClassRule.id),nullable=False)
    gradeID = Column(Integer, ForeignKey(Grade.id),nullable=False)
    teaches = relationship('Teach',backref='class_teach',lazy=False,cascade="all, delete")
    students = relationship('Student', backref='class_student',lazy=False,cascade="all, delete")

class Teach(db.Model):
    __tablename__ = 'teach'
    id = Column(Integer, primary_key=True, autoincrement=True)
    teacherID = Column(Integer, ForeignKey(Teacher.id),nullable=False)
    classID = Column(Integer, ForeignKey(Class.id),nullable=False)

class StudentRule(db.Model):
    __tablename__ = 'studentRule'
    id = Column(Integer, primary_key=True, autoincrement=True)
    maxAge = Column(Integer,nullable=False)
    minAge = Column(Integer,nullable=False)
    students = relationship('Student',backref='studentRule_student',lazy=True,cascade="all, delete")

class Student(db.Model):
    __tablename__ = 'student'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50),nullable=False)
    gender = Column(String(10))
    DOB = Column(DateTime)
    classID = Column(Integer, ForeignKey(Class.id),nullable=True)
    stuRuleID = Column(Integer, ForeignKey(StudentRule.id),nullable=False)
    points = relationship('Point',backref='student_point',lazy=True,cascade="all, delete")

class Subject(db.Model):
    __tablename__ = 'subject'
    id = Column(Integer, primary_key=True, autoincrement=True)
    subjectName = Column(String(50),nullable=False)
    teachers = relationship('Teacher', backref='subject_teacher', lazy=True,cascade="all, delete")
    points = relationship('Point',backref='subject_point',lazy=True,cascade="all, delete")

class Semester(db.Model):
    __tablename__ = 'semester'
    id = Column(Integer, primary_key=True, autoincrement=True)
    semesterName = Column(String(15), nullable=False)
    year = Column(String(30),nullable=False)
    points = relationship('Point',backref='semester_point',lazy=True,cascade="all, delete")

class PointType(db.Model):
    __tablename__ = 'pointtype'
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(30),nullable=False)
    points = relationship('Point', backref='pointType_point',lazy=True,cascade="all, delete")

class Point(db.Model):
    __tablename__='point'
    id = Column(Integer, primary_key=True, autoincrement=True)
    pointValue = Column(Float, nullable=False)
    pointTypeID = Column(Integer, ForeignKey(PointType.id), nullable=False)
    semesterID = Column(Integer, ForeignKey(Semester.id),nullable=False)
    subjectID = Column(Integer, ForeignKey(Subject.id),nullable=False)
    studentID = Column(Integer, ForeignKey(Student.id),nullable=False)


#=================================Hàm thêm dữ liệu mẫu vào bảng=============================================
def seed_data():
    # Xóa dữ liệu cũ
    db.drop_all()
    db.create_all()

    # Thêm User mẫu
    users = [
        User(name="Nguyễn Văn A", gender="Nam", DOB=datetime(1985, 5, 20), email="admin1@example.com", phoneNumber="0123456789", userName="admin1", password="password1"),
        User(name="Trần Thị B", gender="Nữ", DOB=datetime(1990, 8, 15), email="teacher1@example.com", phoneNumber="0987654321", userName="teacher1", password="password2"),
        User(name="Lê Văn C", gender="Nam", DOB=datetime(1995, 3, 10), email="staff1@example.com", phoneNumber="0123445567", userName="staff1", password="password3"),
        User(name="Nguyễn Thị D", gender="Nữ", DOB=datetime(1980, 12, 1), email="teacher2@example.com", phoneNumber="0987651234", userName="teacher2", password="password4"),
        User(name="Phạm Văn E", gender="Nam", DOB=datetime(1992, 7, 25), email="admin2@example.com", phoneNumber="0911223344", userName="admin2", password="password5"),
    ]
    db.session.add_all(users)

    # Thêm Administrator mẫu
    admins = [
        Administrator(adminRole="Principal", userID=1),
        Administrator(adminRole="Vice Principal", userID=5),
    ]
    db.session.add_all(admins)

    # Thêm Staff mẫu
    staffs = [
        Staff(staffRole="Clerk", userID=3),
        Staff(staffRole="Counselor", userID=3),
    ]
    db.session.add_all(staffs)

    # Thêm Teacher mẫu
    teachers = [
        Teacher(yearExperience=10, userID=2, subjectID=1),
        Teacher(yearExperience=8, userID=4, subjectID=2),
    ]
    db.session.add_all(teachers)

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

    # Thêm Student mẫu
    students = [
        Student(name="Trần Văn H", gender="Nam", DOB=datetime(2008, 5, 15), classID=1, stuRuleID=1),
        Student(name="Nguyễn Thị K", gender="Nữ", DOB=datetime(2009, 3, 22), classID=1, stuRuleID=1),
        Student(name="Lê Văn M", gender="Nam", DOB=datetime(2007, 9, 5), classID=1, stuRuleID=1),
        Student(name="Phạm Thị N", gender="Nữ", DOB=datetime(2009, 6, 19), classID=1, stuRuleID=1),
        Student(name="Đặng Thị P", gender="Nữ", DOB=datetime(2008, 8, 12), classID=1, stuRuleID=1),
        Student(name="Trần Thị L", gender="Nữ", DOB=datetime(2007, 7, 17), classID=1, stuRuleID=1),
        Student(name="Hoàng Văn C", gender="Nam", DOB=datetime(2008, 12, 5), classID=1, stuRuleID=1),
        Student(name="Nguyễn Hồng V", gender="Nữ", DOB=datetime(2009, 2, 26), classID=1, stuRuleID=1),
        Student(name="Lê Thị T", gender="Nữ", DOB=datetime(2008, 4, 2), classID=1, stuRuleID=1),
        Student(name="Vũ Minh H", gender="Nam", DOB=datetime(2009, 1, 9), classID=1, stuRuleID=1),
        Student(name="Lê Văn K", gender="Nam", DOB=datetime(2007, 9, 5), classID=1, stuRuleID=1),
        Student(name="Lý Hồng A", gender="Nữ", DOB=datetime(2008, 5, 15), classID=2, stuRuleID=1),
        Student(name="Nguyễn Văn Q", gender="Nam", DOB=datetime(2008, 11, 30), classID=2, stuRuleID=1),
        Student(name="Phan Thị D", gender="Nữ", DOB=datetime(2009, 3, 25), classID=2, stuRuleID=1),
        Student(name="Trần Huy T", gender="Nam", DOB=datetime(2008, 6, 17), classID=2, stuRuleID=1),
        Student(name="Hoàng Văn H", gender="Nam", DOB=datetime(2008, 10, 5), classID=2, stuRuleID=1),
        Student(name="Lý Minh M", gender="Nữ", DOB=datetime(2009, 1, 21), classID=2, stuRuleID=1),
        Student(name="Phạm Thị M", gender="Nữ", DOB=datetime(2008, 4, 19), classID=2, stuRuleID=1),
        Student(name="Trần Minh T", gender="Nam", DOB=datetime(2007, 12, 3), classID=2, stuRuleID=1),
        Student(name="Nguyễn Thị L", gender="Nữ", DOB=datetime(2009, 2, 11), classID=2, stuRuleID=1),
        Student(name="Vũ Thị K", gender="Nữ", DOB=datetime(2008, 7, 29), classID=2, stuRuleID=1),
        Student(name="Lê Hoàng T", gender="Nam", DOB=datetime(2008, 9, 18), classID=3, stuRuleID=1),
        Student(name="Trần Thị H", gender="Nữ", DOB=datetime(2009, 5, 7), classID=3, stuRuleID=1),
        Student(name="Nguyễn Minh L", gender="Nam", DOB=datetime(2008, 8, 24), classID=3, stuRuleID=1),
        Student(name="Phan Minh T", gender="Nam", DOB=datetime(2009, 2, 12), classID=3, stuRuleID=1),
        Student(name="Lý Minh H", gender="Nam", DOB=datetime(2008, 6, 3), classID=3, stuRuleID=1),
        Student(name="Vũ Thị H", gender="Nữ", DOB=datetime(2007, 12, 25), classID=3, stuRuleID=1),
        Student(name="Nguyễn Thanh P", gender="Nam", DOB=datetime(2008, 11, 18), classID=3, stuRuleID=1),
        Student(name="Lê Hương L", gender="Nữ", DOB=datetime(2009, 1, 14), classID=3, stuRuleID=1),
        Student(name="Trần Minh M", gender="Nam", DOB=datetime(2008, 10, 9), classID=3, stuRuleID=1),
        Student(name="Hoàng Thanh D", gender="Nam", DOB=datetime(2009, 3, 3), classID=3, stuRuleID=1),
        Student(name="Lý Hồn A", gender="Nữ", DOB=datetime(2008, 5, 15), classID=2, stuRuleID=1),
        Student(name="Nguyễn Văn L", gender="Nam", DOB=datetime(2008, 11, 30), classID=2, stuRuleID=1),
        Student(name="Phan Thị U", gender="Nữ", DOB=datetime(2009, 3, 25), classID=2, stuRuleID=1),
        Student(name="Nguyễn Hằng P", gender="Nữ", DOB=datetime(2008, 12, 20), classID=4, stuRuleID=1),
        Student(name="Lê Thanh T", gender="Nam", DOB=datetime(2007, 11, 3), classID=4, stuRuleID=1),
        Student(name="Phan Thanh L", gender="Nam", DOB=datetime(2008, 7, 2), classID=4, stuRuleID=1),
        Student(name="Trần Thị P", gender="Nữ", DOB=datetime(2008, 8, 30), classID=4, stuRuleID=1),
        Student(name="Vũ Hồng A", gender="Nam", DOB=datetime(2007, 10, 14), classID=4, stuRuleID=1),
        Student(name="Lý Hương A", gender="Nữ", DOB=datetime(2008, 4, 11), classID=4, stuRuleID=1),
        Student(name="Trần Minh T", gender="Nam", DOB=datetime(2009, 5, 9), classID=4, stuRuleID=1),
        Student(name="Nguyễn Thị P", gender="Nữ", DOB=datetime(2009, 6, 5), classID=4, stuRuleID=1),
        Student(name="Lê Văn A", gender="Nam", DOB=datetime(2008, 12, 2), classID=4, stuRuleID=1),
        Student(name="Nguyễn Thị M", gender="Nữ", DOB=datetime(2008, 1, 22), classID=4, stuRuleID=1),
        Student(name="Lê Minh T", gender="Nam", DOB=datetime(2008, 9, 12), classID=5, stuRuleID=1),
        Student(name="Nguyễn Hồng K", gender="Nữ", DOB=datetime(2009, 4, 22), classID=5, stuRuleID=1),
        Student(name="Phạm Ngọc H", gender="Nam", DOB=datetime(2008, 6, 9), classID=5, stuRuleID=1),
        Student(name="Trần Thị M", gender="Nữ", DOB=datetime(2008, 7, 19), classID=5, stuRuleID=1),
        Student(name="Nguyễn Thị T", gender="Nữ", DOB=datetime(2008, 8, 3), classID=5, stuRuleID=1),
        Student(name="Lý Minh P", gender="Nam", DOB=datetime(2009, 1, 25), classID=5, stuRuleID=1),
        Student(name="Vũ Thị Q", gender="Nữ", DOB=datetime(2008, 12, 14), classID=5, stuRuleID=1),
        Student(name="Phan Minh D", gender="Nam", DOB=datetime(2008, 5, 30), classID=5, stuRuleID=1),
        Student(name="Trần Hương A", gender="Nữ", DOB=datetime(2008, 10, 25), classID=5, stuRuleID=1),
        Student(name="Lê Thanh H", gender="Nam", DOB=datetime(2009, 3, 7), classID=5, stuRuleID=1),
        Student(name="Nguyễn Thị B", gender="Nữ", DOB=datetime(2008, 9, 18), classID=6, stuRuleID=1),
        Student(name="Phạm Quang H", gender="Nam", DOB=datetime(2009, 4, 9), classID=6, stuRuleID=1),
        Student(name="Trần Minh T", gender="Nam", DOB=datetime(2008, 7, 11), classID=6, stuRuleID=1),
        Student(name="Lê Hương T", gender="Nữ", DOB=datetime(2008, 5, 6), classID=6, stuRuleID=1),
        Student(name="Nguyễn Quang V", gender="Nam", DOB=datetime(2007, 12, 17), classID=6, stuRuleID=1),
        Student(name="Trần Quang T", gender="Nam", DOB=datetime(2008, 10, 22), classID=6, stuRuleID=1),
        Student(name="Lý Minh Q", gender="Nam", DOB=datetime(2009, 3, 14), classID=6, stuRuleID=1),
        Student(name="Vũ Minh T", gender="Nam", DOB=datetime(2008, 6, 23), classID=6, stuRuleID=1),
        Student(name="Nguyễn Thanh T", gender="Nam", DOB=datetime(2008, 8, 18), classID=6, stuRuleID=1),
        Student(name="Lê Minh Q", gender="Nam", DOB=datetime(2009, 1, 5), classID=6, stuRuleID=1),
        Student(name="Trần Thị K", gender="Nữ", DOB=datetime(2008, 7, 19), classID=5, stuRuleID=1),
        Student(name="Nguyễn Thị E", gender="Nữ", DOB=datetime(2008, 8, 3), classID=5, stuRuleID=1),
        Student(name="Lý Minh Y", gender="Nam", DOB=datetime(2009, 1, 25), classID=5, stuRuleID=1),
        Student(name="Vũ Thị U", gender="Nữ", DOB=datetime(2008, 12, 14), classID=5, stuRuleID=1),
        Student(name="Nguyễn Thị M", gender="Nữ", DOB=datetime(2008, 12, 29), classID=7, stuRuleID=1),
        Student(name="Trần Văn H", gender="Nam", DOB=datetime(2007, 11, 2), classID=7, stuRuleID=1),
        Student(name="Vũ Thanh L", gender="Nam", DOB=datetime(2008, 9, 7), classID=7, stuRuleID=1),
        Student(name="Phan Hương T", gender="Nữ", DOB=datetime(2009, 2, 20), classID=7, stuRuleID=1),
        Student(name="Lê Minh N", gender="Nam", DOB=datetime(2009, 3, 17), classID=7, stuRuleID=1),
        Student(name="Trần Ngọc M", gender="Nam", DOB=datetime(2008, 4, 10), classID=7, stuRuleID=1),
        Student(name="Nguyễn Thị T", gender="Nữ", DOB=datetime(2009, 1, 14), classID=7, stuRuleID=1),
        Student(name="Lý Minh K", gender="Nam", DOB=datetime(2008, 7, 30), classID=7, stuRuleID=1),
        Student(name="Trần Thị V", gender="Nữ", DOB=datetime(2008, 8, 10), classID=7, stuRuleID=1),
        Student(name="Phạm Thanh T", gender="Nam", DOB=datetime(2009, 5, 3), classID=7, stuRuleID=1),
        Student(name="Lý Minh J", gender="Nam", DOB=datetime(2008, 7, 30), classID=7, stuRuleID=1),
        Student(name="Trần Thị O", gender="Nữ", DOB=datetime(2008, 8, 10), classID=7, stuRuleID=1),
        Student(name="Phạm Thanh T", gender="Nam", DOB=datetime(2009, 5, 3), classID=7, stuRuleID=1),
        Student(name="Lý Minh L", gender="Nam", DOB=datetime(2008, 7, 30), classID=7, stuRuleID=1),
        Student(name="Trần Thị P", gender="Nữ", DOB=datetime(2008, 8, 10), classID=7, stuRuleID=1),
        Student(name="Phạm Thanh T", gender="Nam", DOB=datetime(2009, 5, 3), classID=7, stuRuleID=1),
        Student(name="Lê Hồng P", gender="Nam", DOB=datetime(2008, 12, 8), classID=8, stuRuleID=1),
        Student(name="Nguyễn Thanh T", gender="Nam", DOB=datetime(2008, 6, 17), classID=8, stuRuleID=1),
        Student(name="Lý Minh T", gender="Nam", DOB=datetime(2009, 1, 26), classID=8, stuRuleID=1),
        Student(name="Phan Thanh K", gender="Nam", DOB=datetime(2008, 7, 14), classID=8, stuRuleID=1),
        Student(name="Trần Minh L", gender="Nam", DOB=datetime(2009, 3, 21), classID=8, stuRuleID=1),
        Student(name="Nguyễn Hương T", gender="Nữ", DOB=datetime(2009, 4, 11), classID=8, stuRuleID=1),
        Student(name="Vũ Quang P", gender="Nam", DOB=datetime(2008, 8, 6), classID=8, stuRuleID=1),
        Student(name="Lê Minh K", gender="Nam", DOB=datetime(2008, 12, 25), classID=8, stuRuleID=1),
        Student(name="Trần Hương M", gender="Nữ", DOB=datetime(2008, 5, 10), classID=9, stuRuleID=1),
        Student(name="Nguyễn Thị V", gender="Nữ", DOB=datetime(2009, 1, 7), classID=9, stuRuleID=1),
        Student(name="Lê Quang L", gender="Nam", DOB=datetime(2009, 3, 12), classID=9, stuRuleID=1),
        Student(name="Phan Thanh Q", gender="Nam", DOB=datetime(2008, 11, 25), classID=9, stuRuleID=1),
        Student(name="Trần Minh V", gender="Nam", DOB=datetime(2008, 7, 27), classID=9, stuRuleID=1),
        Student(name="Vũ Thị M", gender="Nữ", DOB=datetime(2009, 4, 4), classID=9, stuRuleID=1),
        Student(name="Lý Thanh K", gender="Nam", DOB=datetime(2008, 10, 10), classID=9, stuRuleID=1),
        Student(name="Nguyễn Hồng M", gender="Nữ", DOB=datetime(2008, 12, 18), classID=9, stuRuleID=1),
        Student(name="Trần Minh T", gender="Nam", DOB=datetime(2009, 2, 2), classID=9, stuRuleID=1),
        Student(name="Phan Minh A", gender="Nam", DOB=datetime(2008, 6, 5), classID=9, stuRuleID=1),
    ]
    db.session.add_all(students)

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
        Semester(semesterName="Học kỳ 1", year="2023-2024"),
        Semester(semesterName="Học kỳ 2", year="2023-2024"),
    ]
    db.session.add_all(semesters)

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

#===================================Hàm chứa các thao tác thêm sửa xóa một phần tử trong bảng=============================



# Hàm tạo dữ liệu điểm cho học sinh
def generate_points():
    points = []
    for student_id in range(1, 103):  # Tổng cộng 90 học sinh
        for semester_id in range(1, 3):  # 2 học kỳ
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



# Tạo dữ liệu điểm cho tất cả học sinh


if __name__ == '__main__':
    with app.app_context():
        #db.create_all()
        seed_data()


