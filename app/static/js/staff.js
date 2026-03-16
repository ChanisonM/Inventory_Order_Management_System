let allStaff = [];      // เก็บรายชื่อทั้งหมดที่ดึงมาจาก Database
let currentPage = 1;    // หน้าปัจจุบัน
const rowsPerPage = 5; // จำนวนรายชื่อต่อหน้า


// async function loadStaffs() {
//     try {
//         const response = await fetch('api/get_staffs');
//         const data = await response.json();
//         // const tableBody = document.getElementById('staff-table-body');
        
//         allStaff = data.staffs

//         displayTable(1)

//         tableBody.innerHTML = '';

//         if (data.staffs.length === 0) {
//             tableBody.innerHTML = `<tr><td colspan="3" class="px-6 py-10 text-center text-gray-400">No staff members found.</td></tr>`;
//             return;
//         }

// data.staffs.forEach(s => {
//             // --- เช็กเงื่อนไขสีของ ROLE ---
//             // ถ้าเป็น admin ใช้สีม่วง (bg-purple-100 text-purple-700)
//             // ถ้าเป็น staff ใช้สีน้ำเงินเดิม (bg-blue-100 text-blue-700)
//             const roleClass = s.role === 'admin' 
//                 ? 'bg-purple-100 text-purple-700 border border-purple-200' 
//                 : 'bg-blue-100 text-blue-700';

//             tableBody.innerHTML += `
//                 <tr class="hover:bg-gray-50/80 transition-colors border-b border-gray-100">
//                     <td class="px-6 py-4 font-medium text-gray-800">
//                         ${s.username} 
//                         ${s.role === 'admin' ? '<i class="fa-solid fa-crown text-amber-500 ml-1 text-xs"></i>' : ''}
//                     </td>
//                     <td class="px-6 py-4">
//                         <span class="px-3 py-1 ${roleClass} rounded-full text-[11px] font-bold uppercase tracking-wider">
//                             ${s.role}
//                         </span>
//                     </td>
//                     <td class="px-6 py-4 text-center">
//                         <button onclick="editStaff(${s.id}, '${s.username}')" class="p-2 text-indigo-600 hover:bg-indigo-50 rounded-lg transition-all active:scale-90">
//                             <i class="fa-solid fa-user-pen"></i>
//                         </button>
//                         <button onclick="deleteStaff(${s.id} , '${s.username}')" class="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-all active:scale-90">
//                             <i class="fa-solid fa-trash-can"></i>
//                         </button>
//                     </td>
//                 </tr>
//             `;
//         });    
//     } catch (error) {
//         console.error('Error:', error);
//     }
// }

async function loadStaffs() {
    try {
        const response = await fetch('api/get_staffs');
        const data = await response.json();
        
        // 1. เก็บข้อมูลลงตัวแปรหลัก
        allStaff = data.staffs;
        
        // 2. เรียกใช้การแสดงผลแบบแบ่งหน้า (หน้า 1)
        // ฟังก์ชันนี้จะจัดการ tableBody.innerHTML ให้เองครับ
        displayTable(1);


    } catch (error) {
        console.error('Error:', error);
    }
}

// เรียกโหลดทันทีเมื่อเปิดหน้า
document.addEventListener('DOMContentLoaded', loadStaffs);


// --- 1. ฟังก์ชัน เปิด-ปิด Modal (แยกออกจาก Logic การส่งข้อมูล) ---
function toggleUserModal() {
    const modal = document.getElementById('userModal');
    modal.classList.toggle('hidden');
    modal.classList.toggle('flex');
}

// --- 2. ฟังก์ชันส่งข้อมูล API (วางไว้นอกฟังก์ชัน toggle) ---
document.getElementById("userForm").addEventListener('submit', async (e) => {
    e.preventDefault(); // เติมวงเล็บ () เพื่อหยุดการรีโหลดหน้า

    const userData = {
        username: document.getElementById('new_username').value,
        password: document.getElementById('new_password').value
    };

    try {
        const response = await fetch('/api/add_staff', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        });

        const result = await response.json(); // ประกาศตัวแปร result ไว้ใช้งาน

        if (response.ok) {
            Swal.fire({
                icon: "success",
                title: "Success",
                text: "เพิ่มพนักงานเรียบร้อยแล้ว",
                timer: 1500,
                showConfirmButton: false,
            });

            document.getElementById('userForm').reset();
            toggleUserModal(); // ใช้ toggleUserModal ให้ถูกตัว
        } else {
            Swal.fire({
                icon: "error",
                title: "Register failed",
                text: result.message || "เกิดข้อผิดพลาดบางอย่าง",
            });
        }
    } catch (error) {
        console.error('Error', error);
        Swal.fire({
            icon: "error",
            title: "Connection Error",
            text: "ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้",
        });
    }

    loadStaffs()
});


function displayTable(page) {
    currentPage = page;
    const tableBody = document.getElementById('staff-table-body');
    tableBody.innerHTML = '';

    // --- Logic การแบ่งหน้า (Pagination Logic) ---
    const start = (page - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    const paginatedItems = allStaff.slice(start, end);

    if (paginatedItems.length === 0) {
        tableBody.innerHTML = `<tr><td colspan="3" class="px-6 py-10 text-center text-gray-400">No staff members found.</td></tr>`;
        return;
    }

    // วนลูปแสดงผล (ยกโค้ดเดิมของนายมาไว้ตรงนี้)
    paginatedItems.forEach(s => {
        const roleClass = s.role === 'admin' 
            ? 'bg-purple-100 text-purple-700 border border-purple-200' 
            : 'bg-blue-100 text-blue-700';

        tableBody.innerHTML += `
            <tr class="hover:bg-gray-50/80 transition-colors border-b border-gray-100">
                <td class="px-6 py-4 font-medium text-gray-800">
                    ${s.username} 
                    ${s.role === 'admin' ? '<i class="fa-solid fa-crown text-amber-500 ml-1 text-xs"></i>' : ''}
                </td>
                <td class="px-6 py-4">
                    <span class="px-3 py-1 ${roleClass} rounded-full text-[11px] font-bold uppercase tracking-wider">
                        ${s.role}
                    </span>
                </td>
                <td class="px-6 py-4 text-center">
                    <button onclick="editStaff(${s.id}, '${s.username}')" class="p-2 text-indigo-600 hover:bg-indigo-50 rounded-lg transition-all active:scale-90">
                        <i class="fa-solid fa-user-pen"></i>
                    </button>

                    <button onclick="deleteStaff(${s.id} , '${s.username}')" class="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-all active:scale-90">
                        <i class="fa-solid fa-trash-can"></i>
                    </button>
                    
                </td>
            </tr>
        `;
    });

    // เรียกฟังก์ชันสร้างปุ่มเปลี่ยนหน้า
    renderPagination();
}


function renderPagination() {
    const controls = document.getElementById('pagination-controls');
    if (!controls) return; // กัน Error ถ้าลืมใส่ div ใน HTML

    const totalPages = Math.ceil(allStaff.length / rowsPerPage);
    
    controls.innerHTML = `
        <div class="flex items-center justify-between bg-white px-6 py-4 border-t border-gray-100">
            <div class="text-sm text-gray-500">
                Showing <span class="font-bold text-gray-700">${allStaff.length > 0 ? (currentPage - 1) * rowsPerPage + 1 : 0}</span> 
                to <span class="font-bold text-gray-700">${Math.min(currentPage * rowsPerPage, allStaff.length)}</span> 
                of <span class="font-bold text-gray-700">${allStaff.length}</span> staff members
            </div>
            <div class="inline-flex gap-2">
                <button onclick="displayTable(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''} 
                    class="px-4 py-2 text-sm font-semibold bg-white border border-gray-300 rounded-xl hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-all">
                    Previous
                </button>
                <button onclick="displayTable(${currentPage + 1})" ${currentPage === totalPages || totalPages === 0 ? 'disabled' : ''} 
                    class="px-4 py-2 text-sm font-semibold bg-white border border-gray-300 rounded-xl hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-all">
                    Next
                    
                </button>
            </div>
        </div>
    `;
}


async function editStaff(id , currentUsername) {
    const { value : formValues} = await Swal.fire({
        title: 'แก้ไขข้อมูลพนักงาน',
        html:
            `<div>`+
            `<label class="text-left block text-sm font-medium text-gray-700 mb-1">Username</label>` +
            `<input id="swal-input1" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition" placeholder="Username" value="${currentUsername}">` +
            `</div>`+
            `<div>`+
            `<label class="text-left block mb-2 mt-4 text-sm text-gray-600">รหัสผ่านใหม่ (ปล่อยว่างถ้าไม่เปลี่ยน)</label>` +
            `<input id="swal-input2" type="password" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition" placeholder="New Password">`+
            `</div>`,
        focusConfirm: false,
        showCancelButton: true,
        confirmButtonText: 'บันทึก',
        cancelButtonText: 'ยกเลิก',
        preConfirm: () => {
            return {
                username : document.getElementById('swal-input1').value,
                password : document.getElementById('swal-input2').value,
            }
        }    
    })

    if (formValues) {
        try {
            const response = await fetch(`api/update_staff/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formValues)
            });

            const result = await response.json();

            if (response.ok) {
                Swal.fire('สำเร็จ!', result.message, 'success');
                loadStaffs(); // รีโหลดข้อมูลในตารางใหม่
            } else {
                Swal.fire('ผิดพลาด', result.message, 'error');
            }
        } catch (error) {
            Swal.fire('ผิดพลาด', 'ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้', 'error');
        }
    }
}

async function deleteStaff(id, username) {
    const result = await Swal.fire({
        title: 'ยืนยันการลบ?',
        text: `คุณต้องการลบพนักงาน "${username}" ออกจากระบบใช่หรือไม่?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'ใช่, ลบเลย!',
        cancelButtonText: 'ยกเลิก'
    });

    if (result.isConfirmed) {
        try {
            const response = await fetch(`api/delete_staff/${id}`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (response.ok) {
                Swal.fire('ลบสำเร็จ!', data.message, 'success');
                loadStaffs(); // รีโหลดข้อมูลตารางใหม่
            } else {
                Swal.fire('ผิดพลาด', data.message, 'error');
            }
        } catch (error) {
            Swal.fire('ผิดพลาด', 'ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้', 'error');
        }
    }
}