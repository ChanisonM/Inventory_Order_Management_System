from app import create_app , db

app = create_app()  

if __name__ == '__main__':  
    with app.app_context():
        db.create_all()  # สร้างตารางในฐานข้อมูล
        print("Database created successfully.")
    app.run(debug=True)
    