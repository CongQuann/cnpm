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