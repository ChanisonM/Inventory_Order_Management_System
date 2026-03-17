function toggleModal() {
    const modal = document.getElementById('productModal')
    modal.classList.toggle('hidden')
}

// 1. ฟังก์ชันดึงข้อมูลสินค้าทั้งหมดมาโชว์ในตาราง
// async function loadProducts() {
//     const response = await fetch('/api/products'); // อิงจาก @api.route('/api/products', methods=['GET'])
//     const data = await response.json();
//     const tableBody = document.getElementById('product-table-body');

//     if (data.products && data.products.length > 0) {
//         tableBody.innerHTML = '';
//         data.products.forEach(p => {
//             tableBody.innerHTML += `
//                 <tr class="border-b hover:bg-gray-50 transition">
//                     <td class="px-6 py-4">${p.name}</td>
//                     <td class="px-6 py-4 text-center font-bold ${p.stock_quantity < 5 ? 'text-red-500' : 'text-gray-700'}">
//                         ${p.stock_quantity}
//                     </td>
//                     <td class="px-6 py-4 text-center">${Number(p.price).toLocaleString()} บาท</td>
                    
//                     <td class="px-6 py-4 text-center">
//                             <div class="text-sm text-gray-700 font-semibold">${p.created_by}</div>
//                             <div class="text-[10px] text-gray-400 italic">${p.created_at}</div>
//                     </td>
                    
//                     <td class="px-6 py-4 text-center">
//                             <button onclick="editProduct(${p.id})" class="text-blue-500 hover:text-blue-700 mr-3">
//                                 <i class="fa-solid fa-pen-to-square"></i>
//                             </button>
//                             <button onclick="deleteProduct(${p.id})" class="text-red-500 hover:text-red-700">
//                                 <i class="fa-solid fa-trash"></i>
//                             </button>
//                         </td>
//                 </tr>
//             `;
//             tbody.insertAdjacentHTML('beforeend', row);
//         });
//     }
// }

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
                        <button onclick="editProduct(${p.id})" class="text-blue-500 hover:text-blue-700 mr-3">
                            <i class="fa-solid fa-pen-to-square"></i>
                        </button>
                        <button onclick="deleteProduct(${p.id})" class="text-red-500 hover:text-red-700">
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
document.getElementById('productForm').onsubmit = async (e) => {
    e.preventDefault();
    const productData = {
        name: document.getElementById('p_name').value,
        stock_quantity: document.getElementById('p_qty').value,
        price: document.getElementById('p_price').value
    };

    // console.log(productData);


    const response = await fetch('/api/add_product', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(productData)
    });

    if (response.ok) {
        Swal.fire({
            icon: "success",
            title: "Success",
            text: `Save Data Success`,
            timer: 1500,
            showConfirmButton: false,
        })

        //   alert('บันทึกสำเร็จ!');
        document.getElementById('productForm').reset()
        toggleModal(); // ปิด Modal
        loadProducts(); // โหลดตารางใหม่ทันทีไม่ต้อง Refresh หน้า
    } else {
        alert('เกิดข้อผิดพลาดในการบันทึก');
    }
};

// เรียกโหลดข้อมูลครั้งแรกเมื่อเปิดหน้า
loadProducts();

