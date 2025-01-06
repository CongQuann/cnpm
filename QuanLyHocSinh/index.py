import string
from datetime import datetime
import random

from select import select
from werkzeug.security import generate_password_hash, check_password_hash
from flask import render_template, request, redirect, flash, url_for, jsonify, Flask
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
from reportlab.lib import colors
from sqlalchemy.exc import SQLAlchemyError


from QuanLyHocSinh import app, db, dao, utils
from QuanLyHocSinh.dao import get_semester_info, get_subject_name, get_classes, get_student_classes, is_student_passed, \
    calculate_average, get_class_rule, get_student_rule, update_rules, existing_subject_check, add_new_subject, \
    get_subject, delete_subject_by_id, get_subject_by_id, check_existing_subject_name, update_subject_info, \
    existing_user_check, existing_email_check, existing_phone_check, create_user_by_role, send_email, get_user_data, \
    delete_user_by_id, teacher_subject_update, get_teacher, update_class_to_teacher
from QuanLyHocSinh.models import Class, Student, User, Staff, Subject, Semester, StudentRule, ClassRule, Point, \
    Teacher, Administrator, StudentClass, Teach
# Khởi tạo LoginManager để quản lý quá trình đăng nhập
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/'  # Đường dẫn để chuyển hướng khi chưa đăng nhập
mail = Mail(app)

# Middleware kiểm tra việc đăng nhập trước khi truy cập các route được bảo vệ
@app.before_request
def restrict_routes():

    #Bảo vệ các route được chỉ định, yêu cầu người dùng phải đăng nhập trước khi truy cập.
    #Nếu người dùng chưa đăng nhập, họ sẽ được chuyển hướng đến trang đăng nhập.

    # Danh sách các tiền tố của route cần bảo vệ
    protected_prefixes = ['/Administrator', '/Teacher', '/staff']

    # Kiểm tra nếu route hiện tại bắt đầu với bất kỳ tiền tố nào trong danh sách
    if any(request.path.startswith(prefix) for prefix in protected_prefixes):
        # Nếu người dùng chưa đăng nhập, chuyển hướng đến trang đăng nhập
        if not current_user.is_authenticated:
            return redirect(url_for('login'))

# Middleware kiểm tra quyền truy cập dựa trên vai trò của người dùng
@app.before_request
def restrict_by_role():
    """
    Giới hạn quyền truy cập vào các route dựa trên loại tài khoản người dùng.
    Hiển thị thông báo lỗi nếu người dùng không có quyền truy cập.
    """
    # Danh sách route dành cho từng loại người dùng
    admin_routes = ['/Administrator']  # Chỉ dành cho quản trị viên
    staff_routes = ['/staff']          # Chỉ dành cho nhân viên
    teacher_routes = ['/Teacher']      # Chỉ dành cho giáo viên

    # Kiểm tra nếu người dùng truy cập các route quản trị nhưng không phải quản trị viên
    if any(request.path.startswith(prefix) for prefix in admin_routes) and current_user.type != 'administrator':
        return "Bạn không có quyền truy cập vào các trang quản trị.", 403 #trả về lỗi truy cập quyền hạn

    # Kiểm tra nếu người dùng truy cập các route nhân viên nhưng không phải nhân viên
    if any(request.path.startswith(prefix) for prefix in staff_routes) and current_user.type != 'staff':
        return "Bạn không có quyền truy cập vào các trang nhân viên.", 403

    # Kiểm tra nếu người dùng truy cập các route giáo viên nhưng không phải giáo viên
    if any(request.path.startswith(prefix) for prefix in teacher_routes) and current_user.type != 'teacher':
        return "Bạn không có quyền truy cập vào các trang giáo viên.", 403


@login_manager.user_loader
def load_user(user_id):
    #hàm tải người dùng từ cơ sở dữ liệu dựa trên id của người dùng
    return User.query.get(int(user_id))


@app.route("/", methods=["GET", "POST"])
def login():
    #Xử lý logic đăng nhập người dùng
    #nếu là Get thì hiển thị trang đăng nhập, nếu là Post thì xử lý thông tin đăng nhập và phân quyền người dùng
    if request.method == "POST": #Xử lý khi người dùng nhấn đăng nhập
        #lấy thông tin username và password
        username = request.form['username']
        password = request.form['password']

        # Lấy danh sách tất cả người dùng
        users = User.query.all()

        # Duyệt qua tất cả người dùng để tìm người dùng khớp với username đã giải mã
        for user in users:
             # Giải mã tên đăng nhập trong cơ sở dữ liệu

            if user.userName == username:  # Nếu username khớp
                #Kiểm tra mật khẩu và phân quyền dựa trên thuộc tính loại tài khoản
                if check_password_hash(user.password, password) and user.type == 'administrator':
                    #Nếu mật khẩu đúng và loại tài khoản là quản trị viên thì thực hiện login và chuyển hướng đến trang quản trị viên
                    login_user(user)
                    return redirect("/Administrator/Report")
                elif check_password_hash(user.password, password) and user.type == 'teacher':
                    login_user(user)
                    return redirect("/Teacher/EnterPoints")
                elif check_password_hash(user.password, password) and user.type == 'staff':
                    login_user(user)
                    return redirect("/staff/class_edit")
        #Nếu thông tin đăng nhập không trùng khớp thì hiển thị thông báo lỗi
        flash('Tên đăng nhập hoặc mật khẩu không đúng!',"danger")
        #Nếu get hoặc đăng nhập thất bại thì hiển thị lại trang đăng nhập
    return render_template('index.html')

@app.route("/logout")
@login_required #phải đảm bảo người dùng đã đăng nhập trước khi đăng xuất
def logout():
    logout_user() #Thực hiện đăng xuất người dùng
    session.clear()  # Xóa tất cả dữ liệu phiên
    return redirect("/") #thực hiện điều hướng về trang đăng nhập


# Route lấy lại mật khẩu
@app.route('/forgot-password/<int:step>', methods=['GET', 'POST'])
def forgot_password(step):
    #Bước 1: Nhập tên tài khoản và gửi mã xác nhận
    #Bước 2: Nhập mã xác nhận để xác minh tài khoản
    #Bước 3: Đặt lại mật khẩu mới cho tài khoản
    if step == 1: #Bước 1
        if request.method == 'POST': #Nếu người dùng gửi form
            username = request.form['username'] #Thực hiện lấy username từ form
            user = None #tạo biến để lưu người dùng nếu tìm thấy
            users = User.query.all() #lấy tất cả người dùng
            for i in users:#duyệt qua từng người dùng
                if i.userName==username: # Nếu username của người dùng và của form khớp thì gán người dùng cho biến user
                    user = i
            if not user: #nếu không tìm được người dùng thì hiển thị thông báo không tồn tại và khởi động lại trang này
                flash("Tên tài khoản không tồn tại!", "danger")
                return render_template('Administrator/forgot_password.html', step=1)

            # Tạo mã xác nhận và gán cho thuộc tính verification code của người dùng
            verification_code = ''.join(random.choices(string.digits, k=6))
            user.verification_code = verification_code
            db.session.commit()

            # Gửi mã xác nhận qua email
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
            except Exception as e: #Thông báo lỗi nếu có lỗi xảy ra
                flash(f'Đã xảy ra lỗi khi gửi mã xác nhận: {str(e)}', 'danger')

            return redirect(url_for('forgot_password', step=2, username=username)) #chuyển hướng về html bước tiếp theo với tham số username

        return render_template('Administrator/forgot_password.html', step=1)

    elif step == 2:
        username = request.args.get('username') #lấy username từ tham số trên URL
        if not username: #nếu không thấy username thì thực hiện lại bước 1
            flash("Vui lòng bắt đầu lại quy trình!", "danger")
            return redirect(url_for('forgot_password', step=1))

        if request.method == 'POST':
            user = None
            users = User.query.all()
            for i in users:

                if i.userName==username:  # Nếu username khớp, gán người dùng đó cho user
                    user = i
            input_code = request.form['verification_code'] # gán mã xác nhận mà người dùng nhập trên form
            if not user or input_code != user.verification_code: #nếu không tồn tại người dùng hoặc biến chứa mã xác nhận không trùng khớp
                flash("Mã xác nhận không đúng!", "danger")
                return render_template('Administrator/forgot_password.html', step=2, username=username)# khởi động lại trang hiện tại
            #nếu các thông tin trùng khớp thì chuyển sang html bước tiếp theo
            flash("Mã xác nhận hợp lệ! Hãy đặt lại mật khẩu.", "success")
            return redirect(url_for('forgot_password', step=3, username=username))
        #nếu phương thức là GET thì hiển thị giao diện
        return render_template('Administrator/forgot_password.html', step=2, username=username)

    elif step == 3: #nếu tham số step ở bước 3
        username = request.args.get('username')
        if not username:
            flash("Vui lòng bắt đầu lại quy trình!", "danger")
            return redirect(url_for('forgot_password', step=1))

        if request.method == 'POST':
            user = None
            users = User.query.all()
            for i in users:
                if i.userName==username:  # Nếu username khớp
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
            user.password = generate_password_hash(new_password) #thực hiện mã hóa
            user.verification_code = None  # Xóa mã xác nhận
            db.session.commit()
            flash("Đặt lại mật khẩu thành công!", "success")
            return redirect("/") #chuyển hướng về trang đăng nhập

        return render_template('Administrator/forgot_password.html', step=3, username=username)
# ===========================================================ADMINISTRATOR================================================

@login_required
@app.route("/Administrator/Report", methods=["GET", "POST"])
def report():
    # Lấy tất cả các môn học và học kỳ
    subject_list = Subject.query.all()
    semester_list = Semester.query.all()

    #Khởi tạo danh sách thống kê và thông tin cơ bản
    statistics = []
    subject_name = None
    semester_name = None
    year = None

    #Xử lý khi nhận yêu cầu từ form
    if request.method == "POST":
        #lấy môn học và học kì đã chọn từ form
        selected_subject = request.form.get('subject')
        selected_semester = request.form.get('semester')

        #Nếu cả hai đều được chọn giá trị
        if selected_subject and selected_semester:
            subject_id = selected_subject
            semester_id = selected_semester

            #Lấy thông tin chi tiết từ cơ sở dữ liệu thông qua giá trị id đã chọn trên form
            semester = get_semester_info(semester_id)
            subject_name = get_subject_name(subject_id)
            semester_name = semester.semesterName
            year = semester.year

            classes = get_classes()# lấy danh sách lớp

            for cls in classes: #duyệt qua từng lớp để thực hiện tính toán thống kê
                student_classes = get_student_classes(cls.id, semester_id) #lấy danh sách học sinh trong lớp học
                num_students = len(student_classes) #lấy số lượng học sinh
                num_passed = sum(
                    #thống kê số lượng đạt
                    is_student_passed(student_class.student_id, subject_id, semester_id) #nếu đạt thì +1 vào sum
                    for student_class in student_classes
                )

                #tính tỷ lệ đạt
                pass_rate = (num_passed / num_students * 100) if num_students > 0 else 0

                #thêm thống kê của lớp vào danh sách statistic
                statistics.append({
                    "class_name": cls.className,
                    "total_students": num_students,
                    "num_passed": num_passed,
                    "pass_rate": f"{pass_rate:.2f}%"
                })

    #trả về giao diện với dữ liệu báo cáo thống kê
    return render_template(
        'Administrator/Report.html',
        subjects=subject_list,
        semesters=semester_list,
        selected_subject=request.form.get('subject', None),
        selected_semester=request.form.get('semester', None),
        statistics=statistics,
        subject_name=subject_name,
        semester_name=semester_name,
        year=year
    )
# ========================================

@login_required
@app.route("/Administrator/RuleManagement", methods=["GET", "POST"])
def rule():
    if request.method == "POST": #nêú người dùng thực hiện gửi form
        # Lấy dữ liệu từ form
        min_age = request.form.get("min_age")
        max_age = request.form.get("max_age")
        max_class_size = request.form.get("max_class_size")

        # Kiểm tra giá trị nhập vào
        if int(max_age) < int(min_age): #nếu tuổi tối đa nhỏ hơn tối thiểu
            flash("Tuổi tối đa không được nhỏ hơn tuổi tối thiểu!", "warning")
            return redirect("/Administrator/RuleManagement")
        if int(max_class_size) <= 0: #nếu sĩ số lớp <=0
            flash("Sĩ số tối đa phải lớn hơn 0!", "warning")
            return redirect("/Administrator/RuleManagement")

        # Cập nhật quy định
        success = update_rules(min_age, max_age, max_class_size) #thực hiện hàm cập nhật

        #nêu thành công thì thông báo thành công, ngược lại thông báo không thành công
        if success:
            flash("Quy định đã được cập nhật thành công!", "success")
        else:
            flash("Không thể cập nhật quy định. Vui lòng kiểm tra lại!", "error")

        return redirect("/Administrator/RuleManagement")

    # Xử lý GET request
    class_rule = get_class_rule() #lấy thông tin quy định lớp học
    student_rule = get_student_rule()# lấy thông tin quy định học sinh

    return render_template(
        "Administrator/RuleManagement.html",
        class_rule=class_rule,
        student_rule=student_rule,
    )

@login_required
@app.route("/Administrator/SubjectManagement", methods=["GET", "POST"])
def subject_mng():
    if request.method == "POST": #nếu người dùng chọn thêm môn học
        subject_name = request.form.get("subject_name")  # Lấy tên môn học từ form

        if not subject_name:
            flash("Tên môn học không được để trống!", "danger")
            return redirect("/Administrator/SubjectManagement")

        # Kiểm tra xem môn học đã tồn tại chưa

        if existing_subject_check(subject_name):
            flash("Môn học đã tồn tại!", "warning")
            return redirect("/Administrator/SubjectManagement")

        # Thêm môn học mới vào cơ sở dữ liệu
        try:
            add_new_subject(subject_name)
            flash("Thêm môn học thành công!", "success")
            return redirect("/Administrator/SubjectManagement")
        except Exception as e:
            db.session.rollback()
            flash("Có lỗi xảy ra khi thêm môn học.", "danger")

        return redirect("/Administrator/SubjectManagement")

    # Nếu là GET, trả về giao diện
    get_subject() #lấy tất cả môn học
    return render_template('Administrator/SubjectManagement.html', subjects=get_subject())


# ======Thêm route xử lý để xóa môn học=======
@app.route("/Administrator/SubjectManagement/delete", methods=["GET", "POST"])
def delete_subject():
    subject_id = request.form.get("subject_id")  # Lấy subject_id từ input hidden của môn học đó


    # Tìm môn học trong cơ sở dữ liệu
    if not get_subject_by_id(subject_id):
        flash("Môn học không tồn tại.", "warning")
        return redirect("/Administrator/SubjectManagement")

    # Xóa môn học
    try:
        delete_subject_by_id(subject_id) #thực hiện hàm xóa môn học
        flash("Xóa môn học thành công!", "success")
    except Exception as e:
        db.session.rollback()
        print("Error:", e)  # In ra lỗi chi tiết
        flash("Có lỗi xảy ra khi xóa môn học.", "danger")

    return redirect("/Administrator/SubjectManagement")


# ============Phần chỉnh sửa môn học
@app.route("/Administrator/SubjectManagement/edit/<int:subject_id>")  # route để gọi ra trang chỉnh sửa
def edit_subject_page(subject_id):
    subject = get_subject_by_id(subject_id)# lấy tên môn học bằng id
    if not subject:
        flash("Môn học không tồn tại.", "warning")
        return redirect("/Administrator/SubjectManagement")
    return render_template("Administrator/edit_subject.html", subject=subject)


@app.route("/Administrator/SubjectManagement/update",
           methods=["POST"])  # route chứa hàm thực hiện chức năng của trang chỉnh sửa
def update_subject():
    subject_id = request.form.get("subject_id") #lấy id môn học từ input hidden của form
    subject_name = request.form.get("subject_name") #lấy tên môn học
    subject_requirement = request.form.get("subject_requirement") #lấy yêu cầu môn học
    subject_description = request.form.get("subject_description") #lấy mô tả môn học
    # Xử lý cập nhật
    subject = get_subject_by_id(subject_id) #lấy môn học bằng id
    if not subject:
        flash("Không tìm thấy môn học.", "warning")
        return redirect("/Administrator/SubjectManagement")

    try:
        #kiểm tra môn học có thay đổi hay không
        if check_existing_subject_name(subject_name,subject):
            flash("Tên môn học đã được sử dụng!","warning")
            return redirect(url_for('edit_subject_page'))

        #cập nhật các môn học
        update_subject_info(subject,subject_name,subject_requirement,subject_description) #thực hiện cập nhật
        flash("Cập nhật thành công!", "success")
    except Exception as e:
        db.session.rollback()
        print("Error:", e)  # In ra lỗi chi tiết
        flash("Lỗi trong quá trình cập nhật.", "danger")
    return redirect("/Administrator/SubjectManagement")


# =====================================


#route tạo người dùng
@app.route('/Administrator/CreateUser', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        # Lấy thông tin từ form
        name = request.form['name']
        username = request.form['userName']
        email = request.form['email']
        phone_number = request.form['phoneNumber']

        # Kiểm tra nếu các thông tin đã tồn tại
        if existing_user_check(username):
            flash("Tên đăng nhập đã được sử dụng!", "danger")
            return render_template('Administrator/CreateUser.html')
        if existing_email_check(email):
            flash("Email đã được sử dụng!", "danger")
            return render_template('Administrator/CreateUser.html')
        if existing_phone_check(phone_number):
            flash("Số điện thoại đã được sử dụng!", "danger")
            return render_template('Administrator/CreateUser.html')
        gender = request.form['gender']
        dob = request.form['DOB']

        password = request.form['password']
        hashed_password = generate_password_hash(request.form['password']) #mã hóa mật khẩu người dùng
        role = request.form['role']
        staff_role = request.form['staffRole']
        year_experience = request.form['yearExperience']
        admin_role = request.form['adminRole']
        # Tạo bản ghi dựa trên phân quyền
        create_user_by_role(role,name,gender,dob,email,phone_number,username,hashed_password,staff_role,year_experience,admin_role)

        # Gửi email xác nhận
        send_email(name,username,email,password)
        return redirect("/Administrator/UserManagement")  # Redirect sau khi tạo thành công
    return render_template('Administrator/CreateUser.html')


# ============Quản lý người dùng
@login_required
@app.route("/Administrator/UserManagement", methods=["GET", "POST"])
def user_mng():
    # Gọi hàm từ dao.py để lấy dữ liệu người dùng
    users = get_user_data()

    # Render template và truyền dữ liệu vào
    return render_template('Administrator/UserManagement.html', users=users)

#hàn chỉnh sửa người dùng dựa vào id người dùng trong trang quản lý người dùng
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
@login_required
def delete_user():
    user_id = request.form.get("user_id")  # Lấy user_id từ form

    if not user_id:
        flash("Không tìm thấy người dùng cần xóa.", "danger")
        return redirect("/Administrator/UserManagement")

    # Gọi hàm từ dao.py để xóa người dùng
    result = delete_user_by_id(user_id)

    if result:
        flash("Xóa người dùng thành công!", "success")
    else:
        flash(f"Đã xảy ra lỗi khi xóa người dùng: {result}", "danger")

    return redirect("/Administrator/UserManagement")




# =================================================
@login_required
@app.route("/Administrator/TeacherManagement", methods=["GET", "POST"])
def teacher_mng():
    if request.method == 'POST':
        teacher_subject_update() #Xử lý cập nhật môn học cho giáo viên

    return render_template('Administrator/TeacherManagement.html', teachers=get_teacher(), subjects=get_subject())

@login_required
@app.route("/Administrator/TeachManagement", methods=["GET", "POST"])
def teach_mng():
    if request.method == "POST":
        # Xử lý thêm lớp cho giáo viên
       update_class_to_teacher()



    return render_template(
        "Administrator/TeachManagement.html", teachers=get_teacher(), classes=get_classes()
    )


# ===========================================END ADMINISTRATOR===============================================================
@login_required
@app.route("/Teacher/EnterPoints", methods=["GET", "POST"])
def enter_point():
    # Kiểm tra nếu người dùng không có subjectID (không phải giáo viên hoặc chưa được gán môn học)
    if not hasattr(current_user, 'subjectID'):
        flash("Bạn chưa được cấp chuyên môn. Vui lòng liên hệ quản trị viên!", "error")
        return render_template('Teacher/EnterPoints.html', subject_name='')

    # Lấy thông tin môn học của giáo viên hiện tại
    _subject = db.session.query(Subject).filter(Subject.id == current_user.subjectID).first()

    # Kiểm tra nếu không tìm thấy môn học (trường hợp dữ liệu không nhất quán)
    if not _subject:
        flash("Bạn chưa được cấp chuyên môn. Vui lòng liên hệ quản trị viên!", "error")
        return render_template('Teacher/EnterPoints.html', subject_name='')

    semesters = Semester.query.all()
    classes = Class.query.all()
    class_name= sorted({classindex.className for classindex in classes})
    unique_years = sorted({semester.year for semester in semesters}, key=None, reverse=True)
    unique_semesters = sorted({semester.semesterName for semester in semesters})
    subject_name = _subject.subjectName




    return render_template('Teacher/EnterPoints.html', subject_name=subject_name, unique_semesters=unique_semesters, unique_years=unique_years, class_name=class_name)


@login_required
@app.route("/Teacher/GenerateTranscript", methods=["GET", "POST"])
def generate_transcript():
    if not hasattr(current_user, 'subjectID'):
        flash("Bạn chưa được cấp chuyên môn. Vui lòng liên hệ quản trị viên!", "error")
        return render_template('Teacher/GenerateTranscript.html', subject_name='')

    # Lấy thông tin môn học của giáo viên hiện tại
    _subject = db.session.query(Subject).filter(Subject.id == current_user.subjectID).first()

    # Kiểm tra nếu không tìm thấy môn học (trường hợp dữ liệu không nhất quán)
    if not _subject:
        flash("Bạn chưa được cấp chuyên môn. Vui lòng liên hệ quản trị viên!", "error")
        return render_template('Teacher/GenerateTranscript.html', subject_name='')
    semesters = Semester.query.all()
    classes = Class.query.all()
    class_name = sorted({classindex.className for classindex in classes})
    unique_years = sorted({semester.year for semester in semesters}, key=None, reverse=True)
    unique_semesters = sorted({semester.semesterName for semester in semesters})
    # Nếu có môn học, lấy tên môn học
    subject_name = _subject.subjectName

    return render_template('Teacher/GenerateTranscript.html', subject_name=subject_name,unique_semesters=unique_semesters, unique_years=unique_years, class_name=class_name)


@login_required
@app.route("/Teacher/ImportPoints", methods=["GET", "POST"])
def import_points():
    semester_id = session.get('semester_id')
    class_id = session.get('class_id')
    # Lấy danh sách học sinh
    students = db.session.query(Student).join(StudentClass).filter(
        StudentClass.class_id == class_id,
        StudentClass.semester_id == semester_id
    ).all()
    existing_15min = {}
    existing_test = {}
    existing_exam = {}
    for student in students:
        # Kiểm tra số lượng điểm 15 phút hiện tại của học sinh
        existing_15min[student.id] = 5 - db.session.query(Point).filter(
            Point.studentID == student.id,
            Point.pointTypeID == 1,  # 1 là mã cho điểm 15 phút
            Point.semesterID == semester_id,
            Point.subjectID == current_user.subjectID
        ).count()
        existing_test[student.id] = 3 - db.session.query(Point).filter(
            Point.studentID == student.id,
            Point.pointTypeID == 2,  # 1 là mã cho điểm 15 phút
            Point.semesterID == semester_id,
            Point.subjectID == current_user.subjectID
        ).count()
        existing_exam[student.id] = 1 - db.session.query(Point).filter(
            Point.studentID == student.id,
            Point.pointTypeID == 3,  # 1 là mã cho điểm 15 phút
            Point.semesterID == semester_id,
            Point.subjectID == current_user.subjectID
        ).count()


    return render_template('Teacher/ImportPoints.html',
                           students = students,
                           existing_15min=existing_15min,
                           existing_exam =existing_exam,
                           existing_test =existing_test)


@login_required
@app.route("/Teacher/ExportTranscript", methods=["GET", "POST"])
def export_points():

    return render_template('Teacher/ExportTranscript.html')

# staff

@app.route('/staff/InfoUser')
@login_required
def info_user():
    try:
        # Giải mã User Name và Password
        username = current_user.userName
    except Exception as e:
        username = None

        print(f"Lỗi khi giải mã dữ liệu: {e}")
    return render_template(
        'staff/InfoUser.html',
        Cuser=current_user,
        username = username
    )

@app.route('/staff/password_info', methods=['GET'])
@login_required
def password_info():
    return render_template('staff/PasswordChange.html')


@app.route('/staff/change_password', methods=['POST'])
@login_required
def change_password():
    try:
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')



        # Kiểm tra mật khẩu hiện tại
        if not check_password_hash(current_user.password,current_password):
            flash("Mật khẩu hiện tại không đúng!", "error")
            return redirect(url_for('password_info'))

        # Kiểm tra mật khẩu mới và xác nhận mật khẩu
        if new_password != confirm_password:
            flash("Mật khẩu mới và xác nhận mật khẩu không khớp!", "error")
            return redirect(url_for('password_info'))

        # Cập nhật mật khẩu mới (băm trước khi lưu)
        current_user.password = generate_password_hash(new_password)  # Lưu mật khẩu đã mã hóa
        db.session.commit()

        flash("Thay đổi mật khẩu thành công!", "success")
        return redirect(url_for('info_user'))

    except Exception as e:
        db.session.rollback()
        flash(f"Lỗi không mong muốn: {e}", "error")
        return redirect(url_for('password_info'))


@app.route('/staff/student_add', methods=["GET", "POST"])
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

@app.route('/staff/student_edit', methods=["GET", "POST"])
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


@app.route('/staff/update_student_NoClass/<int:student_id>', methods=['POST'])
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


@app.route('/staff/student_delete/<int:student_id>', methods=['GET','POST'])
def student_delete(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('student_edit'))

@app.route('/staff/student_info/<int:student_id>')
def student_info(student_id):
    student = Student.query.get_or_404(student_id)  # Lấy thông tin học sinh
    return render_template('staff/StudentInfo.html', student=student)


@app.route('/staff/class_edit', methods=['GET', 'POST'])
def class_edit():
    class_list = Class.query.all()
    semester_list = Semester.query.all()
    students = []
    class_id = None
    semester_id = None
    # Lấy tên lớp và học kỳ từ ID
    selected_class = Class.query.get(class_id) if class_id and class_id != "none" else None
    selected_semester = Semester.query.get(semester_id) if semester_id and semester_id != "none" else None
    selected_class = None
    selected_semester = None

    if request.method == 'POST':
        class_id = request.form.get('class')
        semester_id = request.form.get('semester')
        student_name = request.form.get('searchStudent', '').strip()

        if class_id and class_id != "none":
            selected_class = next((cls for cls in class_list if str(cls.id) == class_id), None)
        if semester_id and semester_id != "none":
            selected_semester = next((sem for sem in semester_list if str(sem.id) == semester_id), None)

        # Truy vấn danh sách học sinh dựa trên điều kiện
        if class_id and semester_id and class_id != "none" and semester_id != "none":
            students_query = (
                Student.query.join(StudentClass)
                .filter(
                    StudentClass.class_id == class_id,
                    StudentClass.semester_id == semester_id,
                )
            )
        elif class_id == "none" and semester_id == "none":
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
        semester_id=semester_id,
        selected_class=selected_class,
        selected_semester=selected_semester,
    )
@app.route('/staff/student_delete_class', methods=['POST'])
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

@app.route('/staff/student_class_info/<int:student_id>', methods=['GET', 'POST'])
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
@app.route('/staff/update_student/<int:student_id>', methods=['POST'])
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


@app.route('/Teacher/InfoUser')
@login_required
def info_user_teacher():
    try:
        # Giải mã User Name và Password
        username = current_user.userName
    except Exception as e:
        username = None

        print(f"Lỗi khi giải mã dữ liệu: {e}")
    return render_template(
        'Teacher/InforUser.html',
        Cuser=current_user,
        username=username
    )

@app.route('/Teacher/password_info', methods=['GET'])
@login_required
def password_info_teacher():
    return render_template('Teacher/PasswordChange.html')


@app.route('/Teacher/change_password_teacher', methods=['POST'])
@login_required
def change_password_teacher():
    try:
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # Giải mã mật khẩu hiện tại

        # Kiểm tra mật khẩu hiện tại
        if not check_password_hash(current_user.password, current_password):
            flash("Mật khẩu hiện tại không đúng!", "error")
            return redirect(url_for('password_info_teacher'))

        # Kiểm tra mật khẩu mới và xác nhận mật khẩu
        if new_password != confirm_password:
            flash("Mật khẩu mới và xác nhận mật khẩu không khớp!", "error")
            return redirect(url_for('password_info_teacher'))

        # Cập nhật mật khẩu mới (băm trước khi lưu)
        current_user.password = generate_password_hash(new_password)  # Lưu mật khẩu đã mã hóa
        db.session.commit()

        flash("Thay đổi mật khẩu thành công!", "success")
        return redirect(url_for('info_user_teacher'))

    except Exception as e:
        db.session.rollback()
        flash(f"Lỗi không mong muốn: {e}", "error")
        return redirect(url_for('password_info_teacher'))


@app.route('/Teacher/EnterPoints/class_filter', methods=['POST', 'GET'])
def class_filter():
    # Kiểm tra nếu người dùng không phải là giáo viên
    if not hasattr(current_user, 'subjectID'):
        flash("Bạn chưa được cấp chuyên môn. Vui lòng liên hệ quản trị viên!", "error")
        return render_template('Teacher/EnterPoints.html', subject_name='', )
    if current_user.subjectID:
        _subject = db.session.query(Subject).filter(Subject.id == current_user.subjectID).first()
        subject_name = _subject.subjectName
        student_scores = {}  # Điểm của sinh viên
        averages = {}  # Điểm trung bình của sinh viên

        if request.method == 'POST':
            # Lấy dữ liệu từ form
            class_name = request.form.get('class-input')
            semester_name = request.form.get('semester-input')
            year = request.form.get('academic-year-input')

            # Kiểm tra dữ liệu từ form
            if not class_name or not semester_name or not year:
                flash("Vui lòng nhập đầy đủ lớp, học kỳ và năm học!", "error")
                return redirect(url_for('enter_point'))

            # Tìm lớp và học kỳ từ dữ liệu nhập vào
            _class = db.session.query(Class).filter(Class.className == class_name).first()
            _semester = db.session.query(Semester).filter(Semester.semesterName == semester_name,
                                                          Semester.year == year).first()
            session["semester_name"]=_semester.semesterName
            session["class_name"]=_class.className
            session["year"]=_semester.year

            # Kiểm tra nếu không tìm thấy lớp hoặc học kỳ
            if not _class or not _semester:
                flash("Không tìm thấy lớp hoặc học kỳ phù hợp!", "error")
                return redirect(url_for('enter_point'))

            session['class_id'] = _class.id
            session['semester_id'] = _semester.id
            # Lấy danh sách học sinh trong lớp và học kỳ
            students = db.session.query(Student).join(StudentClass).filter(
                StudentClass.class_id == _class.id,
                StudentClass.semester_id == _semester.id
            ).all()

            # Kiểm tra nếu không có sinh viên
            if not students:
                flash("Không tìm thấy sinh viên trong lớp và học kỳ này!", "error")
                return redirect(url_for('enter_point'))


            existing_15min = {}
            existing_test = {}
            existing_exam = {}

            for student in students:
                # Kiểm tra số lượng điểm 15 phút hiện tại của học sinh
                existing_15min[student.id] = 5 - db.session.query(Point).filter(
                    Point.studentID == student.id,
                    Point.pointTypeID == 1,  # 1 là mã cho điểm 15 phút
                    Point.semesterID == _semester.id,
                    Point.subjectID == current_user.subjectID
                ).count()
                existing_test[student.id] = 3 - db.session.query(Point).filter(
                    Point.studentID == student.id,
                    Point.pointTypeID == 2,  # 1 là mã cho điểm 15 phút
                    Point.semesterID == _semester.id,
                    Point.subjectID == current_user.subjectID
                ).count()
                existing_exam[student.id] = 1 - db.session.query(Point).filter(
                    Point.studentID == student.id,
                    Point.pointTypeID == 3,  # 1 là mã cho điểm 15 phút
                    Point.semesterID == _semester.id,
                    Point.subjectID == current_user.subjectID
                ).count()




            # Render trang ExportTranscript nếu không có lỗi
            return render_template('Teacher/ImportPoints.html',
                                   subject_name=subject_name,
                                   students=students,
                                   student_scores=student_scores,
                                   averages=averages,
                                   existing_15min=existing_15min,
                                   existing_exam =existing_exam,
                                   existing_test=existing_test,
                                   semester_name = semester_name,
                                   year = year,
                                   class_name = class_name)
    flash("Bạn chưa được cấp chuyên môn. Vui lòng liên hệ quản trị viên!", "error")
    return render_template('Teacher/EnterPoints.html', subject_name='', )

@app.route("/Teacher/GenerateTranscript/generate", methods=["GET", "POST"])
def generate():
    if not hasattr(current_user, 'subjectID'):
        flash("Bạn chưa được cấp chuyên môn. Vui lòng liên hệ quản trị viên!", "error")
        return render_template('Teacher/GenerateTranscript.html', subject_name='', )
    if current_user.subjectID:
        _subject = db.session.query(Subject).filter(Subject.id == current_user.subjectID).first()
        subject_name = _subject.subjectName
        student_scores_1 = {}  # Điểm của sinh viên
        student_scores_2 = {}  # Điểm của sinh viên
        averages_1 = {}  # Điểm trung bình của sinh viên
        averages_2 = {}  # Điểm trung bình của sinh viên

        if request.method == 'POST':
            # Lấy dữ liệu từ form
            class_name = request.form.get('class-input')
            year = request.form.get('academic-year-input')
            # Kiểm tra dữ liệu từ form
            if not class_name or not year:
                flash("Vui lòng nhập đầy đủ lớp, học kỳ và năm học!", "error")
                return redirect(url_for('generate_transcript'))

            # Tìm lớp và học kỳ từ dữ liệu nhập vào
            _class = db.session.query(Class).filter(Class.className == class_name).first()

            _semester_1= db.session.query(Semester).filter(Semester.semesterName == "Học kỳ 1",
                                                           Semester.year == year).first()
            _semester_2= db.session.query(Semester).filter(Semester.semesterName == "Học kỳ 2",
                                                          Semester.year == year).first()
            session["year"] = year

            # Kiểm tra nếu không tìm thấy lớp hoặc học kỳ
            if not _class or not _semester_1 or not _semester_2:
                flash("Không tìm thấy lớp!", "error")
                return redirect(url_for('generate_transcript'))
            session['class_id'] = _class.id
            session['semester_1_id'] = _semester_1.id
            session['semester_2_id'] = _semester_2.id
            # Lấy danh sách học sinh trong lớp và học kỳ
            students = db.session.query(Student).join(StudentClass).filter(
                StudentClass.class_id == _class.id,
                StudentClass.semester_id == _semester_1.id
            ).all()
            # Kiểm tra nếu không có sinh viên
            if not students:
                flash("Không tìm thấy sinh viên trong lớp này!", "error")
                return redirect(url_for('generate_transcript'))

            # Lấy điểm của các học sinh
            for student in students:
                points = db.session.query(Point).filter(
                    Point.studentID == student.id,
                    Point.subjectID == _subject.id,
                    Point.semesterID == _semester_1.id
                ).all()
                student_scores_1[student.id] = points

            for student in students:
                points = db.session.query(Point).filter(
                    Point.studentID == student.id,
                    Point.subjectID == _subject.id,
                    Point.semesterID == _semester_2.id
                ).all()
                student_scores_2[student.id] = points  # Lưu điểm của từng học sinh
            print(student_scores_1)
            print(student_scores_2)
            # Tính điểm trung bình cho từng sinh viên
            for student in students:
                average = calculate_average(student.id, _subject.id, _semester_1.id)
                averages_1[student.id] = average
            for student in students:
                average = calculate_average(student.id, _subject.id, _semester_2.id)
                averages_2[student.id] = average


    # Render trang ExportTranscript nếu không có lỗi
            return render_template('Teacher/ExportTranscript.html',
                                   subject_name=subject_name,
                                   students=students,
                                   student_scores_1=student_scores_1,student_scores_2=student_scores_2,
                                   averages_1=averages_1, averages_2=averages_2 ,
                                   class_name = _class.className,
                                   year=year)
    flash("Bạn chưa được cấp chuyên môn. Vui lòng liên hệ quản trị viên!", "error")
    return render_template('Teacher/GenerateTranscript.html', subject_name='', )


@app.route('/Teacher/EnterPoints/save_points', methods=['POST'])
def save_points():
    try:
        # Lấy danh sách dữ liệu từ form
        scores_15min = request.form.getlist('scores_15min[]')
        scores_test = request.form.getlist('scores_test[]')
        scores_exam = request.form.getlist('scores_exam[]')
        semester_id = session.get('semester_id')
        class_id = session.get('class_id')
        students = db.session.query(Student).join(StudentClass).filter(
            StudentClass.class_id == class_id,
            StudentClass.semester_id == semester_id
        ).all()

            # Kiểm tra dữ liệu trống hoặc không hợp lệ

        existing_15min = {}
        existing_test = {}
        existing_exam = {}

        for student in students:
            # Kiểm tra số lượng điểm 15 phút hiện tại của học sinh
            existing_15min[student.id] = 5 - db.session.query(Point).filter(
                Point.studentID == student.id,
                Point.pointTypeID == 1,  # 1 là mã cho điểm 15 phút
                Point.semesterID == semester_id,
                Point.subjectID == current_user.subjectID
            ).count()
            existing_test[student.id] = 3 - db.session.query(Point).filter(
                Point.studentID == student.id,
                Point.pointTypeID == 2,  # 1 là mã cho điểm 15 phút
                Point.semesterID == semester_id,
                Point.subjectID == current_user.subjectID
            ).count()
            existing_exam[student.id] = 1 - db.session.query(Point).filter(
                Point.studentID == student.id,
                Point.pointTypeID == 3,  # 1 là mã cho điểm 15 phút
                Point.semesterID == semester_id,
                Point.subjectID == current_user.subjectID
            ).count()



        for id, student in enumerate(students):
            if student.id in existing_15min:
                for i in range(existing_15min[student.id]):

                    if scores_15min:
                        score = scores_15min.pop(0)  # Lấy điểm đầu tiên từ scores_15min và loại bỏ nó
                        if score:  # Nếu score hợp lệ (không None hoặc không rỗng)
                            db.session.add(
                                Point(
                                    pointValue=float(score),
                                    pointTypeID=1,
                                    semesterID=semester_id,
                                    subjectID=current_user.subjectID,
                                    studentID=student.id
                                )
                            )

                try:
                    db.session.commit()  # Commit sau khi đã thêm các điểm
                except Exception as e:
                    print(f"Error occurred: {e}")
                    db.session.rollback()
            if student.id in existing_test:
                for i in range(existing_test[student.id]):

                    if scores_test:
                        score = scores_test.pop(0)  # Lấy điểm đầu tiên từ scores_15min và loại bỏ nó
                        if score:  # Nếu score hợp lệ (không None hoặc không rỗng)
                            db.session.add(
                                Point(
                                    pointValue=float(score),
                                    pointTypeID=2,
                                    semesterID=semester_id,
                                    subjectID=current_user.subjectID,
                                    studentID=student.id
                                )
                            )
                try:
                    db.session.commit()  # Commit sau khi đã thêm các điểm
                except Exception as e:
                    print(f"Error occurred: {e}")
                    db.session.rollback()
            if student.id in existing_exam:
                for i in range(existing_exam[student.id]):
                    if scores_exam:
                        score = scores_exam.pop(0)
                        if score:
                            db.session.add(
                                Point(
                                    pointValue=float(score),
                                    pointTypeID=3,
                                    semesterID=semester_id,
                                    subjectID=current_user.subjectID,
                                    studentID=student.id
                                )
                            )
                try:
                    db.session.commit()  # Commit sau khi đã thêm các điểm
                except Exception as e:
                    print(f"Error occurred: {e}")
                    db.session.rollback()

    except SQLAlchemyError as db_err:
        db.session.rollback()
        flash(f"Lỗi cơ sở dữ liệu: {db_err}", "danger")
    except ValueError as val_err:
        flash(f"Lỗi dữ liệu đầu vào: {val_err}", "danger")
    except Exception as e:
        flash(f"Có lỗi xảy ra: {e}", "danger")
    flash(f"Lưu thành công", "message")
    # Nếu có lỗi xảy ra, vẫn giữ lại danh sách học sinh trên trang ImportPoints
    return redirect(url_for('enter_point'))





@app.route('/Teacher/ExportTranscript/export_pdf', methods=['GET'])
def export_pdf():
    # Register custom font
    font_path = 'static/fonts/Arial.ttf'  # Ensure correct path to .ttf file
    pdfmetrics.registerFont(TTFont('Arial', font_path))
    logo_path = 'static/images/Logo_THPT_Chu_Van_An.jpg'  # Path to logo

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Arial", 12)

    # Add logo at the top right
    c.drawImage(logo_path, 480, 695, width=80, height=80, mask='auto')

    # Fetch data from the database
    class_id = session.get('class_id')
    semester_1_id = session.get('semester_1_id')
    semester_2_id = session.get('semester_2_id')

    class_info = db.session.query(Class).filter(Class.id == class_id).first()
    class_name = class_info.className if class_info else "Unknown Class"

    students = db.session.query(Student).join(StudentClass).filter(
        StudentClass.class_id == class_id,
        StudentClass.semester_id == semester_1_id
    ).all()

    # Calculate averages for each student
    averages1 = {}
    averages2 = {}
    for student in students:
        averages1[student.id] = calculate_average(student.id, current_user.subjectID, semester_1_id)
        averages2[student.id] = calculate_average(student.id, current_user.subjectID, semester_2_id)

    y_position = 730  # Initial y position

    # Add header
    c.setFont("Arial", 16)
    c.drawString(50, y_position, "Trường Trung Học Quốc Gia Chu Văn An")
    y_position -= 20
    c.setFont("Arial", 14)
    c.drawString(50, y_position, "Môn học: Toán học")
    y_position -= 40

    # Add title
    c.setFont("Arial", 12)
    c.drawString(50, y_position, "Danh sách điểm sinh viên")
    y_position -= 20

    # Define column positions and row height
    col_positions = [35, 205, 285, 435, 585]  # Adjusted positions for proper spacing
    row_height = 25  # Increased row height for readability

    # Draw table header
    c.setFont("Arial", 12)
    c.line(col_positions[0], y_position, col_positions[-1], y_position)  # Top line
    c.drawString(col_positions[0] + 45, y_position - 4 - row_height / 2 , "Tên Sinh Viên")
    c.drawString(col_positions[1] + 20, y_position - 4 - row_height / 2, "Lớp SV")
    c.drawString(col_positions[2] + 25, y_position - 4 - row_height / 2, "Điểm TB Học Kỳ 1")
    c.drawString(col_positions[3] + 25, y_position - 4 - row_height / 2, "Điểm TB Học Kỳ 2")
    y_position -= row_height

    # Draw vertical lines for header
    for col in col_positions:
        c.line(col, y_position + row_height, col, y_position)

    # Draw each student's data
    for student in students:
        average1 = averages1.get(student.id, 0)
        average2 = averages2.get(student.id, 0)

        # Write student data
        c.drawString(col_positions[0] + 5, y_position - 4 - row_height / 2, student.name)
        c.drawString(col_positions[1] + 25, y_position - 4 - row_height / 2, class_name)
        c.drawString(col_positions[2] + 60, y_position - 4 - row_height / 2, f"{average1:.2f}")
        c.drawString(col_positions[3] + 60, y_position - 4 - row_height / 2, f"{average2:.2f}")

        # Draw row lines
        c.line(col_positions[0], y_position, col_positions[-1], y_position)
        y_position -= row_height

        # Draw vertical lines for the row
        for col in col_positions:
            c.line(col, y_position + row_height, col, y_position)

        if y_position < 100:  # If space runs out, start a new page
            c.showPage()
            c.setFont("Arial", 12)
            c.drawImage(logo_path, 480, 730, width=80, height=80, mask='auto')
            y_position = 700
            c.line(col_positions[0], y_position, col_positions[-1], y_position)  # Top line
            c.drawString(col_positions[0] + 45, y_position - 4 - row_height / 2, "Tên Sinh Viên")
            c.drawString(col_positions[1] + 20, y_position - 4 - row_height / 2, "Lớp SV")
            c.drawString(col_positions[2] + 25, y_position - 4 - row_height / 2, "Điểm TB Học Kỳ 1")
            c.drawString(col_positions[3] + 25, y_position - 4 - row_height / 2, "Điểm TB Học Kỳ 2")
            y_position -= row_height
            c.line(col_positions[0], y_position, col_positions[-1], y_position)

    c.line(col_positions[0], y_position, col_positions[-1], y_position)

    # Add signature
    c.setFont("Arial", 12)
    c.drawString(50, 50, "Chữ ký của giáo viên:")
    c.line(200, 50, 350, 50)

    c.showPage()
    c.save()

    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="diem_sinh_vien.pdf", mimetype='application/pdf')






if __name__ == '__main__':
    app.run(debug=True)
