
document.addEventListener('DOMContentLoaded', function () {
        const studentRows = document.getElementById('student-rows');
        studentRows.addEventListener('input', (event) => {
            const target = event.target;
            if (target.type === 'number') {
                if (target.value < 0) target.value = 0;
                if (target.value > 10) target.value = 10;
            }
        });

    });

setTimeout(function() {
    var flashMessages = document.getElementById('flash-messages');
    if (flashMessages) {
      flashMessages.style.display = 'none';
    }
  }, 5000);


