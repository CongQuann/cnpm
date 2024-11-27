document.getElementById('add-subject-form').addEventListener('submit', function (e) {
    e.preventDefault();
    const subjectName = document.getElementById('subject-name').value;
    if (subjectName) {
        // Gửi yêu cầu thêm môn học tới server hoặc thêm vào danh sách hiển thị
        alert('Môn học đã được thêm!');
        this.reset(); // Reset form
    }
});





