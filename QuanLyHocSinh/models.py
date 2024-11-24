
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
    admins = relationship('Administrator',backref='user_administrator',lazy=True)
    staffs = relationship('Staff',backref='user_staff',lazy = True)
    teachers = relationship('Teacher',backref='user_teacher',lazy=True)

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
    teaches = relationship('Teach',backref='teacher_teach',lazy=True)

class Grade(db.Model):
    __tablename__ = 'grade'
    id = Column(Integer, primary_key=True, autoincrement=True)
    gradeName = Column(String(20),nullable=False)
    classes = relationship('Class',backref='grade_class',lazy=True)

class ClassRule(db.Model):
    __tablename__ = 'classRule'
    id = Column(Integer, primary_key=True, autoincrement=True)
    maxNoStudent = Column(Integer,nullable=False)
    classes = relationship('Class',backref='classRule_class',lazy=True)


class Class(db.Model):
    __tablename__ = 'class'
    id = Column(Integer, primary_key=True, autoincrement=True)
    className = Column(String(20),nullable=False)
    classRuleID = Column(Integer, ForeignKey(ClassRule.id),nullable=False)
    gradeID = Column(Integer, ForeignKey(Grade.id),nullable=False)
    teaches = relationship('Teach',backref='class_teach',lazy=False)
    students = relationship('Student', backref='class_student',lazy=False)

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
    students = relationship('Student',backref='studentRule_student',lazy=True)

class Student(db.Model):
    __tablename__ = 'student'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50),nullable=False)
    gender = Column(String(10))
    DOB = Column(DateTime)
    classID = Column(Integer, ForeignKey(Class.id),nullable=True)
    stuRuleID = Column(Integer, ForeignKey(StudentRule.id),nullable=False)
    points = relationship('Point',backref='student_point',lazy=True)

class Subject(db.Model):
    __tablename__ = 'subject'
    id = Column(Integer, primary_key=True, autoincrement=True)
    subjectName = Column(String(50),nullable=False)
    teachers = relationship('Teacher', backref='subject_teacher', lazy=True)
    points = relationship('Point',backref='subject_point',lazy=True)

class Semester(db.Model):
    __tablename__ = 'semester'
    id = Column(Integer, primary_key=True, autoincrement=True)
    semesterName = Column(String(15), nullable=False)
    year = Column(String(30),nullable=False)
    points = relationship('Point',backref='semester_point',lazy=True)

class PointType(db.Model):
    __tablename__ = 'pointtype'
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(30),nullable=False)
    points = relationship('Point', backref='pointType_point',lazy=True)

class Point(db.Model):
    __tablename__='point'
    id = Column(Integer, primary_key=True, autoincrement=True)
    pointValue = Column(Float, nullable=False)
    pointTypeID = Column(Integer, ForeignKey(PointType.id), nullable=False)
    semesterID = Column(Integer, ForeignKey(Semester.id),nullable=False)
    subjectID = Column(Integer, ForeignKey(Subject.id),nullable=False)
    studentID = Column(Integer, ForeignKey(Student.id),nullable=False)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
