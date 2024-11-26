

from flask import render_template, request

from QuanLyHocSinh import app,db
from QuanLyHocSinh.models import Class,Student,User,Administrator,Staff,Subject,Semester,StudentRule,ClassRule,Point,PointType,Teach,Teacher,Grade


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template('index.html')

#=========================Administrator==============================
@app.route("/Administrator/Report", methods=["GET", "POST"])
def report():
    # Dữ liệu mẫu bạn muốn hiển thị trong bảng
    class_list = Class.query.all()
    subject_list = Subject.query.all()
    semester_list = Semester.query.all()

    checkPassed = is_student_passed(2,9,1)



    return render_template('Administrator/Report.html',
                           classes=class_list,
                           subjects = subject_list,
                           semesters = semester_list,
                           checkPassed = checkPassed)


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
    regulations = {
        "min_age": 6,
        "max_age": 18,
        "max_class_size": 40
    }
    return render_template('Administrator/RuleManagement.html',regulations=regulations)


@app.route("/Administrator/SubjectManagement",methods=["GET","POST"])
def subject_mng():
    # Dữ liệu mẫu
    subjects = [
        {"id": 1, "name": "Toán", "max_students": 40},
        {"id": 2, "name": "Vật lý", "max_students": 35},
        {"id": 3, "name": "Hóa học", "max_students": 30}
    ]

    # Truyền dữ liệu đến template
    return render_template('Administrator/SubjectManagement.html', subjects=subjects)

@app.route("/Administrator/TeacherManagement",methods=["GET","POST"])
def teacher_mng():
    # Dữ liệu mẫu (sau này thay bằng database)
    teachers = [
        {"id": 1, "name": "Nguyễn Văn A", "subject": "Toán"},
        {"id": 2, "name": "Trần Thị B", "subject": "Vật lý"}
    ]

    subjects = ["Toán", "Vật lý", "Hóa học", "Sinh học"]

    if request.method == "POST":
        # Xử lý thêm giáo viên
        new_teacher = {
            "id": len(teachers) + 1,  # Tăng ID tự động
            "name": request.form["teacher_name"],
            "subject": request.form["subject"]
        }
        teachers.append(new_teacher)

    return render_template('Administrator/TeacherManagement.html', teachers=teachers, subjects=subjects)


#======================================================================================================
@app.route("/Teacher/EnterPoints", methods=["GET", "POST"])
def enter_point():
    regulations = {

    }
    return render_template('Teacher/EnterPoints.html',regulations=regulations)


#của bé
@app.route('/staff')
def staff():
    return render_template('staff/staff.html')

if __name__ == '__main__':
    app.run(debug=True)
