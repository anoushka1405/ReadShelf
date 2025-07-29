document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll('.mark-read-link').forEach(btn => {
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        confetti({
          particleCount: 150,
          spread: 70,
          origin: { y: 0.6 },
        });
        setTimeout(() => {
          window.location.href = this.dataset.href;
        }, 1000);
      });
    });
  });
  