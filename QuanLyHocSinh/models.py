
from sqlalchemy import Column, Integer, String, Double, DateTime, Float, Boolean, ForeignKey, column,Enum
import enum
from QuanLyHocSinh import db, app
from sqlalchemy.orm import relationship, backref
from datetime import datetime





if __name__ == '__main__':
    with app.app_context():
        db.create_all()
