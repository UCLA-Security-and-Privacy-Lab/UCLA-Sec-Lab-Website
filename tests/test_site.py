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


class ShellTest(unittest.TestCase):
    def test_body_is_the_light_canvas(self):
        self.assertIn("background:#f7f7f5", st.css_rules("body"))

    def test_every_page_body_is_one_white_card(self):
        rules = st.css_rules(".page-body")
        for decl in ("width:calc(100%-32px)", "max-width:1180px", "border:1pxsolid#d8d8d2", "border-radius:10px", "overflow:hidden"):
            self.assertIn(decl, rules)
        self.assertRegex(rules, r"background:#fff(fff)?[;}]?")

    def test_card_goes_edge_to_edge_on_phones(self):
        rules = st.css_rules(".page-body", media="(max-width: 767.98px)")
        self.assertIn("border-radius:0", rules)
        self.assertIn("width:100%", rules)

    def test_sections_are_divided_by_lines(self):
        self.assertIn("border-top:1pxsolid#d8d8d2", st.css_rules(".page-body .home-section + .home-section"))

    def test_navbar_matches_kwchang(self):
        self.assertIn("background:#3c58ad!important", st.css_rules(".navbar"))
        link = st.css_rules(".navbar .nav-link")
        for decl in ("text-transform:uppercase", "font-weight:800", "font-size:13px"):
            self.assertIn(decl, link)
        self.assertRegex(link, r"letter-spacing:0?\.6px")
        self.assertIn("color:#f2be42!important", st.css_rules(".navbar .nav-link:hover"))

    def test_current_page_gets_a_gold_underline_not_gold_text(self):
        self.assertIn("border-bottom:3pxsolid#f2be42", st.css_rules(".navbar .nav-link.active span"))

    def test_detail_pages_mark_their_section_in_the_navbar(self):
        nav = st.page("publication/2026-oakland/").find("ul", cls="navbar-nav")
        self.assertEqual([a.text() for a in nav.find_all("a", cls="active")], ["PUBLICATIONS"])

    def test_shared_components(self):
        self.assertIn("background:#1f65ab", st.css_rules(".action-pill.primary"))
        label = st.css_rules(".section-label")
        self.assertIn("text-transform:uppercase", label)
        self.assertRegex(label, r"letter-spacing:0?\.08em")
        self.assertIn("background:#e7f1ff", st.css_rules(".chip"))
        self.assertIn("border-bottom:1pxsolid#d8d8d2", st.css_rules(".highlight-list a"))

    def test_previous_ucla_rules_are_gone(self):
        self.assertNotIn("ucla-hero", st.css_compact())


class LogoTest(unittest.TestCase):
    SVG = os.path.join(st.ROOT, "static", "media", "logo-bruinsec.svg")

    def test_logo_is_the_hooded_bear_with_shades(self):
        with open(self.SVG, encoding="utf-8") as fh:
            svg = fh.read()
        self.assertIn('viewBox="150 68 300 300"', svg)
        self.assertIn("<!-- sunglasses -->", svg)
        self.assertNotIn("var(", svg)

    def test_icons_are_512px_rgba_pngs(self):
        for rel in ("assets/media/icon.png", "static/media/icon.png"):
            self.assertEqual(st.png_info(os.path.join(st.ROOT, rel)), (512, 512, 6), rel)

    def test_navbar_logo_uses_a_relative_url(self):
        rules = st.css_rules(".navbar .navbar-brand::before") + st.css_rules(".navbar .navbar-brand:before")
        self.assertRegex(rules, r"url\(['\"]?\.\./media/logo-bruinsec\.svg")
        self.assertTrue(os.path.isfile(os.path.join(st.public_dir(), "media", "logo-bruinsec.svg")))

    def test_favicon_links_resolve(self):
        icons = [link.attrs["href"] for link in st.page("").find_all("link") if "icon" in link.attrs.get("rel", "")]
        self.assertTrue(icons)
        for href in icons:
            self.assertTrue(st.resolves(href), href)


if __name__ == "__main__":
    unittest.main()
