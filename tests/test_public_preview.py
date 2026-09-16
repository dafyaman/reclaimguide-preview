from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
PRIVACY = ROOT / "privacy.html"
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

    def test_waitlist_is_a_countable_github_issue_form(self):
        self.assertIn("https://github.com/dafyaman/reclaimguide-preview/issues/new?template=waitlist.yml", self.html)
        self.assertIn("Join the early-access list", self.html)
        template = (ROOT / ".github" / "ISSUE_TEMPLATE" / "waitlist.yml").read_text(encoding="utf-8")
        self.assertIn('labels: ["waitlist"]', template)
        self.assertIn("id: price", template)
        self.assertIn("id: consent", template)

    def test_waitlist_discloses_github_requirement(self):
        self.assertIn("GitHub account required", self.html)

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
        self.assertEqual(INDEXNOW_KEY.read_text(encoding="utf-8").strip(), INDEXNOW_KEY.stem)


if __name__ == "__main__":
    unittest.main()
