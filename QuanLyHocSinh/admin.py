from QuanLyHocSinh import admin,db
from QuanLyHocSinh.models import Teacher, Subject
from flask_admin.contrib.sqla import ModelView

admin.add_view(ModelView(Teacher,db.session))
admin.add_view(ModelView(Subject,db.session))
