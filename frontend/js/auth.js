const form = document.querySelector("#login-form");
const message = document.querySelector("#login-message");

function showMessage(text, type = "error") {
    message.textContent = text;
    message.className = `message ${type}`;
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
