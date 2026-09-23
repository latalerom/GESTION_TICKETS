const ui = {
    toastRoot: null,
    dialog: null,
    themeKey: "ticketflowTheme",
    cookieNoticeKey: "ticketflowCookieNoticeAccepted",

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

            this.bindDialogKeyboard(overlay, close, false);

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

            this.bindDialogKeyboard(overlay, close, null);

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

    bindDialogKeyboard(overlay, close, cancelResult = false) {
        overlay.addEventListener("keydown", (event) => {
            if (event.key === "Escape") {
                close(cancelResult);
                return;
            }

            if (event.key !== "Tab") {
                return;
            }

            const focusable = [...overlay.querySelectorAll(
                "a[href], button:not([disabled]), textarea, input, select, [tabindex]:not([tabindex='-1'])"
            )].filter((element) => element.offsetParent !== null);

            if (focusable.length === 0) {
                return;
            }

            const first = focusable[0];
            const last = focusable[focusable.length - 1];

            if (event.shiftKey && document.activeElement === first) {
                event.preventDefault();
                last.focus();
            } else if (!event.shiftKey && document.activeElement === last) {
                event.preventDefault();
                first.focus();
            }
        });
    },

    initTheme() {
        const savedTheme = localStorage.getItem(this.themeKey) || "system";
        this.applyTheme(savedTheme);
        this.renderThemeControl(savedTheme);
    },

    applyTheme(theme) {
        const normalized = ["light", "dark", "system"].includes(theme) ? theme : "system";
        document.documentElement.dataset.theme = normalized;
        localStorage.setItem(this.themeKey, normalized);
    },

    renderThemeControl(theme) {
        if (document.querySelector(".theme-control")) {
            return;
        }

        const control = document.createElement("label");
        control.className = "theme-control";
        control.innerHTML = `
            <span class="sr-only">Tema visual</span>
            <select aria-label="Tema visual">
                <option value="system">Automatico</option>
                <option value="light">Claro</option>
                <option value="dark">Oscuro</option>
            </select>
        `;

        const select = control.querySelector("select");
        select.value = theme;
        select.addEventListener("change", () => this.applyTheme(select.value));

        document.body.appendChild(control);
    },

    initCookieNotice() {
        if (localStorage.getItem(this.cookieNoticeKey) === "true") {
            return;
        }

        const notice = document.createElement("section");
        notice.className = "cookie-notice";
        notice.setAttribute("aria-label", "Aviso de cookies");
        notice.innerHTML = `
            <p>Usamos cookie de sesion necesaria y preferencias locales. No usamos cookies de publicidad.</p>
            <div>
                <a href="cookies.html">Ver politica</a>
                <button class="button primary" type="button">Entendido</button>
            </div>
        `;

        notice.querySelector("button").addEventListener("click", () => {
            localStorage.setItem(this.cookieNoticeKey, "true");
            notice.remove();
        });

        document.body.appendChild(notice);
    },
};


/*
 * Inicialización general de la interfaz.
 */
document.addEventListener("DOMContentLoaded", () => {
    ui.setupPasswordToggles();
    ui.initTheme();
    ui.initCookieNotice();
});
