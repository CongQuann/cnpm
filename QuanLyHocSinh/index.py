
from flask import render_template, request, redirect, flash, jsonify, url_for

from QuanLyHocSinh import app,db
from datetime import datetime
from QuanLyHocSinh.models import Class,Student,User,Administrator,Staff,Subject,Semester,StudentRule,ClassRule,Point,PointType,Teach,Teacher,Grade

from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, TelField, EmailField, SubmitField
from wtforms.validators import DataRequired, Email, Length


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template('index.html')

#===========================================================ADMINISTRATOR================================================
@app.route("/Administrator/Report", methods=["GET", "POST"])
def report():
    # Dữ liệu mẫu bạn muốn hiển thị trong bảng
    class_list = Class.query.all()
    subject_list = Subject.query.all()
    semester_list = Semester.query.all()

    return render_template('Administrator/Report.html',
                           classes=class_list,
                           subjects = subject_list,
                           semesters = semester_list,)


@app.route('/generate_report', methods=['GET'])
def generate_report():
    # Lấy dữ liệu từ request
    subject_id = request.args.get('subject')  # ID môn học
    semester_id = request.args.get('semester')  # ID học kỳ

    subject_name = Subject.query.with_entities(Subject.subjectName).filter_by(id=subject_id).scalar()
    semester_name = Semester.query.with_entities(Semester.semesterName).filter_by(id=semester_id).scalar()

    # Lấy thông tin từ cơ sở dữ liệu
    classes = Class.query.all()

    # Thống kê số lượng học sinh đạt theo lớp
    statistics = []
    for cls in classes:
        students = Student.query.filter_by(classID=cls.id).all()
        num_students = len(students)
        num_passed = 0
        for student in students:
            average = calculate_average(student.id, subject_id, semester_id)
            if is_student_passed(student.id, subject_id, semester_id):  # Gọi đủ tham số
                num_passed += 1

        # Tính tỷ lệ đạt
        pass_rate = (num_passed / num_students * 100) if num_students > 0 else 0
        statistics.append({
            "class_name": cls.className,
            "total_students": num_students,
            "num_passed": num_passed,
            "pass_rate": f"{pass_rate:.2f}%"  # Làm tròn 2 chữ số thập phân
        })

    # Render template với dữ liệu thống kê
    return render_template('Administrator/Report.html',
                           statistics=statistics,
                           subjects=Subject.query.all(),
                           semesters=Semester.query.all(),
                           subject_name=subject_name,
                           semester_name=semester_name,)


def calculate_average(student_id, subject_id,semester_id):
    # Lấy tất cả các điểm của học sinh trong môn học cụ thể
    points = Point.query.filter_by(studentID=student_id, subjectID=subject_id, semesterID=semester_id).all()

    # Khởi tạo các biến để tính toán tổng điểm và số lượng cột
    total_points = 0
    total_weight = 0

    # Duyệt qua tất cả các điểm để tính tổng và trọng số
    for point in points:
        point_type = point.pointType_point.type  # Lấy loại điểm (15p, 1 tiết, cuối kỳ)

        if point_type == "15 phút":
            total_points += point.pointValue
            total_weight += 1  # Trọng số 1 cho điểm 15p
        elif point_type == "1 tiết":
            total_points += 2 * point.pointValue
            total_weight += 2  # Trọng số 2 cho điểm 1 tiết
        elif point_type == "Cuối kỳ":
            total_points += 3 * point.pointValue
            total_weight += 3  # Trọng số 3 cho điểm cuối kỳ

    # Tính điểm trung bình
    if total_weight == 0:  # Tránh trường hợp chia cho 0 nếu không có điểm nào
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


#======Thêm route xử lý để xóa môn học=======
@app.route("/Administrator/SubjectManagement/delete", methods=["POST"])
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



#============Phần chỉnh sửa môn học
@app.route("/Administrator/SubjectManagement/edit/<int:subject_id>") #route để gọi ra trang chỉnh sửa
def edit_subject_page(subject_id):
    subject = Subject.query.get(subject_id)
    if not subject:
        flash("Môn học không tồn tại.", "warning")
        return redirect("/Administrator/SubjectManagement")
    return render_template("Administrator/edit_subject.html", subject=subject)


@app.route("/Administrator/SubjectManagement/update", methods=["POST"]) #route chứa hàm thực hiện chức năng của trang chỉnh sửa
def update_subject():
    subject_id = request.form.get("subject_id")
    subject_name = request.form.get("subject_name")

    # Xử lý cập nhật
    subject = Subject.query.get(subject_id)
    if not subject:
        flash("Không tìm thấy môn học.", "warning")
        return redirect("/Administrator/SubjectManagement")

    try:
        subject.subjectName = subject_name
        db.session.commit()
        flash("Cập nhật thành công!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Lỗi trong quá trình cập nhật.", "danger")
    return redirect("/Administrator/SubjectManagement")

#=====================================





@app.route('/Administrator/CreateUser', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        # Lấy thông tin từ form
        name = request.form['name']
        gender = request.form['gender']
        dob = request.form['DOB']
        email = request.form['email']
        phone_number = request.form['phoneNumber']
        username = request.form['userName']
        password = request.form['password']
        role = request.form['role']

        # Tạo User
        new_user = User(
            name=name,
            gender=gender,
            DOB=dob,
            email=email,
            phoneNumber=phone_number,
            userName=username,
            password=password
        )
        db.session.add(new_user)
        db.session.commit()

        # Tạo bản ghi cho Staff hoặc Teacher dựa trên phân quyền
        if role == 'Staff':
            staffRole = request.form['staffRole']  # Thêm thông tin cho Staff
            new_staff = Staff(
                staffRole=staffRole,
                userID=new_user.id
            )
            db.session.add(new_staff)

        elif role == 'Teacher':
            yearExperience = request.form['yearExperience']  # Thêm kinh nghiệm giảng dạy cho Teacher
            new_teacher = Teacher(
                yearExperience=yearExperience,
                userID=new_user.id
            )
            db.session.add(new_teacher)

        db.session.commit()
        flash('Tạo tài khoản thành công!', 'success')
        return redirect("/Administrator/CreateUser")  # Redirect sau khi tạo thành công

    return render_template('Administrator/CreateUser.html')

#===================================================================================================================
@app.route("/Teacher/EnterPoints", methods=["GET", "POST"])
def enter_point():
    regulations = {

    }
    return render_template('Teacher/EnterPoints.html',regulations=regulations)


#staff

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
        print(student_rule.minAge)
        # Kiểm tra tuổi học sinh
        today = datetime.today()
        print(today)
        age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
        print(age)
        if not (student_rule.minAge <= age <= student_rule.maxAge):
            flash(f"Tuổi học sinh phải nằm trong khoảng {student_rule.minAge} đến {student_rule.maxAge} tuổi.",
                      "error")
            return redirect(url_for("staff"))

        gender = request.form.get("gender")
        address = request.form.get("address")
        phone = request.form.get("phone")
        email = request.form.get("email")
        class_id = request.form.get("class")
        # Kiểm tra dữ liệu bắt buộc
        if not all([name, dob, gender, address, phone, class_id]):
            flash("Vui lòng điền đầy đủ thông tin!", "error")
            return redirect(url_for("staff"))

        # Tạo một đối tượng Student
        new_student = Student(
            name=name,
            DOB=dob,
            gender=gender,
            address=address,
            phone=phone,
            email=email,
            classID=class_id,
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
    return render_template('staff/staff.html', classes=classes)

@app.route('/class_edit', methods=['GET'])
def class_edit():
    class_list = Class.query.all()
    class_id = request.args.get("class_id")
    print(class_id)
    students = Student.query.filter_by(classID=class_id).all()

    return render_template('staff/ClassList.html', class_list=class_list)

@app.route('/student_edit')
def student_edit():
    return render_template('staff/StudentEdit.html')

if __name__ == '__main__':
    app.run(debug=True)
