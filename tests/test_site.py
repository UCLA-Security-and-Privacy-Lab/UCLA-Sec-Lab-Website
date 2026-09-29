"""Site tests: build the Hugo site under the production subpath and check the rendered pages.

Run from the repository root:
    python3 -m unittest -v tests.test_site              # everything
    python3 -m unittest -v tests.test_site.ThemeTest    # one group
"""
import json
import os
import re
import shutil
import subprocess
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

    def test_navbar_is_compact(self):
        # kwchang's 90px bar looked too tall here: 64px on desktop, 56px on phones, 32px logo.
        rules = st.css_rules(".navbar")
        self.assertNotIn("min-height:90px", rules)
        self.assertIn("height:64px", rules)
        self.assertIn("height:56px", st.css_rules(".navbar", media="(max-width: 767.98px)"))
        logo = st.css_rules(".navbar .navbar-brand::before") + st.css_rules(".navbar .navbar-brand:before")
        self.assertIn("width:32px", logo)

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

    def test_footer_text_is_left_aligned(self):
        # Hugo Blox centres every `footer p`; the blurb and column labels must line up with the links.
        self.assertIn("text-align:left", st.css_rules(".lab-footer p"))

    def test_footer_is_kwchang_blue_and_stacks_on_phones(self):
        self.assertIn("background:#1f65ab", st.css_rules(".page-footer"))
        self.assertIn("grid-template-columns:1fr", st.css_rules(".lab-footer-grid", media="(max-width: 767.98px)"))


class MarkdownLinkTest(unittest.TestCase):
    def test_site_root_markdown_links_get_the_subpath(self):
        code, log, pages = st.build_variant(
            "content/contact/index.md",
            "We are always looking for motivated students",
            "See [all publications](/publication/). We are always looking for motivated students",
            pages=["contact/"])
        self.assertEqual(code, 0, log)
        link = [a for a in pages["contact/"].find_all("a") if a.text() == "all publications"][0]
        self.assertEqual(link.attrs["href"], st.BASE_PATH + "publication/")

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

    def test_summary_links_the_pi_homepage(self):
        link = self.hero.find("p", cls="lab-hero-summary").find("a")
        self.assertEqual(link.text(), "Prof. Yuan Tian")
        self.assertEqual(link.attrs["href"], "https://www.ytian.info/")

    def test_lab_illustration_instead_of_the_pi_portrait(self):
        self.assertIsNone(self.hero.find(cls="lab-pi-card"))
        imgs = self.hero.find_all("img")
        self.assertEqual(len(imgs), 1)
        img = self.hero.find(cls="lab-hero-art").find("img")
        self.assertIs(img, imgs[0])
        self.assertTrue(img.attrs["alt"].startswith("Anime illustration"), img.attrs["alt"])
        self.assertTrue(img.attrs["width"] and img.attrs["height"])
        self.assertTrue(st.resolves(img.attrs["src"]), img.attrs["src"])
        sources = [part.strip().split(" ") for part in img.attrs["srcset"].split(",")]
        self.assertEqual([w for _, w in sources], ["640w", "960w", "1536w"])
        for url, _ in sources:
            self.assertTrue(url.endswith(".webp") and st.resolves(url), url)

    def test_missing_illustration_fails_the_build(self):
        code, log = st.build_variant("content/_index.md", "media/lab-hero.jpg", "media/nope.jpg")
        self.assertNotEqual(code, 0)
        self.assertIn("media/nope.jpg", log)

    def test_hero_grid_stacks_on_tablets(self):
        self.assertIn("grid-template-columns:minmax(0,1fr)430px", st.css_rules(".lab-hero"))
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

    def test_hrefs_use_the_page_permalink_not_the_typed_path(self):
        # GitHub Pages is case-sensitive: a url typed with the folder's casing must still link to the real page.
        code, log, pages = st.build_variant("content/_index.md", "url: publication/2026-oakland/",
                                            "url: publication/2026-Oakland/", pages=[""])
        self.assertEqual(code, 0, log)
        chip = [a for a in pages[""].find_all("a", cls="chip") if a.text() == "GDPR Consent (S&P '26)"][0]
        self.assertEqual(chip.attrs["href"], st.BASE_PATH + "publication/2026-oakland/")

    def test_content_path_to_an_author_gives_the_author_permalink(self):
        code, log, pages = st.build_variant("content/_index.md", "url: people/", "url: authors/Prof-YuanTian/", pages=[""])
        self.assertEqual(code, 0, log)
        pill = [a for a in pages[""].find(cls="lab-hero").find_all("a", cls="action-pill") if a.text() == "People"][0]
        self.assertEqual(pill.attrs["href"], st.BASE_PATH + "author/yuan-tian/")

    def test_link_without_url_fails_the_build(self):
        code, log = st.build_variant("content/_index.md", "          - label: People\n            url: people/\n",
                                     "          - label: People\n")
        self.assertNotEqual(code, 0, log)
        self.assertIn("has no url", log)


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
    AREAS = ["ai-security", "data-privacy", "system-security"]

    @classmethod
    def setUpClass(cls):
        cls.page = st.page("research/")
        cls.cards = cls.page.find_all("article", cls="research-card")
        cls.front = publication_front_matter()

    def test_header_links_to_all_publications(self):
        header = self.page.find(cls="research-header")
        self.assertEqual(header.find("h1").text(), "Research")
        link = header.find("a")
        self.assertEqual(link.text(), "See all publications")
        self.assertTrue(st.resolves(link.attrs["href"]), link.attrs["href"])
        self.assertIn("text-align:center", st.css_rules(".research-header"))

    def test_filter_chips(self):
        chips = self.page.find(cls="research-filter").find_all("button")
        self.assertEqual([c.text() for c in chips], ["All", "AI Security", "Data Privacy", "System Security"])
        self.assertEqual([c.attrs.get("data-filter") for c in chips], ["all"] + self.AREAS)

    def test_one_card_per_area_with_an_active_status(self):
        self.assertEqual([c.attrs.get("id") for c in self.cards], self.AREAS)
        self.assertEqual([c.attrs.get("data-topic") for c in self.cards], self.AREAS)
        self.assertEqual([c.find("h2").text() for c in self.cards], ["AI Security", "Data Privacy", "System Security"])
        for card in self.cards:
            self.assertEqual(card.find(cls="research-status").text(), "Active")
            self.assertTrue(card.find("p", cls="research-card-desc").text())

    def test_projects_and_sponsors_are_listed(self):
        self.assertEqual(len(self.cards), 3, "research cards not rendered")
        for card in self.cards:
            self.assertTrue(card.find("ul", cls="research-projects").find_all("li"), card.attrs["id"])
            self.assertTrue(card.find_all(cls="sponsor-chip"), card.attrs["id"])

    def test_related_papers_come_from_each_papers_research_area(self):
        self.assertEqual(len(self.cards), 3, "research cards not rendered")
        for card in self.cards:
            area = card.attrs["id"]
            expected = sum(1 for f in self.front.values() if re.search(r"(?m)^research_area:\s*%s\s*$" % area, f))
            chips = card.find(cls="research-papers").find_all("a", cls="paper-chip")
            self.assertEqual(len(chips), expected, area)
            for chip in chips:
                self.assertTrue(chip.attrs["href"].startswith(st.BASE_PATH + "publication/"), chip.attrs["href"])
                self.assertTrue(st.resolves(chip.attrs["href"]), chip.attrs["href"])
                self.assertLessEqual(len(chip.text()), 45, chip.text())

    def test_every_paper_has_a_short_label(self):
        for slug, front in self.front.items():
            title = re.search(r"(?m)^title:\s*(.+)$", front).group(1)
            self.assertTrue(":" in title or re.search(r"(?m)^short_title:\s*\S", front), slug)

    def test_all_papers_link_preselects_the_area_on_the_publications_page(self):
        self.assertEqual(len(self.cards), 3, "research cards not rendered")
        for card in self.cards:
            more = card.find("a", cls="research-more")
            self.assertEqual(more.attrs["href"], st.BASE_PATH + "publication/#" + card.attrs["id"])

    def test_long_publication_lists_are_gone(self):
        self.assertEqual(self.page.find_all("h2", cls="research-area-heading"), [])
        self.assertFalse([a for a in self.page.find_all("a") if "Details" in a.text()])

    def test_cards_use_kwchang_panels_and_two_columns(self):
        self.assertIn("background:#fbfbf8", st.css_rules(".research-card"))
        self.assertIn("grid-template-columns:minmax(0,1fr)minmax(0,1fr)", st.css_rules(".research-card-body"))
        self.assertIn("grid-template-columns:1fr", st.css_rules(".research-card-body", media="(max-width: 767.98px)"))

    def test_filter_script_loads_under_the_subpath(self):
        scripts = [x.attrs["src"] for x in self.page.find_all("script") if "lab-research" in x.attrs.get("src", "")]
        self.assertEqual(len(scripts), 1)
        self.assertTrue(st.resolves(scripts[0]), scripts[0])


class PeopleTest(unittest.TestCase):
    def setUp(self):
        self.page = st.page("people/")

    def grid_items(self):
        return {li.find(cls="people-compact-name").text(): li for li in self.page.find_all("li", cls="people-compact-item")}

    def test_students_and_interns_use_the_compact_grid(self):
        items = self.grid_items()
        for name in ("Ying Li", "Jinghuai Zhang", "Peiran Wang", "Sean Tang", "Bomin Wei", "Nasir Hussain"):
            self.assertIn(name, items)

    def test_phd_students_have_photos_in_the_grid(self):
        items = self.grid_items()
        for name in ("Ying Li", "Jinghuai Zhang", "Peiran Wang", "Zhiyuan Zhang",
                     "Kaiyuan Zhang", "Sean Tang", "Jingmiao Zhang"):
            img = items[name].find("img")
            self.assertIsNotNone(img, name)
            self.assertTrue(st.resolves(img.attrs["src"]), img.attrs["src"])

    def test_phd_photos_match_the_faculty_photo_size(self):
        self.assertIn("width:150px", st.css_rules(".people-person .avatar"))
        photo = st.css_rules(".people-compact-photo")
        self.assertIn("width:150px", photo)
        self.assertIn("height:150px", photo)
        self.assertNotIn("width:100%", photo)
        # Cards with a photo are centred like the faculty cards.
        for name, li in self.grid_items().items():
            if li.find("img") is not None:
                self.assertIn("people-compact-item--photo", li.classes, name)
        self.assertIn("text-align:center", st.css_rules(".people-compact-item--photo"))

    def test_phd_cards_match_the_faculty_card_size(self):
        faculty = st.css_rules(".people-person")
        self.assertIn("width:200px", faculty)
        card = st.css_rules(".people-compact-item--photo")
        self.assertIn("width:200px", card)
        self.assertIn("padding:16px", card)
        # Photo cards sit in a wrapping row like the faculty cards, not in the stretched 4-column grid.
        self.assertIn("display:flex", st.css_rules(".people-compact-grid--photo"))
        grids = self.page.find_all("ul", cls="people-compact-grid")
        self.assertIn("people-compact-grid--photo", grids[0].classes)      # PhD Students
        self.assertNotIn("people-compact-grid--photo", grids[1].classes)   # Research Interns

    def test_research_interns_stay_text_only(self):
        items = self.grid_items()
        for name in ("Bomin Wei", "Nasir Hussain", "Esha Shivakumar", "Isaac Khabra", "Kevin Hong", "Tiancheng Zheng"):
            self.assertIsNone(items[name].find("img"), name)

    def test_kunlin_cai_is_a_phd_alumnus_at_meta(self):
        self.assertNotIn("Kunlin Cai", self.grid_items())
        alumni = {li.find("a").text(): li for li in self.page.find_all("li", cls="alumni-list-item") if li.find("a")}
        self.assertIn("Kunlin Cai", alumni)
        self.assertEqual(alumni["Kunlin Cai"].find(cls="alumni-first-employment").text(), "— PhD grad in 2026, now at Meta")
        self.assertEqual(alumni["Kunlin Cai"].find("a").attrs["href"], "https://kunlin-cai.com/")

    def test_jingmiao_zhang_joins_as_a_fall_2026_phd_student(self):
        phd_grid = self.page.find_all("ul", cls="people-compact-grid")[0]
        names = [n.text() for n in phd_grid.find_all(cls="people-compact-name")]
        self.assertIn("Jingmiao Zhang", names)
        role = self.grid_items()["Jingmiao Zhang"].find(cls="people-compact-role").text()
        self.assertEqual(role, "PhD Student from 26\u2019Fall")  # markdownify curls the apostrophe, as for everyone else

    def test_faculty_and_postdocs_keep_photo_cards(self):
        cards = {c.find("h2").text(): c for c in self.page.find_all(cls="people-person")}
        self.assertEqual(set(cards), {"Yuan Tian", "Zihang Xiang"})
        for card in cards.values():
            self.assertIsNotNone(card.find("img"))

    def test_external_homepages_open_in_a_new_tab(self):
        a = self.grid_items()["Ying Li"].find("a", cls="people-compact-name")
        self.assertEqual(a.attrs["href"], "https://y1ngli.github.io/")
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
    def test_news_rows_put_the_date_first_without_reading_time(self):
        self.assertIn("order:-1", st.css_rules(".view-compact .stream-meta"))
        self.assertIn("display:none", st.css_rules(".view-compact .article-reading-time"))

    def test_list_pages_fill_the_card(self):
        # Hugo Blox fixes .universal-wrapper at width:1000px, centred; inside our 1180px card it must fill the card.
        widths = [d for d in st.css_rules(".page-body .universal-wrapper").split(";") if d.startswith("width")]
        self.assertEqual(widths, ["width:auto"])

    def test_compact_publication_rows_elsewhere_show_the_venue(self):
        # Taxonomy pages (e.g. publication type) still use Hugo Blox's compact view, extended with the venue.
        rows = st.page("publication-type/paper-conference/").find_all(cls="view-compact")
        self.assertTrue(rows)
        self.assertTrue(all(r.find(cls="pub-venue") is not None for r in rows))

    def test_list_page_links_work_under_the_subpath(self):
        for path in ("publication/", "post/"):
            for a in st.page(path).find(cls="page-body").find_all("a"):
                href = a.attrs.get("href", "")
                if href.startswith("/"):
                    self.assertTrue(st.resolves(href), (path, href))

AREAS = {"ai-security": "AI Security", "data-privacy": "Data Privacy", "system-security": "System Security"}


def publication_front_matter():
    """{slug: front-matter text} for every publication bundle."""
    out = {}
    root = os.path.join(st.ROOT, "content", "publication")
    for name in sorted(os.listdir(root)):
        path = os.path.join(root, name, "index.md")
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as fh:
                out[name.lower()] = fh.read().split("---")[1]
    return out


class PublicationsPageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = st.page("publication/")
        cls.entries = cls.page.find_all("article", cls="pub-entry")
        cls.front = publication_front_matter()

    def entry(self, slug):
        return [e for e in self.entries
                if e.find("h3", cls="pub-title").find("a").attrs["href"].rstrip("/").endswith("/" + slug)][0]

    def actions(self, entry):
        return [a.text() for a in entry.find(cls="pub-actions").find_all() if a.tag in ("a", "button")]

    def test_every_publication_declares_a_research_area(self):
        for slug, front in self.front.items():
            m = re.search(r"(?m)^research_area:\s*['\"]?([a-z-]+)", front)
            self.assertTrue(m and m.group(1) in AREAS, slug)

    def test_header_links(self):
        links = self.page.find(cls="pub-header-links").find_all("a")
        self.assertEqual([a.text() for a in links], ["Google Scholar", "Research areas"])
        self.assertEqual(links[0].attrs["href"], "https://scholar.google.com/citations?user=ja0GtqgAAAAJ")
        self.assertTrue(st.resolves(links[1].attrs["href"]), links[1].attrs["href"])

    def test_explorer_has_search_abstract_toggle_and_topic_chips(self):
        explorer = self.page.find(cls="pub-explorer")
        self.assertEqual({i.attrs.get("id") for i in explorer.find_all("input")}, {"pub-search", "pub-search-abstract"})
        chips = explorer.find_all("button", cls="pub-filter-chip")
        self.assertEqual([c.text() for c in chips], ["All", "AI Security", "Data Privacy", "System Security"])
        self.assertEqual([c.attrs.get("data-filter") for c in chips], ["all", "ai-security", "data-privacy", "system-security"])
        self.assertEqual(explorer.find(cls="pub-filter-status").text(),
                         "Showing %d publications for all topics." % len(self.front))

    def test_entries_are_grouped_by_year_newest_first(self):
        years = [h.text() for h in self.page.find_all("h2", cls="pub-year")]
        expected = sorted({re.search(r"(?m)^date:\s*['\"]?(\d{4})", f).group(1) for f in self.front.values()}, reverse=True)
        self.assertEqual(years, expected)
        self.assertEqual(len(self.entries), len(self.front))

    def test_entry_reads_title_then_authors_venue_and_year(self):
        e = self.entry("2026-oakland")
        self.assertEqual(e.find("h3", cls="pub-title").text(), "Breaking the Illusion: Automated Reasoning of GDPR Consent Violations")
        line = e.find("p", cls="pub-authors").text()
        self.assertTrue(line.startswith("Ying Li, Wenjun Qiu, "), line)
        self.assertTrue(line.endswith(", and Yuan Tian, in IEEE S&P, 2026."), line)
        # A venue that already names the year does not repeat it.
        self.assertTrue(self.entry("2019-birthday").find("p", cls="pub-authors").text().endswith("in USENIX Security 2019."))

    def test_actions_point_only_at_real_things(self):
        self.assertTrue(self.entries, "no publication entries rendered")
        for e in self.entries:
            for node in e.find(cls="pub-actions").find_all():
                href = node.attrs.get("href", "")
                self.assertNotRegex(href, r"hugoblox|hugo-blox|youtube\.com")
                if node.tag == "a" and href not in ("", "#") and not href.startswith("http"):
                    self.assertTrue(st.resolves(href), href)
                if "js-cite-modal" in node.classes:
                    self.assertTrue(st.resolves(node.attrs["data-filename"]), node.attrs["data-filename"])
            self.assertEqual(self.actions(e)[-1], "Details")

    def test_full_text_abstract_and_bibtex_appear_only_when_available(self):
        root = os.path.join(st.ROOT, "content", "publication")
        for name in os.listdir(root):
            folder = os.path.join(root, name)
            if not os.path.isdir(folder):
                continue
            slug, files, front = name.lower(), os.listdir(folder), self.front[name.lower()]
            got = self.actions(self.entry(slug))
            self.assertEqual("Full Text" in got, any(f.endswith(".pdf") for f in files), slug)
            self.assertEqual("BibTeX" in got, "cite.bib" in files, slug)
            m = re.search(r"(?m)^abstract:[ \t]*(.*)$", front)
            has_abstract = bool(m and m.group(1).strip().strip("'\"").strip())
            self.assertEqual("Abstract" in got, has_abstract, slug)

    def test_abstract_buttons_control_a_hidden_abstract(self):
        self.assertTrue(self.entries, "no publication entries rendered")
        for e in self.entries:
            for button in e.find_all("button", cls="pub-abstract-toggle"):
                box = [d for d in e.find_all(cls="pub-abstract") if d.attrs.get("id") == button.attrs["aria-controls"]]
                self.assertEqual(len(box), 1)
                self.assertIn("hidden", box[0].attrs)
                self.assertEqual(button.attrs.get("aria-expanded"), "false")

    def test_entries_carry_their_topic_for_filtering(self):
        self.assertTrue(self.entries, "no publication entries rendered")
        for e in self.entries:
            topic = e.attrs.get("data-topic")
            self.assertIn(topic, AREAS)
            self.assertIn("pub-topic-dot--" + topic, e.find(cls="pub-topic-dot").classes)
            self.assertTrue(e.attrs.get("data-search"))

    def test_filter_script_loads_under_the_subpath(self):
        scripts = [x.attrs["src"] for x in self.page.find_all("script") if "publications" in x.attrs.get("src", "")]
        self.assertEqual(len(scripts), 1)
        self.assertTrue(st.resolves(scripts[0]), scripts[0])

    def test_year_panels_use_kwchang_panel_colours(self):
        rules = st.css_rules(".pub-year-group")
        self.assertIn("background:#fbfbf8", rules)
        self.assertIn("border:1pxsolid#e1e1dc", rules)

    def test_missing_research_area_fails_the_build(self):
        code, log = st.build_variant("content/publication/2026-Oakland/index.md", "research_area: data-privacy\n", "")
        self.assertNotEqual(code, 0, log)
        self.assertIn("research_area", log)


class PublicationFilterScriptTest(unittest.TestCase):
    """The filter logic in assets/js/lab-publications.js, run with Node."""
    SCRIPT = os.path.join(st.ROOT, "assets", "js", "lab-publications.js")

    def node(self, expression):
        node = shutil.which("node") or "/opt/homebrew/opt/node@22/bin/node"
        if not os.path.exists(node):
            self.skipTest("node not installed")
        code = "const P = require(%s); console.log(JSON.stringify(%s));" % (json.dumps(self.SCRIPT), expression)
        result = subprocess.run([node, "-e", code], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    ENTRY = "{topic: 'ai-security', search: 'badmerging: backdoor attacks against model merging jinghuai zhang ccs 2024', abstract: 'fine-tuned task-specific models'}"

    def test_topic_must_match_unless_all(self):
        self.assertTrue(self.node("P.matches(%s, 'all', [], false)" % self.ENTRY))
        self.assertTrue(self.node("P.matches(%s, 'ai-security', [], false)" % self.ENTRY))
        self.assertFalse(self.node("P.matches(%s, 'data-privacy', [], false)" % self.ENTRY))

    def test_every_term_must_appear(self):
        self.assertTrue(self.node("P.matches(%s, 'all', ['backdoor', 'ccs'], false)" % self.ENTRY))
        self.assertFalse(self.node("P.matches(%s, 'all', ['backdoor', 'gdpr'], false)" % self.ENTRY))

    def test_abstract_is_searched_only_when_asked(self):
        self.assertFalse(self.node("P.matches(%s, 'all', ['fine-tuned'], false)" % self.ENTRY))
        self.assertTrue(self.node("P.matches(%s, 'all', ['fine-tuned'], true)" % self.ENTRY))

    def test_query_is_split_into_lower_case_terms(self):
        self.assertEqual(self.node("P.terms('  BackDoor   CCS ')"), ["backdoor", "ccs"])

    def test_status_text(self):
        self.assertEqual(self.node("P.statusText(29, 'all topics', '')"), "Showing 29 publications for all topics.")
        self.assertEqual(self.node("P.statusText(1, 'Data Privacy', 'gdpr')"),
                         "Showing 1 publication for Data Privacy matching \u201cgdpr\u201d.")



class AwardsPageTest(unittest.TestCase):
    PEOPLE = ["Peiran Wang", "Ying Li", "Kunlin Cai", "Jinghuai Zhang", "Zihang Xiang",
              "Faysal Hossain Shezan", "Tamjid Al Rahat", "Fnu Suya", "Jianfeng Chi"]

    @classmethod
    def setUpClass(cls):
        cls.page = st.page("awards/")

    def test_header_is_centred(self):
        self.assertEqual(self.page.find(cls="awards-header").find("h1").text(), "Awards & Service")
        self.assertIn("text-align:center", st.css_rules(".awards-header"))
        self.assertIn("margin-bottom:20px", st.css_rules(".awards-header"))

    def test_faculty_awards_list_with_years_on_the_right(self):
        rows = self.page.find("ul", cls="award-timeline").find_all("li")
        self.assertEqual(len(rows), 7)
        self.assertEqual(rows[0].find(cls="award-name").text(), "Okawa Foundation Award")
        self.assertEqual(rows[0].find(cls="award-year").text(), "2022")
        self.assertEqual(rows[1].find(cls="award-name").text(), "Best Paper Award, IEEE TPS")
        self.assertIn("justify-content:space-between", st.css_rules(".award-row"))

    def test_every_student_and_postdoc_award_is_kept(self):
        cards = self.page.find_all(cls="award-person")
        self.assertEqual([c.find(cls="award-person-name").text() for c in cards], self.PEOPLE)
        self.assertEqual(sum(len(c.find_all("li")) for c in cards), 34)
        ying = cards[1].find_all("li")
        self.assertEqual(ying[0].find(cls="award-name").text(), "Distinguished Artifact Reviewer, USENIX Security")
        self.assertEqual(ying[0].find(cls="award-year").text(), "2025")

    def test_kunlin_is_listed_as_an_alumnus(self):
        card = self.page.find_all(cls="award-person")[2]
        self.assertEqual(card.find(cls="award-person-role").text(), "PhD Alumni, now at Meta")

    def test_service_lists_are_kept(self):
        organizing = self.page.find("ul", cls="service-organizing").find_all("li")
        self.assertEqual(len(organizing), 7)
        self.assertEqual(organizing[0].find(cls="award-name").text(), "Associate Chair, IEEE S&P (Oakland)")
        self.assertEqual(organizing[0].find(cls="award-year").text(), "2027")
        committees = self.page.find("ul", cls="service-committees").find_all("li")
        self.assertEqual([li.find(cls="award-name").text() for li in committees],
                         ["IEEE S&P (Oakland)", "USENIX Security", "ACM CCS", "NDSS"])

    def test_people_cards_flow_in_two_columns_without_stretching(self):
        # A grid stretches every card to its row's tallest one, leaving empty boxes; columns pack them.
        rules = st.css_rules(".award-people")
        self.assertIn("column-count:2", rules)
        self.assertNotIn("display:grid", rules)
        self.assertIn("break-inside:avoid", st.css_rules(".award-person"))
        self.assertIn("column-count:1", st.css_rules(".award-people", media="(max-width: 767.98px)"))

    def test_faculty_awards_use_the_same_two_columns_as_service(self):
        rules = st.css_rules(".award-timeline")
        self.assertIn("column-count:2", rules)
        self.assertNotIn("max-width", rules)
        self.assertIn("break-inside:avoid", st.css_rules(".award-timeline .award-row"))
        self.assertIn("column-count:1", st.css_rules(".award-timeline", media="(max-width: 767.98px)"))


def member_pictures(pages):
    """{(where, name): kind of picture} on the People page, Zhiyuan Zhang's profile page and a publication page,
    where kind is "avatar" (the photo), "stylized-bear" or "stylized-human". `pages` maps site paths to parsed pages."""
    def kind(src):
        name = src.rsplit("/", 1)[-1]
        for k in ("avatar", "stylized-bear", "stylized-human"):
            if name.startswith(k + "_"):
                return k
        raise AssertionError(src)
    out = {}
    people = pages["people/"]
    for card in people.find_all(cls="people-person"):
        img = card.find("img")
        if img is not None:
            out[("people", card.find("h2").text())] = kind(img.attrs["src"])
    for li in people.find_all("li", cls="people-compact-item--photo"):
        out[("people", li.find(cls="people-compact-name").text())] = kind(li.find("img").attrs["src"])
    out[("profile", "Zhiyuan Zhang")] = kind(pages["author/zhiyuan-zhang/"].find("img", cls="avatar").attrs["src"])
    for img in pages["publication/2026-ndss/"].find_all("img", cls="avatar"):
        out[("paper", img.attrs["alt"])] = kind(img.attrs["src"])
    return out


class AvatarStyleTest(unittest.TestCase):
    """params.people.avatar_style shows each member's stylized-<style>.jpg instead of their photo; a member's own
    avatar_style overrides it, and members without that picture keep their photo."""
    PAGES = ["people/", "author/zhiyuan-zhang/", "publication/2026-ndss/"]

    @classmethod
    def setUpClass(cls):
        cls.default = member_pictures({p: st.page(p) for p in cls.PAGES})
        code, log, pages = st.build_variant("config/_default/params.yaml", "avatar_style: photo", "avatar_style: bear",
                                            pages=cls.PAGES)
        assert code == 0, log
        cls.bear = member_pictures(pages)
        code, log, pages = st.build_variant("content/authors/PhD-Zhiyuan/_index.md", "\nfirst_name:",
                                            "\navatar_style: human\nfirst_name:", pages=cls.PAGES)
        assert code == 0, log
        cls.override = member_pictures(pages)

    def test_photos_by_default(self):
        self.assertIn(("people", "Yuan Tian"), self.default)
        self.assertIn(("people", "Ying Li"), self.default)
        self.assertEqual(set(self.default.values()), {"avatar"}, self.default)

    def test_site_wide_style_on_every_page(self):
        for key in [("people", "Yuan Tian"), ("people", "Zihang Xiang"), ("people", "Ying Li"),
                    ("people", "Sean Tang"), ("profile", "Zhiyuan Zhang"), ("paper", "Ying Li"), ("paper", "Yuan Tian")]:
            self.assertEqual(self.bear[key], "stylized-bear", key)

    def test_members_without_that_picture_keep_their_photo(self):
        self.assertEqual(self.bear[("people", "Jinghuai Zhang")], "avatar")   # has no bear picture
        self.assertEqual(self.bear[("paper", "Jinghuai Zhang")], "avatar")
        self.assertEqual(self.bear[("paper", "Kunlin Cai")], "avatar")        # alumnus, photo only

    def test_a_member_can_choose_their_own_style(self):
        self.assertEqual(self.override[("people", "Zhiyuan Zhang")], "stylized-human")
        self.assertEqual(self.override[("profile", "Zhiyuan Zhang")], "stylized-human")
        self.assertEqual(self.override[("people", "Ying Li")], "avatar")

    def test_stylized_pictures_are_jpgs_next_to_a_photo(self):
        root = os.path.join(st.ROOT, "content", "authors")
        found = 0
        for folder in sorted(os.listdir(root)):
            names = os.listdir(os.path.join(root, folder)) if os.path.isdir(os.path.join(root, folder)) else []
            for name in names:
                if name.startswith("stylized-"):
                    found += 1
                    self.assertRegex(name, r"^stylized-[a-z]+\.jpg$", folder)
                    self.assertTrue(any(n.startswith("avatar.") for n in names), folder)
                    with open(os.path.join(root, folder, name), "rb") as fh:
                        head = fh.read(4096)
                    self.assertTrue(head.startswith(b"\xff\xd8"), (folder, name))
        self.assertEqual(found, 17)


NEWS_TYPES = ["Paper", "Funding", "Award", "Service", "Talk", "People"]


def post_front_matter():
    """{bundle folder (lower-case): front-matter text} for every news post."""
    out = {}
    root = os.path.join(st.ROOT, "content", "post")
    for name in sorted(os.listdir(root)):
        path = os.path.join(root, name, "index.md")
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as fh:
                out[name.lower()] = fh.read().split("---")[1]
    return out


class NewsListTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = st.page("post/")
        cls.entries = cls.page.find_all("article", cls="news-entry")

    def entry(self, slug):
        return [e for e in self.entries
                if e.find("h3", cls="news-title").find("a").attrs["href"].rstrip("/").endswith("/" + slug)][0]

    def test_header_is_centred(self):
        self.assertEqual(self.page.find(cls="news-header").find("h1").text(), "Latest News")
        self.assertIn("text-align:center", st.css_rules(".news-header"))

    def test_posts_are_grouped_by_year_newest_first(self):
        groups = self.page.find_all("section", cls="news-year-group")
        self.assertEqual([g.attrs["data-year"] for g in groups], ["2026", "2025"])
        self.assertEqual([g.find("h2", cls="news-year").text() for g in groups], ["2026", "2025"])
        titles = [e.find("h3", cls="news-title").text() for e in self.entries]
        self.assertEqual(titles, st.newest_post_titles(len(post_front_matter())))

    def test_each_post_shows_its_month_and_day(self):
        self.assertEqual(self.entry("26-sean-kaiyuan-phd").find(cls="news-date").text(), "MAR 18")
        self.assertEqual(self.entry("25-05-sp-keynote").find(cls="news-date").text(), "MAY 15")

    def test_every_post_declares_a_news_type(self):
        front = post_front_matter()
        self.assertTrue(front)
        for slug, text in front.items():
            m = re.search(r"(?m)^news_type:\s*(\S+)", text)
            self.assertTrue(m, slug)
            self.assertIn(m.group(1), NEWS_TYPES, slug)

    def test_type_chip_on_every_entry(self):
        self.assertTrue(self.entries)
        for e in self.entries:
            chip = e.find(cls="news-type")
            self.assertIsNotNone(chip)
            self.assertIn("news-type--" + chip.text().lower(), chip.classes)
        self.assertEqual(self.entry("26-ndss-paper").find(cls="news-type").text(), "Paper")
        self.assertEqual(self.entry("26-nsf-medical-ai").find(cls="news-type").text(), "Funding")

    def test_summary_does_not_repeat_the_title(self):
        # Hidden when it only repeats the title; the repeated opening sentence is dropped otherwise.
        self.assertIsNone(self.entry("26-welcome-new-members").find(cls="news-summary"))
        self.assertIsNone(self.entry("25-05-sp-keynote").find(cls="news-summary"))
        self.assertEqual(self.entry("26-sp2027-associate-chair").find(cls="news-summary").text(),
                         "Please submit your interesting papers!")
        self.assertTrue(self.entry("26-sean-kaiyuan-phd").find(cls="news-summary").text().startswith("Sean Tang,"))
        self.assertTrue(self.entry("26-amazon-nova-challenge").find(cls="news-summary").text().startswith("We are excited"))

    def test_featured_image_becomes_a_thumbnail(self):
        thumb = self.entry("25-05-sp-keynote").find("img", cls="news-thumb")
        self.assertIsNotNone(thumb)
        # The featured image is a banner with text on it: scale it, never crop it.
        self.assertIn("height:auto", st.css_rules(".news-thumb"))
        self.assertNotIn("object-fit:cover", st.css_rules(".news-thumb"))
        self.assertTrue(st.resolves(thumb.attrs["src"]), thumb.attrs["src"])
        self.assertIsNone(self.entry("26-ndss-paper").find("img", cls="news-thumb"))


class NewsPostTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = st.page("post/26-ndss-paper/")
        cls.post = cls.page.find("article", cls="news-post")

    def test_back_link_to_all_news(self):
        back = self.post.find("a", cls="news-back")
        self.assertEqual(back.text(), "\u2190 All news")
        self.assertTrue(back.attrs["href"].endswith("/post/"), back.attrs["href"])
        self.assertTrue(st.resolves(back.attrs["href"]))

    def test_date_and_type_above_a_smaller_title(self):
        meta = self.post.find(cls="news-post-meta")
        self.assertEqual(meta.find("time").text(), "Mar 12, 2026")
        self.assertEqual(meta.find(cls="news-type").text(), "Paper")
        self.assertEqual(self.post.find("h1").text(), "Our paper on XR Security and Privacy accepted at NDSS 2026!")
        self.assertIn("font-size:30px", st.css_rules(".page-body .news-post h1"))

    def test_no_share_buttons_or_author_box(self):
        self.assertIsNone(self.page.find(cls="share-box"))
        self.assertIsNone(self.page.find(cls="author-card"))

    def test_pager_links_the_older_and_newer_posts(self):
        pager = self.post.find("nav", cls="news-pager")
        older, newer = pager.find("a", cls="news-older"), pager.find("a", cls="news-newer")
        self.assertIn("Thanks, NSF, for supporting our research on trustworthy medical AI!", older.text())
        self.assertIn("Our paper on GDPR Consent Violations will appear at IEEE S&P (Oakland) 2026!", newer.text())
        self.assertTrue(st.resolves(older.attrs["href"]) and st.resolves(newer.attrs["href"]))

    def test_pager_ends(self):
        oldest = st.page("post/25-05-sp-keynote/").find("nav", cls="news-pager")
        self.assertIsNone(oldest.find("a", cls="news-older"))
        self.assertIsNotNone(oldest.find("a", cls="news-newer"))
        newest = st.page("post/26-sean-kaiyuan-phd/").find("nav", cls="news-pager")
        self.assertIsNone(newest.find("a", cls="news-newer"))
        self.assertIsNotNone(newest.find("a", cls="news-older"))

    def test_featured_image_is_shown_in_the_post(self):
        img = st.page("post/25-05-sp-keynote/").find("img", cls="news-featured")
        self.assertIsNotNone(img)
        self.assertTrue(st.resolves(img.attrs["src"]), img.attrs["src"])

    def test_card_is_as_tall_as_its_content(self):
        # Hugo Blox stretches .page-body to fill the viewport, leaving a blank card under short posts.
        self.assertIn("align-self:start", st.css_rules(".page-body"))
        # ...and the pager at the end keeps a gap above the card's bottom edge.
        self.assertIn("padding-bottom:32px", st.css_rules(".news-post"))

    def test_unknown_news_type_fails_the_build(self):
        code, log = st.build_variant("content/post/26-ndss-paper/index.md", "news_type: Paper", "news_type: Papers")
        self.assertNotEqual(code, 0)
        self.assertIn("news_type", log)


class ResearchFilterScriptTest(PublicationFilterScriptTest):
    """Small pure helpers of assets/js/lab-research.js and the hash preselect in lab-publications.js."""
    SCRIPT = os.path.join(st.ROOT, "assets", "js", "lab-research.js")

    def test_topic_filter(self):
        self.assertTrue(self.node("P.shows('all', 'ai-security')"))
        self.assertTrue(self.node("P.shows('ai-security', 'ai-security')"))
        self.assertFalse(self.node("P.shows('data-privacy', 'ai-security')"))

    # The inherited PublicationFilterScriptTest cases target lab-publications.js; skip them here.
    test_topic_must_match_unless_all = test_every_term_must_appear = test_abstract_is_searched_only_when_asked = None
    test_query_is_split_into_lower_case_terms = test_status_text = None


class PublicationHashTest(PublicationFilterScriptTest):
    def test_hash_preselects_a_known_topic(self):
        keys = "['all', 'ai-security', 'data-privacy', 'system-security']"
        self.assertEqual(self.node("P.topicFromHash('#data-privacy', %s)" % keys), "data-privacy")
        self.assertEqual(self.node("P.topicFromHash('#nope', %s)" % keys), "all")
        self.assertEqual(self.node("P.topicFromHash('', %s)" % keys), "all")

    test_topic_must_match_unless_all = test_every_term_must_appear = test_abstract_is_searched_only_when_asked = None
    test_query_is_split_into_lower_case_terms = test_status_text = None


if __name__ == "__main__":
    unittest.main()
