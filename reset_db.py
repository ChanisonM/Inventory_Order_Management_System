from app import create_app
from app.models import db, User, Category
from datetime import datetime, timezone

app = create_app()

def reset_database():
    with app.app_context():
        print("⏳ กำลังลบฐานข้อมูลเก่า...")
        db.drop_all()  # ลบ Table ทั้งหมดทิ้ง
        
        print("🏗️ กำลังสร้างโครงสร้างฐานข้อมูลใหม่...")
        db.create_all() # สร้าง Table ใหม่ตาม Model ล่าสุด
        
        # 1. สร้าง Admin คนแรก
        print("👤 กำลังสร้างบัญชี Admin...")
        admin = User(
            username="admin", 
            role="admin",
            is_active=True
        )
        admin.set_password("admin12345") # เปลี่ยนรหัสผ่านตรงนี้ได้เลย
        db.session.add(admin)
        db.session.commit() # Commit ก่อนเพื่อให้ได้ admin.id มาใช้ต่อ
        
        # 2. สร้างหมวดหมู่เริ่มต้น (Optional)
        print("📦 กำลังสร้างหมวดหมู่เริ่มต้น...")
        default_cat = Category(
            name="ทั่วไป",
            created_by_id=admin.id # บันทึกว่า Admin เป็นคนสร้าง
        )
        db.session.add(default_cat)
        
        db.session.commit()
        print("✅ เสร็จสิ้น! ระบบพร้อมใช้งานแล้ว")
        print(f"ล็อกอินด้วย Username: admin | Password: admin12345")

if __name__ == "__main__":
    reset_database()