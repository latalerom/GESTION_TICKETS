const userInfo = document.querySelector("#user-info");
const logoutButton = document.querySelector("#logout-button");
const reloadButton = document.querySelector("#reload-button");
const ticketForm = document.querySelector("#ticket-form");
const ticketId = document.querySelector("#ticket-id");
const titulo = document.querySelector("#titulo");
const descripcion = document.querySelector("#descripcion");
const pageTitle = document.querySelector("#page-title");
const formTitle = document.querySelector("#form-title");
const ticketsTitle = document.querySelector("#tickets-title");
const roleSummary = document.querySelector("#role-summary");
const statsRow = document.querySelector("#stats-row");
const ticketsHead = document.querySelector("#tickets-head");
const ticketsBody = document.querySelector("#tickets-body");
const ticketMessage = document.querySelector("#ticket-message");
const realtimeStatus = document.querySelector("#realtime-status");
const activityList = document.querySelector("#activity-list");
const invitePanel = document.querySelector("#invite-panel");
const inviteForm = document.querySelector("#invite-form");
const inviteMessage = document.querySelector("#invite-message");
const inviteLink = document.querySelector("#invite-link");
const submitButton = document.querySelector("#submit-button");
const cancelEditButton = document.querySelector("#cancel-edit-button");

let currentUser = null;
let ticketEvents = null;
let activityItems = [];

function showMessage(text, type = "success") {
    ticketMessage.textContent = text;
    ticketMessage.className = `message ${type}`;
}

function showInviteMessage(text, type = "success") {
    inviteMessage.textContent = text;
    inviteMessage.className = `message ${type}`;
}

function clearMessage() {
    ticketMessage.textContent = "";
    ticketMessage.className = "message hidden";
}

function setRealtimeStatus(connected) {
    realtimeStatus.textContent = connected
        ? "Tiempo real conectado"
        : "Tiempo real desconectado";
    realtimeStatus.className = `realtime-status ${connected ? "online" : "offline"}`;
}

function addActivity(payload) {
    const now = new Date();
    const time = now.toLocaleTimeString("es-CO", {
        hour: "2-digit",
        minute: "2-digit",
    });

    activityItems.unshift({
        message: payload.message || "Accion registrada",
        time,
    });
    activityItems = activityItems.slice(0, 8);

    activityList.innerHTML = activityItems.map((item) => `
        <li>
            <span>${escapeHtml(item.message)}</span>
            <small>${item.time}</small>
        </li>
    `).join("");
}

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function stateBadge(estado) {
    const labels = {
        pendiente: "Pendiente",
        proceso: "En Proceso",
        resuelto: "Resuelto",
    };

    return `<span class="badge ${estado}">${labels[estado] || estado}</span>`;
}

function statusCounts(tickets) {
    return tickets.reduce((counts, ticket) => {
        counts[ticket.estado] = (counts[ticket.estado] || 0) + 1;
        return counts;
    }, { pendiente: 0, proceso: 0, resuelto: 0 });
}

function renderStats(tickets) {
    const counts = statusCounts(tickets);

    statsRow.innerHTML = `
        <div class="stat">
            <strong>${tickets.length}</strong>
            <span>Total</span>
        </div>
        <div class="stat">
            <strong>${counts.pendiente}</strong>
            <span>Pendientes</span>
        </div>
        <div class="stat">
            <strong>${counts.proceso}</strong>
            <span>En proceso</span>
        </div>
        <div class="stat">
            <strong>${counts.resuelto}</strong>
            <span>Resueltos</span>
        </div>
    `;
}

function renderTableHead() {
    const userColumn = currentUser?.rol === "admin" ? "<th>Usuario</th>" : "";

    ticketsHead.innerHTML = `
        <tr>
            <th>ID</th>
            <th>Titulo</th>
            <th>Descripcion</th>
            ${userColumn}
            <th>Estado</th>
            <th>Acciones</th>
        </tr>
    `;
}

function ticketActions(ticket) {
    const stateControl = currentUser?.rol === "admin"
        ? `<select data-action="state" data-id="${ticket.id}">
            <option value="pendiente" ${ticket.estado === "pendiente" ? "selected" : ""}>Pendiente</option>
            <option value="proceso" ${ticket.estado === "proceso" ? "selected" : ""}>Proceso</option>
            <option value="resuelto" ${ticket.estado === "resuelto" ? "selected" : ""}>Resuelto</option>
        </select>`
        : "";

    return `
        <div class="row-actions">
            <button class="button secondary" data-action="edit" data-id="${ticket.id}">Editar</button>
            <button class="button danger" data-action="delete" data-id="${ticket.id}">Eliminar</button>
            ${stateControl}
        </div>
    `;
}

function renderTickets(tickets) {
    renderTableHead();
    renderStats(tickets);

    if (tickets.length === 0) {
        const colspan = currentUser?.rol === "admin" ? 6 : 5;
        ticketsBody.innerHTML = `<tr><td colspan="${colspan}">No hay tickets registrados.</td></tr>`;
        return;
    }

    ticketsBody.innerHTML = tickets.map((ticket) => `
        <tr>
            <td>${ticket.id}</td>
            <td>${escapeHtml(ticket.titulo)}</td>
            <td>${escapeHtml(ticket.descripcion)}</td>
            ${currentUser?.rol === "admin" ? `<td>${escapeHtml(ticket.usuario || "Sin usuario")}</td>` : ""}
            <td>${stateBadge(ticket.estado)}</td>
            <td>${ticketActions(ticket)}</td>
        </tr>
    `).join("");
}

function applyRoleView(user) {
    const isAdmin = user.rol === "admin";
    const roleLabel = isAdmin ? "Administrador" : "Cliente";
    const displayName = user.nombre || user.email || roleLabel;

    pageTitle.textContent = isAdmin ? "Panel de Administracion" : "Mis Tickets";
    formTitle.textContent = isAdmin ? "Registrar ticket" : "Crear solicitud";
    ticketsTitle.textContent = isAdmin ? "Todos los tickets" : "Mis solicitudes";
    roleSummary.textContent = isAdmin
        ? "Puedes consultar todos los tickets, cambiar estados y gestionar registros."
        : "Puedes crear y consultar tus solicitudes. El estado lo actualiza el equipo de soporte.";
    userInfo.textContent = `${displayName} - ${roleLabel}`;
    invitePanel.classList.toggle("hidden", !isAdmin);
}

async function loadSession() {
    try {
        const session = await api.session();
        currentUser = session.user;
        applyRoleView(currentUser);
    } catch (error) {
        window.location.href = "login.html";
    }
}

async function loadTickets() {
    const colspan = currentUser?.rol === "admin" ? 6 : 5;
    ticketsBody.innerHTML = `<tr><td colspan="${colspan}">Cargando tickets...</td></tr>`;

    try {
        const tickets = await api.listTickets();
        renderTickets(tickets);
    } catch (error) {
        showMessage(error.message, "error");
    }
}

function startRealtimeUpdates() {
    if (ticketEvents) {
        ticketEvents.close();
    }

    ticketEvents = new EventSource("/api/tickets/stream");

    ticketEvents.addEventListener("connected", () => {
        setRealtimeStatus(true);
    });

    ["ticket_created", "ticket_updated", "ticket_deleted"].forEach((eventName) => {
        ticketEvents.addEventListener(eventName, async () => {
            await loadTickets();
        });
    });

    ticketEvents.addEventListener("activity", (event) => {
        addActivity(JSON.parse(event.data));
    });

    ticketEvents.onerror = () => {
        setRealtimeStatus(false);
    };
}

function resetForm() {
    ticketId.value = "";
    ticketForm.reset();
    submitButton.textContent = "Crear ticket";
    cancelEditButton.classList.add("hidden");
}

ticketForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessage();

    const payload = {
        titulo: titulo.value.trim(),
        descripcion: descripcion.value.trim(),
    };

    try {
        if (ticketId.value) {
            await api.updateTicket(ticketId.value, payload);
            showMessage("Ticket actualizado correctamente");
        } else {
            await api.createTicket(payload);
            showMessage("Ticket creado correctamente");
        }

        resetForm();
        await loadTickets();
    } catch (error) {
        showMessage(error.message, "error");
    }
});

cancelEditButton.addEventListener("click", () => {
    resetForm();
    clearMessage();
});

reloadButton.addEventListener("click", loadTickets);

inviteForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const formData = new FormData(inviteForm);

    try {
        const result = await api.createInvitation(
            formData.get("email"),
            formData.get("rol"),
        );

        inviteForm.reset();
        showInviteMessage(
            result.email_sent
                ? "Invitacion enviada correctamente."
                : "Invitacion creada. Configura SMTP para enviar correos reales.",
        );
        inviteLink.textContent = `Enlace: ${result.registration_link}`;
    } catch (error) {
        showInviteMessage(error.message, "error");
        inviteLink.textContent = "";
    }
});

logoutButton.addEventListener("click", async () => {
    if (ticketEvents) {
        ticketEvents.close();
    }

    await api.logout();
    window.location.href = "login.html";
});

ticketsBody.addEventListener("click", async (event) => {
    const button = event.target.closest("button");

    if (!button) {
        return;
    }

    const id = button.dataset.id;

    if (button.dataset.action === "edit") {
        const row = button.closest("tr");
        const cells = row.querySelectorAll("td");

        ticketId.value = id;
        titulo.value = cells[1].textContent;
        descripcion.value = cells[2].textContent;
        submitButton.textContent = "Guardar cambios";
        cancelEditButton.classList.remove("hidden");
        window.scrollTo({ top: 0, behavior: "smooth" });
    }

    if (button.dataset.action === "delete") {
        const confirmed = confirm("Seguro que quieres eliminar este ticket?");

        if (!confirmed) {
            return;
        }

        await api.deleteTicket(id);
        showMessage("Ticket eliminado correctamente");
        await loadTickets();
    }
});

ticketsBody.addEventListener("change", async (event) => {
    const select = event.target.closest("select[data-action='state']");

    if (!select) {
        return;
    }

    try {
        await api.updateTicket(select.dataset.id, { estado: select.value });
        showMessage("Estado actualizado correctamente");
        await loadTickets();
    } catch (error) {
        showMessage(error.message, "error");
    }
});

async function initDashboard() {
    await loadSession();
    await loadTickets();
    startRealtimeUpdates();
}

initDashboard();
