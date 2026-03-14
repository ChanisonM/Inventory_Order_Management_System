async function loadStaffs() {
    try {
        const response = await fetch('api/get_staffs');
        const data = await response.json();
        const tableBody = document.getElementById('staff-table-body');
        
        tableBody.innerHTML = '';

        if (data.staffs.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="3" class="px-6 py-10 text-center text-gray-400">No staff members found.</td></tr>`;
            return;
        }

data.staffs.forEach(s => {
            // --- เช็กเงื่อนไขสีของ ROLE ---
            // ถ้าเป็น admin ใช้สีม่วง (bg-purple-100 text-purple-700)
            // ถ้าเป็น staff ใช้สีน้ำเงินเดิม (bg-blue-100 text-blue-700)
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
                    </td>
                </tr>
            `;
        });    } catch (error) {
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
});