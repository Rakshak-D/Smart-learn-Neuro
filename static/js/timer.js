document.addEventListener('DOMContentLoaded', function() {
    const progressBar = document.querySelector('.progress-bar');
    if (progressBar) {
        let progress = parseFloat(progressBar.style.width) || 0;
        const updateProgress = () => {
            if (progress < 100) {
                progress += 10;
                progressBar.style.width = `${progress}%`;
                progressBar.setAttribute('aria-label', `Progress: ${progress}%`);
            }
        };
        setInterval(updateProgress, 2000);
    }
});