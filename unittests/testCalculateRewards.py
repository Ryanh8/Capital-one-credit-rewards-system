import unittest
from app import calculateRewards


class TestCalculateRewards(unittest.TestCase):

    def test1(self):
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
        expected_points = 251
        self.assertEqual(calculateRewards(transactions), expected_points)

    def test2(self):
        transactions = {
            "T01": {
                "date": "2021-05-01",
                "merchant_code": "sportcheck",
                "amount_cents": 750000,
            },
            "T02": {
                "date": "2021-05-01",
                "merchant_code": "tim_hortons",
                "amount_cents": 25000,
            },
        }
        expected_points = 28375
        self.assertEqual(calculateRewards(transactions), expected_points)

    def test3(self):
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
        expected_points = 251
        self.assertEqual(calculateRewards(transactions), expected_points)

    def test4(self):
        transactions = {
            "T01": {
                "date": "2021-05-09",
                "merchant_code": "sportcheck",
                "amount_cents": 2500,
            },
            "T02": {
                "date": "2021-05-10",
                "merchant_code": "tim_hortons",
                "amount_cents": 1000,
            },
            "T03": {
                "date": "2021-05-10",
                "merchant_code": "the_bay",
                "amount_cents": 500,
            },
        }
        expected_points = 95
        self.assertEqual(calculateRewards(transactions), expected_points)

    def test5(self):
        transactions = {
            "T01": {
                "date": "2021-05-09",
                "merchant_code": "sportcheck",
                "amount_cents": 2500,
            },
            "T02": {
                "date": "2021-05-10",
                "merchant_code": "tim_hortons",
                "amount_cents": 1000,
            },
            "T03": {
                "date": "2021-05-10",
                "merchant_code": "the_bay",
                "amount_cents": 500,
            },
        }
        expected_points = 95
        self.assertEqual(calculateRewards(transactions), expected_points)

    def test6(self):
        transactions = {
            "T01": {
                "date": "2021-05-01",
                "merchant_code": "sportcheck",
                "amount_cents": 21000,
            },
            "T02": {
                "date": "2021-05-02",
                "merchant_code": "sportcheck",
                "amount_cents": 8700,
            },
            "T03": {
                "date": "2021-05-03",
                "merchant_code": "tim_hortons",
                "amount_cents": 323,
            },
            "T04": {
                "date": "2021-05-04",
                "merchant_code": "tim_hortons",
                "amount_cents": 1267,
            },
            "T05": {
                "date": "2021-05-05",
                "merchant_code": "tim_hortons",
                "amount_cents": 2116,
            },
            "T06": {
                "date": "2021-05-06",
                "merchant_code": "tim_hortons",
                "amount_cents": 2211,
            },
            "T07": {
                "date": "2021-05-07",
                "merchant_code": "subway",
                "amount_cents": 1853,
            },
            "T08": {
                "date": "2021-05-08",
                "merchant_code": "subway",
                "amount_cents": 2153,
            },
            "T09": {
                "date": "2021-05-09",
                "merchant_code": "sportcheck",
                "amount_cents": 7326,
            },
            "T10": {
                "date": "2021-05-10",
                "merchant_code": "tim_hortons",
                "amount_cents": 1321,
            },
        }
        expected_points = 1677
        self.assertEqual(calculateRewards(transactions), expected_points)


if __name__ == "__main__":
    unittest.main()
