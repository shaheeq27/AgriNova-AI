// ================================
// AI Crop Recommender Script
// ================================

// ------------------------
// Loading Screen
// ------------------------
function showLoader() {
    const loader = document.getElementById("loading-screen");

    if (loader) {
        loader.style.display = "flex";
        loader.style.opacity = "0";

        setTimeout(() => {
            loader.style.transition = "opacity 0.4s ease";
            loader.style.opacity = "1";
        }, 10);
    }
}

// ------------------------
// Floating Seed Particles
// ------------------------
document.addEventListener("DOMContentLoaded", () => {

    const container = document.getElementById("seeds");

    if (!container) return;

    const colors = [
        { col: "#4ee86a", glow: "#4ee86a88" },
        { col: "#a8e86a", glow: "#a8e86a66" },
        { col: "#6adc50", glow: "#6adc5066" },
        { col: "#c8ff90", glow: "#c8ff9044" },
        { col: "#2db84a", glow: "#2db84a55" },
        { col: "#88ee44", glow: "#88ee4455" }
    ];

    for (let i = 0; i < 45; i++) {

        const seed = document.createElement("div");
        seed.className = "seed";

        const colour = colors[Math.floor(Math.random() * colors.length)];

        const width = 4 + Math.random() * 6;
        const height = width * (1.4 + Math.random() * 0.6);

        seed.style.cssText = `
            --x:${Math.random() * 100}%;
            --dur:${4 + Math.random() * 5}s;
            --delay:${Math.random() * 6}s;
            --w:${width}px;
            --h:${height}px;
            --rot:${Math.random() * 60 - 30}deg;
            --sway:${(Math.random() - 0.5) * 120}px;
            --col:${colour.col};
            --glow:${colour.glow};
        `;

        container.appendChild(seed);
    }

});

// ------------------------
// Button Hover Effect
// ------------------------
document.addEventListener("DOMContentLoaded", () => {

    const btn = document.querySelector(".analyze-btn");

    if (!btn) return;

    btn.addEventListener("mouseenter", () => {
        btn.style.transform = "translateY(-3px)";
    });

    btn.addEventListener("mouseleave", () => {
        btn.style.transform = "translateY(0px)";
    });

});

// ------------------------
// Fade In Form
// ------------------------
document.addEventListener("DOMContentLoaded", () => {

    const content = document.querySelector(".content");

    if (!content) return;

    content.style.opacity = "0";
    content.style.transform = "translateY(30px)";

    setTimeout(() => {

        content.style.transition =
            "opacity .9s ease, transform .9s ease";

        content.style.opacity = "1";
        content.style.transform = "translateY(0)";

    }, 200);

});

// ------------------------
// Feature Card Animation
// ------------------------
document.addEventListener("DOMContentLoaded", () => {

    const cards = document.querySelectorAll(".feature-card");

    cards.forEach((card, index) => {

        card.style.opacity = "0";
        card.style.transform = "translateY(30px)";

        setTimeout(() => {

            card.style.transition =
                "all .7s cubic-bezier(.16,1,.3,1)";

            card.style.opacity = "1";
            card.style.transform = "translateY(0)";

        }, 700 + index * 180);

    });

});
document.addEventListener("DOMContentLoaded", () => {

    const city = document.getElementById("city");
    const soil = document.getElementById("soil");
    const season = document.getElementById("season");

    const previewCity = document.getElementById("preview-city");
    const previewSoil = document.getElementById("preview-soil");
    const previewSeason = document.getElementById("preview-season");

    if (!city || !soil || !season || !previewCity || !previewSoil || !previewSeason) {
        return;
    }

    city.addEventListener("input", () => {
        previewCity.textContent = city.value.trim() || "Waiting for input...";
    });

    soil.addEventListener("change", () => {
        previewSoil.textContent = soil.value || "Awaiting selection...";
    });

    season.addEventListener("change", () => {
        previewSeason.textContent = season.value || "Awaiting selection...";
    });

});