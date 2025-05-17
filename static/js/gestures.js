document.addEventListener('DOMContentLoaded', () => {
    const video = document.createElement('video');
    video.style.display = 'none';
    document.body.appendChild(video);

    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            video.srcObject = stream;
            video.play();
        })
        .catch(err => console.error("Camera access denied:", err));

    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    function processFrame() {
        if (video.videoWidth && video.videoHeight) {
            canvas.width = video.videoWidth / 2;  // Downsample
            canvas.height = video.videoHeight / 2;
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            const frame = ctx.getImageData(0, 0, canvas.width, canvas.height).data;

            fetch('/ai/gesture/process/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken') || ''
                },
                body: JSON.stringify({ frame: Array.from(frame), width: canvas.width, height: canvas.height })
            })
            .then(response => response.json())
            .then(data => {
                if (data.gesture === 'swipe_left') {
                    window.location.href = getNextLessonUrl();
                } else if (data.gesture === 'swipe_right') {
                    window.location.href = getPreviousLessonUrl();
                }
            });
        }
        requestAnimationFrame(processFrame);
    }

    video.addEventListener('play', () => requestAnimationFrame(processFrame));

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function getNextLessonUrl() {
        return document.querySelector('a.next-lesson')?.href || window.location.href;
    }

    function getPreviousLessonUrl() {
        return document.querySelector('a.previous-lesson')?.href || window.location.href;
    }
});