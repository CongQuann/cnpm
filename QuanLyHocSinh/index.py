import base64
import string
from datetime import datetime
import random


from cryptography.fernet import Fernet
from flask import render_template, request, redirect, flash, url_for
from flask_login import login_user, LoginManager, login_required, logout_user,current_user
from flask_mail import Mail, Message
from sqlalchemy.orm import joinedload
from flask_login import current_user
from flask import session
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from io import BytesIO
from flask import send_file
from sqlalchemy.exc import SQLAlchemyError


from QuanLyHocSinh import app, db
from QuanLyHocSinh.models import Class, Student, User, Staff, Subject, Semester, StudentRule, ClassRule, Point, \
    Teacher, Administrator, StudentClass, Teach

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/'

mail = Mail(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        # Lấy danh sách tất cả người dùng
        users = User.query.all()

        # Duyệt qua tất cả người dùng để tìm người dùng khớp với username đã giải mã
        for user in users:
            decrypted_username = decrypt_data(user.userName)  # Giải mã tên đăng nhập trong cơ sở dữ liệu

            if decrypted_username == username:  # Nếu username khớp
                decrypted_password = decrypt_data(user.password)  # Giải mã mật khẩu

                if decrypted_password == password and user.type == 'administrator':
                    login_user(user)
                    return redirect("/Administrator/Report")
                elif decrypted_password == password and user.type == 'teacher':
                    login_user(user)
                    return redirect("/Teacher/EnterPoints")
                elif decrypted_password ==password and user.type == 'staff':
                    login_user(user)
                    return redirect("/class_edit")
        flash('Tên đăng nhập hoặc mật khẩu không đúng!',"danger")
    return render_template('index.html')

@app.route("/logout")
@login_required #phải đảm bảo người dùng đã đăng nhập trước khi đăng xuất
def logout():
    logout_user() #Thực hiện đăng xuất người dùng
    return redirect("/") #thực hiện điều hướng về trang đăng nhập


# Route lấy lại mật khẩu
@app.route('/forgot-password/<int:step>', methods=['GET', 'POST'])
def forgot_password(step):
    if step == 1:
        if request.method == 'POST':
            username = request.form['username']
            user = None
            users = User.query.all()
            for i in users:
                decrypted_username = decrypt_data(i.userName)  # Giải mã tên đăng nhập trong cơ sở dữ liệu

                if decrypted_username == username:  # Nếu username khớp
                    user = i


            if not user:
                flash("Tên tài khoản không tồn tại!", "danger")
                return render_template('Administrator/forgot_password.html', step=1)

            # Tạo mã xác nhận
            verification_code = ''.join(random.choices(string.digits, k=6))
            user.verification_code = verification_code
            db.session.commit()

            # Gửi mã xác nhận qua email (giả sử có hàm send_email)
            try:
                # Tạo đối tượng email
                msg = Message(
                    subject="Xác nhận đặt lại mật khẩu hệ thống quản lý học sinh!",  # Tiêu đề email
                    recipients=[user.email],  # Người nhận
                    # Nội dung email
                    body=f"Chào {user.name},\n\nMã xác nhận của bạn là: {user.verification_code}"
                )
                mail.send(msg)  # Gửi email
                flash('Đã gửi mã xác nhận!', 'success')
            except Exception as e:
                flash(f'Đã xảy ra lỗi khi gửi mã xác nhận: {str(e)}', 'danger')

            print(f"Mã xác nhận đã được gửi đến email {user.email}: {verification_code}")
            return redirect(url_for('forgot_password', step=2, username=username))

        return render_template('Administrator/forgot_password.html', step=1)

    elif step == 2:
        username = request.args.get('username')
        if not username:
            flash("Vui lòng bắt đầu lại quy trình!", "danger")
            return redirect(url_for('forgot_password', step=1))

        if request.method == 'POST':
            user = None
            users = User.query.all()
            for i in users:
                decrypted_username = decrypt_data(i.userName)  # Giải mã tên đăng nhập trong cơ sở dữ liệu

                if decrypted_username == username:  # Nếu username khớp
                    user = i
            input_code = request.form['verification_code']
            if not user or input_code != user.verification_code:
                flash("Mã xác nhận không đúng!", "danger")
                return render_template('Administrator/forgot_password.html', step=2, username=username)

            flash("Mã xác nhận hợp lệ! Hãy đặt lại mật khẩu.", "success")
            return redirect(url_for('forgot_password', step=3, username=username))

        return render_template('Administrator/forgot_password.html', step=2, username=username)

    elif step == 3:
        username = request.args.get('username')
        if not username:
            flash("Vui lòng bắt đầu lại quy trình!", "danger")
            return redirect(url_for('forgot_password', step=1))

        if request.method == 'POST':
            user = None
            users = User.query.all()
            for i in users:
                decrypted_username = decrypt_data(i.userName)  # Giải mã tên đăng nhập trong cơ sở dữ liệu

                if decrypted_username == username:  # Nếu username khớp
                    user = i
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']
            if not user:
                flash("Người dùng không tồn tại!", "danger")
                return redirect(url_for('forgot_password', step=1))
            if new_password != confirm_password:
                flash("Mật khẩu xác nhận không trùng khớp!", "danger")
                return render_template('Administrator/forgot_password.html', step=3, username=username)

            # Cập nhật mật khẩu
            user.password = encrypt_data(new_password)
            user.verification_code = None  # Xóa mã xác nhận
            db.session.commit()
            flash("Đặt lại mật khẩu thành công!", "success")
            return redirect("/")

        return render_template('Administrator/forgot_password.html', step=3, username=username)
# ===========================================================ADMINISTRATOR================================================

@login_required
@app.route("/Administrator/Report", methods=["GET", "POST"])
def report():
    # Lấy tất cả các môn học và học kỳ
    subject_list = Subject.query.all()
    semester_list = Semester.query.all()

    # Khởi tạo biến statistics để giữ dữ liệu nếu có chọn môn học và học kỳ
    statistics = []
    subject_name = None
    semester_name = None
    year = None

    # Xử lý form khi người dùng chọn môn học và học kỳ
    if request.method == "POST":
        selected_subject = request.form.get('subject')
        selected_semester = request.form.get('semester')

        # Tính toán thống kê cho môn học và học kỳ đã chọn
        if selected_subject and selected_semester:
            subject_id = selected_subject
            semester_id = selected_semester

            # Lấy thông tin học kỳ và môn học
            semester = Semester.query.get(semester_id)
            subject_name = Subject.query.with_entities(Subject.subjectName).filter_by(id=subject_id).scalar()
            semester_name = semester.semesterName
            year = semester.year

            # Lấy thông tin lớp học (Class)
            classes = Class.query.all()

            # Thống kê số lượng học sinh đạt theo lớp
            for cls in classes:
                # Lọc các học sinh theo lớp và học kỳ
                student_classes = StudentClass.query.filter_by(class_id=cls.id, semester_id=semester_id).all()

                num_students = len(student_classes)
                num_passed = 0

                for student_class in student_classes:
                    # Lấy học sinh từ StudentClass
                    student = Student.query.get(student_class.student_id)
                    if student:
                        # Tính điểm trung bình của học sinh và kiểm tra nếu học sinh đã đạt
                        if is_student_passed(student.id, subject_id, semester_id):
                            num_passed += 1

                # Tính tỷ lệ đạt
                pass_rate = (num_passed / num_students * 100) if num_students > 0 else 0
                statistics.append({
                    "class_name": cls.className,
                    "total_students": num_students,
                    "num_passed": num_passed,
                    "pass_rate": f"{pass_rate:.2f}%"  # Làm tròn 2 chữ số thập phân
                })

    # Render lại form và dữ liệu thống kê khi trang đầu tiên hoặc sau khi người dùng chọn môn học và học kỳ
    return render_template('Administrator/Report.html',
                           subjects=subject_list,
                           semesters=semester_list,
                           selected_subject=request.form.get('subject', None),
                           selected_semester=request.form.get('semester', None),
                           statistics=statistics,
                           subject_name=subject_name,
                           semester_name=semester_name,
                           year=year)


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
    if average >= 5:
        return True  # Học sinh đạt môn
    else:
        return False  # Học sinh không đạt môn


# ========================================

@login_required
@app.route("/Administrator/RuleManagement", methods=["GET", "POST"])
def rule():
    if request.method == "POST":
        # Lấy dữ liệu từ form
        min_age = request.form.get("min_age")
        max_age = request.form.get("max_age")
        max_class_size = request.form.get("max_class_size")

        # Lấy bản ghi đầu tiên trong bảng
        student_rule = StudentRule.query.first()
        class_rule = ClassRule.query.first()

        # Kiểm tra nếu các bản ghi tồn tại
        if student_rule and class_rule:
            # Cập nhật quy định
            student_rule.minAge = int(min_age)
            student_rule.maxAge = int(max_age)
            class_rule.maxNoStudent = int(max_class_size)

            # Lưu thay đổi vào cơ sở dữ liệu
            db.session.commit()

            flash("Quy định đã được cập nhật thành công!", "success")
        else:
            flash("Không thể cập nhật quy định. Vui lòng kiểm tra lại!", "error")

        return redirect("/Administrator/RuleManagement")

        # Xử lý GET request
    class_rule = ClassRule.query.first()
    student_rule = StudentRule.query.first()

    return render_template(
        "Administrator/RuleManagement.html",
        class_rule=class_rule,
        student_rule=student_rule,
    )

@login_required
@app.route("/Administrator/SubjectManagement", methods=["GET", "POST"])
def subject_mng():
    if request.method == "POST":
        subject_name = request.form.get("subject_name")  # Lấy tên môn học từ form

        if not subject_name:
            flash("Tên môn học không được để trống!", "danger")
            return redirect("/Administrator/SubjectManagement")

        # Kiểm tra xem môn học đã tồn tại chưa
        existing_subject = Subject.query.filter_by(subjectName=subject_name).first()
        if existing_subject:
            flash("Môn học đã tồn tại!", "warning")
            return redirect("/Administrator/SubjectManagement")

        # Thêm môn học mới vào cơ sở dữ liệu
        try:
            new_subject = Subject(subjectName=subject_name)
            db.session.add(new_subject)
            db.session.commit()
            flash("Thêm môn học thành công!", "success")
            return redirect("/Administrator/SubjectManagement")
        except Exception as e:
            db.session.rollback()
            flash("Có lỗi xảy ra khi thêm môn học.", "danger")

        return redirect("/Administrator/SubjectManagement")

    # Nếu là GET, trả về giao diện
    subjects = Subject.query.all()
    return render_template('Administrator/SubjectManagement.html', subjects=subjects)


# ======Thêm route xử lý để xóa môn học=======
@app.route("/Administrator/SubjectManagement/delete", methods=["GET", "POST"])
def delete_subject():
    subject_id = request.form.get("subject_id")  # Lấy subject_id từ form

    if not subject_id:
        flash("Không tìm thấy môn học cần xóa.", "danger")
        return redirect("/Administrator/SubjectManagement")

    # Tìm môn học trong cơ sở dữ liệu
    subject = Subject.query.get(subject_id)
    if not subject:
        flash("Môn học không tồn tại.", "warning")
        return redirect("/Administrator/SubjectManagement")

    # Xóa môn học
    try:
        db.session.delete(subject)
        db.session.commit()
        flash("Xóa môn học thành công!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Có lỗi xảy ra khi xóa môn học.", "danger")

    return redirect("/Administrator/SubjectManagement")


# ============Phần chỉnh sửa môn học
@app.route("/Administrator/SubjectManagement/edit/<int:subject_id>")  # route để gọi ra trang chỉnh sửa
def edit_subject_page(subject_id):
    subject = Subject.query.get(subject_id)
    if not subject:
        flash("Môn học không tồn tại.", "warning")
        return redirect("/Administrator/SubjectManagement")
    return render_template("Administrator/edit_subject.html", subject=subject)


@app.route("/Administrator/SubjectManagement/update",
           methods=["POST"])  # route chứa hàm thực hiện chức năng của trang chỉnh sửa
def update_subject():
    subject_id = request.form.get("subject_id")
    subject_name = request.form.get("subject_name")
    subject_requirement = request.form.get("subject_requirement")
    subject_description = request.form.get("subject_description")
    # Xử lý cập nhật
    subject = Subject.query.get(subject_id)
    if not subject:
        flash("Không tìm thấy môn học.", "warning")
        return redirect("/Administrator/SubjectManagement")

    try:
        subject.subjectName = subject_name
        subject.subjectRequirement = subject_requirement
        subject.subjectDescription = subject_description
        db.session.commit()
        flash("Cập nhật thành công!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Lỗi trong quá trình cập nhật.", "danger")
    return redirect("/Administrator/SubjectManagement")


# =====================================



@app.route('/Administrator/CreateUser', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        # Lấy thông tin từ form
        name = request.form['name']
        username = encrypt_data(request.form['userName'])
        email = request.form['email']
        phone_number = request.form['phoneNumber']
        # Kiểm tra nếu tên đăng nhập đã tồn tại
        existing_user = User.query.filter_by(userName=username).first()
        existing_email = User.query.filter_by(email=email).first()
        existing_phone_number = User.query.filter_by(phoneNumber=phone_number).first()
        if existing_user:
            flash("Tên đăng nhập đã được sử dụng!", "danger")
            return render_template('Administrator/CreateUser.html')
        if existing_email:
            flash("Email đã được sử dụng!", "danger")
            return render_template('Administrator/CreateUser.html')
        if existing_phone_number:
            flash("Số điện thoại đã được sử dụng!", "danger")
            return render_template('Administrator/CreateUser.html')
        gender = request.form['gender']
        dob = request.form['DOB']


        password = encrypt_data(request.form['password'])
        role = request.form['role']

        # Tạo bản ghi dựa trên phân quyền
        if role == 'Staff':
            staff_role = request.form['staffRole']
            new_user = Staff(
                name=name,
                gender=gender,
                DOB=dob,
                email=email,
                phoneNumber=phone_number,
                userName=username,
                password=password,
                staffRole=staff_role
            )
        elif role == 'Teacher':
            year_experience = request.form['yearExperience']
            new_user = Teacher(
                name=name,
                gender=gender,
                DOB=dob,
                email=email,
                phoneNumber=phone_number,
                userName=username,
                password=password,
                yearExperience=year_experience
            )
        elif role == 'Administrator':
            admin_role = request.form['adminRole']
            new_user = Administrator(
                name=name,
                gender=gender,
                DOB=dob,
                email=email,
                phoneNumber=phone_number,
                userName=username,
                password=password,
                adminRole=admin_role
            )
        else:
            flash("Vai trò không hợp lệ!", "danger")
            return render_template('Administrator/CreateUser.html')

        # Thêm bản ghi vào cơ sở dữ liệu
        db.session.add(new_user)
        db.session.commit()

        # Gửi email xác nhận
        try:
            # Tạo đối tượng email
            msg = Message(
                subject="Xác nhận đăng ký hệ thống quản lý học sinh!",  # Tiêu đề email
                recipients=[email],  # Người nhận
                # Nội dung email
                body=f"Chào {name},\n\nThông tin tài khoản của bạn là:\n\nUsername: {decrypt_data(username)}\nPassword: {decrypt_data(password)}\n\nChúc bạn một ngày tốt lành!"
            )
            mail.send(msg)  # Gửi email
            flash('Tạo tài khoản thành công và email xác nhận đã được gửi!', 'success')
        except Exception as e:
            flash(f'Đã xảy ra lỗi khi gửi email xác nhận: {str(e)}', 'danger')

        return redirect("/Administrator/CreateUser")  # Redirect sau khi tạo thành công

    return render_template('Administrator/CreateUser.html')


# ============Quản lý người dùng
@login_required
@app.route("/Administrator/UserManagement", methods=["GET", "POST"])
def user_mng():
    users = db.session.query(User).options(
        joinedload(User.staffs),
        joinedload(User.teachers),
        joinedload(User.admins)
    ).all()

    # Xử lý thông tin vai trò người dùng
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

        decrypted_username = decrypt_data(user.userName)

        user_data.append({
            "id": user.id,
            "name": user.name,
            "gender": user.gender,
            "DOB": user.DOB.strftime('%Y-%m-%d') if user.DOB else None,
            "email": user.email,
            "phoneNumber": user.phoneNumber,
            "userName": decrypted_username,
            "role": role,
            "additional_info": additional_info
        })

    return render_template('Administrator/UserManagement.html', users=user_data)


@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        # Lấy dữ liệu từ form
        user.name = request.form.get('name')
        user.gender = request.form.get('gender')
        user.DOB = request.form.get('DOB')
        user.email = request.form.get('email')
        user.phoneNumber = request.form.get('phoneNumber')

        # Cập nhật thông tin vào cơ sở dữ liệu
        db.session.commit()

        # Quay lại trang quản lý người dùng sau khi cập nhật
        return redirect(url_for('user_mng'))

    return render_template('Administrator/edit_user.html', user=user)


@app.route('/delete_user', methods=['POST'])
def delete_user():
    user_id = request.form.get("user_id")  # Lấy user_id từ form

    if not user_id:
        flash("Không tìm thấy người dùng cần xóa.", "danger")
        return redirect("/Administrator/UserManagement")

    # Lấy thông tin người dùng từ bảng User
    user = db.session.get(User, user_id)
    if not user:
        flash("Người dùng không tồn tại.", "warning")
        return redirect("/Administrator/UserManagement")

    try:
        # Xóa bản ghi trong bảng con theo loại người dùng
        # if user.type == "administrator":
        #     db.session.query(Administrator).filter_by(id=user_id).delete(synchronize_session=False)

        if user.type == "staff":
            db.session.query(Staff).filter_by(id=user_id).delete(synchronize_session=False)

        elif user.type == "teacher":
            # Xóa các bản ghi liên quan trong bảng `Teach` trước
            # db.session.query(Teach).filter_by(teacher_id=user_id).delete(synchronize_session=False)
            db.session.query(Teacher).filter_by(id=user_id).delete(synchronize_session=False)

        # Xóa bản ghi cha `User`
        db.session.query(User).filter_by(id=user_id).delete(synchronize_session=False)

        db.session.commit()
        flash("Xóa người dùng thành công!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Đã xảy ra lỗi khi xóa người dùng: {str(e)}", "danger")

    return redirect("/Administrator/UserManagement")


# ============================== MÃ HÓA DỮ LIỆU NGƯỜI DÙNG=====================
# Tạo và lưu khóa vào tệp

# Tải khóa từ tệp
def load_key():
    with open("secret.key", "rb") as key_file:
        return key_file.read()


# Hàm mã hóa
def encrypt_data(data):
    key = load_key()
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(data.encode())
    encrypted_data_base64 = base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
    return encrypted_data_base64


def decrypt_data(encrypted_data_base64):
    try:
        # Giải mã base64 thành dữ liệu mã hóa gốc
        encrypted_data = base64.urlsafe_b64decode(encrypted_data_base64.encode('utf-8'))

        key = load_key()
        fernet = Fernet(key)
        decrypted = fernet.decrypt(encrypted_data)  # Giải mã dữ liệu
        return decrypted.decode()  # Chuyển về chuỗi ban đầu
    except Exception as e:
        print(f"Error during decryption: {e}")
        return None


# =================================================
@login_required
@app.route("/Administrator/TeacherManagement", methods=["GET", "POST"])
def teacher_mng():
    if request.method == 'POST':
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

    teachers = Teacher.query.all()
    subjects = Subject.query.all()
    return render_template('Administrator/TeacherManagement.html', teachers=teachers, subjects=subjects)

@login_required
@app.route("/Administrator/TeachManagement", methods=["GET", "POST"])
def teach_mng():
    if request.method == "POST":
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

        # Truy vấn danh sách giáo viên và lớp học
    teachers = Teacher.query.all()
    classes = Class.query.all()

    return render_template(
        "Administrator/TeachManagement.html", teachers=teachers, classes=classes
    )


# ===========================================END ADMINISTRATOR===============================================================
@login_required
@app.route("/Teacher/EnterPoints", methods=["GET", "POST"])
def enter_point():
    _subject = db.session.query(Subject).filter(Subject.id == current_user.subjectID).first()
    subject_name = _subject.subjectName

    return render_template('Teacher/EnterPoints.html', subject_name=subject_name)
@login_required
@app.route("/Teacher/GenerateTranscript", methods=["GET", "POST"])
def generate_transcript():
    _subject = db.session.query(Subject).filter(Subject.id == current_user.subjectID).first()
    subject_name = _subject.subjectName

    return render_template('Teacher/GenerateTranscript.html', subject_name=subject_name)


@login_required
@app.route("/Teacher/ImportPoints", methods=["GET", "POST"])
def import_points():

    return render_template('Teacher/ImportPoints.html')


@login_required
@app.route("/Teacher/ExportTranscript", methods=["GET", "POST"])
def export_points():

    return render_template('Teacher/ExportTranscript.html')

# staff

@app.route('/InfoUser')
@login_required
def info_user():
    try:
        # Giải mã User Name và Password
        decrypted_username = decrypt_data(current_user.userName)
        decrypted_password = decrypt_data(current_user.password)
    except Exception as e:
        decrypted_username = None
        decrypted_password = None
        print(f"Lỗi khi giải mã dữ liệu: {e}")
    return render_template(
        'staff/InfoUser.html',
        Cuser=current_user,
        decrypted_password = decrypted_password,
        decrypted_username = decrypted_username
    )

@app.route('/password_info', methods=['GET'])
@login_required
def password_info():
    return render_template('staff/PasswordChange.html')


@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    try:
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # Giải mã mật khẩu hiện tại
        decrypted_password = decrypt_data(current_user.password)

        # Kiểm tra mật khẩu hiện tại
        if decrypted_password != current_password:
            flash("Mật khẩu hiện tại không đúng!", "error")
            return redirect(url_for('password_info'))

        # Kiểm tra mật khẩu mới và xác nhận mật khẩu
        if new_password != confirm_password:
            flash("Mật khẩu mới và xác nhận mật khẩu không khớp!", "error")
            return redirect(url_for('password_info'))

        # Cập nhật mật khẩu mới (băm trước khi lưu)
        current_user.password = encrypt_data(new_password)  # Lưu mật khẩu đã mã hóa
        db.session.commit()

        flash("Thay đổi mật khẩu thành công!", "success")
        return redirect(url_for('info_user'))

    except Exception as e:
        db.session.rollback()
        flash(f"Lỗi không mong muốn: {e}", "error")
        return redirect(url_for('password_info'))


@app.route('/student_add', methods=["GET", "POST"])
def staff():
    # Nếu là GET request, chỉ trả về giao diện
    classes = Class.query.all()
    if request.method == "POST":
        # Lấy dữ liệu từ form
        name = request.form.get("name")
        dob = request.form.get("dob")
        try:
            dob_date = datetime.strptime(dob, "%Y-%m-%d")  # Định dạng đúng: YYYY-MM-DD
        except ValueError:
            flash("Ngày sinh không hợp lệ!", "error")
            return redirect(url_for("staff"))

        student_rule = StudentRule.query.first()
        # Kiểm tra tuổi học sinh
        today = datetime.today()
        age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
        if not (student_rule.minAge <= age <= student_rule.maxAge):
            flash(f"Tuổi học sinh phải nằm trong khoảng {student_rule.minAge} đến {student_rule.maxAge} tuổi.",
                      "error")
            return redirect(url_for("staff"))

        gender = request.form.get("gender")
        address = request.form.get("address")
        phone = request.form.get("phone")
        email = request.form.get("email")
        # Kiểm tra dữ liệu bắt buộc
        if not all([name, dob, gender, address, phone]):
            flash("Vui lòng điền đầy đủ thông tin!", "error")
            return redirect(url_for("staff"))
        # Kiểm tra định dạng số điện thoại (chỉ chứa các chữ số 0-9)
        if not phone.isdigit():
            flash("Số điện thoại không không hợp lệ!", "error")
            return redirect(url_for("staff"))
        #kiểm tra số điện thoại có tồn tại chưa
        existing_student = Student.query.filter_by(phone=phone).first()
        if existing_student:
            flash("Số điện thoại này đã tồn tại trong hệ thống!", "error")
            return redirect(url_for("staff"))
        if name.isdigit():
            flash("Họ và tên không hợp lệ!", "error")
            return redirect(url_for("staff"))
        if address.isdigit():
            flash("Địa chỉ không hợp lệ!", "error")
            return redirect(url_for("staff"))
        if email.isdigit():
            flash("Email không hợp lệ!", "error")
            return redirect(url_for("staff"))
        #kiểm tra email
        existing_email = Student.query.filter_by(email=email).first()
        if existing_email:
            flash("Email này đã tồn tại trong hệ thống!", "error")
            return redirect(url_for("staff"))
        # Tạo một đối tượng Student
        new_student = Student(
            name=name,
            DOB=dob,
            gender=gender,
            address=address,
            phone=phone,
            email=email,
            stuRuleID=1
        )

        # Lưu dữ liệu vào database
        try:
            db.session.add(new_student)
            db.session.commit()
            flash("Thêm học sinh thành công!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Có lỗi xảy ra: {str(e)}", "error")
        return redirect(url_for("staff"))
    return render_template('staff/staff.html')

@app.route('/student_edit', methods=["GET", "POST"])
def student_edit():
    students = []
    students_query = Student.query
    if request.method == 'POST':
        student_name = request.form.get('searchStudent', '').strip()
        if student_name:
            # Tìm kiếm theo tên học sinh (không phân biệt chữ hoa/chữ thường)
            students_query = students_query.filter(Student.name.ilike(f'%{student_name}%'))
    students = students_query.all()
    return render_template('staff/StudentEdit.html', students= students)


@app.route('/update_student_NoClass/<int:student_id>', methods=['POST'])
def update_student_NoClass(student_id):
    #lấy id của hs hiện tại
    student = Student.query.get_or_404(student_id)
    check_student = Student.query.filter(Student.id != student.id).all()
    name = request.form.get("name")
    dob = request.form.get("dob")
    gender = request.form.get("gender")
    address = request.form.get("address")
    phone = request.form.get("phone")
    email = request.form.get("email")

    # Kiểm tra dữ liệu bắt buộc
    if not all([name, dob, gender, address, phone]):
        flash("Vui lòng điền đầy đủ thông tin!", "error")
        return redirect(url_for("student_edit"))
    # Kiểm tra định dạng số điện thoại (chỉ chứa các chữ số 0-9)
    if not phone.isdigit():
        flash("Số điện thoại không không hợp lệ!", "error")
        return redirect(url_for("student_edit"))
    # kiểm tra số điện thoại có tồn tại chưa
    existing_student = next((s for s in check_student if s.phone == phone), None)
    if existing_student:
        flash("Số điện thoại này đã tồn tại trong hệ thống!", "error")
        return redirect(url_for("student_edit"))
    if name.isdigit():
        flash("Họ và tên không hợp lệ!", "error")
        return redirect(url_for("student_edit"))
    if address.isdigit():
        flash("Địa chỉ không hợp lệ!", "error")
        return redirect(url_for("student_edit"))
    if email.isdigit():
        flash("Email không hợp lệ!", "error")
        return redirect(url_for("student_edit"))
    # kiểm tra email
    existing_email = next((s for s in check_student if s.email == email), None)
    if existing_email:
        flash("Email này đã tồn tại trong hệ thống!", "error")
        return redirect(url_for("student_edit"))

    # Lấy thông tin học sinh

    # Lấy dữ liệu từ form và cập nhật thông tin học sinh
    student.name = request.form.get('name', student.name)
    student.gender = request.form.get('gender', student.gender)
    student.DOB = request.form.get('dob', student.DOB)
    student.address = request.form.get('address', student.address)
    student.phone = request.form.get('phone', student.phone)
    student.email = request.form.get('email', student.email)


    try:
        dob_date = datetime.strptime(student.DOB, "%Y-%m-%d")  # Định dạng đúng: YYYY-MM-DD
    except ValueError:
        flash("Ngày sinh không hợp lệ!", "error")
        return redirect(url_for("student_edit"))

    student_rule = StudentRule.query.first()
    # Kiểm tra tuổi học sinh
    today = datetime.today()
    age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
    if not (student_rule.minAge <= age <= student_rule.maxAge):
        flash(f"Tuổi học sinh phải nằm trong khoảng {student_rule.minAge} đến {student_rule.maxAge} tuổi.",
              "error")
        return redirect(url_for("student_edit"))


    # Lưu thay đổi vào cơ sở dữ liệu
    try:
        db.session.commit()
        flash('Cập nhật thành công!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi: {e}', 'danger')

    # Điều hướng về trang phù hợp
    return redirect(url_for('student_edit', student_id=student_id))


@app.route('/student_delete/<int:student_id>', methods=['GET','POST'])
def student_delete(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('student_edit'))

@app.route('/student_info/<int:student_id>')
def student_info(student_id):
    student = Student.query.get_or_404(student_id)  # Lấy thông tin học sinh
    return render_template('staff/StudentInfo.html', student=student)


@app.route('/class_edit', methods=['GET', 'POST'])
def class_edit():
    class_list = Class.query.all()
    semester_list = Semester.query.all()
    students = []
    class_id = None
    semester_id = None

    if request.method == 'POST':
        # Lấy các tham số từ form
        class_id = request.form.get('class')
        semester_id = request.form.get('semester')
        student_name = request.form.get('searchStudent', '').strip()

        # Truy vấn lại danh sách học sinh
        if class_id and semester_id and class_id != "none" and semester_id != "none":
            students_query = (
                Student.query.join(StudentClass)
                .filter(
                    StudentClass.class_id == class_id,
                    StudentClass.semester_id == semester_id,
                )
            )
        elif class_id == "none" and semester_id == "none":
            # Lấy danh sách học sinh không có trong bảng StudentClass
            students_query = Student.query.filter(
                ~Student.id.in_(
                    db.session.query(StudentClass.student_id).distinct()
                )
            )
        else:
            flash("Không Có Dữ Liệu Nào!", "error")
            return redirect(url_for("class_edit"))

        if student_name:
            students_query = students_query.filter(Student.name.ilike(f'%{student_name}%'))

        students = students_query.all()

    return render_template(
        'staff/ClassList.html',
        class_list=class_list,
        students=students,
        semester_list=semester_list,
        class_id=class_id,
        semester_id=semester_id
    )
@app.route('/student_delete_class', methods=['POST'])
def student_delete_class():
    student_id = request.form.get('student_id')
    class_id = request.form.get('class_id')
    semester_id = request.form.get('semester_id')
    student_class = None
    if not student_id or not class_id or not semester_id:
        flash("Thông tin không đầy đủ!", "error")
        return redirect(url_for('class_edit'))
    if class_id == "none" and semester_id == "none":
        student_class = Student.query.get_or_404(student_id)
    else:
        student_class = StudentClass.query.filter_by(
            student_id=student_id,
            class_id=class_id,
            semester_id=semester_id
        ).first()

    if not student_class:
        flash("Không tìm thấy học sinh trong lớp!", "error")
        return redirect(url_for('class_edit'))

    db.session.delete(student_class)
    db.session.commit()

    flash("Học sinh đã được xóa khỏi lớp thành công!", "success")

    return redirect(url_for('class_edit'))

@app.route('/student_class_info/<int:student_id>', methods=['GET', 'POST'])
def student_class_info(student_id):
    # Lấy tham số class_id và semester_id từ request arguments (GET/POST)
    class_id = request.args.get('class_id', None)
    semester_id = request.args.get('semester_id', None)

    # Lấy thông tin sinh viên
    student = Student.query.get_or_404(student_id)

    # Truy vấn thông tin lớp và học kỳ hiện tại
    if class_id and semester_id:
        student_class = StudentClass.query.filter_by(
            student_id=student_id,
            class_id=class_id,
            semester_id=semester_id
        ).first()
    else:
        student_class = None

    current_class_id = student_class.class_id if student_class else None
    current_semester_id = student_class.semester_id if student_class else None

    # Lấy danh sách tất cả các lớp và học kỳ
    all_classes = Class.query.all()
    all_semesters = Semester.query.all()

    return render_template(
        'staff/StudentClassInfo.html',
        student=student,
        classes=all_classes,
        semesters=all_semesters,
        current_class_id=current_class_id,
        current_semester_id=current_semester_id
    )
@app.route('/update_student/<int:student_id>', methods=['POST'])
def update_student(student_id):

    # lấy id của hs hiện tại
    student = Student.query.get_or_404(student_id)
    check_student = Student.query.filter(Student.id != student.id).all()
    name = request.form.get("name")
    dob = request.form.get("dob")
    gender = request.form.get("gender")
    address = request.form.get("address")
    phone = request.form.get("phone")
    email = request.form.get("email")

    # Kiểm tra dữ liệu bắt buộc
    if not all([name, dob, gender, address, phone]):
        flash("Vui lòng điền đầy đủ thông tin!", "error")
        return redirect(url_for("class_edit"))
    # Kiểm tra định dạng số điện thoại (chỉ chứa các chữ số 0-9)
    if not phone.isdigit():
        flash("Số điện thoại không không hợp lệ!", "error")
        return redirect(url_for("class_edit"))
    # kiểm tra số điện thoại có tồn tại chưa
    existing_student = next((s for s in check_student if s.phone == phone), None)
    if existing_student:
        flash("Số điện thoại này đã tồn tại trong hệ thống!", "error")
        return redirect(url_for("class_edit"))
    if name.isdigit():
        flash("Họ và tên không hợp lệ!", "error")
        return redirect(url_for("class_edit"))
    if address.isdigit():
        flash("Địa chỉ không hợp lệ!", "error")
        return redirect(url_for("class_edit"))
    if email.isdigit():
        flash("Email không hợp lệ!", "error")
        return redirect(url_for("class_edit"))
    # kiểm tra email
    existing_email = next((s for s in check_student if s.email == email), None)
    if existing_email:
        flash("Email này đã tồn tại trong hệ thống!", "error")
        return redirect(url_for("class_edit"))

    # Lấy thông tin học sinh

    # Lấy dữ liệu từ form
    student.name = request.form.get('name', student.name)
    student.gender = request.form.get('gender', student.gender)
    student.DOB = request.form.get('dob', student.DOB)
    student.address = request.form.get('address', student.address)
    student.phone = request.form.get('phone', student.phone)
    student.email = request.form.get('email', student.email)

    # Kiểm tra ngày sinh
    try:
        dob_date = datetime.strptime(student.DOB, "%Y-%m-%d")
    except ValueError:
        flash("Ngày sinh không hợp lệ! Định dạng phải là YYYY-MM-DD.", "error")
        return redirect(url_for("class_edit", student_id=student_id))

    # Kiểm tra tuổi học sinh
    student_rule = StudentRule.query.first()
    today = datetime.today()
    age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
    if not (student_rule.minAge <= age <= student_rule.maxAge):
        flash(f"Tuổi học sinh phải nằm trong khoảng {student_rule.minAge} đến {student_rule.maxAge}.", "error")
        return redirect(url_for("class_edit", student_id=student_id))

    # Lấy thông tin lớp và học kỳ từ form
    class_id = request.form.get('class')
    semester_id = request.form.get('semester')

    if class_id == "none" or semester_id == "none":
        flash("Không được để trống lớp hoặc học kỳ!", "error")
        return redirect(url_for("class_edit", student_id=student_id))

    # Kiểm tra số lượng học sinh trong lớp và học kỳ
    current_class = Class.query.get_or_404(class_id)
    current_students_count = StudentClass.query.filter_by(class_id=class_id, semester_id=semester_id).count()

    if current_students_count >= current_class.classRule_class.maxNoStudent:
        flash(f"Lớp {current_class.className} đã đạt tối đa số lượng học sinh ({current_class.classRule_class.maxNoStudent}).", "error")
        return redirect(url_for("class_edit", student_id=student_id))

    # Kiểm tra và xử lý StudentClass
    student_class = StudentClass.query.filter_by(student_id=student_id, semester_id=semester_id).first()

    if student_class:
        # Nếu tồn tại, cập nhật thông tin lớp
        student_class.class_id = class_id
    else:
        # Nếu không tồn tại, tạo mới StudentClass
        student_class = StudentClass(
            student_id=student_id,
            class_id=class_id,
            semester_id=semester_id,
        )
        db.session.add(student_class)

    # Lưu thay đổi vào cơ sở dữ liệu
    try:
        db.session.commit()
        flash('Cập nhật thành công!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi khi cập nhật: {e}', 'danger')

    # Điều hướng trở lại trang quản lý học sinh
    return redirect(url_for('class_edit', student_id=student_id))


@app.route('/Teacher/EnterPoints/class_filter', methods=['POST', 'GET'])
def class_filter():
    _subject = db.session.query(Subject).filter(Subject.id == current_user.subjectID).first()
    subject_name = _subject.subjectName
    students = []  # Khởi tạo danh sách sinh viên rỗng hoặc có thể là danh sách mặc định nếu cần
    error = None
    if request.method =='POST':
        # Lấy dữ liệu từ form
        class_name = request.form.get('class-input')
        semester_name = request.form.get('semester-input')
        year = request.form.get('academic-year-input')

        # Kiểm tra dữ liệu từ form
        if not class_name or not semester_name or not year:
            return render_template(
                'Teacher/EnterPoints.html',
                error="Vui lòng nhập đầy đủ lớp, học kỳ và năm học!",
            )

        # Tìm lớp và học kỳ
        _class = db.session.query(Class).filter(Class.className == class_name).first()
        _semester = db.session.query(Semester).filter(Semester.semesterName == semester_name,
                                                      Semester.year == year).first()

        # Kiểm tra dữ liệu lớp hoặc học kỳ
        if not _class or not _semester:
            return render_template(
                'Teacher/EnterPoints.html',
                error="Không tìm thấy lớp hoặc học kỳ phù hợp!",
            )
        session['semester_id'] = _semester.id
        # Lấy danh sách học sinh
        students = db.session.query(Student).join(StudentClass).filter(
            StudentClass.class_id == _class.id,
            StudentClass.semester_id == _semester.id
        ).all()

        # Kiểm tra nếu không có sinh viên
        if not students:
            return render_template(
                'Teacher/EnterPoints.html',
                error="Không tìm thấy sinh viên trong lớp và học kỳ này!",
            )

    # Trả về template với danh sách sinh viên
    return render_template('Teacher/ImportPoints.html', students=students, subject_name = subject_name,error = error)


@app.route('/Teacher/EnterPoints/save_points', methods=['POST'])
def save_points():
    try:
        # Lấy danh sách dữ liệu từ form
        student_ids = request.form.getlist('student_ids[]')
        scores_15min = request.form.getlist('scores_15min[]')
        scores_test = request.form.getlist('scores_test[]')
        scores_exam = request.form.getlist('scores_exam[]')
        semester_id = session.get('semester_id')

        # Kiểm tra dữ liệu đầu vào
        if len(scores_15min) % len(student_ids) != 0 or len(scores_test) % len(student_ids) != 0:
            flash("Dữ liệu điểm không đồng bộ với số lượng học sinh.", "danger")
            return redirect(url_for('class_filter'))

        # Lặp qua từng học sinh
        for i, student_id in enumerate(student_ids):
            # Xử lý điểm 15 phút
            start_idx_15min = i * len(scores_15min) // len(student_ids)
            end_idx_15min = start_idx_15min + len(scores_15min) // len(student_ids)
            student_scores_15min = scores_15min[start_idx_15min:end_idx_15min]
            for score in student_scores_15min:
                if score:
                    db.session.add(
                        Point(
                            pointValue=float(score),
                            pointTypeID=1,
                            semesterID=semester_id,
                            subjectID=current_user.subjectID,
                            studentID=student_id
                        )
                    )

            # Xử lý điểm 1 tiết
            start_idx_test = i * len(scores_test) // len(student_ids)
            end_idx_test = start_idx_test + len(scores_test) // len(student_ids)
            student_scores_test = scores_test[start_idx_test:end_idx_test]
            for score in student_scores_test:
                if score:
                    db.session.add(
                        Point(
                            pointValue=float(score),
                            pointTypeID=2,
                            semesterID=semester_id,
                            subjectID=current_user.subjectID,
                            studentID=student_id
                        )
                    )

            # Xử lý điểm thi
            point_exam = scores_exam[i] if i < len(scores_exam) else None
            if point_exam:
                db.session.add(
                    Point(
                        pointValue=float(point_exam),
                        pointTypeID=3,
                        semesterID=semester_id,
                        subjectID=current_user.subjectID,
                        studentID=student_id
                    )
                )

        # Lưu thay đổi vào DB
        db.session.commit()
        flash("Lưu điểm thành công!", "success")
        return redirect(url_for('class_filter'))

    except SQLAlchemyError as db_err:
        db.session.rollback()
        flash(f"Lỗi cơ sở dữ liệu: {db_err}", "danger")
    except ValueError as val_err:
        flash(f"Lỗi dữ liệu đầu vào: {val_err}", "danger")
    except Exception as e:
        flash(f"Có lỗi xảy ra: {e}", "danger")

    return redirect(url_for('class_filter'))




@app.route("/Teacher/GenerateTranscript/generate", methods=["GET", "POST"])
def generate():
    # Lấy thông tin môn học của giáo viên hiện tại
    _subject = db.session.query(Subject).filter(Subject.id == current_user.subjectID).first()
    subject_name = _subject.subjectName
    students = []  # Khởi tạo danh sách sinh viên rỗng
    student_scores = {}  # Khởi tạo dictionary lưu điểm của sinh viên
    averages = {}  # Khởi tạo dictionary lưu điểm trung bình của sinh viên
    error = None

    if request.method == 'POST':
        # Lấy dữ liệu từ form
        class_name = request.form.get('class-input')
        semester_name = request.form.get('semester-input')
        year = request.form.get('academic-year-input')

        # Kiểm tra dữ liệu từ form
        if not class_name or not semester_name or not year:
            return render_template(
                'Teacher/GenerateTranscript.html',
                error="Vui lòng nhập đầy đủ lớp, học kỳ và năm học!"
            )

        # Tìm lớp và học kỳ từ dữ liệu nhập vào
        _class = db.session.query(Class).filter(Class.className == class_name).first()
        _semester = db.session.query(Semester).filter(Semester.semesterName == semester_name,
                                                      Semester.year == year).first()

        # Kiểm tra nếu không tìm thấy lớp hoặc học kỳ
        if not _class or not _semester:
            return render_template(
                'Teacher/GenerateTranscript.html',
                error="Không tìm thấy lớp hoặc học kỳ phù hợp!"
            )

        # Lấy danh sách học sinh trong lớp và học kỳ
        students = db.session.query(Student).join(StudentClass).filter(
            StudentClass.class_id == _class.id,
            StudentClass.semester_id == _semester.id
        ).all()

        # Lấy điểm của các học sinh
        for student in students:
            points = db.session.query(Point).filter(
                Point.studentID == student.id,
                Point.subjectID == _subject.id,
                Point.semesterID == _semester.id
            ).all()
            student_scores[student.id] = points  # Lưu điểm của từng học sinh

        # Tính điểm trung bình cho từng sinh viên
        for student in students:
            average = calculate_average(student.id, _subject.id, _semester.id)
            averages[student.id] = average

    return render_template('Teacher/ExportTranscript.html', subject_name=subject_name, students=students,
                           student_scores=student_scores, averages=averages, error=error)

@app.route('/Teacher/ExportTranscript/export_pdf', methods=['GET'])
def export_pdf():
    # Tạo PDF trong bộ nhớ

    font_path = 'static/fonts/Arial.ttf'  # Đảm bảo đường dẫn chính xác tới file .ttf
    pdfmetrics.registerFont(TTFont('Arial', font_path))

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    c.setFont("Arial", 12)

    # Dữ liệu điểm cần xuất (ví dụ từ cơ sở dữ liệu)
    students = db.session.query(Student).all()  # Lấy danh sách sinh viên từ cơ sở dữ liệu
    y_position = 750  # Vị trí y để in trên PDF

    c.drawString(100, y_position, "Danh sách điểm sinh viên")
    y_position -= 20

    # Thêm tiêu đề cột
    c.drawString(100, y_position, "Tên Sinh Viên")
    c.drawString(300, y_position, "Điểm 15 phút")
    c.drawString(400, y_position, "Điểm Kiểm Tra")
    c.drawString(500, y_position, "Điểm Thi")
    y_position -= 20

    # Lặp qua sinh viên và in điểm
    for student in students:
        c.drawString(100, y_position, student.name)
        # Giả sử bạn đã có các điểm trong cơ sở dữ liệu
        points = db.session.query(Point).filter(Point.studentID == student.id).all()
        c.drawString(300, y_position, str(points[0].pointValue if points else ''))
        c.drawString(400, y_position, str(points[1].pointValue if len(points) > 1 else ''))
        c.drawString(500, y_position, str(points[2].pointValue if len(points) > 2 else ''))
        y_position -= 20

    c.showPage()
    c.save()

    # Trả về PDF dưới dạng file
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="diem_sinh_vien.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
