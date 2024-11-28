

document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("search-input");
    const subjectRows = document.querySelectorAll("#subject-list tr");

    // Hàm lọc bảng
    const filterTable = () => {
        const searchText = searchInput.value.toLowerCase();

        subjectRows.forEach(row => {
            const subjectName = row.querySelector("td:nth-child(3)").innerText.toLowerCase();
            if (subjectName.includes(searchText)) {
                row.style.display = ""; // Hiển thị
            } else {
                row.style.display = "none"; // Ẩn
            }
        });
    };

    // Thực hiện tìm kiếm khi người dùng gõ
    searchInput.addEventListener("input", filterTable);

    // Xử lý khi ấn nút reset
    const resetButton = document.getElementById("reset-btn");
    resetButton.addEventListener("click", () => {
        searchInput.value = ""; // Xóa nội dung tìm kiếm
        subjectRows.forEach(row => (row.style.display = "")); // Hiển thị lại tất cả
    });
});