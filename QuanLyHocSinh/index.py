from flask import render_template

from QuanLyHocSinh import app


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template('index.html')


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

@app.route("/Teacher/EnterPoints", methods=["GET", "POST"])
def enter_point():
    regulations = {

    }
    return render_template('Teacher/EnterPoints.html',regulations=regulations)

if __name__ == '__main__':
    app.run(debug=True)
