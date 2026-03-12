from flask import Blueprint, Flask, jsonify, request , render_template
from app.models import User, db, Category , Product , Order , OrderItem
from app.schemas import CategorySchema , ProductSchema
from marshmallow import ValidationError
from flask_login import login_user, logout_user, login_required, current_user 

# สร้าง Blueprint เพื่อแยกส่วน Route ออกมา
api = Blueprint('api', __name__)
@api.route('/categories', methods=['POST'])
def create_category():
    json_data = request.get_json()
    if not json_data:
        return jsonify({'message': 'ไม่มีข้อมูลส่งมา'}), 400
    
    schema = CategorySchema()
    try:
        # 1. Validation: ตรวจสอบข้อมูลด้วย Marshmallow
        data = schema.load(json_data)
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400

    # 2. Check Duplicate: เช็กว่าชื่อหมวดหมู่ซ้ำไหม (นอกเหนือจาก Schema)
    existing_category = Category.query.filter_by(name=data['name']).first()
    if existing_category:
        return jsonify({'message': 'หมวดหมู่นี้มีอยู่แล้ว'}), 400
    
    # 3. Save to Database: ถ้าผ่านหมดให้บันทึกจริง
    new_category = Category(name=data['name'])
    db.session.add(new_category)
    db.session.commit()

    return jsonify({'message': 'เพิ่มหมวดหมู่สำเร็จ', 'category': schema.dump(new_category)}), 201

@api.route('/categories', methods=['POST'])
def get_categories():
    categories = Category.query.all()
    schema = CategorySchema(many=True)
    return jsonify({'categories': schema.dump(categories)}), 200


@api.route('/products', methods=['POST'])
def add_product():
    jsoin_data = request.get_json()
    schema = ProductSchema()

    try:    
        # 1. Validation (เช็ก SKU, ราคา, สต็อก)
        data = schema.load(jsoin_data)
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400
    
    # 2. Check SKU Duplicate
    if Product.query.filter_by(sku=data['sku']).first():
        return jsonify({'message': 'รหัสสินค้า (SKU) นี้มีอยู่ในระบบแล้ว'}), 400

    # 3. Check if Category exists
    if not Category.query.get(data['category_id']):
        return jsonify({'message': 'ไม่พบหมวดหมู่สินค้าที่ระบุ'}), 400
    
    # 4. Save to Database
    new_product = Product(
        sku=data['sku'],
        name=data['name'],
        price=data['price'],
        stock_quantity=data['stock_quantity'],
        category_id=data['category_id']
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'message': 'เพิ่มสินค้าสำเร็จ', 'product': schema.dump(new_product)}), 201

@api.route('/products', methods=['GET'])    
def get_products():
    products = Product.query.all()
    schema = ProductSchema(many=True)
    return jsonify({'products': schema.dump(products)}), 200

@api.route('/orders', methods=['POST'])
@login_required
def create_order():
    json_data = request.get_json()  
    # ในโปรเจกต์จริงเราจะดึง user_id จาก Session/Login 
    # แต่ตอนนี้ขอสมมติเป็นเลข 1 ไปก่อนครับ
    user_id = current_user.id 

    items_data = json_data.get('items' , [])
    if not items_data:
        return jsonify({'message': 'ต้องมีรายการสินค้าอย่างน้อย 1 รายการ'}), 400

    total_amount = 0
    order_items_to_save = [] 

    try:
        for item in items_data:
            product =Product.query.get(item['product_id'])
            if not product:
                return jsonify({'message': f"ไม่พบสินค้าที่มี ID {item['product_id']}"}), 404
            
            # --- จุดสำคัญ: ตรวจสอบสต็อกก่อนขาย ---
            if product.stock_quantity < item['quantity']:
                return jsonify({"message": f"สินค้า {product.name} มีไม่พอ (คงเหลือ {product.stock_quantity})"}), 400
            # คำนวณยอดรวม
            line_total = product.price * item['quantity']
            total_amount += line_total

            # เตรียมข้อมูล OrderItem (บันทึกราคา ณ วันที่ขายด้วย)
            new_item = OrderItem(
                product_id=product.id,
                quantity=item['quantity'],
                unit_price=product.price
            ) 
            order_items_to_save.append((new_item, product))  # เก็บคู่กับสินค้าและจำนวนเพื่ออัปเดตสต็อกทีหลัง 
        # --- เริ่มบันทึกข้อมูลลง Database ---
        new_order = Order(user_id=user_id, total_amount=total_amount)
        db.session.add(new_order)
        db.session.flush()  # เพื่อให้ new_order มี ID ก่อนบันทึก OrderItem

        for oi , prod in order_items_to_save:
            oi.order_id = new_order.id  # กำหนด order_id ให้ OrderItem
            db.session.add(oi)
            # --- ตัดสต็อกสินค้า ---
            prod.stock_quantity -= oi.quantity
        db.session.commit()  # บันทึกทั้งหมดในครั้งเดียว
        return jsonify({'message': 'สร้างออเดอร์สำเร็จ', 'order_id': new_order.id , "total": total_amount}), 201
    except Exception as e:
        db.session.rollback() # ถ้าพลาดตรงไหน ให้ยกเลิกทั้งหมด (ข้อมูลไม่พัง)
        return jsonify({'message': 'เกิดข้อผิดพลาด', "error" : str(e)}), 500
    
@api.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'ชื่อผู้ใช้นี้มีอยู่แล้ว'}), 400
    new_user = User(username=data['username'])
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'สมัครสมาชิกสำเร็จ'}), 201

@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    # ตรวจสอบชื่อผู้ใช้ และเช็ครหัสผ่านที่ Hash ไว้
    if user and user.check_password(data['password']):
        login_user(user) # สร้าง Session ให้ User
        return jsonify({
            'message': 'เข้าสู่ระบบสำเร็จ',
            "user" : {
                "username" : user.username,
                "role" : user.role
            }
            }), 200
    return jsonify({'message': 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง'}), 401   


@api.route('/login' , methods=['GET'])
def login_page():
    return render_template('login.html')



@api.route('/logout', methods=['GET'])
@login_required 
def logout():
    logout_user() # ลบ Session ของ User
    return jsonify({'message': 'ออกจากระบบสำเร็จ'}), 200

