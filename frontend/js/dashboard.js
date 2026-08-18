const userInfo = document.querySelector("#user-info");
const appBody = document.querySelector(".app-body");
const sidebarToggle = document.querySelector("#sidebar-toggle");
const sessionPhotoPreview = document.querySelector("#session-photo-preview");
const sessionAvatar = document.querySelector("#session-avatar");
const sessionName = document.querySelector("#session-name");
const sessionRole = document.querySelector("#session-role");
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
const incidentOtherField = document.querySelector("#incident-other-field");
const incidenteOtro = document.querySelector("#incidente-otro");
const selectedTicketPath = document.querySelector("#selected-ticket-path");
const departmentTree = document.querySelector("#department-tree");
const ticketDetails = document.querySelector("#ticket-details");
const pageTitle = document.querySelector("#page-title");
const formTitle = document.querySelector("#form-title");
const ticketsTitle = document.querySelector("#tickets-title");
const roleSummary = document.querySelector("#role-summary");
const statsRow = document.querySelector("#stats-row");
const ticketsHead = document.querySelector("#tickets-head");
const ticketsBody = document.querySelector("#tickets-body");
const ticketSearch = document.querySelector("#ticket-search");
const reportsSummary = document.querySelector("#reports-summary");
const reportsBody = document.querySelector("#reports-body");
const reportSearch = document.querySelector("#report-search");
const exportExcelButton = document.querySelector("#export-excel-button");
const exportPdfButton = document.querySelector("#export-pdf-button");
const realtimeStatus = document.querySelector("#realtime-status");
const activityList = document.querySelector("#activity-list");
const createCounter = document.querySelector("#create-counter");
const caseTipText = document.querySelector("#case-tip-text");
const inviteForm = document.querySelector("#invite-form");
const inviteLink = document.querySelector("#invite-link");
const usersBody = document.querySelector("#users-body");
const reloadUsersButton = document.querySelector("#reload-users-button");
const submitButton = document.querySelector("#submit-button");
const cancelEditButton = document.querySelector("#cancel-edit-button");
const profileAvatar = document.querySelector("#profile-avatar");
const profilePhotoInput = document.querySelector("#profile-photo");
const profilePhotoPreview = document.querySelector("#profile-photo-preview");
const profileForm = document.querySelector("#profile-form");
const profileNombre = document.querySelector("#profile-nombre");
const profilePhone = document.querySelector("#profile-phone");
const profileCargo = document.querySelector("#profile-cargo");
const profileBio = document.querySelector("#profile-bio");
const profileName = document.querySelector("#profile-name");
const profileEmail = document.querySelector("#profile-email");
const profileRole = document.querySelector("#profile-role");

let currentUser = null;
let ticketEvents = null;
let activityItems = [];
let ticketsCache = [];
let usersCache = [];

function setSidebarCollapsed(collapsed) {
    appBody?.classList.toggle("sidebar-collapsed", collapsed);

    if (sidebarToggle) {
        sidebarToggle.setAttribute("aria-expanded", String(!collapsed));
        sidebarToggle.setAttribute("aria-label", collapsed ? "Expandir menu" : "Contraer menu");
        sidebarToggle.querySelector("span").textContent = collapsed ? ">" : "<";
    }
}

function showMessage(text, type = "info") {
    ui.toast(text, type);
}

function showInviteMessage(text, type = "info") {
    ui.toast(text, type);
}

function clearMessage() {
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

function clippedText(value, fallback = "-") {
    const text = String(value || fallback);
    return `<span class="clip-text" title="${escapeHtml(text)}">${escapeHtml(text)}</span>`;
}

function priorityBadge(prioridad) {
    const labels = {
        baja: "Baja",
        media: "Media",
        alta: "Alta",
        critica: "Critica",
    };

    return `<span class="badge priority-${prioridad || "media"}">${labels[prioridad] || prioridad || "Media"}</span>`;
}

function isTicketResolved(ticket) {
    return ticket.estado === "resuelto";
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
}

function setCreateStep(hasSelection) {
    document.querySelectorAll(".create-step").forEach((step) => {
        const isDetailsStep = step.dataset.step === "details";
        step.classList.toggle("active", hasSelection ? isDetailsStep : !isDetailsStep);
        step.classList.toggle("complete", hasSelection && !isDetailsStep);
    });

    if (createCounter) {
        createCounter.textContent = hasSelection ? "2/2" : "1/2";
    }
}

function setTicketPath(departmentValue, areaValue, typeValue) {
    departamento.value = departmentValue;
    area.value = areaValue;
    tipoTicket.value = typeValue;

    if (selectedTicketPath) {
        selectedTicketPath.textContent = `${departmentValue} / ${areaValue} / ${typeValue}`;
        selectedTicketPath.classList.add("selected-path-ready");
    }

    if (caseTipText) {
        caseTipText.textContent = `${departmentValue} - ${areaValue} - ${typeValue}`;
    }

    setCreateStep(true);
    revealTicketDetails();
}

function revealTicketDetails() {
    if (!ticketDetails) {
        return;
    }

    ticketDetails.classList.remove("hidden");
    ticketDetails.classList.add("revealed");
}

function hideTicketDetails() {
    if (!ticketDetails) {
        return;
    }

    ticketDetails.classList.add("hidden");
    ticketDetails.classList.remove("revealed");

    if (selectedTicketPath) {
        selectedTicketPath.classList.remove("selected-path-ready");
    }

    if (caseTipText) {
        caseTipText.textContent = "Elige una categoria para activar el formulario.";
    }

    setCreateStep(false);
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
            <th>Acciones</th>
        </tr>
    `;
}

function ticketActions(ticket) {
    if (isTicketResolved(ticket)) {
        return `
            <div class="row-actions">
                <span class="locked-note">Cerrado</span>
            </div>
        `;
    }

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

function renderTickets(tickets, emptyMessage = "No hay tickets registrados.") {
    renderTableHead();
    renderStats(tickets);

    if (tickets.length === 0) {
        const colspan = currentUser?.rol === "admin" ? 7 : 6;
        ticketsBody.innerHTML = `<tr><td colspan="${colspan}">${emptyMessage}</td></tr>`;
        return;
    }

    ticketsBody.innerHTML = tickets.map((ticket) => `
        <tr>
            <td><strong>#${ticket.id}</strong></td>
            <td>${escapeHtml(ticket.tipo_ticket || "General")}</td>
            <td>${escapeHtml(ticket.departamento || "-")}<br><span class="muted">${escapeHtml(ticket.area || "-")}</span></td>
            ${currentUser?.rol === "admin" ? `<td>${escapeHtml(ticket.reportado_por || ticket.usuario || "Sin usuario")}</td>` : ""}
            <td>${priorityBadge(ticket.prioridad)}</td>
            <td>${stateBadge(ticket.estado)}</td>
            <td>${ticketActions(ticket)}</td>
        </tr>
    `).join("");
}

function filteredTickets() {
    const term = (ticketSearch?.value || "").trim().toLowerCase();

    if (!term) {
        return ticketsCache;
    }

    return ticketsCache.filter((ticket) => matchesTicketSearch(ticket, term));
}

function renderFilteredTickets() {
    const hasSearch = Boolean((ticketSearch?.value || "").trim());
    renderTickets(
        filteredTickets(),
        hasSearch ? "No se encontraron tickets con ese criterio." : "No hay tickets registrados.",
    );
}

function matchesTicketSearch(ticket, term) {
    const searchable = [
        `#${ticket.id}`,
        String(ticket.id),
        ticket.area,
        ticket.reportado_por,
        ticket.usuario,
    ].join(" ").toLowerCase();

    return searchable.includes(term);
}

function filteredReports() {
    const term = (reportSearch?.value || "").trim().toLowerCase();

    if (!term) {
        return ticketsCache;
    }

    return ticketsCache.filter((ticket) => matchesTicketSearch(ticket, term));
}

function renderFilteredReports() {
    const hasSearch = Boolean((reportSearch?.value || "").trim());
    renderReports(
        filteredReports(),
        hasSearch ? "No se encontraron reportes con ese criterio." : "No hay reportes disponibles.",
    );
}

function renderReports(tickets, emptyMessage = "No hay reportes disponibles.") {
    if (!reportsBody) {
        return;
    }

    if (reportsSummary) {
        const counts = statusCounts(tickets);
        const critical = tickets.filter((ticket) => ticket.prioridad === "critica").length;
        reportsSummary.innerHTML = `
            <span><strong>${tickets.length}</strong> casos</span>
            <span><strong>${counts.pendiente}</strong> pendientes</span>
            <span><strong>${counts.proceso}</strong> en proceso</span>
            <span><strong>${counts.resuelto}</strong> resueltos</span>
            <span><strong>${critical}</strong> criticos</span>
        `;
    }

    if (tickets.length === 0) {
        reportsBody.innerHTML = `<tr><td colspan="7">${emptyMessage}</td></tr>`;
        return;
    }

    reportsBody.innerHTML = tickets.map((ticket) => {
        const locked = isTicketResolved(ticket);
        const lockedText = locked ? `<small class="locked-note">Bloqueado por cierre</small>` : "";
        const priorityControl = locked
            ? priorityBadge(ticket.prioridad)
            : `
                ${priorityBadge(ticket.prioridad)}
                <select data-report-action="priority" data-id="${ticket.id}">
                    ${["baja", "media", "alta", "critica"].map((priority) => `
                        <option value="${priority}" ${ticket.prioridad === priority ? "selected" : ""}>${priority}</option>
                    `).join("")}
                </select>
            `;
        const stateControl = locked
            ? stateBadge(ticket.estado)
            : `
                ${stateBadge(ticket.estado)}
                <select data-report-action="state" data-id="${ticket.id}">
                    ${["pendiente", "proceso", "resuelto"].map((state) => `
                        <option value="${state}" ${ticket.estado === state ? "selected" : ""}>${state}</option>
                    `).join("")}
                </select>
            `;

        return `
            <tr class="report-row status-${ticket.estado || "pendiente"} priority-${ticket.prioridad || "media"} ${locked ? "is-locked" : ""}">
                <td>
                    <strong>#${ticket.id}</strong>
                    ${lockedText}
                </td>
                <td>
                    ${clippedText(ticket.tipo_ticket || "General")}
                </td>
                <td>${clippedText(ticket.area || "-")}</td>
                <td>${clippedText(ticket.observacion || ticket.descripcion || "-")}</td>
                <td>${clippedText(ticket.reportado_por || ticket.usuario || "-")}</td>
                <td>
                    <div class="report-control">
                        ${priorityControl}
                    </div>
                </td>
                <td>
                    <div class="report-control">
                        ${stateControl}
                    </div>
                </td>
            </tr>
        `;
    }).join("");
}

function roleBadge(role) {
    const label = role === "admin" ? "Administrador" : "Cliente";
    const className = role === "admin" ? "priority-alta" : "priority-baja";
    return `<span class="badge ${className}">${label}</span>`;
}

function activeBadge(active) {
    return `<span class="badge ${active ? "resuelto" : "pendiente"}">${active ? "Activo" : "Inactivo"}</span>`;
}

function renderUsers(users) {
    if (!usersBody) {
        return;
    }

    if (users.length === 0) {
        usersBody.innerHTML = `<tr><td colspan="5">No hay usuarios registrados.</td></tr>`;
        return;
    }

    usersBody.innerHTML = users.map((user) => {
        const displayName = user.nombre || "Sin nombre";
        const isCurrentUser = currentUser?.id === user.id;
        const avatar = user.foto_perfil
            ? `<img class="mini-photo" src="${escapeHtml(user.foto_perfil)}" alt="Foto de ${escapeHtml(displayName)}">`
            : `<span class="mini-avatar">${escapeHtml(displayName.charAt(0).toUpperCase())}</span>`;

        return `
            <tr>
                <td>
                    <div class="user-cell">
                        ${avatar}
                        <div>
                            <strong>${escapeHtml(displayName)}</strong>
                            <span class="muted">${escapeHtml(user.email)}</span>
                        </div>
                    </div>
                </td>
                <td>${roleBadge(user.rol)}</td>
                <td>${activeBadge(user.activo)}</td>
                <td>
                    ${escapeHtml(user.telefono || "-")}<br>
                    <span class="muted">${escapeHtml(user.cargo || "Sin cargo")}</span>
                </td>
                <td>
                    <button class="button secondary" type="button" data-user-action="reset-password" data-id="${user.id}" ${!user.activo ? "disabled" : ""}>
                        Restablecer
                    </button>
                    ${isCurrentUser ? `<span class="muted user-note">Tu cuenta</span>` : ""}
                </td>
            </tr>
        `;
    }).join("");
}

async function loadUsers() {
    if (!usersBody || currentUser?.rol !== "admin") {
        return;
    }

    usersBody.innerHTML = `<tr><td colspan="5">Cargando usuarios...</td></tr>`;

    try {
        const result = await api.listUsers();
        usersCache = result.users || [];
        renderUsers(usersCache);
    } catch (error) {
        usersBody.innerHTML = `<tr><td colspan="5">No se pudieron cargar los usuarios.</td></tr>`;
        showMessage(error.message, "error");
    }
}

function reportRows() {
    return filteredReports().map((ticket) => ({
        caso: `#${ticket.id}`,
        titulo: ticket.titulo || "",
        departamento: ticket.departamento || "",
        area: ticket.area || "",
        tipo: ticket.tipo_ticket || "General",
        observacion: ticket.observacion || ticket.descripcion || "",
        reportadoPor: ticket.reportado_por || ticket.usuario || "",
        prioridad: ticket.prioridad || "media",
        estado: ticket.estado || "pendiente",
        fecha: formatDate(ticket.creado_en),
    }));
}

function reportFileName(extension) {
    const date = new Date().toISOString().slice(0, 10);
    return `reportes-casos-${date}.${extension}`;
}

function downloadBlob(content, type, filename) {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
}

function excelText(value) {
    const text = String(value ?? "");
    return /^[=+\-@]/.test(text) ? `'${text}` : text;
}

function exportReportsExcel() {
    const rows = reportRows();

    if (rows.length === 0) {
        showMessage("No hay reportes para exportar.", "error");
        return;
    }

    const headers = ["Caso", "Titulo", "Departamento", "Area", "Tipo", "Observacion", "Quien lo realizo", "Prioridad", "Estado", "Fecha"];
    const body = rows.map((row) => `
        <tr>
            <td>${escapeHtml(row.caso)}</td>
            <td>${escapeHtml(excelText(row.titulo))}</td>
            <td>${escapeHtml(excelText(row.departamento))}</td>
            <td>${escapeHtml(excelText(row.area))}</td>
            <td>${escapeHtml(excelText(row.tipo))}</td>
            <td>${escapeHtml(excelText(row.observacion))}</td>
            <td>${escapeHtml(excelText(row.reportadoPor))}</td>
            <td>${escapeHtml(excelText(row.prioridad))}</td>
            <td>${escapeHtml(excelText(row.estado))}</td>
            <td>${escapeHtml(excelText(row.fecha))}</td>
        </tr>
    `).join("");
    const content = `
        <html>
            <head><meta charset="UTF-8"></head>
            <body>
                <table>
                    <thead><tr>${headers.map((header) => `<th>${header}</th>`).join("")}</tr></thead>
                    <tbody>${body}</tbody>
                </table>
            </body>
        </html>
    `;

    downloadBlob(content, "application/vnd.ms-excel;charset=utf-8", reportFileName("xls"));
    showMessage("Reporte Excel exportado correctamente.", "success");
}

function exportReportsPdf() {
    const rows = reportRows();

    if (rows.length === 0) {
        showMessage("No hay reportes para exportar.", "error");
        return;
    }

    const printWindow = window.open("", "_blank");

    if (!printWindow) {
        showMessage("Permite ventanas emergentes para generar el PDF.", "error");
        return;
    }

    const rowsHtml = rows.map((row) => `
        <tr>
            <td>${escapeHtml(row.caso)}</td>
            <td>${escapeHtml(row.tipo)}</td>
            <td>${escapeHtml(row.area)}</td>
            <td>${escapeHtml(row.observacion)}</td>
            <td>${escapeHtml(row.reportadoPor)}</td>
            <td>${escapeHtml(row.prioridad)}</td>
            <td>${escapeHtml(row.estado)}</td>
            <td>${escapeHtml(row.fecha)}</td>
        </tr>
    `).join("");

    printWindow.document.write(`
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Reportes generales</title>
            <style>
                body { color: #222831; font-family: Arial, Helvetica, sans-serif; margin: 28px; }
                h1 { margin: 0 0 6px; font-size: 24px; }
                p { color: #6b7280; margin: 0 0 18px; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #d9dee5; padding: 8px; text-align: left; vertical-align: top; }
                th { background: #f4f6f8; color: #374151; font-size: 12px; text-transform: uppercase; }
                td { font-size: 12px; }
                @media print { body { margin: 16mm; } }
            </style>
        </head>
        <body>
            <h1>Reportes generales</h1>
            <p>Generado el ${new Date().toLocaleString("es-CO")}</p>
            <table>
                <thead>
                    <tr>
                        <th>Caso</th>
                        <th>Tipo</th>
                        <th>Area</th>
                        <th>Observacion</th>
                        <th>Quien lo realizo</th>
                        <th>Prioridad</th>
                        <th>Estado</th>
                        <th>Fecha</th>
                    </tr>
                </thead>
                <tbody>${rowsHtml}</tbody>
            </table>
            <script>
                window.addEventListener("load", () => {
                    window.print();
                });
            <\/script>
        </body>
        </html>
    `);
    printWindow.document.close();
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
    const initial = displayName.charAt(0).toUpperCase();

    pageTitle.textContent = isAdmin ? "Panel de Administracion" : "Mis Tickets";
    formTitle.textContent = isAdmin ? "Registrar caso" : "Crear solicitud";
    ticketsTitle.textContent = isAdmin ? "Bandeja general" : "Mis solicitudes";
    roleSummary.textContent = isAdmin
        ? "Vista centralizada de casos por area, prioridad y estado."
        : "Seguimiento de tus solicitudes registradas en mesa de ayuda.";
    userInfo.textContent = `${displayName} - ${roleLabel}`;
    sessionName.textContent = displayName;
    sessionRole.textContent = roleLabel;
    sessionAvatar.textContent = initial;
    sidebarRole.textContent = roleLabel;

    document.querySelectorAll(".admin-only").forEach((element) => {
        element.classList.toggle("hidden", !isAdmin);
    });

    profileAvatar.textContent = initial;
    profileName.textContent = displayName;
    profileEmail.textContent = user.email;
    profileRole.textContent = roleLabel;
    reportadoPor.value = displayName;
    profileNombre.value = user.nombre || "";
    profilePhone.value = user.telefono || "";
    profileCargo.value = user.cargo || "";
    profileBio.value = user.bio || "";
    renderUserPhoto(user.foto_perfil);
}

function renderUserPhoto(photo) {
    if (photo) {
        profilePhotoPreview.src = photo;
        sessionPhotoPreview.src = photo;
        profilePhotoPreview.classList.remove("hidden");
        sessionPhotoPreview.classList.remove("hidden");
        profileAvatar.classList.add("hidden");
        sessionAvatar.classList.add("hidden");
        return;
    }

    profilePhotoPreview.removeAttribute("src");
    sessionPhotoPreview.removeAttribute("src");
    profilePhotoPreview.classList.add("hidden");
    sessionPhotoPreview.classList.add("hidden");
    profileAvatar.classList.remove("hidden");
    sessionAvatar.classList.remove("hidden");
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
        await loadUsers();
    } catch (error) {
        window.location.href = "login.html";
    }
}

async function loadTickets() {
    const colspan = currentUser?.rol === "admin" ? 7 : 6;
    ticketsBody.innerHTML = `<tr><td colspan="${colspan}">Cargando tickets...</td></tr>`;

    try {
        ticketsCache = await api.listTickets();
        renderFilteredTickets();
        renderFilteredReports();
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

function updateIncidentOtherField() {
    const showOther = tipoTicket.value === "Otro";
    incidentOtherField.classList.toggle("hidden", !showOther);
    incidenteOtro.required = showOther;

    if (!showOther) {
        incidenteOtro.value = "";
    }
}

function resetForm() {
    ticketId.value = "";
    ticketForm.reset();
    reportadoPor.value = currentUser?.nombre || currentUser?.email || "";
    departamento.value = "Oficina";
    area.value = "";
    tipoTicket.value = "";
    incidenteOtro.value = "";
    titulo.value = "";
    observacion.value = "";
    updateIncidentOtherField();

    if (selectedTicketPath) {
        selectedTicketPath.textContent = "Sin seleccion";
    }

    hideTicketDetails();
    submitButton.textContent = "Crear ticket";
    cancelEditButton.classList.add("hidden");
}

ticketForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessage();

    const selectedArea = area.value.trim();
    const selectedIncident = tipoTicket.value.trim();
    const otherIncident = incidenteOtro.value.trim();
    const incidentDetail = selectedIncident === "Otro" ? otherIncident : "";
    const payload = {
        titulo: titulo.value.trim() || `Caso de ${selectedArea}`,
        descripcion: descripcion.value.trim(),
        observacion: incidentDetail || observacion.value.trim(),
        reportado_por: reportadoPor.value.trim(),
        departamento: departamento.value || "Oficina",
        area: selectedArea,
        tipo_ticket: selectedIncident,
    };

    if (!payload.reportado_por || !payload.area || !payload.tipo_ticket || !payload.descripcion) {
        showMessage("Completa quien reporta, area, tipo de incidente y descripcion antes de continuar.", "error");
        return;
    }

    if (payload.tipo_ticket === "Otro" && !otherIncident) {
        showMessage("Especifica cual es el incidente.", "error");
        return;
    }

    try {
        if (ticketId.value) {
            await api.updateTicket(ticketId.value, payload);
            showMessage("Ticket actualizado correctamente", "success");
        } else {
            await api.createTicket(payload);
            showMessage("Ticket creado correctamente", "success");
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
exportExcelButton?.addEventListener("click", exportReportsExcel);
exportPdfButton?.addEventListener("click", exportReportsPdf);
reloadUsersButton?.addEventListener("click", loadUsers);
tipoTicket.addEventListener("change", updateIncidentOtherField);
ticketSearch?.addEventListener("input", renderFilteredTickets);
reportSearch?.addEventListener("input", renderFilteredReports);
sidebarToggle?.addEventListener("click", () => {
    const collapsed = !appBody.classList.contains("sidebar-collapsed");
    setSidebarCollapsed(collapsed);
    localStorage.setItem("sidebarCollapsed", collapsed ? "true" : "false");
});

inviteForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(inviteForm);

    try {
        const result = await api.createInvitation(formData.get("email"), formData.get("rol"));
        inviteForm.reset();
        await loadUsers();
        const emailStatus = result.email_sent
            ? "Invitacion enviada correctamente."
            : `Invitacion creada, pero el correo no se pudo enviar${result.email_error ? `: ${result.email_error}` : ""}. Comparte el enlace manualmente.`;

        showInviteMessage(
            emailStatus,
            result.email_sent ? "success" : "error",
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

departmentTree?.addEventListener("click", (event) => {
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

    if (isTicketResolved(ticket)) {
        showMessage("El ticket ya esta resuelto y no puede modificarse.", "error");
        return;
    }

    if (button.dataset.action === "edit") {
        ticketId.value = ticket.id;
        titulo.value = ticket.titulo || "";
        descripcion.value = ticket.descripcion || "";
        observacion.value = ticket.observacion || "";
        reportadoPor.value = ticket.reportado_por || ticket.usuario || "";
        departamento.value = ticket.departamento || "Oficina";
        area.value = ticket.area || "";
        tipoTicket.value = ticket.tipo_ticket || "";
        incidenteOtro.value = ticket.tipo_ticket === "Otro" ? ticket.observacion || "" : "";
        updateIncidentOtherField();
        submitButton.textContent = "Guardar cambios";
        cancelEditButton.classList.remove("hidden");
        showView("create");
    }

    if (button.dataset.action === "delete") {
        const confirmed = await ui.confirm({
            title: "Eliminar ticket",
            message: "Seguro que quieres eliminar este ticket? Esta accion no se puede deshacer.",
            confirmText: "Eliminar",
            cancelText: "Conservar",
            danger: true,
        });

        if (!confirmed) {
            return;
        }

        await api.deleteTicket(id);
        showMessage("Ticket eliminado correctamente", "success");
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

    if (payload.estado === "resuelto") {
        const solution = await ui.textareaPrompt({
            title: "Cerrar ticket",
            message: "Antes de marcar este caso como resuelto, registra como termino y que solucion se dio.",
            label: "Solucion del caso",
            placeholder: "Ejemplo: Se valido la solicitud, se corrigio la novedad y se notifico al area responsable.",
            confirmText: "Cerrar ticket",
            cancelText: "Volver",
        });

        if (!solution) {
            showMessage("Para cerrar el caso debes registrar la solucion.", "error");
            renderFilteredReports();
            return;
        }

        payload.solucion_cierre = solution;
    }

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

usersBody?.addEventListener("click", async (event) => {
    const button = event.target.closest("button[data-user-action='reset-password']");

    if (!button) {
        return;
    }

    const user = usersCache.find((item) => item.id === Number(button.dataset.id));

    if (!user) {
        return;
    }

    const confirmed = await ui.confirm({
        title: "Restablecer contrasena",
        message: `Se asignara una contrasena temporal a ${user.email} y se enviara un correo con el dato.`,
        confirmText: "Restablecer",
        cancelText: "Cancelar",
    });

    if (!confirmed) {
        return;
    }

    try {
        button.disabled = true;
        const result = await api.resetUserPassword(user.id);
        await loadUsers();
        showMessage(
            result.email_sent
                ? "Contrasena temporal enviada por correo."
                : `Contrasena temporal: ${result.temporary_password}. Configura SMTP para enviarla por correo.`,
            result.email_sent ? "success" : "warning",
        );
    } catch (error) {
        button.disabled = false;
        showMessage(error.message, "error");
    }
});

profilePhotoInput.addEventListener("change", () => {
    const file = profilePhotoInput.files[0];

    if (!file) {
        return;
    }

    if (!file.type.startsWith("image/")) {
        showMessage("Selecciona una imagen valida para tu perfil.", "error");
        profilePhotoInput.value = "";
        return;
    }

    if (file.size > 900 * 1024) {
        showMessage("La imagen debe pesar menos de 900 KB.", "error");
        profilePhotoInput.value = "";
        return;
    }

    const reader = new FileReader();
    reader.addEventListener("load", () => renderUserPhoto(reader.result));
    reader.readAsDataURL(file);
});

profileForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const payload = {
        nombre: profileNombre.value.trim(),
        telefono: profilePhone.value.trim(),
        cargo: profileCargo.value.trim(),
        bio: profileBio.value.trim(),
        foto_perfil: profilePhotoPreview.getAttribute("src") || null,
    };

    try {
        const result = await api.updateProfile(payload);
        currentUser = result.user;
        applyRoleView(currentUser);
        showMessage("Perfil actualizado correctamente", "success");
    } catch (error) {
        showMessage(error.message, "error");
    }
});

async function initDashboard() {
    setSidebarCollapsed(localStorage.getItem("sidebarCollapsed") === "true");
    renderDepartmentTree();
    await loadSession();
    await loadTickets();
    startRealtimeUpdates();
}

initDashboard();
