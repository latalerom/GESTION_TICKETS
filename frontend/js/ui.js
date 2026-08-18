const ui = {
    toastRoot: null,
    dialog: null,

    ensureToastRoot() {
        if (this.toastRoot) {
            return this.toastRoot;
        }

        this.toastRoot = document.createElement("div");
        this.toastRoot.className = "toast-stack";
        this.toastRoot.setAttribute("aria-live", "polite");
        document.body.appendChild(this.toastRoot);

        return this.toastRoot;
    },

    toast(text, type = "info") {
        const root = this.ensureToastRoot();
        const tone = this.toastTone(type);

        const toast = document.createElement("div");
        toast.className = `toast toast-${tone}`;

        toast.innerHTML = `
            <span class="toast-dot" aria-hidden="true"></span>
            <p>${this.escape(text)}</p>
            <button
                type="button"
                aria-label="Cerrar notificación"
            >
                &times;
            </button>
        `;

        const close = () => {
            toast.classList.add("toast-leaving");

            window.setTimeout(() => {
                toast.remove();
            }, 180);
        };

        toast.querySelector("button").addEventListener("click", close);

        root.appendChild(toast);

        window.setTimeout(close, 4200);
    },

    toastTone(type) {
        const aliases = {
            danger: "error",
            failed: "error",
            failure: "error",
            ok: "success",
            warn: "warning",
        };

        const tone = aliases[type] || type || "info";

        return ["success", "error", "info", "warning"].includes(tone)
            ? tone
            : "info";
    },

    confirm({
        title,
        message,
        confirmText = "Confirmar",
        cancelText = "Cancelar",
        danger = false,
    }) {
        return new Promise((resolve) => {
            const overlay = document.createElement("div");
            overlay.className = "dialog-overlay";

            overlay.innerHTML = `
                <section
                    class="dialog"
                    role="dialog"
                    aria-modal="true"
                    aria-labelledby="dialog-title"
                >
                    <h2 id="dialog-title">
                        ${this.escape(title)}
                    </h2>

                    <p>
                        ${this.escape(message)}
                    </p>

                    <div class="dialog-actions">
                        <button
                            class="button secondary"
                            type="button"
                            data-dialog="cancel"
                        >
                            ${this.escape(cancelText)}
                        </button>

                        <button
                            class="button ${danger ? "danger" : "primary"}"
                            type="button"
                            data-dialog="confirm"
                        >
                            ${this.escape(confirmText)}
                        </button>
                    </div>
                </section>
            `;

            const close = (result) => {
                overlay.classList.add("dialog-leaving");

                window.setTimeout(() => {
                    overlay.remove();
                }, 160);

                resolve(result);
            };

            overlay.addEventListener("click", (event) => {
                if (
                    event.target === overlay ||
                    event.target.dataset.dialog === "cancel"
                ) {
                    close(false);
                    return;
                }

                if (event.target.dataset.dialog === "confirm") {
                    close(true);
                }
            });

            document.body.appendChild(overlay);

            overlay
                .querySelector("[data-dialog='cancel']")
                .focus();
        });
    },

    textareaPrompt({
        title,
        message,
        label,
        placeholder = "",
        confirmText = "Guardar",
        cancelText = "Cancelar",
        required = true,
    }) {
        return new Promise((resolve) => {
            const overlay = document.createElement("div");
            overlay.className = "dialog-overlay";

            overlay.innerHTML = `
                <section
                    class="dialog dialog-wide"
                    role="dialog"
                    aria-modal="true"
                    aria-labelledby="dialog-title"
                >
                    <h2 id="dialog-title">
                        ${this.escape(title)}
                    </h2>

                    <p>
                        ${this.escape(message)}
                    </p>

                    <label for="dialog-textarea">
                        ${this.escape(label)}
                    </label>

                    <textarea
                        id="dialog-textarea"
                        rows="5"
                        placeholder="${this.escape(placeholder)}"
                    ></textarea>

                    <p class="dialog-error hidden">
                        Este campo es obligatorio.
                    </p>

                    <div class="dialog-actions">
                        <button
                            class="button secondary"
                            type="button"
                            data-dialog="cancel"
                        >
                            ${this.escape(cancelText)}
                        </button>

                        <button
                            class="button primary"
                            type="button"
                            data-dialog="confirm"
                        >
                            ${this.escape(confirmText)}
                        </button>
                    </div>
                </section>
            `;

            const textarea = overlay.querySelector("#dialog-textarea");
            const error = overlay.querySelector(".dialog-error");

            const close = (result) => {
                overlay.classList.add("dialog-leaving");

                window.setTimeout(() => {
                    overlay.remove();
                }, 160);

                resolve(result);
            };

            overlay.addEventListener("click", (event) => {
                if (
                    event.target === overlay ||
                    event.target.dataset.dialog === "cancel"
                ) {
                    close(null);
                    return;
                }

                if (event.target.dataset.dialog === "confirm") {
                    const value = textarea.value.trim();

                    if (required && !value) {
                        error.classList.remove("hidden");
                        textarea.focus();
                        return;
                    }

                    close(value);
                }
            });

            overlay.addEventListener("keydown", (event) => {
                if (event.key === "Escape") {
                    close(null);
                }
            });

            document.body.appendChild(overlay);

            textarea.focus();
        });
    },

    setupPasswordToggles(root = document) {
        root
            .querySelectorAll("[data-password-toggle]")
            .forEach((button) => {
                const selector = button.dataset.passwordToggle;

                if (!selector) {
                    return;
                }

                const input = root.querySelector(selector);

                if (!input) {
                    return;
                }

                const icon = button.querySelector(".password-icon");

                if (!icon) {
                    return;
                }

                button.addEventListener("click", () => {
                    const visible = input.type === "text";

                    input.type = visible ? "password" : "text";

                    const isVisible = !visible;

                    button.setAttribute(
                        "aria-pressed",
                        String(isVisible)
                    );

                    button.setAttribute(
                        "aria-label",
                        isVisible
                            ? "Ocultar contraseña"
                            : "Mostrar contraseña"
                    );

                    button.title = isVisible
                        ? "Ocultar contraseña"
                        : "Mostrar contraseña";

                    if (isVisible) {
                        icon.innerHTML = `
                            <path d="M3 3l18 18"></path>

                            <path d="
                                M10.6 5.2
                                A10.7 10.7 0 0 1 12 5
                                C18 5 21.5 12 21.5 12
                                A17.7 17.7 0 0 1 18.4 15.7
                            "></path>

                            <path d="
                                M6.2 6.3
                                C3.8 8.1 2.5 12 2.5 12
                                S6 19 12 19
                                C13.6 19 15 18.6 16.2 18
                            "></path>

                            <path d="
                                M9.9 9.9
                                A3 3 0 0 0 14.1 14.1
                            "></path>
                        `;
                    } else {
                        icon.innerHTML = `
                            <path d="
                                M2.5 12
                                S6 6 12 6
                                S21.5 12 21.5 12
                                S18 18 12 18
                                S2.5 12 2.5 12Z
                            "></path>

                            <circle
                                cx="12"
                                cy="12"
                                r="2.8"
                            ></circle>
                        `;
                    }
                });
            });
    },

    escape(value) {
        return String(value ?? "")
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    },
};


/*
 * Inicialización general de la interfaz.
 */
document.addEventListener("DOMContentLoaded", () => {
    ui.setupPasswordToggles();
});