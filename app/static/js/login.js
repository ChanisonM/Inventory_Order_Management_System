document.getElementById("loginForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    // console.log(username , password);

    try {
        const response = await fetch("/api/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password }),
        });

        const data = await response.json();

        if (response.ok) {
            Swal.fire({
                icon: "success",
                title: "เข้าสู่ระบบสำเร็จ",
                text: `ยินดีต้อนรับคุณ ${data.user.username}`,
                timer: 1500,
                showConfirmButton: false,
            }).then(() => {
                window.location.href = "/dashboard"; // ย้ายไปหน้า Dashboard
            });
        } else {
            Swal.fire({
                icon: "error",
                title: "เข้าสู่ระบบไม่สำเร็จ",
                text: data.message || "ชื่อผู้ใช้หรือรหัสผ่านผิด",
            });
        }
    } catch (error) {
        console.log("Error", error);
        Swal.fire({
            icon: "error",
            title: "เกิดข้อผิดพลาด",
            text: "ไม่สามารถติดต่อเซิร์ฟเวอร์ได้",
        });
    }
});
