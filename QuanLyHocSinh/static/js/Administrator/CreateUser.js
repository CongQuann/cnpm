document.addEventListener("DOMContentLoaded", function () {
    const roleSelect = document.getElementById("role");
    const staffRoleDiv = document.getElementById("staff-role");
    const teacherInfoDiv = document.getElementById("teacher-info");

    // Hiển thị mặc định cho Staff
    staffRoleDiv.style.display = "block";
    teacherInfoDiv.style.display = "none";

    // Thay đổi hiển thị theo phân quyền
    roleSelect.addEventListener("change", function () {
        const selectedRole = roleSelect.value;
        staffRoleDiv.style.display = selectedRole === "Staff" ? "block" : "none";
        teacherInfoDiv.style.display = selectedRole === "Teacher" ? "block" : "none";
    });

    // Kiểm tra xác nhận mật khẩu
    const form = document.getElementById("create-user-form");
    const passwordInput = document.getElementById("password");
    const confirmPasswordInput = document.getElementById("confirm-password");

    form.addEventListener("submit", function (e) {
        if (passwordInput.value !== confirmPasswordInput.value) {
            e.preventDefault();
            alert("Mật khẩu và xác nhận mật khẩu không trùng khớp!");
        }


        // Kiểm tra userName không có khoảng trắng và ký tự đặc biệt
        const userNameInput = document.getElementById("userName");
        const userNameRegex = /^[A-Za-z0-9]+$/; // Không cho phép khoảng trắng và ký tự đặc biệt
        if (!userNameRegex.test(userNameInput.value)) {
            e.preventDefault();
            alert("Tên đăng nhập không được chứa khoảng trắng hoặc ký tự đặc biệt!");
        }

        // Kiểm tra số năm kinh nghiệm không âm
        const yearExperienceInput = document.getElementById("yearExperience");
        const yearExperience = parseInt(yearExperienceInput.value);
        if (yearExperience < 0) {
            e.preventDefault();
            alert("Số năm kinh nghiệm không được âm!");
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const passwordInput = document.getElementById("password");
    const strengthBar = document.getElementById("password-strength-bar");
    const strengthText = document.getElementById("password-strength-text");

    passwordInput.addEventListener("input", function () {
        const password = passwordInput.value;
        const strength = calculatePasswordStrength(password);

        // Cập nhật thanh tiến trình
        strengthBar.style.width = `${strength.percent}%`;
        strengthBar.className = "progress-bar " + strength.colorClass;

        // Cập nhật thông báo độ mạnh
        strengthText.textContent = `Độ mạnh mật khẩu: ${strength.label}`;
    });

    function calculatePasswordStrength(password) {
        let score = 0;

        // Tăng điểm dựa trên độ dài
        if (password.length >= 8) score += 1;
        if (password.length >= 12) score += 1;

        // Tăng điểm dựa trên các loại ký tự
        if (/[a-z]/.test(password)) score += 1; // Chữ thường
        if (/[A-Z]/.test(password)) score += 1; // Chữ hoa
        if (/\d/.test(password)) score += 1; // Số
        if (/[\W_]/.test(password)) score += 1; // Ký tự đặc biệt

        // Xác định độ mạnh và màu sắc
        let strength = {
            percent: (score / 5) * 100,
            label: "Yếu",
            colorClass: "bg-danger"
        };

        if (score === 3) {
            strength.label = "Trung bình";
            strength.colorClass = "bg-warning";
        } else if (score >= 4) {
            strength.label = "Mạnh";
            strength.colorClass = "bg-success";
        }

        return strength;
    }
});

