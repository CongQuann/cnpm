from flask import flash,request

from QuanLyHocSinh.models import Point, Semester, Subject, Student, StudentClass, Teach, Class, StudentRule, ClassRule, User, \
    Staff, Teacher, Administrator
from QuanLyHocSinh import db,app
from flask_mail import Mail, Message
from sqlalchemy.orm import joinedload, deferred
from sqlalchemy.exc import SQLAlchemyError

mail = Mail(app)

def calculate_average(student_id, subject_id, semester_id):
    query = Point.query.filter_by(studentID=student_id, semesterID=semester_id)
    if subject_id:
        query = query.filter_by(subjectID=subject_id)

    points = query.all()
    total_points = 0
    total_weight = 0

    for point in points:
        point_type = point.pointType_point.type

        if point_type == "15 phút":
            total_points += point.pointValue
            total_weight += 1
        elif point_type == "1 tiết":
            total_points += 2 * point.pointValue
            total_weight += 2
        elif point_type == "Cuối kỳ":
            total_points += 3 * point.pointValue
            total_weight += 3

    if total_weight == 0:
        return 0

    average = total_points / total_weight

    return average

def is_student_passed(student_id, subject_id, semester_id):
    # Tính điểm trung bình của học sinh cho môn học và học kỳ cụ thể
    average = calculate_average(student_id, subject_id, semester_id)

    # Kiểm tra nếu điểm trung bình >= 5 thì đạt
    return average >= 5

def get_subject_name(subject_id):
    return Subject.query.with_entities(Subject.subjectName).filter_by(id=subject_id).scalar() #trả về kết qủa đầu tiên của hàng và cột

def get_semester_info(semester_id):
    return Semester.query.get(semester_id)

def get_classes():
    return Class.query.all()

def get_student_classes(class_id, semester_id):
    return StudentClass.query.filter_by(class_id=class_id, semester_id=semester_id).all()

def get_student_rule():
    """Lấy quy định về học sinh."""
    return StudentRule.query.first()

def get_class_rule():
    return ClassRule.query.first()

def update_rules(min_age, max_age, max_class_size):
    student_rule = get_student_rule()
    class_rule = get_class_rule()

    if student_rule and class_rule:
        student_rule.minAge = int(min_age)
        student_rule.maxAge = int(max_age)
        class_rule.maxNoStudent = int(max_class_size)

        db.session.commit()
        return True  # Cập nhật thành công
    return False  # Không thể cập nhật

def existing_subject_check(subject_name):
    return Subject.query.filter_by(subjectName=subject_name).first()

def add_new_subject(subject_name):
    new_subject = Subject(subjectName=subject_name)
    db.session.add(new_subject)
    db.session.commit()

def get_subject():
    return Subject.query.all()

def get_subject_by_id(subject_id):
    return Subject.query.get(subject_id)


def delete_subject_by_id(subject_id):
    subject = Subject.query.filter_by(id=subject_id).first()
    db.session.delete(subject)
    db.session.commit()

def check_existing_subject_name(subject_name,subject):
    if subject.subjectName != subject_name:
        # kiểm tra xem tên người dùng nhập mới đã tồn tại hay chưa
        return Subject.query.filter_by(subjectName=subject_name).first()

def update_subject_info(subject,subject_name,subject_requirement,subject_description):
    subject.subjectName = subject_name
    subject.subjectRequirement = subject_requirement
    subject.subjectDescription = subject_description
    db.session.commit()

def existing_user_check(username):
    return User.query.filter_by(userName=username).first()

def existing_email_check(email):
    return User.query.filter_by(email=email).first()

def existing_phone_check(phone_number):
    return User.query.filter_by(phoneNumber=phone_number).first()

def create_user_by_role(role,name,gender,dob,email,phone_number,username,hashed_password,staff_role,year_experience,admin_role):
    if role == 'Staff':

        new_user = Staff(
            name=name,
            gender=gender,
            DOB=dob,
            email=email,
            phoneNumber=phone_number,
            userName=username,
            password=hashed_password,
            staffRole=staff_role
        )
        db.session.add(new_user)
        db.session.commit()
    elif role == 'Teacher':

        new_user = Teacher(
            name=name,
            gender=gender,
            DOB=dob,
            email=email,
            phoneNumber=phone_number,
            userName=username,
            password=hashed_password,
            yearExperience=year_experience
        )
        db.session.add(new_user)
        db.session.commit()
    elif role == 'Administrator':

        new_user = Administrator(
            name=name,
            gender=gender,
            DOB=dob,
            email=email,
            phoneNumber=phone_number,
            userName=username,
            password=hashed_password,
            adminRole=admin_role
        )
        db.session.add(new_user)
        db.session.commit()
        # Thêm bản ghi vào cơ sở dữ liệu

def send_email(name,username,email,password):
    msg = Message(
        subject="Xác nhận đăng ký hệ thống quản lý học sinh!",  # Tiêu đề email
        recipients=[email],  # Người nhận
        # Nội dung email
        body=f"Chào {name},\n\nThông tin tài khoản của bạn là:\n\nUsername: {username}\nPassword: {password}\n\nChúc bạn một ngày tốt lành!"
    )
    mail.send(msg)  # Gửi email
    flash('Tạo tài khoản thành công và email xác nhận đã được gửi!', 'success')


def get_user_data():
    # Lấy danh sách người dùng, bỏ qua người dùng có vai trò là Administrator
    users = db.session.query(User).options(
        joinedload(User.staffs),
        joinedload(User.teachers),
        joinedload(User.admins)
    ).all()

    user_data = []
    for user in users:
        # Bỏ qua người dùng có vai trò là Administrator
        if user.admins:
            continue

        role = None
        additional_info = None

        # Kiểm tra vai trò và lấy thông tin từ các mối quan hệ
        if user.staffs:
            role = "Staff"
            additional_info = f"Role: {user.staffs[0].staffRole}"
        elif user.teachers:
            role = "Teacher"
            additional_info = f"Experience: {user.teachers[0].yearExperience}, Subject ID: {user.teachers[0].subjectID}"

        # Lưu thông tin người dùng vào danh sách
        user_data.append({
            "id": user.id,
            "name": user.name,
            "gender": user.gender,
            "DOB": user.DOB.strftime('%Y-%m-%d') if user.DOB else None,
            "email": user.email,
            "phoneNumber": user.phoneNumber,
            "userName": user.userName,
            "role": role,
            "additional_info": additional_info
        })

    return user_data


def delete_user_by_id(user_id):
    try:
        # Lấy thông tin người dùng từ bảng User
        user = db.session.get(User, user_id)
        if not user:
            return None  # Không tìm thấy người dùng

        # Xóa thông tin từ bảng Staff nếu người dùng là staff
        if user.type == "staff":
            db.session.query(Staff).filter_by(id=user_id).delete(synchronize_session=False)

        # Xóa thông tin từ bảng Teacher nếu người dùng là teacher
        elif user.type == "teacher":
            db.session.query(Teacher).filter_by(id=user_id).delete(synchronize_session=False)

        # Xóa bản ghi cha `User`
        db.session.query(User).filter_by(id=user_id).delete(synchronize_session=False)

        db.session.commit()  # Lưu thay đổi vào cơ sở dữ liệu
        return True  # Thành công
    except SQLAlchemyError as e:
        db.session.rollback()  # Rollback nếu có lỗi
        return str(e)  # Trả về lỗi

def teacher_subject_update():
    # Lặp qua tất cả giáo viên và cập nhật môn học của họ
    for teacher in Teacher.query.all():
        subject_id = request.form.get(f"subject_{teacher.id}")  # Lấy môn học từ form
        # Nếu subject_id không phải là rỗng, gán giá trị môn học cho giáo viên
        if subject_id:
            teacher.subjectID = subject_id
        else:
            teacher.subjectID = None  # Nếu không có môn học, gán là None (Chưa có chuyên môn)

    # Lưu thay đổi vào cơ sở dữ liệu
    db.session.commit()
    flash('Cập nhật thành công!', 'success')

def get_teacher():
    return Teacher.query.all()

def update_class_to_teacher():
    # Xử lý thêm lớp cho giáo viên
    for teacher in Teacher.query.all():
        add_class_id = request.form.get(f"add_class_{teacher.id}")
        if add_class_id:
            # Kiểm tra nếu lớp này đã được gán cho giáo viên chưa
            existing_assignment = Teach.query.filter_by(
                teacherID=teacher.id, classID=add_class_id
            ).first()
            if not existing_assignment:
                new_teach = Teach(teacherID=teacher.id, classID=add_class_id)
                db.session.add(new_teach)

        # Xử lý xóa lớp dạy
        for teach in teacher.teaches:
            remove_key = f"remove_class_{teach.id}"
            if remove_key in request.form:
                db.session.delete(teach)

    # Lưu thay đổi vào cơ sở dữ liệu
    db.session.commit()
    flash("Cập nhật thành công!", "success")
