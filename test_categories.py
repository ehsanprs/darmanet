"""Checks for the tagging rules in categories.py, using real wording from the data.

Run: .venv\\Scripts\\python -m unittest test_categories
"""
import unittest

from categories import tag


def center(type_, name, note=None):
    return {"type": type_, "name": name, "note": note}


class TaggingTest(unittest.TestCase):
    def assertTags(self, c, cats=(), services=(), no_cats=(), no_services=()):
        got_cats, got_services, _ = tag(c)
        for k in cats:
            self.assertIn(k, got_cats, f"{c['name']}: category {k} missing ({got_cats})")
        for k in services:
            self.assertIn(k, got_services, f"{c['name']}: service {k} missing ({got_services})")
        for k in no_cats:
            self.assertNotIn(k, got_cats, f"{c['name']}: unexpected category {k}")
        for k in no_services:
            self.assertNotIn(k, got_services, f"{c['name']}: unexpected service {k}")

    # ---- imaging spellings and synonyms
    def test_mri_spellings(self):
        for note in ("ام آر آی", "ام آر ای", "ام ار ای", "MRI", "mri-سونوگرافی", "ام آرآی", "چربی کبدباMRI"):
            self.assertTags(center("تصویربرداری", "x", note), services=["mri"])

    def test_radiology_spellings(self):
        for note in ("رادیولوژی", "رادیولولوژی(عکس فک و دندان)", "رادیوگرافی دیجیتال", "هیستروگرافی"):
            self.assertTags(center("تصویربرداری", "x", f"سونوگرافی - {note}"), services=["xray"])

    def test_ct_variants(self):
        for note in ("سی تی اسکن", "سیتی اسکن", "سی اسکن", "سی تی آنژیوگرافی"):
            self.assertTags(center("تصویربرداری", "x", note), services=["ct"], no_services=["angiography"])
        self.assertTags(center("درمانگاه", "سی تیر", None), no_services=["ct"])

    def test_bone_density_and_nuclear(self):
        self.assertTags(center("تصویربرداری", "x", "سونوگرافی-رادیولوژی-ماموگرافی-دانسیتومتری"),
                        services=["bone_density", "mammography"])
        self.assertTags(center("تصویربرداری", "x", "سونوگرافی - سنجش تراکم استخوان(BMD)"), services=["bone_density"])
        for note in ("اسپکت قلب", "پت اسکن", "انواع اسکن شامل اسکن قلب ، استخوان ، تیروئید", "اسکن هسته ای-تیروئیدی"):
            self.assertTags(center("تصویربرداری", "x", note), services=["nuclear"])
        self.assertTags(center("تصویربرداری", "x", "سونوگرافی - اسکن کف پا"), no_services=["nuclear"])

    def test_dental_imaging_is_not_general_xray(self):
        self.assertTags(center("تصویربرداری", "رادیولوژی دهان ، فک و صورت آرشام"),
                        services=["dental_imaging"], no_services=["xray"])
        self.assertTags(center("تصویربرداری", "x", "OPG -PA- CBCT-بایت وینگ"), services=["dental_imaging"])
        self.assertTags(center("تصویربرداری", "x", "پری اپیکال - پانورکس - cbct"), services=["dental_imaging"])

    def test_doppler(self):
        self.assertTags(center("تصویربرداری", "x", "سونوگرافی معمولی-داپلر"), services=["ultrasound"])
        self.assertTags(center("درمانگاه", "x", "اکو داپلر- نوار عصب عضله - ویزیت"),
                        services=["echo", "emg"], no_services=["ultrasound"])

    # ---- exclusions in descriptions
    def test_negations(self):
        self.assertTags(center("مرکز جراحی محدود", "چشم پزشکی آبان", "خدمات لیزیک ، لازک شامل قرارداد نمی شود"),
                        services=["ophthalmology"], no_services=["eye_surgery"])
        self.assertTags(center("مرکز جراحی محدود", "حکیمان نور", "جراحی- خدمات سرپایی ( به جز لازک و لیزیک)"),
                        no_services=["eye_surgery"])
        self.assertTags(center("مرکز جراحی محدود", "کاپری", "عدم پذیرش بیماران جهت جراحی آندوسکوپی بینی و سینوس"),
                        no_cats=["gi"], no_services=["endoscopy"])
        self.assertTags(center("کلینیک", "x", "انواع نوار نگاری شامل : نوار مغز - نوار عصب عضله و ... به جز ویزیت"),
                        services=["eeg", "emg"], no_services=["visit"])
        self.assertTags(center("تصویربرداری", "x", "سونوگرافی ساده و داپلر(سونوگرافی غربالگری انجام نمیدهند )"),
                        services=["ultrasound"])

    # ---- heart, neuro, typos
    def test_heart_services(self):
        c = center("درمانگاه", "شبانه روزی مولانا", "قلب و عروق ( نوار قلب ، اکوکاردیوگرافی ، تست ورزش) -ویزیت")
        self.assertTags(c, cats=["clinic", "heart"],
                        services=["heart_visit", "ecg", "echo", "stress_test", "visit"])
        self.assertTags(center("درمانگاه", "x", "ویزیت - بخش قلب (نوار قلب)"), services=["heart_visit"])
        self.assertTags(center("درمانگاه", "x", "قلب و عروق (اکوکاردیوگرافی - نوار برق )"), services=["ecg"])
        self.assertTags(center("مطب", "x", "نوارقلب - تست ورزش -اکوکاردیوگرافی - مانیتورینگ"), services=["holter"])
        self.assertTags(center("درمانگاه", "x", "نوار قلب - ویزیت"), no_services=["heart_visit"])

    def test_angiography(self):
        self.assertTags(center("بیمارستان", "بهارلو", "فقط جهت خدمات آنژیوگرافی و آنژیوپلاستی"),
                        cats=["heart"], services=["angiography"])
        self.assertTags(center("بیمارستان", "x", "PRP ، OCT ، آنژیوگرافی چشم"),
                        cats=["eye"], services=["eye_tests"], no_services=["angiography"])

    def test_neuro_typos(self):
        for note in ("نورا عصب عضله", "نوارعصب و عضله", "نوار مغر", "نورا مغز", "نقشه مغزی", "انواع نوارنگاری"):
            self.assertTags(center("درمانگاه", "x", note), cats=["neuro"])

    # ---- eye
    def test_eye_words_in_shop_names(self):
        for name in ("چشمان کاشان", "چشم انداز", "چشمک", "سرچشمه", "چشم شهر"):
            self.assertTags(center("عینک سازی", name), cats=["eye"], services=["optician"],
                            no_services=["ophthalmology"])
        self.assertTags(center("آزمایشگاه", "تشخیص پزشکی بیمارستان چشم پزشکی نگاه"), no_cats=["eye"])
        self.assertTags(center("مرکز جراحی محدود", "کلینیک مرکزی شهر(چشمخانه)"), cats=["eye"])

    # ---- clinics offering several departments
    def test_polyclinic_cross_listing(self):
        c = center("درمانگاه", "شبانه روزی بهبود", "آزمایشگاه ، دندانپزشکی ، بخش قلب (اکو ، تست ورزش ، نوار قلب ، هولتر )")
        self.assertTags(c, cats=["clinic", "lab", "dental", "heart"])
        c = center("درمانگاه", "خیریه فرمانفرمائیان", "آزمایشگاه- تصویربرداری-فیزیوتراپی")
        self.assertTags(c, cats=["lab", "imaging", "rehab"])

    def test_kidney_word_is_not_urology(self):
        self.assertTags(center("درمانگاه", "x", "ویزیت متخصص چشم -کلیه عکس برداری چشم"), no_services=["urology"])
        self.assertTags(center("درمانگاه", "x", "ویزیت و خدمات سرپایی - نوار مثانه - سنگ شکن"), services=["urology"])

    # ---- hospitals and oncology
    def test_hospital_specialties_from_name_only(self):
        self.assertTags(center("بیمارستان", "قلب جماران"), cats=["heart"], services=["hosp_heart"])
        self.assertTags(center("بیمارستان", "مادر و کودک غدیر"), services=["hosp_women", "hosp_children"])
        self.assertTags(center("بیمارستان", "نگاه", "اکو کاردیوگرافی قلب، نوار قلب"), no_services=["hosp_heart"])
        self.assertTags(center("بیمارستان", "روانپزشکی ایرانیان"), services=["hosp_psych"])

    def test_oncology(self):
        self.assertTags(center("کلینیک", "رادیوتراپی بیمارستان گاندی"), cats=["oncology"], services=["radiotherapy"])
        self.assertTags(center("کلینیک", "x", "رادیوتراپی - شیمی درمانی"), services=["radiotherapy", "chemotherapy"])
        self.assertTags(center("تصویربرداری", "گامانایف ایران"), cats=["oncology"])
        self.assertTags(center("تصویربرداری", "پرتو"), no_cats=["oncology"])

    # ---- dental and 24h
    def test_dental_specialties(self):
        c = center("دندانپزشکی", "کلینیک دندانپزشکی بهبود",
                   "ایمپلنت-جراحی فک وصورت-اطفال-ترمیم-ارتودنسی-درمان ریشه-انواع پروتزهای دندانی ثابت و متحرک")
        self.assertTags(c, services=["implant", "oral_surgery", "kids_dentistry", "orthodontics",
                                     "endodontics", "prosthodontics"])
        self.assertTags(center("دندانپزشکی", "دکتر x (متخصص ارتودنسی و ناهنجاری فک و صورت)"),
                        services=["orthodontics"])

    def test_all_day(self):
        self.assertTrue(tag(center("داروخانه", "شبانه روزی دکتر x"))[2])
        self.assertTrue(tag(center("خدمات اورژانس", "x"))[2])
        self.assertFalse(tag(center("داروخانه", "دکتر x"))[2])


if __name__ == "__main__":
    unittest.main()
