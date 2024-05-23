document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("transactionForm");
    const transactionsTable = document.getElementById("transactionsTable").getElementsByTagName('tbody')[0];
    const pointsByMonthDiv = document.getElementById("pointsByMonth");
    const calculatePointsButton = document.getElementById("calculatePoints");
    const resetTransactionsButton = document.getElementById("resetTransactions");

    let transactions = {};

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        const date = document.getElementById("date").value;
        const merchant = document.getElementById("merchant").value;
        const amount = parseFloat(document.getElementById("amount").value);

        if (date && merchant && amount) {
            const transactionId = "T" + (Object.keys(transactions).length + 1).toString().padStart(2, '0');
            const amountCents = Math.round(amount * 100);

            transactions[transactionId] = {
                date: date,
                merchant_code: merchant,
                amount_cents: amountCents
            };

            const newRow = transactionsTable.insertRow();
            newRow.insertCell(0).appendChild(document.createTextNode(date));
            newRow.insertCell(1).appendChild(document.createTextNode(merchant.replace('_', ' ')));
            newRow.insertCell(2).appendChild(document.createTextNode(amount.toFixed(2)));

            form.reset();
        }
    });

    calculatePointsButton.addEventListener("click", function () {
        fetch("/calculate_points", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(transactions)
        })
        .then(response => response.json())
        .then(data => {
            pointsByMonthDiv.innerHTML = "";
            for (const [month, points] of Object.entries(data)) {
                const p = document.createElement("p");
                p.textContent = `${month}: ${points} points`;
                pointsByMonthDiv.appendChild(p);
            }
        })
        .catch(error => console.error("Error:", error));
    });

    resetTransactionsButton.addEventListener("click", function () {
        transactions = {};
        transactionsTable.innerHTML = "";
        pointsByMonthDiv.innerHTML = "";
    });
});
