from enum import unique
from sqlalchemy import Column, Integer, String, Double, DateTime, Float, Boolean, ForeignKey, column,Enum
import enum
from QuanLyHocSinh import db, app
from sqlalchemy.orm import relationship, backref
from datetime import datetime


class User(db.Model):
    __tablename__ = 'user'
    userID = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    dateOfBirth = Column(DateTime, nullable=True)
    gender = Column(String(10))
    phoneNumber = Column(String(11), unique=True)
    email = Column(String(50), unique=True)
    userAccount = Column(String(50), unique=True)
    password = Column(String(50))
    admins = relationship('Admin', backref='user', lazy=True)
    teachers = relationship('Teacher',backref='user',lazy=True)
    staffs = relationship('Staff',backref='user',lazy=True)

    def __str__(self):
        return self.name


class Admin(db.Model):
    __tablename__ = 'admin'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.userID'), nullable=False)

    def __str__(self):
        return str(self.id)

# Định nghĩa Enum cho khối lớp
class GradeLevel(enum.Enum):
    GRADE_10 = "10"
    GRADE_11 = "11"
    GRADE_12 = "12"

class Subject(db.Model):
    __tablename__ = 'subject'
    subjectID = Column(Integer, primary_key=True)
    subjectName = Column(String(50), nullable=False)
    grade_level = Column(Enum(GradeLevel), nullable=False)
    teachers = relationship('Teacher',backref='subject',lazy=True)
    points = relationship('Point',backref='subject',lazy=True)
    def __str__(self):
        return self.subjectName




class Teacher(db.Model):
    __tablename__ = 'teacher'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.userID'), nullable=False)
    teaches = relationship('Teach',backref='teacher',lazy=True)
    subject_ID = Column(Integer, ForeignKey('subject.subjectID'))

    def __str__(self):
        return str(self.id)

class Staff(db.Model):
    __tablename__ = 'staff'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.userID'), nullable=False)

    def __str__(self):
        return str(self.id)

class Year(db.Model):
    __tablename__ = 'year'
    yearID = Column(Integer, primary_key=True, autoincrement=True)
    yearName = Column(String(50),nullable=False)
    classes = relationship('Class', backref='year', lazy=True)
    semesters = relationship('Semester',backref='year',lazy=True)

    def __str__(self):
        return self.yearName


class Semester(db.Model):
    __tablename__ = 'semester'
    semesterID = Column(Integer, primary_key=True, autoincrement=True)
    semesterName = Column(String(20), nullable=False)
    year_ID = Column(Integer, ForeignKey('year.yearID'),nullable=False)
    points = relationship('Point',backref='semester',lazy=True)
    def __str__(self):
        return self.semesterName


class ClassRule(db.Model):
    __tablename__ = 'class_rule'
    classRuleID = Column(Integer, primary_key=True, autoincrement=True)
    maxNumber = Column(Integer, nullable=False)
    classes = relationship('Class', backref='class_rule', lazy=True)

    def __str__(self):
        return str(self.classRuleID)

class Class(db.Model):
    __tablename__ = 'class'
    classID = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    number = Column(Integer)
    year_ID = Column(Integer, ForeignKey('year.yearID'), nullable=False)
    classRule_ID = Column(Integer, ForeignKey('class_rule.classRuleID'), nullable=False)
    teaches = relationship('Teach', backref='class', lazy=True)
    studies = relationship('Study', backref='class',lazy=True)
    grade_level = Column(Enum(GradeLevel), nullable=False)

    def __str__(self):
        return self.name

class Teach(db.Model):
    __tablename__ = 'teach'
    id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_ID = Column(Integer,ForeignKey('teacher.id'), nullable=False)
    class_ID = Column(Integer,ForeignKey('class.classID'), nullable=False)

    def __str__(self):
        return str(self.id)

class Study(db.Model):
    __tablename__ = 'study'
    id = Column(Integer, primary_key=True, autoincrement=True)
    class_ID = Column(Integer, ForeignKey('class.classID'),nullable=False)
    student_ID = Column(Integer, ForeignKey('student.studentID'),nullable=False)

    def __str__(self):
        return str(self.id)

class StudentRule(db.Model):
    __tablename__ = 'student_rule'
    stuRuleID = Column(Integer, primary_key=True, autoincrement=True)
    maxAge = Column(Integer, nullable=False)
    minAge = Column(Integer, nullable=False)
    classes = relationship('Student', backref='student_rule', lazy=True)

    def __str__(self):
        return str(self.classRuleID)

class Student(db.Model):
    __tablename__ = 'student'
    studentID = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    gender = Column(String(10))
    dateOfBirth = Column(DateTime, nullable=True)
    address = Column(String(50))
    phoneNumber = Column(String(11), unique=True)
    email = Column(String(50), unique=True)
    stuRule_ID = Column(Integer, ForeignKey('student_rule.stuRuleID'),nullable=False)
    studies = relationship('Study',backref='student', lazy=True)
    points = relationship('Point',backref='student',lazy=True)
    def __str__(self):
        return self.name


class Point(db.Model):
    __tablename__ = 'point'
    pointID = Column(Integer,primary_key=True,autoincrement=True)
    subject_ID = Column(Integer,ForeignKey('subject.subjectID'),nullable=False)
    student_ID = Column(Integer,ForeignKey('student.studentID'),nullable=False)
    semester_ID = Column(Integer,ForeignKey('semester.semesterID'),nullable=False)
    pointDetails = relationship('PointDetails',backref='point',lazy=True)
    def __str__(self):
        return str(self.pointID)

class PointTypes(enum.Enum):
    EX15_MIN = "1"
    EX45_MIN = "2"
    FINAL_EXAM = "3"



class PointDetails(db.Model):
    __tablename__ = 'point_details'
    id = Column(Integer,primary_key=True,autoincrement=True)
    value = Column(Float, nullable=True)
    point_types =  Column(Enum(PointTypes), nullable=False)
    point_ID = Column(Integer,ForeignKey('point.pointID'),nullable=False)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # u1 = User(name='Hau', dateOfBirth=datetime.strptime('2004-10-17', '%Y-%m-%d'), gender='Nam',
        #           phoneNumber='0346916012', email='abc@gmail.com', userAccount='user1', password='123')
        # db.session.add(u1)
        # db.session.commit()
