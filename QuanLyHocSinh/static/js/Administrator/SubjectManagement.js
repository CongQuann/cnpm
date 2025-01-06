
//Đợi DOM tải xong
document.addEventListener("DOMContentLoaded", () => {
    //lấy input tìm kiếm và các hàng trong bảng
    const searchInput = document.getElementById("search-input");
    const subjectRows = document.querySelectorAll("#subject-list tr");

    // Hàm lọc bảng dựa trên nội dung tìm kiếm
    const filterTable = () => {
        const searchText = searchInput.value.toLowerCase(); //chuyển nội dung tìm kiếm sang chữ thường để không phân biên hoa thường

        //duyệt qua từng hàng
        subjectRows.forEach(row => {
            //lấy cột thứ 3 (cột tên môn học) để chuyển sang chữ thường
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
    //lấy nút reset
    const resetButton = document.getElementById("reset-btn");
    //thêm sự kiện click vào cho nút reset
    resetButton.addEventListener("click", () => {
        searchInput.value = ""; // Xóa nội dung tìm kiếm
        subjectRows.forEach(row => (row.style.display = "")); // Hiển thị lại tất cả
    });
});