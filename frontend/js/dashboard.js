const DEPARTMENT_TREE = [
    {
        name: "Tecnologia",
        areas: [
            { name: "Soporte tecnico", types: ["Equipo de computo", "Acceso a sistemas", "Correo institucional"] },
            { name: "Infraestructura", types: ["Red", "Servidor", "Telefonia"] },
        ],
    },
    {
        name: "Administracion",
        areas: [
            { name: "Talento humano", types: ["Solicitud de usuario", "Novedad de personal"] },
            { name: "Financiera", types: ["Facturacion", "Pagos", "Proveedor"] },
        ],
    },
    {
        name: "Academica",
        areas: [
            { name: "Registro", types: ["Matricula", "Notas", "Certificado"] },
            { name: "Bienestar", types: ["Solicitud estudiantil", "Acompanamiento"] },
        ],
    },
];

const userInfo = document.querySelector("#user-info");
const sidebarRole = document.querySelector("#sidebar-role");
const logoutButton = document.querySelector("#logout-button");
const reloadButton = document.querySelector("#reload-button");
const ticketForm = document.querySelector("#ticket-form");
const ticketId = document.querySelector("#ticket-id");
const titulo = document.querySelector("#titulo");
const descripcion = document.querySelector("#descripcion");
const observacion = document.querySelector("#observacion");
const reportadoPor = document.querySelector("#reportado-por");
const departamento = document.querySelector("#departamento");
const area = document.querySelector("#area");
const tipoTicket = document.querySelector("#tipo-ticket");
const selectedTicketPath = document.querySelector("#selected-ticket-path");
const departmentTree = document.querySelector("#department-tree");
const pageTitle = document.querySelector("#page-title");
const formTitle = document.querySelector("#form-title");
const ticketsTitle = document.querySelector("#tickets-title");
const roleSummary = document.querySelector("#role-summary");
const statsRow = document.querySelector("#stats-row");
const ticketsHead = document.querySelector("#tickets-head");
const ticketsBody = document.querySelector("#tickets-body");
const reportsBody = document.querySelector("#reports-body");
const ticketMessage = document.querySelector("#ticket-message");
const realtimeStatus = document.querySelector("#realtime-status");
const activityList = document.querySelector("#activity-list");
const inviteForm = document.querySelector("#invite-form");
const inviteMessage = document.querySelector("#invite-message");
const inviteLink = document.querySelector("#invite-link");
const submitButton = document.querySelector("#submit-button");
const cancelEditButton = document.querySelector("#cancel-edit-button");
const profileAvatar = document.querySelector("#profile-avatar");
const profileName = document.querySelector("#profile-name");
const profileEmail = document.querySelector("#profile-email");
const profileRole = document.querySelector("#profile-role");

let currentUser = null;
let ticketEvents = null;
let activityItems = [];
let ticketsCache = [];

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
    realtimeStatus.textContent = connected ? "Tiempo real conectado" : "Tiempo real desconectado";
    realtimeStatus.className = `realtime-status ${connected ? "online" : "offline"}`;
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
        proceso: "En proceso",
        resuelto: "Resuelto",
    };

    return `<span class="badge ${estado}">${labels[estado] || estado}</span>`;
}

function priorityBadge(prioridad) {
    return `<span class="badge priority-${prioridad || "media"}">${prioridad || "media"}</span>`;
}

function statusCounts(tickets) {
    return tickets.reduce((counts, ticket) => {
        counts[ticket.estado] = (counts[ticket.estado] || 0) + 1;
        return counts;
    }, { pendiente: 0, proceso: 0, resuelto: 0 });
}

function renderStats(tickets) {
    const counts = statusCounts(tickets);
    const highPriority = tickets.filter((ticket) => ["alta", "critica"].includes(ticket.prioridad)).length;

    statsRow.innerHTML = `
        <div class="stat"><strong>${tickets.length}</strong><span>Total casos</span></div>
        <div class="stat"><strong>${counts.pendiente}</strong><span>Pendientes</span></div>
        <div class="stat"><strong>${counts.proceso}</strong><span>En proceso</span></div>
        <div class="stat"><strong>${highPriority}</strong><span>Alta prioridad</span></div>
    `;
}

function renderDepartmentTree() {
    departmentTree.innerHTML = DEPARTMENT_TREE.map((department) => `
        <details class="tree-node">
            <summary>${escapeHtml(department.name)}</summary>
            ${department.areas.map((areaItem) => `
                <details class="tree-node nested">
                    <summary>${escapeHtml(areaItem.name)}</summary>
                    <div class="tree-options">
                        ${areaItem.types.map((type) => `
                            <button type="button" class="tree-option"
                                data-department="${escapeHtml(department.name)}"
                                data-area="${escapeHtml(areaItem.name)}"
                                data-type="${escapeHtml(type)}">
                                ${escapeHtml(type)}
                            </button>
                        `).join("")}
                    </div>
                </details>
            `).join("")}
        </details>
    `).join("");
}

function setTicketPath(departmentValue, areaValue, typeValue) {
    departamento.value = departmentValue;
    area.value = areaValue;
    tipoTicket.value = typeValue;
    selectedTicketPath.textContent = `${departmentValue} / ${areaValue} / ${typeValue}`;
}

function renderTableHead() {
    const userColumn = currentUser?.rol === "admin" ? "<th>Usuario</th>" : "";

    ticketsHead.innerHTML = `
        <tr>
            <th>Caso</th>
            <th>Tipo</th>
            <th>Area</th>
            ${userColumn}
            <th>Prioridad</th>
            <th>Estado</th>
            <th>Fecha</th>
            <th>Acciones</th>
        </tr>
    `;
}

function ticketActions(ticket) {
    return `
        <div class="row-actions">
            <button class="button secondary" data-action="edit" data-id="${ticket.id}">Editar</button>
            <button class="button danger" data-action="delete" data-id="${ticket.id}">Eliminar</button>
        </div>
    `;
}

function formatDate(value) {
    if (!value) {
        return "Sin fecha";
    }

    return new Date(value).toLocaleString("es-CO", {
        dateStyle: "medium",
        timeStyle: "short",
    });
}

function renderTickets(tickets) {
    renderTableHead();
    renderStats(tickets);

    if (tickets.length === 0) {
        const colspan = currentUser?.rol === "admin" ? 8 : 7;
        ticketsBody.innerHTML = `<tr><td colspan="${colspan}">No hay tickets registrados.</td></tr>`;
        renderReports([]);
        return;
    }

    ticketsBody.innerHTML = tickets.map((ticket) => `
        <tr>
            <td>#${ticket.id}<br><strong>${escapeHtml(ticket.titulo)}</strong></td>
            <td>${escapeHtml(ticket.tipo_ticket || "General")}</td>
            <td>${escapeHtml(ticket.departamento || "-")}<br><span class="muted">${escapeHtml(ticket.area || "-")}</span></td>
            ${currentUser?.rol === "admin" ? `<td>${escapeHtml(ticket.reportado_por || ticket.usuario || "Sin usuario")}</td>` : ""}
            <td>${priorityBadge(ticket.prioridad)}</td>
            <td>${stateBadge(ticket.estado)}</td>
            <td>${formatDate(ticket.creado_en)}</td>
            <td>${ticketActions(ticket)}</td>
        </tr>
    `).join("");

    renderReports(tickets);
}

function renderReports(tickets) {
    if (!reportsBody) {
        return;
    }

    if (tickets.length === 0) {
        reportsBody.innerHTML = `<tr><td colspan="6">No hay reportes disponibles.</td></tr>`;
        return;
    }

    reportsBody.innerHTML = tickets.map((ticket) => `
        <tr>
            <td>#${ticket.id}</td>
            <td>${escapeHtml(ticket.tipo_ticket || "General")}</td>
            <td>${escapeHtml(ticket.observacion || ticket.descripcion || "-")}</td>
            <td>${escapeHtml(ticket.reportado_por || ticket.usuario || "-")}</td>
            <td>
                <select data-report-action="priority" data-id="${ticket.id}">
                    ${["baja", "media", "alta", "critica"].map((priority) => `
                        <option value="${priority}" ${ticket.prioridad === priority ? "selected" : ""}>${priority}</option>
                    `).join("")}
                </select>
            </td>
            <td>
                <select data-report-action="state" data-id="${ticket.id}">
                    ${["pendiente", "proceso", "resuelto"].map((state) => `
                        <option value="${state}" ${ticket.estado === state ? "selected" : ""}>${state}</option>
                    `).join("")}
                </select>
            </td>
        </tr>
    `).join("");
}

function addActivity(payload) {
    const time = new Date().toLocaleTimeString("es-CO", { hour: "2-digit", minute: "2-digit" });
    activityItems.unshift({ message: payload.message || "Accion registrada", time });
    activityItems = activityItems.slice(0, 8);

    activityList.innerHTML = activityItems.map((item) => `
        <li><span>${escapeHtml(item.message)}</span><small>${item.time}</small></li>
    `).join("");
}

function applyRoleView(user) {
    const isAdmin = user.rol === "admin";
    const roleLabel = isAdmin ? "Administrador" : "Cliente";
    const displayName = user.nombre || user.email || roleLabel;

    pageTitle.textContent = isAdmin ? "Panel de Administracion" : "Mis Tickets";
    formTitle.textContent = isAdmin ? "Registrar caso" : "Crear solicitud";
    ticketsTitle.textContent = isAdmin ? "Bandeja general" : "Mis solicitudes";
    roleSummary.textContent = isAdmin
        ? "Vista centralizada de casos por area, prioridad y estado."
        : "Seguimiento de tus solicitudes registradas en mesa de ayuda.";
    userInfo.textContent = `${displayName} - ${roleLabel}`;
    sidebarRole.textContent = roleLabel;

    document.querySelectorAll(".admin-only").forEach((element) => {
        element.classList.toggle("hidden", !isAdmin);
    });

    profileAvatar.textContent = displayName.charAt(0).toUpperCase();
    profileName.textContent = displayName;
    profileEmail.textContent = user.email;
    profileRole.textContent = roleLabel;
    reportadoPor.value = displayName;
}

function showView(viewName) {
    document.querySelectorAll(".module-view").forEach((view) => {
        view.classList.toggle("active", view.id === `view-${viewName}`);
    });

    document.querySelectorAll(".nav-item").forEach((item) => {
        item.classList.toggle("active", item.dataset.view === viewName);
    });
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
    const colspan = currentUser?.rol === "admin" ? 8 : 7;
    ticketsBody.innerHTML = `<tr><td colspan="${colspan}">Cargando tickets...</td></tr>`;

    try {
        ticketsCache = await api.listTickets();
        renderTickets(ticketsCache);
    } catch (error) {
        showMessage(error.message, "error");
    }
}

function startRealtimeUpdates() {
    if (ticketEvents) {
        ticketEvents.close();
    }

    ticketEvents = new EventSource("/api/tickets/stream");

    ticketEvents.addEventListener("connected", () => setRealtimeStatus(true));

    ["ticket_created", "ticket_updated", "ticket_deleted"].forEach((eventName) => {
        ticketEvents.addEventListener(eventName, loadTickets);
    });

    ticketEvents.addEventListener("activity", (event) => addActivity(JSON.parse(event.data)));
    ticketEvents.onerror = () => setRealtimeStatus(false);
}

function resetForm() {
    ticketId.value = "";
    ticketForm.reset();
    reportadoPor.value = currentUser?.nombre || currentUser?.email || "";
    departamento.value = "";
    area.value = "";
    tipoTicket.value = "";
    selectedTicketPath.textContent = "Sin seleccion";
    submitButton.textContent = "Crear ticket";
    cancelEditButton.classList.add("hidden");
}

ticketForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessage();

    const payload = {
        titulo: titulo.value.trim(),
        descripcion: descripcion.value.trim(),
        observacion: observacion.value.trim(),
        reportado_por: reportadoPor.value.trim(),
        departamento: departamento.value,
        area: area.value,
        tipo_ticket: tipoTicket.value,
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
        showView("tickets");
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
        const result = await api.createInvitation(formData.get("email"), formData.get("rol"));
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

departmentTree.addEventListener("click", (event) => {
    const option = event.target.closest(".tree-option");

    if (!option) {
        return;
    }

    setTicketPath(option.dataset.department, option.dataset.area, option.dataset.type);
});

ticketsBody.addEventListener("click", async (event) => {
    const button = event.target.closest("button");

    if (!button) {
        return;
    }

    const id = Number(button.dataset.id);
    const ticket = ticketsCache.find((item) => item.id === id);

    if (!ticket) {
        return;
    }

    if (button.dataset.action === "edit") {
        ticketId.value = ticket.id;
        titulo.value = ticket.titulo || "";
        descripcion.value = ticket.descripcion || "";
        observacion.value = ticket.observacion || "";
        reportadoPor.value = ticket.reportado_por || ticket.usuario || "";
        setTicketPath(ticket.departamento || "", ticket.area || "", ticket.tipo_ticket || "");
        submitButton.textContent = "Guardar cambios";
        cancelEditButton.classList.remove("hidden");
        showView("create");
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

reportsBody.addEventListener("change", async (event) => {
    const select = event.target.closest("select[data-report-action]");

    if (!select) {
        return;
    }

    const payload = select.dataset.reportAction === "priority"
        ? { prioridad: select.value }
        : { estado: select.value };

    try {
        await api.updateTicket(select.dataset.id, payload);
        await loadTickets();
    } catch (error) {
        showMessage(error.message, "error");
    }
});

document.querySelectorAll(".nav-item").forEach((button) => {
    button.addEventListener("click", () => showView(button.dataset.view));
});

async function initDashboard() {
    renderDepartmentTree();
    await loadSession();
    await loadTickets();
    startRealtimeUpdates();
}

initDashboard();
