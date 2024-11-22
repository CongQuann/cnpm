from QuanLyHocSinh import app,db
from QuanLyHocSinh.models import User,Administrator,GradeLevel,Subject,Teacher,Staff,Year,Semester,ClassRule,Class,Teach,Study,StudentRule,Student,Point,PointTypes,PointDetails
from flask_admin import  Admin
from flask_admin.contrib.sqla import ModelView

admin = Admin(app=app, name = "StudentManagement Administration", template_mode='bootstrap4')

admin.add_view(ModelView(User,db.session))
admin.add_view(ModelView(Administrator,db.session,column_display_pk=True))
admin.add_view(ModelView(Subject,db.session))
admin.add_view(ModelView(Teacher,db.session))
admin.add_view(ModelView(Staff,db.session))
admin.add_view(ModelView(Year,db.session))
admin.add_view(ModelView(Semester,db.session))
admin.add_view(ModelView(ClassRule,db.session))
admin.add_view(ModelView(Class,db.session))
admin.add_view(ModelView(Teach,db.session))
admin.add_view(ModelView(Study,db.session))
admin.add_view(ModelView(StudentRule,db.session))
admin.add_view(ModelView(Student,db.session))
admin.add_view(ModelView(Point,db.session))
admin.add_view(ModelView(PointDetails,db.session))














