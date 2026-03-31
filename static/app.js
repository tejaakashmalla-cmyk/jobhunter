document.querySelectorAll("a").forEach(link => {
    link.addEventListener("click", function(e) {
        document.body.style.opacity = 0;
    });
});