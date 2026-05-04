(function () {
    const statusEl = document.getElementById("qr-status");
    const manualForm = document.getElementById("manual-form");

    async function submitToken(token) {
        statusEl.textContent = "Doğrulanıyor...";
        try {
            const res = await fetch("/qr-login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ token })
            });
            if (!res.ok) {
                const data = await res.json().catch(() => ({}));
                statusEl.textContent = data.detail || "QR tanınmadı.";
                return;
            }
            const data = await res.json();
            window.location.href = data.redirect || "/";
        } catch (e) {
            statusEl.textContent = "Bağlantı hatası: " + e.message;
        }
    }

    if (window.Html5Qrcode) {
        const reader = new Html5Qrcode("qr-reader");
        reader.start(
            { facingMode: "environment" },
            { fps: 10, qrbox: 240 },
            (decoded) => {
                reader.stop().catch(() => {});
                submitToken(decoded);
            },
            () => {}
        ).catch((err) => {
            statusEl.textContent = "Kamera açılamadı: " + err;
        });
    } else {
        statusEl.textContent = "QR kütüphanesi yüklenemedi.";
    }

    if (manualForm) {
        manualForm.addEventListener("submit", (ev) => {
            ev.preventDefault();
            const token = document.getElementById("manual-token").value.trim();
            if (token) submitToken(token);
        });
    }
})();
