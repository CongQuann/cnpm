from flask import render_template, request
import os
from QuanLyHocSinh import app


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template('index.html')


@app.route("/Administrator", methods=["GET", "POST"])
def report():
    # Dữ liệu mẫu bạn muốn hiển thị trong bảng
    data = [
        {"class": "10A1", "avg_score": 8.5, "max_score": 10, "min_score": 7, "total_students": 45},
        {"class": "10A2", "avg_score": 7.8, "max_score": 9, "min_score": 6, "total_students": 50},
    ]
    return render_template('Administrator/Report.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
