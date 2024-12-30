
document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("search-input");
    const userRows = document.querySelectorAll("#user-table-body tr");

    // Hàm lọc bảng
    const filterTable = () => {
        const searchText = searchInput.value.toLowerCase();

        userRows.forEach(row => {
            const userName = row.querySelector("td:nth-child(3)").innerText.toLowerCase();
            if (userName.includes(searchText)) {
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
        userRows.forEach(row => (row.style.display = "")); // Hiển thị lại tất cả
    });
});
