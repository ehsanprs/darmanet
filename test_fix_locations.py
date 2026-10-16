"""Offline checks for how fix_locations.py picks a search result (no API calls).

Run: .venv\\Scripts\\python -m unittest test_fix_locations
"""
import unittest

from fix_locations import core, judge, name_score

ARINA = {"id": "x", "type": "تصویربرداری", "name": "آرینا", "province": "تهران", "city": "تهران",
         "address": "تهران - پاسداران - نگارستان دوم (کاشی ها) - پلاک 2"}
PASDARAN = {"lat": 35.7757, "lng": 51.4665}


def place(title, lat, lng, address="", category="place", type_="مرکز درمانی"):
    return {"title": title, "address": address, "category": category, "type": type_,
            "location": {"x": lng, "y": lat}, "neighbourhood": ""}


class MatchingTest(unittest.TestCase):
    def test_core_words(self):
        self.assertEqual(core("مرکز تصویربرداری آرینا"), ["آرینا"])
        self.assertEqual(core("دکتر علی محمدی (متخصص ارتودنسی)"), ["علی", "محمدی", "ارتودنسی"])
        self.assertEqual(core("پاتوبیولوژی مادر تبریز", "تبریز"), ["مادر"])

    def test_name_score(self):
        self.assertEqual(name_score(["آرینا"], "مرکز تصویربرداری آرینا"), 1.0)
        self.assertEqual(name_score(["آرینا"], "آرین"), 0.0)
        self.assertEqual(name_score(["علی", "محمدی"], "مطب دکتر علی محمدی"), 1.0)
        self.assertEqual(name_score(["علی", "محمدی"], "دکتر علی رضایی"), 0.5)

    def test_picks_the_place_in_the_right_neighborhood(self):
        items = [place("تصویربرداری آرینا", 35.7762, 51.4659, "تهران، پاسداران، نگارستان دوم"),
                 place("آرینا", 35.659, 51.306, "تهران، شمس آباد، نگارستان دوم")]
        best, verdict, _ = judge(ARINA, items, PASDARAN, 2.5, "neighborhood «پاسداران»")
        self.assertEqual(verdict, "ok")
        self.assertAlmostEqual(best[1]["lat"], 35.7762)

    def test_rejects_same_name_far_away(self):
        items = [place("آرینا", 35.659, 51.306, "تهران، شمس آباد")]
        self.assertEqual(judge(ARINA, items, PASDARAN, 2.5, "neighborhood")[1], "no_match")

    def test_rejects_streets_and_non_health_places(self):
        items = [place("آرینا", 35.776, 51.466, category="municipal", type_="خیابان"),
                 place("مسجد آرینا", 35.776, 51.466, type_="مسجد")]
        self.assertEqual(judge(ARINA, items, PASDARAN, 2.5, "neighborhood")[1], "no_match")

    def test_two_different_close_matches_is_ambiguous(self):
        items = [place("آرینا", 35.7760, 51.4660), place("آرینا", 35.7800, 51.4700)]
        self.assertEqual(judge(ARINA, items, PASDARAN, 2.5, "neighborhood")[1], "ambiguous")

    def test_duplicate_listing_of_one_place_is_fine(self):
        items = [place("تصویربرداری آرینا", 35.7760, 51.4660), place("آرینا", 35.7761, 51.4661)]
        self.assertEqual(judge(ARINA, items, PASDARAN, 2.5, "neighborhood")[1], "ok")

    def test_city_level_search_needs_street_confirmation(self):
        city_mid = {"lat": 35.70, "lng": 51.40}
        weak = [place("آرینا", 35.75, 51.45, "تهران، ونک")]
        self.assertEqual(judge(ARINA, weak, city_mid, 20, "city")[1], "ok")  # full name match alone is enough
        partial = {**ARINA, "name": "آرینا نوین"}
        self.assertEqual(judge(partial, [place("آرینا مهر", 35.75, 51.45, "تهران، ونک")], city_mid, 20, "city")[1],
                         "no_match")


if __name__ == "__main__":
    unittest.main()
