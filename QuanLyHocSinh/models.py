
from sqlalchemy import Column, Integer, String, Double, DateTime, Float, Boolean, ForeignKey, column,Enum
import enum

from wtforms.fields.numeric import IntegerField

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
def insert_sample_data():
    # Thêm User
    user1 = User(name="Nguyễn Văn A", gender="Nam", DOB="1990-01-01", email="vana@example.com", phoneNumber="0912345678", userName="vana", password="password123")
    user2 = User(name="Lê Thị B", gender="Nữ", DOB="1995-05-15", email="leb@example.com", phoneNumber="0923456789", userName="leb", password="password456")
    db.session.add_all([user1, user2])
    db.session.commit()

    # Thêm Administrator
    admin1 = Administrator(adminRole="Quản trị viên chính", userID=user1.id)
    db.session.add(admin1)

    # Thêm Staff
    staff1 = Staff(staffRole="Nhân viên hành chính", userID=user2.id)
    db.session.add(staff1)

    # Thêm Subject
    subject1 = Subject(subjectName="Toán")
    subject2 = Subject(subjectName="Văn")
    db.session.add_all([subject1, subject2])
    db.session.commit()

    # Thêm Teacher
    teacher1 = Teacher(yearExperience=5, userID=user1.id, subjectID=subject1.id)
    teacher2 = Teacher(yearExperience=3, userID=user2.id, subjectID=subject2.id)
    db.session.add_all([teacher1, teacher2])
    db.session.commit()

    # Thêm Grade
    grade1 = Grade(gradeName="Lớp 10")
    grade2 = Grade(gradeName="Lớp 11")
    db.session.add_all([grade1, grade2])
    db.session.commit()

    # Thêm ClassRule
    class_rule1 = ClassRule(maxNoStudent=40)
    db.session.add(class_rule1)
    db.session.commit()

    # Thêm Class
    class1 = Class(className="10A1", classRuleID=class_rule1.id, gradeID=grade1.id)
    class2 = Class(className="11B1", classRuleID=class_rule1.id, gradeID=grade2.id)
    db.session.add_all([class1, class2])
    db.session.commit()

    # Thêm StudentRule
    student_rule1 = StudentRule(maxAge=18, minAge=16)
    db.session.add(student_rule1)
    db.session.commit()

    # Thêm Student
    student1 = Student(name="Phạm Minh C", gender="Nam", DOB="2006-09-12", classID=class1.id, stuRuleID=student_rule1.id)
    student2 = Student(name="Hoàng Thị D", gender="Nữ", DOB="2007-07-08", classID=class2.id, stuRuleID=student_rule1.id)
    db.session.add_all([student1, student2])
    db.session.commit()

    # Thêm Semester
    semester1 = Semester(semesterName="Học kỳ 1", year="2024-2025")
    semester2 = Semester(semesterName="Học kỳ 2", year="2024-2025")
    db.session.add_all([semester1, semester2])
    db.session.commit()

    # Thêm PointType
    point_type1 = PointType(type="Kiểm tra 15 phút")
    point_type2 = PointType(type="Kiểm tra 1 tiết")
    db.session.add_all([point_type1, point_type2])
    db.session.commit()

    # Thêm Point
    point1 = Point(pointValue=8.5, pointTypeID=point_type1.id, semesterID=semester1.id, subjectID=subject1.id, studentID=student1.id)
    point2 = Point(pointValue=7.0, pointTypeID=point_type2.id, semesterID=semester1.id, subjectID=subject2.id, studentID=student2.id)
    db.session.add_all([point1, point2])
    db.session.commit()

    print("Dữ liệu mẫu đã được thêm thành công!")



#===================================Hàm chứa các thao tác thêm sửa xóa một phần tử trong bảng=============================


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        insert_sample_data()


        # class_to_delete = Class.query.get(1)
        #
        # if class_to_delete:
        #     db.session.delete(class_to_delete)  # Tự động xóa liên quan nhờ cascade
        #     db.session.commit()
        #     print(f"Đã xóa lớp có ID {1} và các bản ghi liên quan.")
        # else:
        #     print(f"Không tìm thấy lớp có ID {1}.")