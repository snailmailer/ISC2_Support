const API_URL = "http://localhost:8000/tickets";

// Handle Ticket Submission (index.html)
const ticketForm = document.getElementById('ticketForm');
if (ticketForm) {
    ticketForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(ticketForm);
        const data = Object.fromEntries(formData.entries());

        // Add timestamp if needed by backend, though backend handles it
        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });

            if (response.ok) {
                const result = await response.json();
                document.getElementById('newTicketId').textContent = result.ticket_id;
                document.getElementById('successMessage').classList.remove('hidden');
                ticketForm.reset();
            } else {
                alert('Error submitting ticket. Please try again.');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Network error. Check console.');
        }
    });
}

// Handle Dashboard Loading (dashboard.html)
const ticketList = document.getElementById('ticketList');
if (ticketList) {
    fetchTickets();
}

async function fetchTickets() {
    const status = document.getElementById('statusFilter')?.value || 'all';
    const priority = document.getElementById('priorityFilter')?.value || 'all';

    let url = `${API_URL}?skip=0&limit=100`;
    if (status !== 'all') url += `&status=${status}`;
    if (priority !== 'all') url += `&priority=${priority}`;

    try {
        const response = await fetch(url);
        const tickets = await response.json();
        renderTickets(tickets);
    } catch (error) {
        console.error('Error fetching tickets:', error);
    }
}

function applyFilters() {
    fetchTickets();
}

function exportCSV() {
    window.location.href = `${API_URL}/export`;
}

function renderTickets(tickets) {
    ticketList.innerHTML = '';

    // Sort by ID desc (newest first) but can be overridden by backend sorting later if implemented
    tickets.sort((a, b) => b.id - a.id);

    if (tickets.length === 0) {
        ticketList.innerHTML = '<li style="text-align:center; padding: 20px; color: #888;">No tickets found.</li>';
        return;
    }

    tickets.forEach(ticket => {
        const li = document.createElement('li');
        li.className = 'ticket-item';

        const date = new Date(ticket.created_at).toLocaleString();
        let resolutionTime = "";

        if (ticket.resolved_at) {
            const created = new Date(ticket.created_at);
            const resolved = new Date(ticket.resolved_at);
            const diffMs = resolved - created;
            const diffHrs = (diffMs / (1000 * 60 * 60)).toFixed(1);
            resolutionTime = `<div style="font-size: 0.8rem; color: hsl(var(--status-resolved));">Matches resolved in ${diffHrs} hrs</div>`;
        }

        li.innerHTML = `
            <div>
                <div style="display:flex; gap:10px; align-items:center; margin-bottom: 5px;">
                    <span style="font-weight: 700; color: hsl(var(--accent-color));">${ticket.ticket_id}</span>
                    <span class="badge status-${ticket.status.replace(/\s+/g, '')}">${ticket.status}</span>
                    <span class="badge" style="background: rgba(255,255,255,0.1);">${ticket.priority}</span>
                </div>
                <div style="font-weight: 600; font-size: 1.1rem; margin-bottom: 5px;">${ticket.issue_type}</div>
                <div style="color: hsl(var(--text-secondary)); font-size: 0.9rem;">${ticket.description.substring(0, 100)}...</div>
            </div>
            <div style="text-align: right; min-width: 150px;">
                <div style="font-size: 0.9rem; color: hsl(var(--text-secondary)); margin-bottom: 5px;">${ticket.user_name}</div>
                <div style="font-size: 0.8rem; opacity: 0.7;">${date}</div>
                ${resolutionTime}
                <button class="btn btn-secondary" style="margin-top: 10px; padding: 5px 10px; font-size: 0.8rem;" onclick="viewTicket('${ticket.ticket_id}')">View Details</button>
            </div>
        `;
        ticketList.appendChild(li);
    });
}

// Simple view detail stub
function viewTicket(id) {
    alert('Detail view for ' + id + ' would go here (Not implemented in this demo)');
}
