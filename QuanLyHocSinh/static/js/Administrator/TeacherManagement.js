document.getElementById('experience_years').addEventListener('input', function (e) {
    if (e.target.value < 0) {
        alert('Số năm kinh nghiệm không được nhỏ hơn 0!');
        e.target.value = '';
    }
});

document.getElementById('teacher_name').addEventListener('input', function (e) {
    const regex = /^[a-zA-ZÀ-ỹ\s]+$/u;
    if (!regex.test(e.target.value)) {
        alert('Tên giáo viên không được chứa ký tự đặc biệt hoặc số!');
        e.target.value = e.target.value.replace(/[^a-zA-ZÀ-ỹ\s]/gu, '');
    }
});
