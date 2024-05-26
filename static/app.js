document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("transactionForm");
    const transactionsTable = document.getElementById("transactionsTable").getElementsByTagName('tbody')[0];
    const pointsByMonthDiv = document.getElementById("pointsByMonth");
    const calculatePointsButton = document.getElementById("calculatePoints");
    const resetTransactionsButton = document.getElementById("resetTransactions");

    let transactions = {};

    // Fetch previous transactions on page load
    fetch("/transactions")
        .then(response => response.json())
        .then(data => {
            if (data.transactions) {
                data.transactions.forEach(transaction => {
                    const transactionId = "T" + (Object.keys(transactions).length + 1).toString().padStart(2, '0');
                    transactions[transactionId] = transaction;

                    const newRow = transactionsTable.insertRow();
                    newRow.setAttribute("data-id", transactionId);
                    newRow.insertCell(0).appendChild(document.createTextNode(transaction.date));
                    newRow.insertCell(1).appendChild(document.createTextNode(transaction.merchant_code.replace('_', ' ')));
                    newRow.insertCell(2).appendChild(document.createTextNode((transaction.amount_cents / 100).toFixed(2)));
                    newRow.insertCell(3).appendChild(document.createTextNode('Pending...'));
                });
            }
        })
        .catch(error => console.error("Error fetching transactions:", error));

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        const date = document.getElementById("date").value;
        const merchant = document.getElementById("merchant").value;
        const amount = parseFloat(document.getElementById("amount").value);

        if (date && merchant && amount) {
            const transactionId = "T" + (Object.keys(transactions).length + 1).toString().padStart(2, '0');
            const amountCents = Math.round(amount * 100);

            const transaction = {
                date: date,
                merchant_code: merchant,
                amount_cents: amountCents
            };

            transactions[transactionId] = transaction;

            const newRow = transactionsTable.insertRow();
            newRow.setAttribute("data-id", transactionId);
            newRow.insertCell(0).appendChild(document.createTextNode(date));
            newRow.insertCell(1).appendChild(document.createTextNode(merchant.replace('_', ' ')));
            newRow.insertCell(2).appendChild(document.createTextNode(amount.toFixed(2)));
            const pointsCell = newRow.insertCell(3);
            pointsCell.appendChild(document.createTextNode('Pending...'));

            fetch("/transactions", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(transaction)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    fetch(`/transactions?transactionId=${transactionId}`)
                    .then(response => response.json())
                    .then(data => {
                        pointsCell.textContent = data.points + ' points';
                    })
                    .catch(error => {
                        console.error("Error:", error);
                        pointsCell.textContent = 'Error';
                    });
                } else {
                    pointsCell.textContent = 'Error';
                }
            })
            .catch(error => {
                console.error("Error:", error);
                pointsCell.textContent = 'Error';
            });

            form.reset();
            const today = new Date().toISOString().split('T')[0];
            document.getElementById("date").value = today;
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
            for (const [month, details] of Object.entries(data)) {
                const p = document.createElement("p");
                p.textContent = `${month}: ${details.total_points} points`;
                pointsByMonthDiv.appendChild(p);

                for (const [transactionId, maxPoints] of Object.entries(details.transaction_rewards)) {
                    const row = transactionsTable.querySelector(`tr[data-id='${transactionId}']`);
                    if (row) {
                        row.cells[3].textContent = maxPoints + ' points';
                    }
                }
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
