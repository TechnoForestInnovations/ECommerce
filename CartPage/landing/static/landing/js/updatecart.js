// ===============================
// CART FUNCTIONALITY + SELECTION
// ===============================

// Run after page loads
document.addEventListener("DOMContentLoaded", () => {
    setupSelectionFeature();
    updateCartSummary();
});

// ------------------------------
// EVENT DELEGATION FOR QUANTITY BUTTONS
// ------------------------------
document.addEventListener("click", async (e) => {
    if (e.target.classList.contains("qty-btn")) {
        const button = e.target;
        const itemId = button.dataset.id;
        const action = button.classList.contains("increase") ? "increase" : "decrease";
        await updateCart(itemId, action);
        updateCartSummary();
    }
});

// ------------------------------
// UPDATE CART VIA AJAX
// ------------------------------
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
            const qtyEl = document.querySelector(`#qty-${itemId}`);
            if (qtyEl) qtyEl.textContent = data.quantity;

            const subtotalEl = document.querySelector(`#subtotal-${itemId}`);
            if (subtotalEl) {
                const rawSubtotal = data.subtotal ?? data.sub_total ?? 0;
                subtotalEl.textContent = formatCurrency(parseNumber(rawSubtotal), false);
            }
        }

    } catch (error) {
        console.error("Error updating cart:", error);
    }
}

// ------------------------------
// SELECTION FEATURE + SELECT ALL
// ------------------------------
function setupSelectionFeature() {
    const checkboxes = document.querySelectorAll(".select-item");
    const selectAllCheckbox = document.getElementById("select-all");
    const checkoutButton = document.getElementById("checkout-button");

    // Individual checkbox change
    checkboxes.forEach(box => box.addEventListener("change", updateCartSummary));

    // Select All checkbox
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener("change", function () {
            checkboxes.forEach(box => (box.checked = selectAllCheckbox.checked));
            updateCartSummary();
        });
    }

    // Checkout validation
    if (checkoutButton) {
        checkoutButton.addEventListener("click", function (e) {
            const selectedItems = getSelectedItemIDs();
            const warningMessage = document.getElementById("warning-message");

            if (selectedItems.length === 0) {
                e.preventDefault();
                if (warningMessage) {
                    warningMessage.textContent = "⚠️ Please select at least one item before placing the order.";
                    warningMessage.style.display = "block";
                    warningMessage.scrollIntoView({ behavior: "smooth" });
                }
            } else {
                if (warningMessage) warningMessage.style.display = "none";
                placeSelectedOrder(selectedItems);
            }
        });
    }

    // Observe subtotal changes dynamically
    const observer = new MutationObserver(updateCartSummary);
    document.querySelectorAll(".cart-item-subtotal").forEach(el =>
        observer.observe(el, { childList: true })
    );
}

// ------------------------------
// UPDATE CART SUMMARY
// ------------------------------
function updateCartSummary() {
    const checkboxes = document.querySelectorAll(".select-item");
    const totalDisplay = document.getElementById("total-price");
    const summaryItems = document.getElementById("total-items");
    const taxesEl = document.getElementById("taxes");
    const deliveryEl = document.getElementById("delivery-charge");
    const grandTotalEl = document.getElementById("grand-total");
    const warningMessage = document.getElementById("warning-message");

    let total = 0;
    let count = 0;

    checkboxes.forEach(box => {
        if (box.checked) {
            const subtotalEl = document.querySelector(`#subtotal-${box.dataset.id}`);
            if (subtotalEl) {
                total += parseNumber(subtotalEl.textContent);
                count++;
            }
        }
    });

    if (count === 0) {
        if (warningMessage) {
            warningMessage.textContent = "⚠️ Please select at least one item to update summary.";
            warningMessage.style.display = "block";
        }
        setSummaryDisplays(0, 0, 0, 0, 0);
        return;
    } else {
        if (warningMessage) warningMessage.style.display = "none";
    }

    // Example calculation: 5% tax, flat 50 delivery
    const tax = total * 0.05;
    const deliveryCharge = 50;
    const grandTotal = total + tax + deliveryCharge;

    setSummaryDisplays(total, count, tax, deliveryCharge, grandTotal);
}

// Helper to update summary elements
function setSummaryDisplays(total, count, tax, deliveryCharge, grandTotal) {
    const totalDisplay = document.getElementById("total-price");
    const summaryItems = document.getElementById("total-items");
    const taxesEl = document.getElementById("taxes");
    const deliveryEl = document.getElementById("delivery-charge");
    const grandTotalEl = document.getElementById("grand-total");

    if (totalDisplay) totalDisplay.textContent = formatCurrency(total, false);
    if (summaryItems) summaryItems.textContent = count;
    if (taxesEl) taxesEl.textContent = formatCurrency(tax, false);
    if (deliveryEl) deliveryEl.textContent = formatCurrency(deliveryCharge, false);
    if (grandTotalEl) grandTotalEl.textContent = formatCurrency(grandTotal, false);
}

// ------------------------------
// PLACE ORDER
// ------------------------------
async function placeSelectedOrder(selectedItems) {
    try {
        const response = await fetch("/place-order/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({ selected_items: selectedItems }),
        });

        if (!response.ok) throw new Error("Order request failed");

        const data = await response.json();
        alert("✅ Order placed successfully!");
        console.log("Order response:", data);
    } catch (err) {
        console.error(err);
        alert("❌ Error placing order. Please try again.");
    }
}

// ------------------------------
// UTILITIES
// ------------------------------
function getSelectedItemIDs() {
    return Array.from(document.querySelectorAll(".select-item"))
        .filter(box => box.checked)
        .map(box => box.dataset.id);
}

function parseNumber(value) {
    if (!value) return 0;
    const cleaned = String(value).replace(/[^\d.-]/g, "");
    const parsed = parseFloat(cleaned);
    return isNaN(parsed) ? 0 : parsed;
}

function formatCurrency(amount, includeSymbol = true) {
    if (amount === null || amount === undefined || isNaN(amount)) return includeSymbol ? "₹0.00" : "0.00";
    const formatted = Number(amount).toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    return includeSymbol ? `₹${formatted}` : formatted;
}

function getCSRFToken() {
    const name = "csrftoken=";
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
        const trimmed = cookie.trim();
        if (trimmed.startsWith(name)) return trimmed.substring(name.length);
    }
    return "";
}
