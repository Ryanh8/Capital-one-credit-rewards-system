from flask import Flask, render_template, request, jsonify
from datetime import datetime
from collections import defaultdict
import os

app = Flask(__name__)


# Validation function
def validator(transaction):
    required = ["date", "merchant_code", "amount_cents"]
    for field in required:
        if field not in transaction or transaction[field] is None:
            return False
        if field == "amount_cents" and not isinstance(transaction[field], int):
            return False
        if field == "date":
            try:
                datetime.strptime(transaction[field], "%Y-%m-%d")
            except ValueError:
                return False
    return True


# Rules
def rule1(sportscheckAmt, timhortonsAmt, subwayAmt, otherAmt):
    if sportscheckAmt >= 75 and timhortonsAmt >= 25 and subwayAmt >= 25:
        return (
            500,
            round(sportscheckAmt - 75, 2),
            round(timhortonsAmt - 25, 2),
            round(subwayAmt - 25, 2),
            round(otherAmt, 2),
        )
    return 0, sportscheckAmt, timhortonsAmt, subwayAmt, otherAmt


def rule2(sportscheckAmt, timhortonsAmt, subwayAmt, otherAmt):
    if sportscheckAmt >= 75 and timhortonsAmt >= 25:
        return (
            300,
            round(sportscheckAmt - 75, 2),
            round(timhortonsAmt - 25, 2),
            round(subwayAmt, 2),
            round(otherAmt, 2),
        )
    return 0, sportscheckAmt, timhortonsAmt, subwayAmt, otherAmt


def rule3(sportscheckAmt, timhortonsAmt, subwayAmt, otherAmt):
    if sportscheckAmt >= 75:
        return 200, round(sportscheckAmt - 75, 2), timhortonsAmt, subwayAmt, otherAmt
    return 0, sportscheckAmt, timhortonsAmt, subwayAmt, otherAmt


def rule4(sportscheckAmt, timhortonsAmt, subwayAmt, otherAmt):
    if sportscheckAmt >= 25 and timhortonsAmt >= 10 and subwayAmt >= 10:
        return (
            150,
            round(sportscheckAmt - 25, 2),
            round(timhortonsAmt - 10, 2),
            round(subwayAmt - 10, 2),
            round(otherAmt, 2),
        )
    return 0, sportscheckAmt, timhortonsAmt, subwayAmt, otherAmt


def rule5(sportscheckAmt, timhortonsAmt, subwayAmt, otherAmt):
    if sportscheckAmt >= 25 and timhortonsAmt >= 10:
        return (
            75,
            round(sportscheckAmt - 25, 2),
            round(timhortonsAmt - 10, 2),
            round(subwayAmt, 2),
            round(otherAmt, 2),
        )
    return 0, sportscheckAmt, timhortonsAmt, subwayAmt, otherAmt


def rule6(sportscheckAmt, timhortonsAmt, subwayAmt, otherAmt):
    if sportscheckAmt >= 20:
        return (
            75,
            round(sportscheckAmt - 20, 2),
            round(timhortonsAmt, 2),
            round(subwayAmt, 2),
            round(otherAmt, 2),
        )
    return 0, sportscheckAmt, timhortonsAmt, subwayAmt, otherAmt


def rule7(sportscheckAmt, timhortonsAmt, subwayAmt, otherAmt):
    points = sportscheckAmt + timhortonsAmt + subwayAmt + otherAmt
    return points, 0, 0, 0, 0


def calculate_rewards(transactions):
    # Convert transaction amounts to dollars and keep sum totals of each merchant
    totals = {"sportcheck": 0, "tim_hortons": 0, "subway": 0}
    other_amt = 0

    for transaction in transactions.values():
        # skip invalid transactions
        if not validator(transaction):
            continue
        transaction["amount_dollars"] = round(transaction["amount_cents"] / 100, 2)

        if transaction["merchant_code"] in totals:
            totals[transaction["merchant_code"]] += transaction["amount_dollars"]
            totals[transaction["merchant_code"]] = round(
                totals[transaction["merchant_code"]], 2
            )
        else:
            other_amt += transaction["amount_dollars"]
            other_amt = round(other_amt, 2)

    # Initialize dictionary to store currPoints for each state
    curr_points_dict = {}
    # Initialize the first state, currPoints is 0 and original totals
    curr_points_dict[
        (
            totals["sportcheck"],
            totals["tim_hortons"],
            totals["subway"],
            other_amt,
        )
    ] = 0

    # Store all the rules in a list
    rules = [rule1, rule2, rule3, rule4, rule5, rule6, rule7]

    # Initialize queue with the first state
    queue = [(totals["sportcheck"], totals["tim_hortons"], totals["subway"], other_amt)]

    while queue:
        # Get the first state in the queue
        state = queue.pop(0)

        curr_points = curr_points_dict[state]

        curr_sportcheck_amt, curr_tim_hortons_amt, curr_subway_amt, curr_other_amt = (
            state
        )

        # Iterate through all the rules
        for rule in rules:
            # Apply the rule to the state
            new_points, new_sportcheck, new_timhortons, new_subway, new_other = rule(
                curr_sportcheck_amt,
                curr_tim_hortons_amt,
                curr_subway_amt,
                curr_other_amt,
            )
            # If the rule applied current points is greater than 0, otherwise continue
            if new_points > 0:
                # Calculate the new current points
                new_curr_points = curr_points + new_points
                # If the new state has not been visited or the new curr_points is greater than the previous curr_points
                if (
                    new_sportcheck,
                    new_timhortons,
                    new_subway,
                    new_other,
                ) not in curr_points_dict or new_curr_points > curr_points_dict[
                    (new_sportcheck, new_timhortons, new_subway, new_other)
                ]:
                    # Update the curr_points
                    curr_points_dict[
                        (new_sportcheck, new_timhortons, new_subway, new_other)
                    ] = new_curr_points
                    # Add the new state to the queue
                    queue.append(
                        (new_sportcheck, new_timhortons, new_subway, new_other)
                    )

    # Maximum points will be the maximum value in the dictionary
    max_points = max(curr_points_dict.values())
    return int(max_points)


def calculate_points_for_transaction(transaction):
    return calculate_rewards({1: transaction})


def group_transactions_by_month(transactions):
    by_month = defaultdict(dict)
    for key, transaction in transactions.items():
        date = datetime.strptime(transaction["date"], "%Y-%m-%d")
        month = date.strftime("%Y-%m")
        by_month[month][key] = transaction
    return by_month


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/calculate_points", methods=["POST"])
def calculate_points():
    transactions = request.json
    if not transactions:
        return jsonify({"error": "No transactions provided"}), 400
    by_month = group_transactions_by_month(transactions)

    month_dict = {}
    for month, transactions in by_month.items():
        total_points = calculate_rewards(transactions)
        transaction_rewards = {
            k: calculate_points_for_transaction(v) for k, v in transactions.items()
        }
        month_dict[month] = {
            "total_points": total_points,
            "transaction_rewards": transaction_rewards,
        }

    return jsonify(month_dict)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
