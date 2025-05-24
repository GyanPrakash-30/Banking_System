function updateBalance(newBalance) {
    const balanceEl = document.getElementById('balance');
    if (balanceEl) {
        balanceEl.textContent = newBalance.toFixed(2);
    }
}

function showMessage(text, isError = false) {
    const msg = document.getElementById('message');
    msg.textContent = text;
    msg.style.color = isError ? 'red' : 'green';
}

function loadTransactionHistory() {
    fetch('/api/history')
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const list = document.querySelector('#historyPanel ul');
                list.innerHTML = '';
                if (data.transactions.length === 0) {
                    list.innerHTML = '<li>No transactions found.</li>';
                } else {
                    data.transactions.forEach(txn => {
                        const li = document.createElement('li');
                        li.textContent = `${txn.timestamp} - ${txn.type} - ₹${txn.amount} - ${txn.details}`;
                        list.appendChild(li);
                    });
                }
            }
        });
}

function bankAction(action) {
    const inputId = action === 'deposit' ? 'deposit_amount' : 'withdraw_amount';
    const input = document.getElementById(inputId);
    const amount = parseFloat(input?.value);

    if (isNaN(amount) || amount <= 0) {
        return showMessage("Please enter a valid amount.", true);
    }

    fetch(`/api/${action}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ amount })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            updateBalance(data.balance);
            showMessage(`${action.charAt(0).toUpperCase() + action.slice(1)} successful.`);
            loadTransactionHistory(); // ✅ live update
        } else {
            showMessage(data.error || "Something went wrong.", true);
        }
    })
    .catch(() => {
        showMessage("Network or server error occurred.", true);
    });
}

function transfer() {
    const amount = parseFloat(document.getElementById('transfer_amount').value);
    const to = document.getElementById('to_user').value.trim();
    if (isNaN(amount) || amount <= 0 || !to) {
        return showMessage("Enter valid transfer details.", true);
    }

    fetch('/api/transfer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ amount, to })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            updateBalance(data.balance);
            showMessage("Transfer successful.");
            loadTransactionHistory(); // ✅ live update
        } else {
            showMessage(data.error, true);
        }
    })
    .catch(() => {
        showMessage("Network or server error occurred.", true);
    });
}

function payBill() {
    const amount = parseFloat(document.getElementById('bill_amount').value);
    const biller = document.getElementById('biller').value.trim();
    if (isNaN(amount) || amount <= 0 || !biller) {
        return showMessage("Enter valid bill payment details.", true);
    }

    fetch('/api/bill', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ amount, biller })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            updateBalance(data.balance);
            showMessage("Bill paid successfully.");
            loadTransactionHistory(); // ✅ live update
        } else {
            showMessage(data.error, true);
        }
    })
    .catch(() => {
        showMessage("Network or server error occurred.", true);
    });
}
