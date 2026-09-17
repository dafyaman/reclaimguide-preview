from pathlib import Path
import json
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
PRIVACY = ROOT / "privacy.html"
GUIDE = ROOT / "windows-storage-guide.html"
DIAGNOSTIC = ROOT / "c-drive-full-windows-11.html"
PLANNER = ROOT / "storage-cleanup-planner.html"
PLANNER_JS = ROOT / "planner.js"
ROBOTS = ROOT / "robots.txt"
SITEMAP = ROOT / "sitemap.xml"
INDEXNOW_KEY = ROOT / "a85fc997b5115fc41d90d561e830427c.txt"


class PublicPreviewTests(unittest.TestCase):
    def setUp(self):
        self.html = INDEX.read_text(encoding="utf-8")

    def test_preview_has_product_and_validation_price(self):
        self.assertIn("ReclaimGuide", self.html)
        self.assertIn("$19.99", self.html)
        self.assertIn("Early validation", self.html)

    def test_waitlist_uses_account_free_google_form_on_all_conversion_pages(self):
        form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdKrVo85XaOiukX-vTF9yFcdGb92oEZhBRwqqOPdLT9HSV5vg/viewform"
        guide = GUIDE.read_text(encoding="utf-8")
        planner = PLANNER.read_text(encoding="utf-8")
        diagnostic = DIAGNOSTIC.read_text(encoding="utf-8")
        for page in (self.html, guide, planner, diagnostic):
            self.assertIn(form_url, page)
            self.assertIn("No Google account required", page)
            self.assertIn("Share 30-second feedback", page)
        self.assertIn("Two required questions", self.html)
        self.assertIn("Example concept preview", self.html)

    def test_waitlist_privacy_discloses_google_forms_and_collected_data(self):
        privacy = PRIVACY.read_text(encoding="utf-8")
        self.assertIn("Google Forms", privacy)
        self.assertIn("email address", privacy)
        self.assertIn("Email is optional", privacy)
        self.assertIn("Google’s Privacy Policy", privacy)

    def test_compact_desktop_keeps_primary_action_above_fold(self):
        self.assertIn("@media(max-height:700px) and (min-width:781px)", self.html)
        self.assertIn(".hero{min-height:430px", self.html)
        self.assertIn("h1{font-size:56px", self.html)

    def test_no_payment_or_tracking_endpoint_is_present(self):
        lowered = self.html.lower()
        for forbidden in ("stripe.com", "gumroad.com", "paypal.com", "formspree", "google-analytics", "googletagmanager"):
            self.assertNotIn(forbidden, lowered)

    def test_public_page_has_privacy_link_and_no_external_assets(self):
        self.assertIn('href="privacy.html"', self.html)
        self.assertNotIn("<script src=", self.html)
        self.assertNotIn('rel="stylesheet"', self.html)
        self.assertTrue(PRIVACY.exists())

    def test_evergreen_storage_guide_is_grounded_and_converts_to_waitlist(self):
        self.assertTrue(GUIDE.exists())
        guide = GUIDE.read_text(encoding="utf-8")
        self.assertIn("How to free up disk space in Windows 11 safely", guide)
        self.assertIn("Start &gt; Settings &gt; System &gt; Storage", guide)
        self.assertIn("Don’t delete WinSxS manually", guide)
        self.assertIn("support.microsoft.com", guide)
        self.assertIn("learn.microsoft.com", guide)
        self.assertIn("docs.google.com/forms/", guide)
        self.assertNotIn("/ResetBase", guide)
        self.assertNotIn("<script src=", guide)

    def test_c_drive_diagnostic_is_grounded_discoverable_and_converts(self):
        self.assertTrue(DIAGNOSTIC.exists())
        diagnostic = DIAGNOSTIC.read_text(encoding="utf-8")
        self.assertIn("Why is my C drive full in Windows 11?", diagnostic)
        self.assertIn('"@type": "FAQPage"', diagnostic)
        self.assertIn("System &amp; reserved", diagnostic)
        self.assertIn("support.microsoft.com", diagnostic)
        self.assertIn("docs.google.com/forms/", diagnostic)
        self.assertIn("No Google account required", diagnostic)
        self.assertIn('href="#diagnose"', diagnostic)
        self.assertIn("Start the 5-minute diagnosis", diagnostic)
        self.assertNotIn("/ResetBase", diagnostic)
        self.assertNotIn("<script src=", diagnostic)
        self.assertIn('href="c-drive-full-windows-11.html"', self.html)
        self.assertIn('href="c-drive-full-windows-11.html"', GUIDE.read_text(encoding="utf-8"))
        self.assertIn("c-drive-full-windows-11.html", SITEMAP.read_text(encoding="utf-8"))

    def test_private_cleanup_planner_is_linked_and_has_no_network_code(self):
        self.assertTrue(PLANNER.exists())
        self.assertTrue(PLANNER_JS.exists())
        planner = PLANNER.read_text(encoding="utf-8")
        script = PLANNER_JS.read_text(encoding="utf-8")
        self.assertIn("Plan without scanning your files", planner)
        self.assertIn("Nothing you enter leaves this browser", planner)
        self.assertIn('src="planner.js"', planner)
        self.assertIn('href="storage-cleanup-planner.html"', self.html)
        self.assertIn('href="storage-cleanup-planner.html"', GUIDE.read_text(encoding="utf-8"))
        self.assertIn("storage-cleanup-planner.html", SITEMAP.read_text(encoding="utf-8"))
        for forbidden in ("fetch(", "xmlhttprequest", "sendbeacon", "websocket", "localstorage"):
            self.assertNotIn(forbidden, script.lower())

    def test_cleanup_plan_totals_selected_candidates(self):
        result = self.run_planner({
            "currentFree": 12,
            "goalFree": 30,
            "candidates": [
                {"id": "temporary", "label": "Temporary files", "gb": 8, "selected": True, "risk": "low"},
                {"id": "downloads", "label": "Downloads", "gb": 15, "selected": True, "risk": "review"},
                {"id": "apps", "label": "Unused apps", "gb": 10, "selected": False, "risk": "review"},
            ],
        })
        self.assertEqual(result["selectedTotal"], 23)
        self.assertEqual(result["projectedFree"], 35)
        self.assertEqual(result["remainingGap"], 0)
        self.assertTrue(result["goalMet"])

    def test_cleanup_plan_normalizes_invalid_and_negative_numbers(self):
        result = self.run_planner({
            "currentFree": -4,
            "goalFree": "not-a-number",
            "candidates": [
                {"id": "temporary", "label": "Temporary files", "gb": -2, "selected": True, "risk": "low"},
            ],
        })
        self.assertEqual(result["currentFree"], 0)
        self.assertEqual(result["goalFree"], 0)
        self.assertEqual(result["selectedTotal"], 0)
        self.assertTrue(result["goalMet"])

    @staticmethod
    def run_planner(payload):
        program = (
            "const {calculatePlan}=require('./planner.js');"
            f"console.log(JSON.stringify(calculatePlan({json.dumps(payload)})));"
        )
        completed = subprocess.run(
            ["node", "-e", program],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(completed.stdout)

    def test_search_and_social_metadata_are_complete(self):
        canonical = "https://dafyaman.github.io/reclaimguide-preview/"
        self.assertIn(f'<link rel="canonical" href="{canonical}">', self.html)
        self.assertIn('<meta property="og:title"', self.html)
        self.assertIn(f'<meta property="og:url" content="{canonical}">', self.html)
        self.assertIn('<meta name="twitter:card" content="summary">', self.html)
        self.assertIn('"@type": "WebSite"', self.html)

    def test_crawlers_have_a_valid_sitemap(self):
        self.assertTrue(ROBOTS.exists())
        self.assertTrue(SITEMAP.exists())
        robots = ROBOTS.read_text(encoding="utf-8")
        sitemap = SITEMAP.read_text(encoding="utf-8")
        self.assertIn("User-agent: *", robots)
        self.assertIn("Allow: /", robots)
        self.assertIn("Sitemap: https://dafyaman.github.io/reclaimguide-preview/sitemap.xml", robots)
        self.assertIn("https://dafyaman.github.io/reclaimguide-preview/", sitemap)
        self.assertIn("https://dafyaman.github.io/reclaimguide-preview/privacy.html", sitemap)
        self.assertIn("https://dafyaman.github.io/reclaimguide-preview/windows-storage-guide.html", sitemap)
        self.assertIn("https://dafyaman.github.io/reclaimguide-preview/storage-cleanup-planner.html", sitemap)
        self.assertIn("https://dafyaman.github.io/reclaimguide-preview/c-drive-full-windows-11.html", sitemap)
        self.assertEqual(INDEXNOW_KEY.read_text(encoding="utf-8").strip(), INDEXNOW_KEY.stem)


if __name__ == "__main__":
    unittest.main()
