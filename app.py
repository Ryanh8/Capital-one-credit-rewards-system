from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from datetime import datetime
from collections import defaultdict
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
# app.secret_key = "your_secret_key"
app.secret_key = os.environ.get("SECRET_KEY", "your_secret_key")

# "DATABASE_URL",
# "postgres://rodozpcvyghbpw:681f6f4b0a8fc3e2bad459a334620db20cca17cf1e1686e73ee8263dceb5dd89@ec2-54-144-112-84.compute-1.amazonaws.com:5432/d2ii2ugo800k94"
# Use environment variable for database URL or default to a local PostgreSQL database
# app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
#     "DATABASE_URL", "postgresql://ryanhu@localhost/capitalone"
# )
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
print("lol", os.environ.get("DATABASE_URL"))
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), nullable=False)
    merchant_code = db.Column(db.String(50), nullable=False)
    amount_cents = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


def create_app():
    with app.app_context():
        db.create_all()


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


def calculate_rewards(transactions):
    totals = {"sportcheck": 0, "tim_hortons": 0, "subway": 0}
    other_amt = 0

    for transaction in transactions.values():
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

    curr_points_dict = {
        (
            totals["sportcheck"],
            totals["tim_hortons"],
            totals["subway"],
            other_amt,
        ): 0
    }

    rules = [rule1, rule2, rule3, rule4, rule5, rule6, rule7]
    queue = [(totals["sportcheck"], totals["tim_hortons"], totals["subway"], other_amt)]

    while queue:
        state = queue.pop(0)
        curr_points = curr_points_dict[state]
        curr_sportcheck_amt, curr_tim_hortons_amt, curr_subway_amt, curr_other_amt = (
            state
        )

        for rule in rules:
            new_points, new_sportcheck, new_tim_hortons, new_subway, new_other = rule(
                curr_sportcheck_amt,
                curr_tim_hortons_amt,
                curr_subway_amt,
                curr_other_amt,
            )
            if new_points > 0:
                new_curr_points = curr_points + new_points
                new_state = (new_sportcheck, new_tim_hortons, new_subway, new_other)
                if (
                    new_state not in curr_points_dict
                    or new_curr_points > curr_points_dict[new_state]
                ):
                    curr_points_dict[new_state] = new_curr_points
                    queue.append(new_state)

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
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]
    transactions = Transaction.query.filter_by(user_id=user_id).all()
    return render_template("index.html", transactions=transactions)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        session["user_id"] = new_user.id
        return redirect(url_for("index"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session["user_id"] = user.id
            return redirect(url_for("index"))
        return "Invalid username or password"
    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))


@app.route("/calculate_points", methods=["POST"])
def calculate_points():
    if "user_id" not in session:
        return jsonify({"error": "Not authenticated"}), 401
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


@app.route("/transactions", methods=["POST"])
def add_transaction():
    if "user_id" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    data = request.get_json()
    new_transaction = Transaction(
        user_id=session["user_id"],
        date=data["date"],
        merchant_code=data["merchant_code"],
        amount_cents=data["amount_cents"],
    )
    db.session.add(new_transaction)
    db.session.commit()
    return redirect(url_for("index"))
    # return jsonify({"success": True}), 201


@app.route("/transactions", methods=["GET"])
def get_transactions():
    if "user_id" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    transactions = Transaction.query.filter_by(user_id=session["user_id"]).all()
    transactions_data = [
        {
            "id": t.id,
            "date": t.date,
            "merchant_code": t.merchant_code,
            "amount_cents": t.amount_cents,
        }
        for t in transactions
    ]
    return jsonify({"transactions": transactions_data})


if __name__ == "__main__":
    create_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
