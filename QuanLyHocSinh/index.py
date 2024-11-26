

from flask import render_template, request

from QuanLyHocSinh import app
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
    return render_template('Administrator/Report.html',
                           classes=class_list,
                           subjects = subject_list,
                           semesters = semester_list)

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
