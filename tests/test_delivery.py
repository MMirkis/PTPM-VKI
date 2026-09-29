import unittest
import datetime

from src.Delivery import calculate_delivery_cost


FIXED_SEND_DATE = datetime.date(2026, 9, 3)


class TestWeightValidation(unittest.TestCase):

    def test_weight_below_minimum_returns_error(self):
        cost, date = calculate_delivery_cost(0.05, 100, "обычный")
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")

    def test_weight_above_maximum_returns_error(self):
        cost, date = calculate_delivery_cost(51.0, 100, "обычный")
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")

    def test_weight_exactly_minimum_is_accepted(self):
        cost, date = calculate_delivery_cost(0.1, 100, "обычный")
        self.assertNotEqual(cost, -1)

    def test_weight_exactly_maximum_is_accepted(self):
        cost, date = calculate_delivery_cost(50.0, 100, "обычный")
        self.assertNotEqual(cost, -1)


class TestDistanceValidation(unittest.TestCase):

    def test_distance_below_minimum_returns_error(self):
        cost, date = calculate_delivery_cost(1.0, 0, "обычный")
        self.assertEqual(cost, -1)

    def test_distance_above_maximum_returns_error(self):
        cost, date = calculate_delivery_cost(1.0, 5001, "обычный")
        self.assertEqual(cost, -1)

    def test_distance_exactly_maximum_is_accepted(self):
        cost, date = calculate_delivery_cost(1.0, 5000, "обычный")
        self.assertNotEqual(cost, -1)


class TestPackageTypeValidation(unittest.TestCase):

    def test_unknown_package_type_returns_error(self):
        cost, date = calculate_delivery_cost(1.0, 100, "неизвестный")
        self.assertEqual(cost, -1)

    def test_fragile_package_type_is_accepted(self):
        cost, date = calculate_delivery_cost(1.0, 100, "хрупкий")
        self.assertNotEqual(cost, -1)

    def test_dangerous_package_type_is_accepted(self):
        cost, date = calculate_delivery_cost(1.0, 100, "опасный")
        self.assertNotEqual(cost, -1)


class TestBaseCost(unittest.TestCase):

    def test_minimum_order_cost_is_200_plus_distance(self):
        # weight=1.0, distance=1, обычный -> 200 + 1*5 = 205
        cost, date = calculate_delivery_cost(1.0, 1, "обычный")
        self.assertEqual(cost, 205)

    def test_cost_scales_linearly_with_distance(self):
        cost_100, _ = calculate_delivery_cost(1.0, 100, "обычный")
        cost_200, _ = calculate_delivery_cost(1.0, 200, "обычный")
        self.assertEqual(cost_200 - cost_100, 500)  # (200-100)*5


class TestWeightCoefficients(unittest.TestCase):

    def test_weight_up_to_5_no_multiplier(self):
        # 1.0 кг: без надбавки
        cost, _ = calculate_delivery_cost(5.0, 100, "обычный")
        self.assertEqual(cost, 200 + 100 * 5)

    def test_weight_between_5_and_20_gets_1_2_multiplier(self):
        # 10 кг: (200 + 500) * 1.2 = 840
        cost, _ = calculate_delivery_cost(10.0, 100, "обычный")
        self.assertEqual(cost, int((200 + 100 * 5) * 1.2))

    def test_weight_20_and_above_gets_1_5_multiplier(self):
        # 20 кг: (200 + 500) * 1.5 = 1050
        cost, _ = calculate_delivery_cost(20.0, 100, "обычный")
        self.assertEqual(cost, int((200 + 100 * 5) * 1.5))


class TestPackageTypeSurcharges(unittest.TestCase):

    def test_fragile_adds_300(self):
        base, _ = calculate_delivery_cost(1.0, 100, "обычный")
        fragile, _ = calculate_delivery_cost(1.0, 100, "хрупкий")
        self.assertEqual(fragile - base, 300)

    def test_dangerous_adds_1000(self):
        base, _ = calculate_delivery_cost(1.0, 100, "обычный")
        dangerous, _ = calculate_delivery_cost(1.0, 100, "опасный")
        self.assertEqual(dangerous - base, 1000)


class TestExpressDelivery(unittest.TestCase):

    def test_express_should_be_more_expensive_not_cheaper(self):

        normal, _ = calculate_delivery_cost(1.0, 100, "обычный", is_express=False)
        express, _ = calculate_delivery_cost(1.0, 100, "обычный", is_express=True)
        self.assertGreater(express, normal)

    def test_express_delivery_date_not_later_than_normal(self):
        _, normal_date = calculate_delivery_cost(1.0, 1000, "обычный", is_express=False)
        _, express_date = calculate_delivery_cost(1.0, 1000, "обычный", is_express=True)
        self.assertLessEqual(express_date, normal_date)


class TestDeliveryDate(unittest.TestCase):

    def test_minimum_delivery_days_is_one(self):
        _, date = calculate_delivery_cost(1.0, 100, "обычный")
        expected = (FIXED_SEND_DATE + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        self.assertEqual(date, expected)

    def test_distance_500_gives_one_day(self):
        _, date = calculate_delivery_cost(1.0, 500, "обычный")
        expected = (FIXED_SEND_DATE + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        self.assertEqual(date, expected)

    def test_distance_1000_gives_two_days(self):
        _, date = calculate_delivery_cost(1.0, 1000, "обычный")
        expected = (FIXED_SEND_DATE + datetime.timedelta(days=2)).strftime("%Y-%m-%d")
        self.assertEqual(date, expected)

    def test_distance_5000_gives_ten_days(self):
        _, date = calculate_delivery_cost(1.0, 5000, "обычный")
        expected = (FIXED_SEND_DATE + datetime.timedelta(days=10)).strftime("%Y-%m-%d")
        self.assertEqual(date, expected)

    def test_delivery_date_returns_valid_format(self):
        _, date = calculate_delivery_cost(1.0, 100, "обычный")
        datetime.datetime.strptime(date, "%Y-%m-%d")  # не должно бросить исключение


class TestCombinedScenarios(unittest.TestCase):

    def test_fragile_express_combination(self):
        normal, _ = calculate_delivery_cost(1.0, 100, "хрупкий", is_express=False)
        express, _ = calculate_delivery_cost(1.0, 100, "хрупкий", is_express=True)
        self.assertGreater(express, normal)

    def test_dangerous_heavy_long_distance(self):
        # 20 кг, 5000 км, опасный, обычный
        expected_base = (200 + 5000 * 5) * 1.5 + 1000
        cost, _ = calculate_delivery_cost(20.0, 5000, "опасный")
        self.assertEqual(cost, int(expected_base))


if __name__ == "__main__":
    unittest.main()