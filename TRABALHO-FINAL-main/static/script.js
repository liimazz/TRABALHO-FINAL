document.addEventListener("DOMContentLoaded", function () {

    // =========================
    // TEMA ESCURO / CLARO
    // =========================
    const themeBtn = document.getElementById("theme-toggle");
    const htmlElement = document.documentElement;

    const savedTheme = localStorage.getItem("theme");
    if (savedTheme) {
        htmlElement.setAttribute("data-theme", savedTheme);
        atualizarIcone(savedTheme);
    }

    if (themeBtn) {
        themeBtn.addEventListener("click", function () {
            const currentTheme = htmlElement.getAttribute("data-theme");
            const newTheme = currentTheme === "dark" ? "light" : "dark";

            if (newTheme === "dark") {
                htmlElement.setAttribute("data-theme", "dark");
            } else {
                htmlElement.removeAttribute("data-theme");
            }

            localStorage.setItem("theme", newTheme);
            atualizarIcone(newTheme);
        });
    }

    function atualizarIcone(theme) {
        if (!themeBtn) return;
        const icon = themeBtn.querySelector("i");
        if (icon) {
            icon.className = theme === "dark" ? "bi bi-sun-fill" : "bi bi-moon-stars-fill";
        }
    }

    // =========================
    // ANO AUTOMÁTICO NO RODAPÉ
    // =========================
    const anoElement = document.getElementById("ano");
    if (anoElement) {
        anoElement.textContent = new Date().getFullYear();
    }

    // =========================
    // BOTÃO VOLTAR AO TOPO
    // =========================
    const btnTopo = document.getElementById("topo");

    window.addEventListener("scroll", function () {
        if (window.scrollY > 300) {
            btnTopo.style.display = "block";
        } else {
            btnTopo.style.display = "none";
        }
    });

    if (btnTopo) {
        btnTopo.addEventListener("click", function () {
            window.scrollTo({
                top: 0,
                behavior: "smooth"
            });
        });
    }

});