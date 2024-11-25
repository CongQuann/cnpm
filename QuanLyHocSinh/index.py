

from flask import render_template, request

from QuanLyHocSinh import app


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template('index.html')

#=========================Administrator==============================
@app.route("/Administrator/Report", methods=["GET", "POST"])
def report():
    # Dữ liệu mẫu bạn muốn hiển thị trong bảng
    data = [
        {"class": "10A1", "total_students": 45, "pass": 40, "proportion": 55},
        {"class": "10A2", "total_students": 50, "pass": 35, "proportion": 70},
        {"class": "10A3", "total_students": 45, "pass": 40, "proportion": 55},
        {"class": "10A4", "total_students": 45, "pass": 40, "proportion": 55},
        {"class": "10A5", "total_students": 45, "pass": 40, "proportion": 55},
        {"class": "10A6", "total_students": 45, "pass": 40, "proportion": 55},
        {"class": "10A7", "total_students": 45, "pass": 40, "proportion": 55},
        {"class": "10A8", "total_students": 45, "pass": 40, "proportion": 55},
        {"class": "10A9", "total_students": 45, "pass": 40, "proportion": 55},
        {"class": "10A10", "total_students": 45, "pass": 40, "proportion": 55},
        {"class": "10A11", "total_students": 45, "pass": 40, "proportion": 55},
        {"class": "10A12", "total_students": 45, "pass": 40, "proportion": 55},
        {"class": "10A13", "total_students": 45, "pass": 40, "proportion": 55},

    ]
    return render_template('Administrator/Report.html', data=data)

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




if __name__ == '__main__':
    app.run(debug=True)
