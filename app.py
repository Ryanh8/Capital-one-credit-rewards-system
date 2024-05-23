from flask import Flask, render_template, request, jsonify
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)


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


def calculateRewards(transactions):
    # Convert transaction amounts to dollars and keep sum totals of each merchant
    totals = {"sportcheck": 0, "tim_hortons": 0, "subway": 0}
    otherAmt = 0

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
            otherAmt += transaction["amount_dollars"]
            otherAmt = round(otherAmt, 2)

    # Initialize dictionary to store currPoints for each state
    currPointsDict = {}
    # Initialize the first state, currPoints is 0 and original totals
    currPointsDict[
        (
            totals["sportcheck"],
            totals["tim_hortons"],
            totals["subway"],
            otherAmt,
        )
    ] = 0

    # Store all the rules in a list
    rules = [rule1, rule2, rule3, rule4, rule5, rule6, rule7]

    # Initialize queue with the first state
    queue = [(totals["sportcheck"], totals["tim_hortons"], totals["subway"], otherAmt)]

    while queue:
        # Get the first state in the queue
        state = queue.pop(0)

        currPoints = currPointsDict[state]

        currSportcheckAmt, currTimHortonsAmt, currSubwayAmt, currOtherAmt = state

        # Iterate through all the rules
        for rule in rules:
            # Apply the rule to the state
            newPoints, newSportcheck, newTimhortons, newSubway, newOther = rule(
                currSportcheckAmt, currTimHortonsAmt, currSubwayAmt, currOtherAmt
            )
            # If the rule applied current points is greater than 0, otherwise continue
            if newPoints > 0:
                # Calculate the new current points
                new_currPoints = currPoints + newPoints
                # If the new state has not been visited or the new currPoints is greater than the previous currPoints
                if (
                    newSportcheck,
                    newTimhortons,
                    newSubway,
                    newOther,
                ) not in currPointsDict or new_currPoints > currPointsDict[
                    (newSportcheck, newTimhortons, newSubway, newOther)
                ]:
                    # Update the currPoints
                    currPointsDict[
                        (newSportcheck, newTimhortons, newSubway, newOther)
                    ] = new_currPoints
                    # Add the new state to the queue
                    queue.append((newSportcheck, newTimhortons, newSubway, newOther))

    # Maximum points will be the maximum value in the dictionary
    maxPoints = max(currPointsDict.values())
    return int(maxPoints)


def groupTransactionsByMonth(transactions):
    byMonth = defaultdict(dict)
    for key, transaction in transactions.items():
        date = datetime.strptime(transaction["date"], "%Y-%m-%d")
        month = date.strftime("%Y-%m")
        byMonth[month][key] = transaction
    return byMonth


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/calculate_points", methods=["POST"])
def calculatePoints():
    transactions = request.json
    if not transactions:
        return jsonify({"error": "No transactions provided"}), 400
    byMonth = groupTransactionsByMonth(transactions)

    monthDict = {}
    for month, transactions in byMonth.items():
        totalPoints = calculateRewards(transactions)
        monthDict[month] = totalPoints

    return jsonify(monthDict)


if __name__ == "__main__":
    app.run(debug=True)
