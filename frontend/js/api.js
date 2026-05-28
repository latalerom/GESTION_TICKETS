const api = {
    async request(path, options = {}) {
        const response = await fetch(`/api${path}`, {
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json",
                ...(options.headers || {}),
            },
            ...options,
        });

        const contentType = response.headers.get("content-type") || "";
        const payload = contentType.includes("application/json")
            ? await response.json()
            : null;

        if (!response.ok) {
            const message = payload?.error || "Ocurrio un error inesperado";
            throw new Error(message);
        }

        return payload;
    },

    login(email, password) {
        return this.request("/login", {
            method: "POST",
            body: JSON.stringify({ email, password }),
        });
    },

    session() {
        return this.request("/session");
    },

    logout() {
        return this.request("/logout", { method: "POST" });
    },

    createInvitation(email, rol) {
        return this.request("/invitations", {
            method: "POST",
            body: JSON.stringify({ email, rol }),
        });
    },

    getInvitation(token) {
        return this.request(`/invitations/${token}`);
    },

    register(token, nombre, password) {
        return this.request("/register", {
            method: "POST",
            body: JSON.stringify({ token, nombre, password }),
        });
    },

    listTickets() {
        return this.request("/tickets");
    },

    createTicket(ticket) {
        return this.request("/tickets", {
            method: "POST",
            body: JSON.stringify(ticket),
        });
    },

    updateTicket(id, ticket) {
        return this.request(`/tickets/${id}`, {
            method: "PUT",
            body: JSON.stringify(ticket),
        });
    },

    deleteTicket(id) {
        return this.request(`/tickets/${id}`, { method: "DELETE" });
    },
};
