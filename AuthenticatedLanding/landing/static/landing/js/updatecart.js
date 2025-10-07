// Run script after page is fully loaded
document.addEventListener("DOMContentLoaded", () => {
    setupCartButtons();
});

function setupCartButtons() {
    const buttons = document.querySelectorAll(".qty-btn");
    if (!buttons.length) return;

    buttons.forEach(button => {
        button.addEventListener("click", async () => {
            const itemId = button.dataset.id;
            const action = button.classList.contains("increase") ? "increase" : "decrease";
            await updateCart(itemId, action);
        });
    });
}

async function updateCart(itemId, action) {
    try {
        const response = await fetch(`/update-cart/${itemId}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({ action })
        });

        if (!response.ok) throw new Error("Network error");

        const data = await response.json();

        if (data.removed) {
            const itemRow = document.querySelector(`#qty-${itemId}`)?.closest(".cart-item");
            if (itemRow) itemRow.remove();
        } else {
            // Update quantity
            const qtyEl = document.querySelector(`#qty-${itemId}`);
            if (qtyEl) qtyEl.textContent = data.quantity;

            // Update subtotal — selector uses itemId
            const subtotalEl = document.querySelector(`#subtotal-${itemId}`);
            if (subtotalEl) {
                const rawSubtotal = data.subtotal ?? data.sub_total ?? 0;
                const parsed = parseNumber(rawSubtotal);
                subtotalEl.textContent = formatCurrency(parsed, false); // false -> DON'T include ₹ (since HTML already has ₹)
            }
        }

        // Update summary — use the span IDs
        const summaryItems = document.querySelector("#total-items");
        const summaryPrice = document.querySelector("#total-price");

        if (data.cart_summary) {
            if (summaryItems) summaryItems.textContent = String(data.cart_summary.total_items ?? 0);

            if (summaryPrice) {
                const rawTotal = data.cart_summary.total_price ?? data.cart_summary.total ?? 0;
                const parsedTotal = parseNumber(rawTotal);
                summaryPrice.textContent = formatCurrency(parsedTotal, false); // HTML already has the ₹ symbol outside
            }
        }

    } catch (error) {
        console.error("Error updating cart:", error);
    }
}

// Parse a possibly-formatted value into a numeric value (returns null on failure)
function parseNumber(value) {
    if (value === null || value === undefined) return null;
    if (typeof value === "number") return Number.isFinite(value) ? value : null;
    // Remove everything except digits, minus sign and dot
    const cleaned = String(value).replace(/[^\d.-]/g, "");
    const parsed = parseFloat(cleaned);
    return Number.isFinite(parsed) ? parsed : null;
}

// Format number for display. includeSymbol=false returns only the formatted number (no ₹).
function formatCurrency(amount, includeSymbol = true) {
    if (amount === null || amount === undefined || isNaN(amount)) {
        return includeSymbol ? "₹0.00" : "0.00";
    }
    const formatted = Number(amount).toLocaleString("en-IN", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
    return includeSymbol ? `₹${formatted}` : formatted;
}

function getCSRFToken() {
    const name = "csrftoken=";
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
        const trimmedCookie = cookie.trim();
        if (trimmedCookie.startsWith(name)) {
            return trimmedCookie.substring(name.length);
        }
    }
    return "";
}
