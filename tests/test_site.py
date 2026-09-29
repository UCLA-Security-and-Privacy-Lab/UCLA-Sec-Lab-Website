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


ELSEWHERE = [
    "https://www.ytian.info/",
    "https://scholar.google.com/citations?user=ja0GtqgAAAAJ",
    "https://www.ee.ucla.edu/",
    "https://www.cs.ucla.edu/",
    "https://github.com/UCLA-Security-and-Privacy-Lab",
]


class FooterTest(unittest.TestCase):
    def setUp(self):
        self.footer = st.page("").find("footer")

    def test_has_lab_and_elsewhere_columns(self):
        self.assertIsNotNone(self.footer.find(cls="lab-footer-grid"))
        self.assertEqual([p.text() for p in self.footer.find_all("p", cls="lab-footer-label")], ["Lab", "Elsewhere"])

    def test_brand_shows_logo_and_name(self):
        brand = self.footer.find("a", cls="lab-footer-brand")
        self.assertEqual(brand.text(), "BruinSec Lab")
        self.assertTrue(st.resolves(brand.attrs["href"]), brand.attrs["href"])
        self.assertTrue(st.resolves(brand.find("img").attrs["src"]), brand.find("img").attrs["src"])

    def test_lab_column_lists_the_main_menu(self):
        links = self.footer.find_all("nav", cls="lab-footer-col")[0].find_all("a")
        self.assertEqual([a.text() for a in links], ["Research", "News", "People", "Publications", "Awards", "Join Us"])
        for a in links:
            self.assertTrue(st.resolves(a.attrs["href"]), a.attrs["href"])

    def test_elsewhere_links_open_in_a_new_tab(self):
        links = self.footer.find_all("nav", cls="lab-footer-col")[1].find_all("a")
        self.assertEqual([a.attrs["href"] for a in links], ELSEWHERE)
        for a in links:
            self.assertEqual((a.attrs.get("target"), a.attrs.get("rel")), ("_blank", "noopener"))

    def test_copyright_without_hugo_blox_credit(self):
        text = self.footer.text()
        self.assertRegex(text, r"© \d{4} BruinSec Lab\. This work is licensed under CC BY NC ND 4\.0")
        self.assertNotIn("Hugo Blox", text)

    def test_footer_is_kwchang_blue_and_stacks_on_phones(self):
        self.assertIn("background:#1f65ab", st.css_rules(".page-footer"))
        self.assertIn("grid-template-columns:1fr", st.css_rules(".lab-footer-grid", media="(max-width: 767.98px)"))


class MarkdownLinkTest(unittest.TestCase):
    def test_research_page_detail_links_work_under_the_subpath(self):
        links = [a for a in st.page("research/").find_all("a") if "Details" in a.text()]
        self.assertGreaterEqual(len(links), 29)
        for a in links:
            self.assertTrue(st.resolves(a.attrs["href"]), a.attrs["href"])

    def test_external_markdown_links_still_open_in_a_new_tab(self):
        a = [a for a in st.page("publication/2019-oauthlint/").find_all("a")
             if a.attrs.get("href", "").startswith("https://docs.hugoblox.com/")][0]
        self.assertEqual((a.attrs.get("target"), a.attrs.get("rel")), ("_blank", "noopener"))


class HomeHeroTest(unittest.TestCase):
    def setUp(self):
        self.hero = st.page("").find(cls="lab-hero")

    def test_lab_name_roles_and_summary(self):
        self.assertEqual(self.hero.find("h1").text(), "BruinSec Lab")
        self.assertEqual([p.text() for p in self.hero.find_all("p", cls="lab-hero-role")],
                         ["Electrical and Computer Engineering · Computer Science", "University of California, Los Angeles"])
        self.assertIn("led by Prof. Yuan Tian at UCLA", self.hero.find("p", cls="lab-hero-summary").text())

    def test_buttons(self):
        pills = self.hero.find_all("a", cls="action-pill")
        self.assertEqual([a.text() for a in pills], ["Research", "Publications", "People", "News", "Join Us"])
        self.assertEqual([a.text() for a in pills if "primary" in a.classes], ["Research"])
        for a in pills:
            self.assertTrue(st.resolves(a.attrs["href"]), a.attrs["href"])

    def test_pi_card(self):
        card = self.hero.find(cls="lab-pi-card")
        img = card.find("img")
        self.assertTrue(st.resolves(img.attrs["src"]), img.attrs["src"])
        self.assertEqual(card.find("p", cls="lab-pi-name").text(), "Yuan Tian")
        links = {a.text(): a.attrs for a in card.find_all("a")}
        self.assertEqual(links["Email"]["href"], "mailto:yuant@ucla.edu")
        self.assertEqual(links["Homepage"]["href"], "https://www.ytian.info/")
        self.assertEqual(links["Scholar"]["href"], "https://scholar.google.com/citations?user=ja0GtqgAAAAJ")
        self.assertEqual(links["Homepage"].get("target"), "_blank")

    def test_hero_grid_stacks_on_tablets(self):
        self.assertIn("grid-template-columns:minmax(0,1fr)190px", st.css_rules(".lab-hero"))
        self.assertIn("grid-template-columns:1fr", st.css_rules(".lab-hero", media="(max-width: 991.98px)"))


class HomeNewsTest(unittest.TestCase):
    def setUp(self):
        self.news = st.page("").find(cls="lab-news")

    def test_shows_the_five_newest_posts(self):
        items = self.news.find_all("li", cls="lab-news-item")
        self.assertEqual([li.find("a").text() for li in items], st.newest_post_titles(5))

    def test_dates_are_capitalised_month_and_year(self):
        for li in self.news.find_all("li", cls="lab-news-item"):
            self.assertRegex(li.find(cls="lab-news-date").text(), r"^[A-Z]{3} \d{4}$")

    def test_links_resolve(self):
        for a in self.news.find_all("a"):
            self.assertTrue(st.resolves(a.attrs["href"]), a.attrs["href"])

    def test_long_titles_wrap_and_phones_stack_the_date(self):
        self.assertIn("overflow-wrap:anywhere", st.css_rules(".lab-news-item p"))
        self.assertIn("grid-template-columns:1fr", st.css_rules(".lab-news-item", media="(max-width: 767.98px)"))


class LabUrlTest(unittest.TestCase):
    def test_unknown_site_path_fails_the_build(self):
        code, log = st.build_variant("content/_index.md", "url: people/", "url: peeple/")
        self.assertNotEqual(code, 0, log)
        self.assertIn('"peeple/" does not match any page', log)


EXPECTED_CHIPS = {
    "AI Security": ["EIA (ICLR '25)", "BadMerging (CCS '24)", "Chimera (USENIX Sec '25)",
                    "SoK: Vulnerability Repair (USENIX Sec '25)", "Poisoning Attacks (ICML '21)"],
    "Data Privacy": ["GDPR Consent (S&P '26)", "Smart Home IFA (PETS '26)", "City-wide WiFi (PETS '25)",
                     "CHKPLUG (NDSS '23)", "SenRev (PETS '23)"],
    "System Security": ["XR Threats (NDSS '26)", "Waltzz (USENIX Sec '25)", "AuthSaber (CCS '24)",
                        "Alexa Skill Vetting (ICSE '24)", "TKPERM (NDSS '20)"],
}


class HomeMainTest(unittest.TestCase):
    def setUp(self):
        self.main = st.page("").find(cls="lab-main")

    def section(self, label):
        return [s for s in self.main.find_all("section", cls="lab-section")
                if s.find("p", cls="section-label").text() == label][0]

    def test_sections_in_order(self):
        labels = [s.find("p", cls="section-label").text() for s in self.main.find_all("section", cls="lab-section")]
        self.assertEqual(labels, ["Research at a glance", "What we are building", "Highlighted papers"])

    def test_research_areas_and_chips(self):
        items = self.section("Research at a glance").find_all(cls="project-item")
        got = {i.find("h3").text(): [a.text() for a in i.find_all("a", cls="chip")] for i in items}
        self.assertEqual(got, EXPECTED_CHIPS)
        for i in items:
            for a in i.find_all("a", cls="chip"):
                self.assertTrue(a.attrs["href"].startswith(st.BASE_PATH + "publication/"), a.attrs["href"])
                self.assertTrue(st.resolves(a.attrs["href"]), a.attrs["href"])

    def test_project_cards(self):
        cards = self.section("What we are building").find_all("article", cls="lab-project")
        self.assertEqual([c.find("h3").text() for c in cards], ["Bruinweb", "Trustworthy AI Agents", "Trustworthy Medical AI"])
        for c in cards:
            self.assertEqual(c.find(cls="chip-status").text(), "Active")
            self.assertEqual(len(c.find_all(cls="chip-topic")), 2)
            for a in c.find_all("a"):
                self.assertTrue(st.resolves(a.attrs["href"]), a.attrs["href"])

    def test_highlighted_papers(self):
        links = self.section("Highlighted papers").find_all("a")
        self.assertEqual([a.find("span").text() for a in links],
                         ["IEEE S&P 2026", "NDSS 2026", "ACM CCS 2024", "ACM CCS 2024", "USENIX Security 2025", "ICLR 2025"])
        for a in links:
            self.assertTrue(st.resolves(a.attrs["href"]), a.attrs["href"])

    def test_research_items_reset_the_theme_portfolio_margin(self):
        # Hugo Blox styles its own `.project-item` with margin-bottom:1.5rem; ours must win.
        margins = [d for d in st.css_rules(".project-item").split(";") if d.startswith("margin")]
        self.assertEqual(margins[-1], "margin:0")

    def test_two_column_grid_stacks_on_tablets(self):
        self.assertIn("grid-template-columns:minmax(0,1fr)250px", st.css_rules(".lab-grid"))
        self.assertIn("grid-template-columns:1fr", st.css_rules(".lab-grid", media="(max-width: 991.98px)"))


class HomeSideTest(unittest.TestCase):
    def setUp(self):
        self.side = st.page("").find(cls="lab-side")

    def test_sections_in_order(self):
        labels = [s.find("p", cls="section-label").text() for s in self.side.find_all("section", cls="side-card")]
        self.assertEqual(labels, ["Impact", "Funding & support", "Join the lab"])

    def test_impact_tiles(self):
        tiles = self.side.find_all("a", cls="impact-card")
        self.assertEqual([(t.find(cls="impact-value").text(), t.find("p").text()) for t in tiles], [
            ("2020", "NSF CAREER Award"),
            ("2021", "Google Research Scholar Award"),
            ("2022", "Okawa Foundation Award"),
            ("4", "platforms (Android, Chrome, Firefox, iOS) adopted fixes from our research"),
        ])
        for t in tiles:
            self.assertTrue(st.resolves(t.attrs["href"]), t.attrs["href"])

    def test_funding_list(self):
        names = [li.text() for li in self.side.find("ul", cls="award-list").find_all("li")]
        self.assertEqual(names, ["NSF", "Google", "Amazon", "Meta", "Cisco", "Keysight", "Okawa Foundation", "Coefficient Giving"])

    def test_join_callout(self):
        card = self.side.find(cls="callout-card")
        self.assertIn("PhD students, postdocs, and research interns", card.text())
        button = card.find("a", cls="inline-link")
        self.assertEqual(button.text(), "View opportunities")
        self.assertTrue(st.resolves(button.attrs["href"]), button.attrs["href"])


class HomeLinksTest(unittest.TestCase):
    def test_every_internal_link_and_image_on_the_homepage_resolves(self):
        body = st.page("").find("body")
        broken = []
        for node in body.find_all():
            for attr in ("href", "src"):
                value = node.attrs.get(attr, "")
                internal = (value.startswith("/") and not value.startswith("//")) or value.startswith(st.BASE_URL)
                if internal and not st.resolves(value):
                    broken.append(value)
        self.assertEqual(broken, [])


class ResearchPageTest(unittest.TestCase):
    def setUp(self):
        self.page = st.page("research/")
        self.glance = self.page.find("section", cls="wg-research-glance")

    def test_overview_lists_three_areas_without_images(self):
        self.assertEqual(self.glance.find("h1").text(), "Research")
        self.assertEqual([h.text() for h in self.glance.find_all("h3")], ["AI Security", "Data Privacy", "System Security"])
        self.assertEqual(self.glance.find_all("img"), [])
        self.assertEqual(self.glance.find_all("a", cls="chip"), [])

    def test_area_links_jump_to_the_publication_lists(self):
        hrefs = [a.attrs["href"] for a in self.glance.find_all("a", cls="lab-more")]
        anchors = ["ai-security", "data-privacy", "system-security"]
        self.assertEqual(hrefs, [st.BASE_PATH + "research/#" + a for a in anchors])
        ids = [h.attrs.get("id") for h in self.page.find_all("h2", cls="research-area-heading")]
        self.assertEqual(ids, anchors)

    def test_old_icon_cards_are_gone(self):
        self.assertIsNone(self.page.find(cls="research-cards"))


class PeopleTest(unittest.TestCase):
    def setUp(self):
        self.page = st.page("people/")

    def grid_items(self):
        return {li.find(cls="people-compact-name").text(): li for li in self.page.find_all("li", cls="people-compact-item")}

    def test_students_and_interns_use_the_compact_grid(self):
        items = self.grid_items()
        for name in ("Ying Li", "Kunlin Cai", "Peiran Wang", "Sean Tang"):
            self.assertIn(name, items)
        for grid in self.page.find_all("ul", cls="people-compact-grid"):
            self.assertEqual(grid.find_all("img"), [])

    def test_faculty_and_postdocs_keep_photo_cards(self):
        cards = {c.find("h2").text(): c for c in self.page.find_all(cls="people-person")}
        self.assertEqual(set(cards), {"Yuan Tian", "Zihang Xiang"})
        for card in cards.values():
            self.assertIsNotNone(card.find("img"))

    def test_external_homepages_open_in_a_new_tab(self):
        a = self.grid_items()["Kunlin Cai"].find("a")
        self.assertEqual(a.attrs["href"], "https://kunlin-cai.com/")
        self.assertEqual((a.attrs.get("target"), a.attrs.get("rel")), ("_blank", "noopener"))

    def test_profile_links_stay_on_site(self):
        a = self.grid_items()["Zhiyuan Zhang"].find("a")  # no external_link in his profile
        self.assertTrue(st.resolves(a.attrs["href"]), a.attrs["href"])
        self.assertIsNone(a.attrs.get("target"))

    def test_pi_social_links_are_real(self):
        card = [c for c in self.page.find_all(cls="people-person") if c.find("h2").text() == "Yuan Tian"][0]
        hrefs = [a.attrs.get("href", "") for a in card.find_all("a")]
        self.assertIn("mailto:yuant@ucla.edu", hrefs)
        self.assertIn("https://scholar.google.com/citations?user=ja0GtqgAAAAJ", hrefs)
        for placeholder in ("test@example.org", "GeorgeCushen", "gcushen", "sIwtMXoAAAAJ"):
            self.assertNotIn(placeholder, " ".join(hrefs))

    def test_people_page_lines_up_with_the_page_title(self):
        # Hugo Blox centres .people-widget and pulls its row out by the column gutter; the photo cards are the
        # columns themselves, so drop the gutter and left-align everything, as on kwchang's and PASTA's pages.
        aligns = [d for d in st.css_rules(".people-widget").split(";") if d.startswith("text-align")]
        self.assertEqual(aligns[-1], "text-align:left")
        self.assertIn("margin-left:0", st.css_rules(".people-widget.row"))
        self.assertIn("padding-left:0", st.css_rules(".people-widget > .col-md-12"))

    def test_compact_grid_narrows_on_phones(self):
        self.assertIn("grid-template-columns:repeat(4,minmax(0,1fr))", st.css_rules(".people-compact-grid"))
        self.assertIn("grid-template-columns:repeat(2,minmax(0,1fr))",
                      st.css_rules(".people-compact-grid", media="(max-width: 767.98px)"))


class ListPagesTest(unittest.TestCase):
    def test_publication_rows_hide_thumbnails_and_keep_authors_under_the_title(self):
        self.assertIn("display:none", st.css_rules("#container-publications .view-compact .ml-3"))
        self.assertIn("order:0", st.css_rules("#container-publications .view-compact .stream-meta"))

    def test_news_rows_put_the_date_first_without_reading_time(self):
        self.assertIn("order:-1", st.css_rules(".view-compact .stream-meta"))
        self.assertIn("display:none", st.css_rules(".view-compact .article-reading-time"))

    def test_publication_list_still_lists_every_paper(self):
        folder = os.path.join(st.ROOT, "content", "publication")
        papers = [d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))]
        self.assertEqual(len(st.page("publication/").find_all(cls="view-compact")), len(papers))

    def test_list_pages_fill_the_card(self):
        # Hugo Blox fixes .universal-wrapper at width:1000px, centred; inside our 1180px card it must fill the card.
        widths = [d for d in st.css_rules(".page-body .universal-wrapper").split(";") if d.startswith("width")]
        self.assertEqual(widths, ["width:auto"])

    def test_publication_rows_line_up_with_the_title(self):
        # Each publication row is a Bootstrap column inside the isotope grid; drop its gutter.
        self.assertIn("padding-left:0", st.css_rules("#container-publications .isotope-item"))

    def test_list_page_links_work_under_the_subpath(self):
        for path in ("publication/", "post/"):
            for a in st.page(path).find(cls="page-body").find_all("a"):
                href = a.attrs.get("href", "")
                if href.startswith("/"):
                    self.assertTrue(st.resolves(href), (path, href))


if __name__ == "__main__":
    unittest.main()
