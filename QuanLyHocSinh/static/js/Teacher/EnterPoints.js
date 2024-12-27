


document.addEventListener("DOMContentLoaded", function() {
        // Các phần tử input
        const classInput = document.getElementById("class-input");
        const subjectInput = document.getElementById("subject-input");
        const semesterInput = document.getElementById("semester-input");
        const academicYearInput = document.getElementById("academic-year-input");



        // Hiển thị thông tin đã nhập vào
        classInput.addEventListener("input", function() {
            const enteredClass = classInput.value;
            document.getElementById("class-display").textContent = "Lớp đã nhập: " + enteredClass;
        });

        subjectInput.addEventListener("input", function() {
            const enteredSubject = subjectInput.value;
            document.getElementById("subject-display").textContent = "Môn đã nhập: " + enteredSubject;
        });

        semesterInput.addEventListener("input", function() {
            const enteredSemester = semesterInput.value;
            document.getElementById("semester-display").textContent = "Học kỳ đã nhập: " + enteredSemester;
        });

        academicYearInput.addEventListener("input", function() {
            const enteredYear = academicYearInput.value;
            document.getElementById("academic-year-display").textContent = "Năm học đã nhập: " + enteredYear;
        });
    });


document.addEventListener('DOMContentLoaded', function () {
        const studentRows = document.getElementById('student-rows');
        const add15MinBtn = document.getElementById('add-15min-btn');
        const remove15MinBtn = document.getElementById('remove-15min-btn');
        const addTestBtn = document.getElementById('add-test-btn');
        const removeTestBtn = document.getElementById('remove-test-btn');

        // Giới hạn số cột
        const MAX_15MIN = 5;
        const MAX_TEST = 3;




        // Thêm ô nhập điểm 15 phút
        add15MinBtn.addEventListener('click', () => {
        const rows = studentRows.querySelectorAll('tr');
        rows.forEach(row => {
            const container = row.querySelector('.score-15min-container');
            const inputs = container.querySelectorAll('.score-15min');
            if (inputs.length < MAX_15MIN - 1) {
                const newInput = document.createElement('input');
                newInput.type = 'number';
                newInput.className = 'input-cell score-15min';
                newInput.name='scores_15min[]';
                newInput.placeholder = 'Điểm 15’';
                newInput.min = "0";
                newInput.max = "10";
                container.appendChild(newInput);
            }
        });
        });


    // Xóa ô nhập điểm 15 phút cuối cùng
        remove15MinBtn.addEventListener('click', () => {
            const rows = studentRows.querySelectorAll('tr');
            rows.forEach(row => {
                const container = row.querySelector('.score-15min-container');
                const inputs = container.querySelectorAll('.score-15min');
                    if (inputs.length > 0) {
                        container.removeChild(inputs[inputs.length - 1]);
                    }
        });
        });
        addTestBtn.addEventListener('click', () => {
            const rows = studentRows.querySelectorAll('tr');
            rows.forEach(row => {
                const container = row.querySelector('.test-container');
                const inputs = container.querySelectorAll('.test-score');
                if (inputs.length < MAX_TEST - 1) {
                    const newInput = document.createElement('input');
                    newInput.type = 'number';
                    newInput.name = 'scores_test[]';
                    newInput.className = 'input-cell test-score';
                    newInput.placeholder = 'Điểm 1 tiết';
                    newInput.min = "0";
                    newInput.max = "10";
                    container.appendChild(newInput);
                }
            });
        });


        removeTestBtn.addEventListener('click', () => {
            const rows = studentRows.querySelectorAll('tr');
            rows.forEach(row => {
                const container = row.querySelector('.test-container');
                const inputs = container.querySelectorAll('.test-score');
                if (inputs.length > 0) {
                    container.removeChild(inputs[inputs.length - 1]);
                }
            });
        });

        // Đảm bảo giá trị nhập vào nằm trong khoảng 0-10
        studentRows.addEventListener('input', (event) => {
            const target = event.target;
            if (target.type === 'number') {
                if (target.value < 0) target.value = 0;
                if (target.value > 10) target.value = 10;
            }
        });

    });

//setTimeout(function() {
//    var flashMessages = document.getElementById('flash-messages');
//    if (flashMessages) {
//      flashMessages.style.display = 'none';
//    }
//  }, 5000);


