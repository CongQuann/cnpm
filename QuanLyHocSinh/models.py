
from sqlalchemy import Column, Integer, String, Double, DateTime, Float, Boolean, ForeignKey, column,Enum
import enum

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
        Student(name="Nguyễn Thị K", gender="Nữ", DOB=datetime(2009, 3, 22), classID=2, stuRuleID=1),
        Student(name="Lê Văn M", gender="Nam", DOB=datetime(2007, 9, 5), classID=3, stuRuleID=1),
        Student(name="Phạm Thị N", gender="Nữ", DOB=datetime(2009, 6, 19), classID=4, stuRuleID=1),
        Student(name="Nguyễn Văn A", gender="Nam", DOB=datetime(2008, 2, 15), classID=1, stuRuleID=1),
        Student(name="Trần Thị B", gender="Nữ", DOB=datetime(2009, 7, 12), classID=2, stuRuleID=1),
        Student(name="Phạm Văn C", gender="Nam", DOB=datetime(2007, 10, 9), classID=3, stuRuleID=1),
        Student(name="Lê Thị D", gender="Nữ", DOB=datetime(2008, 1, 28), classID=4, stuRuleID=1),
        Student(name="Đỗ Văn E", gender="Nam", DOB=datetime(2009, 3, 16), classID=5, stuRuleID=1),
        Student(name="Hoàng Thị F", gender="Nữ", DOB=datetime(2008, 8, 25), classID=6, stuRuleID=1),
        Student(name="Ngô Văn G", gender="Nam", DOB=datetime(2007, 12, 4), classID=7, stuRuleID=1),
        Student(name="Vũ Thị H", gender="Nữ", DOB=datetime(2009, 9, 10), classID=8, stuRuleID=1),
        Student(name="Bùi Văn I", gender="Nam", DOB=datetime(2008, 6, 19), classID=9, stuRuleID=1),
        Student(name="Phan Thị J", gender="Nữ", DOB=datetime(2007, 11, 2), classID=1, stuRuleID=1),
        Student(name="Nguyễn Văn K", gender="Nam", DOB=datetime(2008, 5, 20), classID=2, stuRuleID=1),
        Student(name="Lê Thị L", gender="Nữ", DOB=datetime(2009, 4, 15), classID=3, stuRuleID=1),
        Student(name="Hoàng Văn M", gender="Nam", DOB=datetime(2007, 8, 8), classID=4, stuRuleID=1),
        Student(name="Phạm Thị N", gender="Nữ", DOB=datetime(2008, 7, 21), classID=5, stuRuleID=1),
        Student(name="Đỗ Văn O", gender="Nam", DOB=datetime(2009, 2, 6), classID=6, stuRuleID=1),
        Student(name="Vũ Thị P", gender="Nữ", DOB=datetime(2008, 11, 30), classID=7, stuRuleID=1),
        Student(name="Ngô Văn Q", gender="Nam", DOB=datetime(2007, 3, 9), classID=8, stuRuleID=1),
        Student(name="Bùi Thị R", gender="Nữ", DOB=datetime(2009, 6, 27), classID=9, stuRuleID=1),
        Student(name="Phan Văn S", gender="Nam", DOB=datetime(2008, 9, 14), classID=1, stuRuleID=1),
        Student(name="Trần Thị T", gender="Nữ", DOB=datetime(2007, 1, 22), classID=2, stuRuleID=1),
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
    points = [
        Point(pointValue=8.5, pointTypeID=1, semesterID=1, subjectID=1, studentID=1),
        Point(pointValue=9.0, pointTypeID=2, semesterID=1, subjectID=1, studentID=1),
        Point(pointValue=7.5, pointTypeID=3, semesterID=1, subjectID=1, studentID=1),
        Point(pointValue=8.0, pointTypeID=1, semesterID=2, subjectID=2, studentID=2),
        Point(pointValue=7.5, pointTypeID=2, semesterID=2, subjectID=2, studentID=2),
        Point(pointValue=9.0, pointTypeID=3, semesterID=2, subjectID=3, studentID=3),
        Point(pointValue=10.0, pointTypeID=1, semesterID=2, subjectID=4, studentID=4),
        Point(pointValue=8.5, pointTypeID=1, semesterID=1, subjectID=1, studentID=5),
        Point(pointValue=7.5, pointTypeID=2, semesterID=1, subjectID=2, studentID=6),
        Point(pointValue=9.0, pointTypeID=3, semesterID=1, subjectID=3, studentID=7),
        Point(pointValue=8.0, pointTypeID=1, semesterID=1, subjectID=4, studentID=8),
        Point(pointValue=7.0, pointTypeID=2, semesterID=1, subjectID=5, studentID=9),
        Point(pointValue=8.5, pointTypeID=3, semesterID=1, subjectID=6, studentID=10),
        Point(pointValue=6.5, pointTypeID=1, semesterID=1, subjectID=7, studentID=11),
        Point(pointValue=9.5, pointTypeID=2, semesterID=1, subjectID=8, studentID=12),
        Point(pointValue=8.0, pointTypeID=3, semesterID=1, subjectID=9, studentID=13),
        Point(pointValue=7.5, pointTypeID=1, semesterID=1, subjectID=10, studentID=14),
        Point(pointValue=9.0, pointTypeID=2, semesterID=2, subjectID=1, studentID=15),
        Point(pointValue=8.0, pointTypeID=3, semesterID=2, subjectID=2, studentID=16),
        Point(pointValue=7.0, pointTypeID=1, semesterID=2, subjectID=3, studentID=17),
        Point(pointValue=8.5, pointTypeID=2, semesterID=2, subjectID=4, studentID=18),
        Point(pointValue=9.5, pointTypeID=3, semesterID=2, subjectID=5, studentID=19),
        Point(pointValue=6.5, pointTypeID=1, semesterID=2, subjectID=6, studentID=20),
        Point(pointValue=8.0, pointTypeID=2, semesterID=2, subjectID=7, studentID=21),
        Point(pointValue=7.5, pointTypeID=3, semesterID=2, subjectID=8, studentID=22),
        Point(pointValue=9.0, pointTypeID=1, semesterID=2, subjectID=9, studentID=23),
        Point(pointValue=10.0, pointTypeID=2, semesterID=2, subjectID=10, studentID=24),
        Point(pointValue=8.5, pointTypeID=3, semesterID=1, subjectID=1, studentID=1),
        Point(pointValue=7.5, pointTypeID=2, semesterID=1, subjectID=2, studentID=2),
        Point(pointValue=8.0, pointTypeID=1, semesterID=1, subjectID=3, studentID=3),
        Point(pointValue=9.5, pointTypeID=3, semesterID=1, subjectID=4, studentID=4),
        Point(pointValue=7.0, pointTypeID=2, semesterID=1, subjectID=5, studentID=5),
        Point(pointValue=6.5, pointTypeID=1, semesterID=1, subjectID=6, studentID=6),
        Point(pointValue=9.0, pointTypeID=2, semesterID=1, subjectID=7, studentID=7),
        Point(pointValue=10.0, pointTypeID=3, semesterID=1, subjectID=8, studentID=8),
        Point(pointValue=8.0, pointTypeID=1, semesterID=1, subjectID=9, studentID=9),
        Point(pointValue=7.5, pointTypeID=2, semesterID=1, subjectID=10, studentID=10),
        Point(pointValue=9.5, pointTypeID=3, semesterID=2, subjectID=1, studentID=11),
        Point(pointValue=8.5, pointTypeID=2, semesterID=2, subjectID=2, studentID=12),
        Point(pointValue=7.0, pointTypeID=1, semesterID=2, subjectID=3, studentID=13),
        Point(pointValue=8.5, pointTypeID=3, semesterID=2, subjectID=4, studentID=14),
        Point(pointValue=9.0, pointTypeID=1, semesterID=2, subjectID=5, studentID=15),
        Point(pointValue=8.0, pointTypeID=2, semesterID=2, subjectID=6, studentID=16),
        Point(pointValue=7.5, pointTypeID=3, semesterID=2, subjectID=7, studentID=17),
        Point(pointValue=9.0, pointTypeID=1, semesterID=2, subjectID=8, studentID=18),
        Point(pointValue=10.0, pointTypeID=2, semesterID=2, subjectID=9, studentID=19),
        Point(pointValue=8.5, pointTypeID=3, semesterID=2, subjectID=10, studentID=20),
    ]
    db.session.add_all(points)

    try:
        db.session.commit()
        print("Data seeding successful!")
    except IntegrityError as e:
        db.session.rollback()
        print(f"Data seeding failed: {e}")

#===================================Hàm chứa các thao tác thêm sửa xóa một phần tử trong bảng=============================


if __name__ == '__main__':
    with app.app_context():
        # db.create_all()
        seed_data()


        # class_to_delete = Class.query.get(1)
        #
        # if class_to_delete:
        #     db.session.delete(class_to_delete)  # Tự động xóa liên quan nhờ cascade
        #     db.session.commit()
        #     print(f"Đã xóa lớp có ID {1} và các bản ghi liên quan.")
        # else:
        #     print(f"Không tìm thấy lớp có ID {1}.")