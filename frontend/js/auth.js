const form = document.querySelector("#login-form");

function showMessage(text, type = "error") {
    ui.toast(text, type);
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const formData = new FormData(form);

    try {
        await api.login(formData.get("email"), formData.get("password"));
        window.location.href = "dashboard.html";
    } catch (error) {
        showMessage(error.message);
    }
});
