from pathlib import Path
import json
import struct
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
PRIVACY = ROOT / "privacy.html"
GUIDE = ROOT / "windows-storage-guide.html"
DIAGNOSTIC = ROOT / "c-drive-full-windows-11.html"
SYSTEM_RESERVED = ROOT / "system-reserved-storage-windows-11.html"
MULTI_DRIVE = ROOT / "manage-storage-across-multiple-drives-windows-11.html"
RESOURCES = ROOT / "windows-storage-resources.html"
PLANNER = ROOT / "storage-cleanup-planner.html"
PLANNER_JS = ROOT / "planner.js"
ROBOTS = ROOT / "robots.txt"
SITEMAP = ROOT / "sitemap.xml"
TEXT_SITEMAP = ROOT / "sitemap.txt"
INDEXNOW_KEY = ROOT / "a85fc997b5115fc41d90d561e830427c.txt"
README = ROOT / "README.md"
SOCIAL_IMAGE = ROOT / "assets" / "reclaimguide-social.png"


class PublicPreviewTests(unittest.TestCase):
    def setUp(self):
        self.html = INDEX.read_text(encoding="utf-8")

    def test_preview_has_product_and_validation_price(self):
        self.assertIn("ReclaimGuide", self.html)
        self.assertIn("$19.99", self.html)
        self.assertIn("Early validation", self.html)

    def test_readme_matches_current_public_validation_flow(self):
        readme = README.read_text(encoding="utf-8")
        self.assertIn("https://dafyaman.github.io/reclaimguide-preview/", readme)
        self.assertIn("docs.google.com/forms/", readme)
        self.assertIn("storage-cleanup-planner.html", readme)
        self.assertIn("system-reserved-storage-windows-11.html", readme)
        self.assertIn("$19.99", readme)
        self.assertIn("Email is optional", readme)
        self.assertIn("Product source and binaries are not published", readme)
        self.assertNotIn("repository's public `waitlist` issue form", readme)

    def test_waitlist_uses_account_free_google_form_on_all_conversion_pages(self):
        form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdKrVo85XaOiukX-vTF9yFcdGb92oEZhBRwqqOPdLT9HSV5vg/viewform"
        guide = GUIDE.read_text(encoding="utf-8")
        planner = PLANNER.read_text(encoding="utf-8")
        diagnostic = DIAGNOSTIC.read_text(encoding="utf-8")
        multi_drive = MULTI_DRIVE.read_text(encoding="utf-8")
        for page in (self.html, guide, planner, diagnostic, multi_drive):
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
        self.assertIn("Disk cleanup in Windows 11: free up space safely", guide)
        self.assertIn("Search for Disk Cleanup", guide)
        self.assertIn("Clean up system files", guide)
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

    def test_system_reserved_guide_is_safe_grounded_and_discoverable(self):
        self.assertTrue(SYSTEM_RESERVED.exists())
        page = SYSTEM_RESERVED.read_text(encoding="utf-8")
        self.assertIn("System &amp; reserved storage too large in Windows 11?", page)
        self.assertIn('"@type": "FAQPage"', page)
        self.assertIn("Never delete WinSxS manually", page)
        self.assertIn("Reviewed against current Microsoft", page)
        self.assertIn("Show more categories &gt; System &amp; reserved", page)
        self.assertIn("support.microsoft.com", page)
        self.assertIn("learn.microsoft.com", page)
        self.assertIn("Share 30-second feedback", page)
        self.assertIn("No Google account required", page)
        self.assertNotIn("/ResetBase", page)
        self.assertNotIn("<script src=", page)
        self.assertIn('href="system-reserved-storage-windows-11.html"', GUIDE.read_text(encoding="utf-8"))
        self.assertIn('href="system-reserved-storage-windows-11.html"', DIAGNOSTIC.read_text(encoding="utf-8"))
        self.assertIn("system-reserved-storage-windows-11.html", SITEMAP.read_text(encoding="utf-8"))

    def test_storage_resource_hub_routes_visitors_without_tracking(self):
        self.assertTrue(RESOURCES.exists())
        page = RESOURCES.read_text(encoding="utf-8")
        self.assertIn("Windows storage help, without risky shortcuts.", page)
        self.assertIn("I need a safe Windows 11 disk cleanup sequence", page)
        self.assertIn('"@type": "CollectionPage"', page)
        for target in (
            "storage-cleanup-planner.html",
            "windows-storage-guide.html",
            "c-drive-full-windows-11.html",
            "system-reserved-storage-windows-11.html",
            "manage-storage-across-multiple-drives-windows-11.html",
        ):
            self.assertIn(f'href="{target}"', page)
        self.assertIn("Share 30-second feedback", page)
        self.assertIn("No Google account required", page)
        self.assertIn("@media(max-height:700px) and (min-width:761px)", page)
        self.assertIn(">About ReclaimGuide →</a>", page)
        self.assertNotIn("<script src=", page)
        self.assertNotIn("google-analytics", page.lower())
        self.assertIn('href="windows-storage-resources.html"', self.html)
        self.assertIn("windows-storage-resources.html", SITEMAP.read_text(encoding="utf-8"))

    def test_multi_drive_guide_is_grounded_safe_and_converts(self):
        self.assertTrue(MULTI_DRIVE.exists())
        page = MULTI_DRIVE.read_text(encoding="utf-8")
        self.assertIn("How to manage storage across multiple drives in Windows 11", page)
        self.assertIn('"@type": "FAQPage"', page)
        self.assertIn("Storage used on other drives", page)
        self.assertIn("Where new content is saved", page)
        self.assertIn("Storage Spaces is not a backup", page)
        self.assertIn("support.microsoft.com", page)
        self.assertIn("Share 30-second feedback", page)
        self.assertIn("No Google account required", page)
        self.assertIn("read-only scan across connected drives", page)
        self.assertIn("not available yet", page)
        self.assertNotIn("<script src=", page)
        self.assertIn('href="manage-storage-across-multiple-drives-windows-11.html"', RESOURCES.read_text(encoding="utf-8"))
        self.assertIn("manage-storage-across-multiple-drives-windows-11.html", SITEMAP.read_text(encoding="utf-8"))

    def test_private_cleanup_planner_is_linked_and_has_no_network_code(self):
        self.assertTrue(PLANNER.exists())
        self.assertTrue(PLANNER_JS.exists())
        planner = PLANNER.read_text(encoding="utf-8")
        script = PLANNER_JS.read_text(encoding="utf-8")
        self.assertIn("Plan without scanning your files", planner)
        self.assertIn("Nothing you enter leaves this browser", planner)
        self.assertIn("This free page is manual", planner)
        self.assertIn("Proposed desktop utility", planner)
        self.assertIn("read-only scan across connected drives", planner)
        self.assertIn("Nothing would move or be deleted without approval", planner)
        self.assertIn("Approval before any file change · Not available yet", planner)
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

    def test_planner_example_reaches_a_clear_result_without_scanning(self):
        planner = PLANNER.read_text(encoding="utf-8")
        self.assertIn('id="load-example"', planner)
        self.assertIn("Try an example", planner)
        self.assertIn("Illustrative values, not a scan", planner)
        program = (
            "const {calculatePlan,examplePlanInput}=require('./planner.js');"
            "console.log(JSON.stringify(calculatePlan(examplePlanInput())));"
        )
        completed = subprocess.run(
            ["node", "-e", program],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)
        self.assertEqual(result["currentFree"], 12)
        self.assertEqual(result["goalFree"], 25)
        self.assertEqual(result["selectedTotal"], 15)
        self.assertEqual(result["projectedFree"], 27)
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
        self.assertIn('<meta name="google-site-verification" content="NN1EcZMzpcxZ8jLUTJqOLclGGfI9jhAWv80HqWLLD_w">', self.html)
        self.assertIn('<meta property="og:title"', self.html)
        self.assertIn(f'<meta property="og:url" content="{canonical}">', self.html)
        self.assertIn('<meta name="twitter:card" content="summary_large_image">', self.html)
        self.assertIn('"@type": "WebSite"', self.html)

    def test_conversion_pages_share_a_valid_social_preview_image(self):
        image_url = "https://dafyaman.github.io/reclaimguide-preview/assets/reclaimguide-social.png"
        payload = SOCIAL_IMAGE.read_bytes()
        self.assertEqual(payload[:8], b"\x89PNG\r\n\x1a\n")
        width, height = struct.unpack(">II", payload[16:24])
        self.assertEqual((width, height), (1200, 630))
        for path in (INDEX, GUIDE, DIAGNOSTIC, SYSTEM_RESERVED, MULTI_DRIVE, PLANNER, RESOURCES):
            page = path.read_text(encoding="utf-8")
            self.assertIn(f'<meta property="og:image" content="{image_url}">', page)
            self.assertIn('<meta property="og:image:width" content="1200">', page)
            self.assertIn('<meta property="og:image:height" content="630">', page)
            self.assertIn('<meta name="twitter:card" content="summary_large_image">', page)
            self.assertIn(f'<meta name="twitter:image" content="{image_url}">', page)

    def test_crawlers_have_a_valid_sitemap(self):
        self.assertTrue(ROBOTS.exists())
        self.assertTrue(SITEMAP.exists())
        self.assertTrue(TEXT_SITEMAP.exists())
        robots = ROBOTS.read_text(encoding="utf-8")
        sitemap = SITEMAP.read_text(encoding="utf-8")
        text_sitemap = TEXT_SITEMAP.read_text(encoding="utf-8")
        self.assertIn("User-agent: *", robots)
        self.assertIn("Allow: /", robots)
        self.assertIn("Sitemap: https://dafyaman.github.io/reclaimguide-preview/sitemap.xml", robots)
        self.assertIn("Sitemap: https://dafyaman.github.io/reclaimguide-preview/sitemap.txt", robots)
        self.assertIn("https://dafyaman.github.io/reclaimguide-preview/", sitemap)
        self.assertIn("https://dafyaman.github.io/reclaimguide-preview/privacy.html", sitemap)
        self.assertIn("https://dafyaman.github.io/reclaimguide-preview/windows-storage-guide.html", sitemap)
        self.assertIn("https://dafyaman.github.io/reclaimguide-preview/storage-cleanup-planner.html", sitemap)
        self.assertIn("https://dafyaman.github.io/reclaimguide-preview/c-drive-full-windows-11.html", sitemap)
        self.assertIn("https://dafyaman.github.io/reclaimguide-preview/system-reserved-storage-windows-11.html", sitemap)
        self.assertIn("https://dafyaman.github.io/reclaimguide-preview/windows-storage-resources.html", sitemap)
        self.assertIn("https://dafyaman.github.io/reclaimguide-preview/manage-storage-across-multiple-drives-windows-11.html", sitemap)
        self.assertIn("https://dafyaman.github.io/reclaimguide-preview/", text_sitemap)
        self.assertIn("https://dafyaman.github.io/reclaimguide-preview/manage-storage-across-multiple-drives-windows-11.html", text_sitemap)
        self.assertEqual(len([line for line in text_sitemap.splitlines() if line]), 8)
        self.assertEqual(INDEXNOW_KEY.read_text(encoding="utf-8").strip(), INDEXNOW_KEY.stem)


if __name__ == "__main__":
    unittest.main()
