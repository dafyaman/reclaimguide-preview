from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
PRIVACY = ROOT / "privacy.html"


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
        self.assertNotIn("<link rel=", self.html)
        self.assertTrue(PRIVACY.exists())


if __name__ == "__main__":
    unittest.main()
