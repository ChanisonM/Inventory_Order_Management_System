from flask import Flask
from .models import db , User
from .routes import api
from flask_login import LoginManager

lofgin_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key-very-hard' # 4. สำคัญมาก! ต้องมี Secret Key สำหรับ Session
    # ตั้งค่าที่เก็บฐานข้อมูล SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # 5. เชื่อมต่อ LoginManager เข้ากับแอป
    lofgin_manager.init_app(app)
    lofgin_manager.login_view = 'api.login'  # ถ้าไม่ล็อกอินจะถูกส่งไปที่หน้าไหน

    # 6. เพิ่มฟังก์ชันโหลด User (ตัวนี้คือสิ่งที่ Error ถามหาครับ)
    @lofgin_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    

    # ลงทะเบียน Blueprint
    app.register_blueprint(api, url_prefix='/api')

    return app