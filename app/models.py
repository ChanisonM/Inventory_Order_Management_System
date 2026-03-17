# นิยม Table ต่างๆ ตาม ED Diagram

from datetime import datetime , timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash



db = SQLAlchemy()

class User(db.Model , UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='staff')  # 'admin' หรือ 'staff'
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now())

    # ฟังก์ชันสำหรับเข้ารหัสผ่าน
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # ฟังก์ชันสำหรับเช็ครหัสผ่านตอน Login
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    #Relationship: พนักงานคนนี้เปิดออเดอร์อะไรไปบ้าง
    orders = db.relationship('Order', backref='staff', lazy=True)
    

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    #Relationship: หมวดหมู่นี้มีสินค้าอะไรบ้าง
    products = db.relationship('Product', backref='category', lazy=True)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    # เพิ่มบรรทัดนี้: ใครเป็นคนเพิ่มสินค้านี้เข้าสต็อก
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    # เพิ่มบรรทัดนี้: ใครเป็นคนเพิ่มสินค้านี้เข้าสต็อก
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_by = db.relationship('User', backref='created_products')
class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime, default=datetime.now)
    total_amount = db.Column(db.Float, nullable=False , default=0.0)
    status = db.Column(db.String(20), default='completed')  # 'pending', 'completed', 'cancelled'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    

    #Relationship: ออเดอร์นี้มีรายการสินค้าอะไรบ้าง
    items = db.relationship('OrderItem', backref='order', lazy=True)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)  # บันทึกราคา ณ วันที่ขาย