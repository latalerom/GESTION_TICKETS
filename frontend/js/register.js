const params = new URLSearchParams(window.location.search);
const token = params.get("token");
const summary = document.querySelector("#register-summary");
const form = document.querySelector("#register-form");

function showMessage(text, type = "error") {
    ui.toast(text, type);
}

async function loadInvitation() {
    if (!token) {
        showMessage("El enlace de registro no contiene token.");
        return;
    }

    try {
        const invitation = await api.getInvitation(token);
        summary.textContent = `Registro para ${invitation.email} como ${invitation.rol}.`;
        form.classList.remove("hidden");
    } catch (error) {
        showMessage(error.message);
        summary.textContent = "No fue posible validar la invitacion.";
    }
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const formData = new FormData(form);

    try {
        await api.register(token, formData.get("nombre"), formData.get("password"), {
            telefono: formData.get("telefono"),
            cargo: formData.get("cargo"),
            bio: formData.get("bio"),
        });
        showMessage("Cuenta creada correctamente. Redirigiendo...", "success");
        window.setTimeout(() => {
            window.location.href = "dashboard.html";
        }, 900);
    } catch (error) {
        showMessage(error.message);
    }
});

loadInvitation();
