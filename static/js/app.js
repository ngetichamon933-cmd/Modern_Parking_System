/* Moih Park Kenya — frontend interactivity
   Two small jobs:
   1. Auto-refresh the slot grid on slots.html so the visual display
      stays current without a manual page reload.
   2. Give the M-Pesa payment button simple "sending..." feedback.
*/

/**
 * Poll /api/slots every 5 seconds and redraw the slot grid + available
 * count in place. Called from slots.html.
 */
function startSlotAutoRefresh() {
    const grid = document.getElementById("slot-grid");
    const countLabel = document.getElementById("available-count");
    if (!grid) return;

    async function refresh() {
        try {
            const response = await fetch("/api/slots");
            if (!response.ok) return;
            const data = await response.json();

            data.slots.forEach((slot) => {
                const cell = grid.querySelector(`[data-slot="${slot.slot_number}"]`);
                if (!cell) return;
                cell.classList.toggle("slot-occupied", slot.is_occupied);
                cell.classList.toggle("slot-free", !slot.is_occupied);
            });

            if (countLabel) countLabel.textContent = data.available_count;
        } catch (error) {
            // Network hiccup — the next 5-second tick will just try again.
            console.warn("Could not refresh slot status:", error);
        }
    }

    refresh();
    setInterval(refresh, 5000);
}

/**
 * Let the user reveal/hide their password while typing, instead of
 * typing blind — a small but common friendliness touch on login forms.
 * Called from login.html.
 */
function setupPasswordToggle() {
    const toggleButton = document.getElementById("password-toggle");
    const passwordInput = document.getElementById("password");
    if (!toggleButton || !passwordInput) return;

    toggleButton.addEventListener("click", () => {
        const isHidden = passwordInput.type === "password";
        passwordInput.type = isHidden ? "text" : "password";
        toggleButton.textContent = isHidden ? "🙈" : "👁";
        toggleButton.setAttribute("aria-label", isHidden ? "Hide password" : "Show password");
    });
}

/**
 * Disable the M-Pesa button and show a short "sending..." message while
 * the STK push request is submitted, so the attendant knows it's working.
 * Called from payment.html.
 */
function setupMpesaFormFeedback() {
    const form = document.getElementById("mpesa-form");
    if (!form) return;

    form.addEventListener("submit", () => {
        const button = form.querySelector("button[type='submit']");
        if (button) {
            button.disabled = true;
            button.textContent = "Sending STK push...";
        }
    });
}
