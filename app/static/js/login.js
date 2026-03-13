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
                title: "Login Success",
                text: `Welcome ${data.user.username}`,
                timer: 1500,
                showConfirmButton: false,
            }).then(() => {
                window.location.href = "/api/dashboard"; // ย้ายไปหน้า Dashboard
            });
        } else {
            Swal.fire({
                icon: "error",
                title: "Login failed",
                text: data.message || "Incorrect username or password.",
            });
        }
    } catch (error) {
        console.log("Error", error);
        Swal.fire({
            icon: "error",
            title: "An error occurred.",
            text: "Unable to contact server",
        });
    }
});
