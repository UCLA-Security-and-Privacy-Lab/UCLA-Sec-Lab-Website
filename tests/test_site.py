"""Site tests: build the Hugo site under the production subpath and check the rendered pages.

Run from the repository root:
    python3 -m unittest -v tests.test_site              # everything
    python3 -m unittest -v tests.test_site.ThemeTest    # one group
"""
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sitetest as st  # noqa: E402


class ThemeTest(unittest.TestCase):
    def test_build_has_no_warnings_or_errors(self):
        log = st.build_log()
        self.assertNotRegex(log, r"(?m)^(WARN|ERROR)", log)

    def test_plus_jakarta_sans_is_loaded(self):
        hrefs = [link.attrs.get("href", "") for link in st.page("").find_all("link")]
        self.assertTrue(any("fonts.googleapis.com" in h and "Plus+Jakarta+Sans" in h for h in hrefs), hrefs)

    def test_lab_theme_colours_reach_the_css(self):
        css = st.css_compact()
        self.assertIn("plusjakartasans", css)
        self.assertIn("#3c58ad", css)

    def test_site_is_named_bruinsec_lab(self):
        home = st.page("")
        self.assertEqual(home.find("title").text(), "BruinSec Lab")
        self.assertEqual(home.find("a", cls="navbar-brand").text(), "BruinSec Lab")

    def test_ucla_brand_packs_are_gone(self):
        for rel in ("data/themes/ucla.toml", "data/fonts/ucla.toml"):
            self.assertFalse(os.path.exists(os.path.join(st.ROOT, rel)), rel)


if __name__ == "__main__":
    unittest.main()
