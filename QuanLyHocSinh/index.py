from flask import render_template

from QuanLyHocSinh import app

@app.route("/")
def home():
    return render_template('index.html')

if __name__ == '__main__':
    from QuanLyHocSinh.admin import *

    app.run(debug=True)