   document.addEventListener('DOMContentLoaded', function () {
   document.getElementById('drawChart').addEventListener('click', function () {
        // Dữ liệu từ bảng
        const classNames = {{ statistics | tojson | safe }};
        const totalStudents = classNames.map(stat => stat.total_students);
        const numPassed = classNames.map(stat => stat.num_passed);

        // Vẽ biểu đồ
        const ctx = document.getElementById('reportChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: classNames.map(stat => stat.class_name),
                datasets: [
                    {
                        label: 'Tổng số học sinh',
                        data: totalStudents,
                        backgroundColor: 'rgba(54, 162, 235, 0.6)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Số học sinh đạt',
                        data: numPassed,
                        backgroundColor: 'rgba(75, 192, 192, 0.6)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    });