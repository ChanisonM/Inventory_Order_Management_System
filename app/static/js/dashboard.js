let allProducts = [];      // สำหรับเก็บข้อมูลสินค้าทั้งหมดที่ fetch มา
let currentPage = 1;       // หน้าปัจจุบัน
const rowsPerPage = 5;     // จำนวนรายการต่อหน้า (ปรับได้ตามชอบ)

function toggleModal() {
  const modal = document.getElementById("productModal");
  modal.classList.toggle("hidden");
}

async function loadProducts() {
    const response = await fetch('/api/products'); 
    const data = await response.json();
    const tableBody = document.getElementById('product-table-body');

    if (data.products && data.products.length > 0) {
        tableBody.innerHTML = ''; // ล้างข้อมูลเก่า
        data.products.forEach(p => {
            // สร้าง HTML Row
            const row = `
                <tr class="border-b hover:bg-gray-50 transition">
                    <td class="px-6 py-4">${p.name}</td>
                    <td class="px-6 py-4 text-center font-bold ${p.stock_quantity < 5 ? 'text-red-500' : 'text-gray-700'}">
                        ${p.stock_quantity}
                    </td>
                    <td class="px-6 py-4 text-center">${Number(p.price).toLocaleString()} บาท</td>
                    <td class="px-6 py-4 text-center">
                        <div class="text-sm text-gray-700 font-semibold">${p.created_by}</div>
                        <div class="text-[10px] text-gray-400 italic">${p.created_at}</div>
                    </td>
                    <td class="px-6 py-4 text-center">
                        <button onclick="editProduct(${p.id}, '${p.name}', ${p.price}, ${p.stock_quantity})" class="text-blue-500 hover:text-blue-700 mr-3">
                            <i class="fa-solid fa-pen-to-square"></i>
                        </button>
                        <button onclick="deleteProduct(${p.id}, '${p.name}')" class="text-red-500 hover:text-red-700">
                            <i class="fa-solid fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
            // ใช้ tableBody ที่ประกาศไว้ตอนต้น
            tableBody.insertAdjacentHTML('beforeend', row);
        });
    }
}
// 2. ฟังก์ชันส่งข้อมูลจาก Modal ไปบันทึก
document.getElementById("productForm").onsubmit = async (e) => {
  e.preventDefault();
  const productData = {
    name: document.getElementById("p_name").value,
    stock_quantity: document.getElementById("p_qty").value,
    price: document.getElementById("p_price").value,
  };

  // console.log(productData);

  const response = await fetch("/api/add_product", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(productData),
  });

  if (response.ok) {
    Swal.fire({
      icon: "success",
      title: "Success",
      text: `Save Data Success`,
      timer: 1500,
      showConfirmButton: false,
    });

    //   alert('บันทึกสำเร็จ!');
    document.getElementById("productForm").reset();
    toggleModal(); // ปิด Modal
    loadProducts(); // โหลดตารางใหม่ทันทีไม่ต้อง Refresh หน้า
  } else {
    alert("เกิดข้อผิดพลาดในการบันทึก");
  }
};

function displayTable(page) {
  currentPage = page;
  const tableBody = document.getElementById("product-table-body");
  tableBody.innerHTML = ""; // ล้างข้อมูลเก่า

  

  

  // ใช้ Logic การสร้าง Row เดิมของนาย
  paginatedItems.forEach((p) => {
    const row = `
      <tr class="border-b hover:bg-gray-50 transition">
          <td class="px-6 py-4">${p.name}</td>
          <td class="px-6 py-4 text-center font-bold ${p.stock_quantity < 5 ? "text-red-500" : "text-gray-700"}">
              ${p.stock_quantity}
          </td>
          <td class="px-6 py-4 text-center">${Number(p.price).toLocaleString()} บาท</td>
          <td class="px-6 py-4 text-center">
              <div class="text-sm text-gray-700 font-semibold">${p.created_by}</div>
              <div class="text-[10px] text-gray-400 italic">${p.created_at}</div>
          </td>
          <td class="px-6 py-4 text-center">
              <button onclick="editProduct(${p.id} , '${p.name}' , ${p.price} , ${p.stock_quantity})" class="text-blue-500 hover:text-blue-700 mr-3">
                  <i class="fa-solid fa-pen-to-square"></i>
              </button>
              <button onclick="deleteProduct(${p.id} , '${p.name}')" class="text-red-500 hover:text-red-700">
                  <i class="fa-solid fa-trash"></i>
              </button>
          </td>
      </tr>
    `;
    tableBody.insertAdjacentHTML("beforeend", row);
  });

  renderPagination(); // สร้างปุ่มกดเปลี่ยนหน้า
} 
// function renderPagination() {
//   const controls = document.getElementById("pagination-controls");
//   if (!controls) return;

//   const totalPages = Math.ceil(allProducts.length / rowsPerPage);

//   controls.innerHTML = `
//     <div class="flex items-center justify-between px-6 py-4 bg-white border-t border-gray-100">
//         <div class="text-sm text-gray-500">
//             Showing <span class="font-bold text-gray-700">${allProducts.length}</span> 
//             หน้า <span class="font-bold text-gray-700">${currentPage}</span> จาก <span class="font-bold text-gray-700">${totalPages}</span>
//     </div>

        
        
//         <div class="inline-flex gap-2">
//             <button onclick="displayTable(${currentPage - 1})" ${currentPage === 1 ? "disabled" : ""} 
//                 class="px-4 py-2 text-sm font-semibold bg-white border border-gray-300 rounded-xl hover:bg-gray-50 disabled:opacity-40 transition-all">
//                 ย้อนกลับ
//             </button>
//             <button onclick="displayTable(${currentPage + 1})" ${currentPage === totalPages || totalPages === 0 ? "disabled" : ""} 
//                 class="px-4 py-2 text-sm font-semibold bg-white border border-gray-300 rounded-xl hover:bg-gray-50 disabled:opacity-40 transition-all">
//                 ถัดไป
//             </button>
//         </div>
//     </div>
//   `;
// }

async function editProduct(id, currentName, currentPrice, currentStock) {
  const { value: formValues } = await Swal.fire({
    title: "แก้ไขข้อมูลสินค้า",
    html:
      `<div class="text-left">` +
      `<label class="block text-sm font-medium text-gray-700 mb-1">ชื่อสินค้า</label>` +
      `<input id="edit-name" class="w-full px-4 py-2 border rounded-lg mb-3" value="${currentName}">` +
      `<label class="block text-sm font-medium text-gray-700 mb-1">ราคา</label>` +
      `<input id="edit-price" type="number" class="w-full px-4 py-2 border rounded-lg mb-3" value="${currentPrice}">` +
      `<label class="block text-sm font-medium text-gray-700 mb-1">จำนวนสต็อก</label>` +
      `<input id="edit-stock" type="number" class="w-full px-4 py-2 border rounded-lg mb-3" value="${currentStock}">` +
      `</div>`,
    focusConfirm: false,
    showCancelButton: true,
    confirmButtonText: "บันทึกการเปลี่ยนแปลง",
    cancelButtonText: "ยกเลิก",
    preConfirm: () => {
      return {
        name: document.getElementById("edit-name").value,
        price: document.getElementById("edit-price").value,
        stock_quantity: document.getElementById("edit-stock").value,
      };
    },
  });

  if (formValues) {
    // 1. ตรวจสอบค่าว่าง (Validation)
    if (!formValues.name.trim()) {
      Swal.fire("ผิดพลาด!", "กรุณาระบุชื่อสินค้า", "error");
      return; // หยุดการทำงาน ไม่ส่ง API
    }

    if (!formValues.price || formValues.price <= 0) {
      Swal.fire("ผิดพลาด!", "กรุณาระบุราคาที่มากกว่า 0", "error");
      return;
    }

    if (formValues.stock_quantity === "" || formValues.stock_quantity < 0) {
      Swal.fire("ผิดพลาด!", "จำนวนสต็อกต้องไม่เป็นค่าว่างหรือติดลบ", "error");
      return;
    }
    // 2. ถ้าผ่านการเช็กทั้งหมด ถึงจะส่ง API
    try {
      const response = await fetch(`/api/update_product/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formValues),
      });

      const result = await response.json();
      if (response.ok) {
        Swal.fire("สำเร็จ!", "อัปเดตข้อมูลสินค้าเรียบร้อย", "success");
        loadProducts(); // รีโหลดตาราง
      } else {
        Swal.fire("ผิดพลาด", result.message, "error");
      }
    } catch (error) {
      Swal.fire("ผิดพลาด", "ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้", "error");
    }
  }
}

// ฟังก์ชันสำหรับลบสินค้า (Soft Delete)
async function deleteProduct(id, productName) {
  console.log(productName);

  const result = await Swal.fire({
    title: "ยืนยันการลบสินค้า?",
    text: `คุณต้องการลบ "${productName}" ใช่หรือไม่? (ข้อมูลจะยังอยู่ในระบบแต่ไม่แสดงหน้าเว็บ)`,
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#d33",
    cancelButtonColor: "#3085d6",
    confirmButtonText: "ใช่, ลบเลย!",
    cancelButtonText: "ยกเลิก",
  });

  if (result.isConfirmed) {
    try {
      // เรียก API ที่นายทำไว้ใน routes.py
      const response = await fetch(`api/delete_product/${id}`, {
        method: "DELETE",
      });

      const data = await response.json();

      if (response.ok) {
        await Swal.fire({
          icon: "success",
          title: "ลบสำเร็จ!",
          text: data.message,
          timer: 1500,
          showConfirmButton: false,
        });

        // ✅ เรียกฟังก์ชันโหลดข้อมูลใหม่ (สมมติว่านายใช้ชื่อ loadProducts)
        if (typeof loadProducts === "function") {
          loadProducts();
        } else {
          location.reload(); // ถ้าไม่มีฟังก์ชันโหลดเฉพาะจุด ให้รีโหลดหน้าแทน
        }
      } else {
        Swal.fire("ผิดพลาด!", data.message || "ไม่สามารถลบสินค้าได้", "error");
      }
    } catch (error) {
      console.error("Error:", error);
      Swal.fire("ผิดพลาด!", "ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้", "error");
    }
  }
}

// เรียกโหลดข้อมูลครั้งแรกเมื่อเปิดหน้า
loadProducts();
