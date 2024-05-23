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


# Memoized recursive function to apply rules and maximize points
memo = {}


def findMaxPoints(sportscheckTotal, timehortonsTotal, subwayTotal, otherTotal):
    state = (
        round(sportscheckTotal, 2),
        round(timehortonsTotal, 2),
        round(subwayTotal, 2),
        round(otherTotal, 2),
    )
    if state in memo:
        return memo[state]

    rules = [rule1, rule2, rule3, rule4, rule5, rule6, rule7]
    maxPoints = 0

    for rule in rules:
        rulePoints, newSportcheck, newTimhortons, newSubway, newOther = rule(
            sportscheckTotal, timehortonsTotal, subwayTotal, otherTotal
        )
        if rulePoints > 0:
            print("applied rule", rule)
            totalPoints = rulePoints + findMaxPoints(
                newSportcheck, newTimhortons, newSubway, newOther
            )
            maxPoints = max(maxPoints, totalPoints)

    memo[state] = maxPoints
    return maxPoints


def calculateRewards(transactions):
    totals = {"sportcheck": 0, "tim_hortons": 0, "subway": 0}
    otherAmt = 0
    for transaction in transactions.values():
        transaction["amount_dollars"] = round(transaction["amount_cents"] / 100, 2)

        if transaction["merchant_code"] in totals:
            totals[transaction["merchant_code"]] += transaction["amount_dollars"]
            totals[transaction["merchant_code"]] = round(
                totals[transaction["merchant_code"]], 2
            )
        else:
            otherAmt += transaction["amount_dollars"]
            otherAmt = round(otherAmt, 2)
    sportscheckAmt, timhortonsAmt, subwayAmt = (
        totals["sportcheck"],
        totals["tim_hortons"],
        totals["subway"],
    )

    maxPoints = findMaxPoints(sportscheckAmt, timhortonsAmt, subwayAmt, otherAmt)
    return maxPoints


transactions = {
    "T01": {
        "date": "2021-05-09",
        "merchant_code": "sportcheck",
        "amount_cents": 7326,
    },
    "T02": {
        "date": "2021-05-10",
        "merchant_code": "tim_hortons",
        "amount_cents": 1321,
    },
}

print(calculateRewards(transactions))
