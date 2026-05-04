(function () {
    const slides = Array.from(document.querySelectorAll("#slideshow .slide"));
    const dots = Array.from(document.querySelectorAll("#slideshow-dots .dot"));
    if (slides.length <= 1) return;

    let current = 0;
    let timer = null;

    function show(idx) {
        slides[current].classList.remove("active");
        dots[current].classList.remove("active");
        current = (idx + slides.length) % slides.length;
        slides[current].classList.add("active");
        dots[current].classList.add("active");
    }

    function next() { show(current + 1); }

    function start() {
        stop();
        timer = setInterval(next, 5000);
    }
    function stop() {
        if (timer) { clearInterval(timer); timer = null; }
    }

    dots.forEach((dot) => {
        dot.addEventListener("click", () => {
            const i = parseInt(dot.dataset.index, 10);
            show(i);
            start();
        });
    });

    start();
})();
