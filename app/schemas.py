from marshmallow import Schema, fields , validate , ValidationError

# 1. สำหรับจัดการหมวดหมู่สินค้า
class CategorySchema(Schema):
    id = fields.Int(dump_only=True) # dump_only คือใช้แสดงผลอย่างเดียว ไม่ต้องรับตอนสร้าง
    name = fields.Str(required=True, validate=validate.Length(min=2 , error="ชื่อหมวดหมู่ต้องมีอย่างน้อย 2 ตัวอักษร"))

# 2. สำหรับจัดการสินค้า (สำคัญมาก!)
class ProductSchema(Schema):
    id = fields.Int(dump_only=True)
    sku = fields.Str(required=True, validate=validate.Length(min=3 , error="SKU ต้องมีอย่างน้อย 3 ตัวอักษร"))
    name = fields.Str(required=True, validate=validate.Length(min=1 , error="ชื่อสินค้าต้องมีอย่างน้อย 1 ตัวอักษร"))
    price = fields.Float(required=True, validate=validate.Range(min=0.01 , error="ราคาต้องมากกว่า 0"))
    stock_quantity = fields.Int(required=True, validate=validate.Range(min=0 , error="สต็อกห้ามติดลบ"))
    category_id = fields.Int(required=True)

# 3. สำหรับรายการสินค้าในออเดอร์
class OrderItemSchema(Schema):
    product_id = fields.Int(required=True)
    quantity = fields.Int(required=True, validate=validate.Range(min=1 , error="จำนวนต้องมากกว่า 1 ชิ้น"))
    unit_price = fields.Float(dump_only=True)  # ราคาดึงมาจาก Product ตอนบันทึกจริง

# 4. สำหรับการสร้างออเดอร์ใหม่
class OrderSchema(Schema):
    id = fields.Int(dump_only=True)
    order_date = fields.DateTime(dump_only=True)
    total_amount = fields.Float(dump_only=True)
    status = fields.Str(dump_only=True)
    items = fields.List(fields.Nested(OrderItemSchema), required=True, validate=validate.Length(min=1 , error="ต้องมีรายการสินค้าอย่างน้อย 1 รายการ"))