from flask import Blueprint, Flask, jsonify, request , render_template , redirect , url_for , make_response
from app.models import User, db, Category , Product , Order , OrderItem
from app.schemas import CategorySchema , ProductSchema
from marshmallow import ValidationError
from flask_login import login_user, logout_user, login_required, current_user

import time # เพิ่มไว้บนสุดของไฟล์

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

@api.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    schema = CategorySchema(many=True)
    return jsonify({'categories': schema.dump(categories)}), 200


@api.route('/products', methods=['POST'])
def add_product():
    json_data = request.get_json()
    schema = ProductSchema()

    try:    
        # 1. Validation (เช็ก SKU, ราคา, สต็อก)
        data = schema.load(json_data)
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
    # แก้จาก Product.query.all() เป็นการกรองเฉพาะ is_deleted=False
    products = Product.query.filter_by(is_deleted=False).all()
    schema = ProductSchema(many=True)

    product_list = []
    for p in products:
        product_list.append({
            'id': p.id,
            'sku': p.sku,
            'name': p.name,
            'price': p.price,
            'stock_quantity': p.stock_quantity,
            'created_by': p.created_by.username if p.created_by else 'System',
            'created_at': p.created_at.strftime('%d/%m/%Y %H:%M') if p.created_at else '-'
        })
        # ส่ง product_list ที่เราจัด format เองกลับไป
    return jsonify({'products': product_list}), 200


@api.route('/add_product' , methods=['POST'])
@login_required
def add_product_from_modal():
    data = request.json
    try :
        # สร้าง SKU แบบไม่ซ้ำโดยใช้เวลาปัจจุบันพ่วงท้าย
        unique_sku = f"PROD-{int(time.time())}"

        new_product = Product(
            name = data['name'] ,
            stock_quantity = data['stock_quantity'],
            price = data['price'],
            sku = unique_sku ,
            category_id=data.get('category_id', 1), # สมมติว่ามีหมวดหมู่ที่ 1 อยู่แล้ว
            created_by_id=current_user.id
        )
        db.session.add(new_product)
        db.session.commit()
        return jsonify({"message" : "Add Product Success !!"}) , 201
    except Exception as e :
        return jsonify({"message" : f"Someting Wrong {str(e)}"}) , 400

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
    user = User.query.filter_by(username=data['username'], is_active=True).first()
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
    return jsonify({'message': 'Incorrect username or password.'}), 401   


@api.route('/login' , methods=['GET'])
def login_page():
    return render_template('login.html')


@api.route('/logout', methods=['GET'])
@login_required 
def logout():
    logout_user() # ลบ Session ของ User
    # jsonify({'message': 'ออกจากระบบสำเร็จ'}), 200
    return redirect(url_for('api.login'))


@api.route('/dashboard')
@login_required
def dashboard():
    # นับจำนวนสินค้าทั้งหมด
    # total_products = Product.query.count()
    # 1. นับเฉพาะสินค้าที่ยังไม่ถูกลบ (is_deleted=False)
    total_products = Product.query.filter_by(is_deleted=False).count()
    # 2. นับสินค้าที่สต็อกต่ำกว่า 5 (ตัวอย่าง)
    # 2. นับสินค้าที่สต็อกต่ำ (ควรกรอง is_deleted ด้วยเช่นกัน)
    low_stock_count = Product.query.filter(
        Product.is_deleted == False, 
        Product.stock_quantity < 5
    ).count()
    # low_stock_count = Product.query.filter(Product.stock_quantity < 5).count()
    # 3. นับจำนวนพนักงาน
    total_staff = User.query.count()
    # 4. (แถม) ดึงสินค้า 5 รายการล่าสุดมาโชว์
    recent_products  = Product.query.order_by(Product.id.desc()).limit(5).all()
    response = make_response(render_template(
        'dashboard.html',
        user = current_user,
        total_products = total_products ,
        low_stock_count = low_stock_count,
        total_staff = total_staff ,
        recent_products = recent_products ,

    ))
    # ป้องกัน Cache เหมือนเดิม
    response.headers['Cache-Control'] = 'no-cache , no-store , must-revalidate'
    return response

@api.route('/inventory')
@login_required
def inventory():
    # เพิ่มการกรอง .filter_by(is_deleted=False) เ1ข้าไปด้วย
    products = Product.query.filter_by(is_deleted=False).all()
    response = make_response(render_template('inventory.html', user=current_user , products=products))
    # สั่ง Browser ว่าห้ามเก็บ Cache หน้านี้เด็ดขาด
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@api.route('/low_inventory')
@login_required
def low_inventory():
    filter_type = request.args.get('filter')
    query = Product.query.filter_by(is_deleted=False)
    
    if filter_type == 'low_stock':
        query = query.filter(Product.stock_quantity < 5)
    
    products = query.order_by(Product.stock_quantity.asc()).all()

    # แปลงข้อมูลเป็น List ของ Dict เพื่อให้ JS ใช้งานได้
    products_json = []
    for p in products:
        products_json.append({
            'id': p.id,
            'name': p.name,
            'price': float(p.price),
            'stock_quantity': p.stock_quantity,
            'category_id': p.category_id
        })

    return render_template(
        'low_inventory.html', 
        user=current_user, 
        products=products, # ยังส่งแบบเดิมเผื่อไว้
        products_json=products_json, # ✅ ส่งแบบ JSON ไปให้ JS
        filter_type=filter_type
    )

@api.route('/add_staff' , methods=["POST"])
@login_required
def add_staff():
    # 1. เช็กก่อนว่าคนกดคือ Admin หรือไม่
    if current_user.role != "admin":
        return jsonify({'message' : 'สิทธิ์ไม่เพียงพอ เฉพาะ Admin เท่านั้น'}), 403
    
    data = request.get_json()

    # 2. ตรวจสอบว่าชื่อผู้ใช้ซ้ำไหม
    if User.query.filter_by(username = data['username']).first():
        return jsonify({'message' : 'ชื่อผู้ใช้นี้มีอยู่ในระบบแล้ว'}) , 400
    
    # 3. บันทึกพนักงานใหม่
    new_user = User(username=data['username'] , role='staff')
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': f"เพิ่มพนักงาน {data['username']} เรียบร้อยแล้ว"}), 201


@api.route('/manage_staff')
@login_required
def manage_staff():
    if current_user.role != 'admin':
        return redirect(url_for('api.dashboard'))
    return render_template('manage_staff.html' , user=current_user)

# API สำหรับดึงข้อมูลพนักงาน (JSON)
@api.route('/api/get_staffs')
@login_required
def get_staff():
    if current_user.role != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    # ดึงทุกคนยกเว้นตัวเราเอง
    # staffs = User.query.filter(User.id != current_user.id).all()
    staffs = User.query.filter_by(is_active=True).order_by(User.role.asc()).all()
    staff_list = []
    for s in staffs :
        staff_list.append({
            'id' : s.id ,
            'username' : s.username ,
            'role' : s.role
        })
    return jsonify({'staffs' : staff_list})

@api.route('api/update_staff/<int:user_id>' , methods=["PUT"])
@login_required
def update_staff(user_id):
    if current_user.role != 'admin':
        return jsonify({'message': 'สิทธิ์ไม่เพียงพอ เฉพาะ Admin เท่านั้น'}), 403
    
    data = request.get_json()
    user = User.query.get_or_404(user_id)

    # แก้ไข Role (เพิ่มส่วนนี้เข้าไปครับ)
    new_role = data.get('role')
    if new_role:
        # ป้องกันไม่ให้ Admin เผลอเปลี่ยน Role ตัวเองเป็น staff (ไม่งั้นจะเข้าหน้านี้ไม่ได้อีก)
        if user.id == current_user.id and new_role == 'staff':
            return jsonify({'message': 'คุณไม่สามารถลดสิทธิ์ตัวเองเป็น Staff ได้'}), 400
        user.role = new_role
    
    # 2. ตรวจสอบการเปลี่ยน Username (แยกออกมา)
    new_username = data.get('username')
    if new_username and new_username != user.username:
        existing_user = User.query.filter(User.username == new_username , User.id != user_id).first()
        if existing_user:
            return jsonify({'message': f'ชื่อผู้ใช้ "{new_username}" มีอยู่ในระบบแล้ว'}), 400
        user.username = new_username

    # 3. ตรวจสอบการเปลี่ยน Password (ย้ายออกมานอกเงื่อนไขชื่อ เพื่อให้เปลี่ยนรหัสอย่างเดียวได้)
    new_password = data.get('password')
    if new_password:
        user.set_password(new_password)
    
    # 4. สั่ง Commit ตรงนี้ (เพื่อให้ครอบคลุมทั้งการเปลี่ยนชื่อ และ/หรือ เปลี่ยนรหัส)
    try:
        db.session.commit()
        return jsonify({'message': f'อัปเดตข้อมูลของ {user.username} สำเร็จ'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'เกิดข้อผิดพลาดในการบันทึกข้อมูล', 'error': str(e)}), 500
    
@api.route('/api/delete_staff/<int:user_id>' , methods=['DELETE'])
@login_required
def delete_staff(user_id):
    if current_user.role != 'admin' :
        return jsonify({'message': 'สิทธิ์ไม่เพียงพอ'}), 403
    # ห้ามลบตัวเอง
    if current_user.id == user_id :
        return jsonify({'message': 'คุณไม่สามารถลบบัญชีของตัวเองได้'}), 400
    user = User.query.get_or_404(user_id)
    try :
        # db.session.delete(user)
        user.is_active = False
        db.session.commit()
        return jsonify({'message': f'ระงับการใช้งานพนักงาน {user.username} เรียบร้อยแล้ว'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'เกิดข้อผิดพลาดในระงับการใช้งานพนักงาน', 'error': str(e)}), 500
    
# --- API สำหรับแก้ไขสินค้า ---
# @api.route('api/update_product/<int:product_id>', methods=['PUT'])
# @login_required
# def update_product(product_id):
#     product = Product.query.get_or_404(product_id)
#     data = request.get_json()
    
#     try:
#         product.name = data.get('name', product.name)
#         product.stock_quantity = data.get('stock_quantity', product.stock_quantity)
#         product.price = data.get('price', product.price)
#         # ถ้ามีหมวดหมู่เพิ่ม สามารถแก้ category_id ตรงนี้ได้
        
#         db.session.commit()
#         return jsonify({'success': True, 'message': 'อัปเดตสินค้าสำเร็จ'})
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'success': False, 'message': str(e)}), 500

@api.route('/update_product/<int:id>', methods=['PUT'])
@login_required
def update_product(id):
    product = Product.query.get_or_404(id)
    data = request.get_json()
    
    product.name = data.get('name', product.name)
    product.price = data.get('price', product.price)
    product.stock_quantity = data.get('stock_quantity', product.stock_quantity)
    
    db.session.commit()
    return jsonify({"message": "Product updated successfully"})

# --- API สำหรับลบสินค้า (Soft Delete) ---
@api.route('/api/delete_product/<int:product_id>', methods=['DELETE'])
@login_required
def delete_product(product_id):
    if current_user.role != 'admin': # <--- เช็คสิทธิ์
        return jsonify({'success': False, 'message': 'สิทธิ์ไม่เพียงพอ'}), 403
    product = Product.query.get_or_404(product_id)
    try:
        # สมมติว่าใน Model Product มีคอลัมน์ is_deleted แล้ว
        product.is_deleted = True 
        db.session.commit()
        return jsonify({'success': True, 'message': 'ลบสินค้าเรียบร้อยแล้ว'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500