document.addEventListener('DOMContentLoaded', function() {
  const progressBar = document.querySelector('div[style*="background"]');
  if (progressBar) {
    let progress = parseFloat(progressBar.style.width) || 0;
    setInterval(() => {
      if (progress < 100) {
        progress += 10;
        progressBar.style.width = `${progress}%`;
      }
    }, 2000);
  }
});