"""Helpers for the site tests: build the Hugo site once, parse pages into a tiny DOM, query the compiled CSS."""
import atexit
import os
import re
import shutil
import subprocess
import tempfile
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_PATH = "/UCLA-Sec-Lab-Website/"  # production is served from this subpath
BASE_URL = "http://example.org" + BASE_PATH
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}

_public = None
_log = ""
_pages = {}
_css = None


def hugo_bin():
    for candidate in (os.environ.get("HUGO"), os.path.expanduser("~/.local/bin/hugo"), shutil.which("hugo")):
        if candidate and os.path.exists(candidate):
            return candidate
    raise RuntimeError("Hugo 0.135.0 extended not found; set HUGO=/path/to/hugo")


def _run_hugo(site_dir, out_dir):
    env = dict(os.environ, PATH="/opt/homebrew/bin:" + os.environ.get("PATH", ""))  # Hugo Modules need Go
    result = subprocess.run([hugo_bin(), "--gc", "--baseURL", BASE_URL, "-d", out_dir],
                            cwd=site_dir, env=env, capture_output=True, text=True)
    return result.returncode, result.stdout + result.stderr


def public_dir():
    """Build the site once per test run and return the output directory."""
    global _public, _log
    if _public is None:
        out = tempfile.mkdtemp(prefix="bruinsec-site-")
        atexit.register(shutil.rmtree, out, True)
        code, _log = _run_hugo(ROOT, out)
        if code != 0:
            raise RuntimeError("hugo build failed:\n" + _log)
        _public = out
    return _public


def build_log():
    public_dir()
    return _log


def _ignore_at_root(src, names):
    if os.path.samefile(src, ROOT):
        return {".git", "public", "resources"} & set(names)
    return set()


def build_variant(relpath, old, new):
    """Build a copy of the site with one text replacement in `relpath`; return (exit code, log)."""
    tmp = tempfile.mkdtemp(prefix="bruinsec-variant-")
    try:
        site = os.path.join(tmp, "site")
        shutil.copytree(ROOT, site, ignore=_ignore_at_root)
        path = os.path.join(site, relpath)
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        if old not in text:
            raise AssertionError(f"{old!r} not found in {relpath}")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text.replace(old, new, 1))
        return _run_hugo(site, os.path.join(tmp, "out"))
    finally:
        shutil.rmtree(tmp, True)


class Node:
    def __init__(self, tag, attrs, parent=None):
        self.tag = tag
        self.attrs = {k: (v or "") for k, v in attrs}
        self.parent = parent
        self.children = []

    @property
    def classes(self):
        return self.attrs.get("class", "").split()

    def text(self):
        parts = [c if isinstance(c, str) else c.text() for c in self.children]
        return " ".join("".join(parts).split())

    def find_all(self, tag=None, cls=None):
        found = []
        for child in self.children:
            if isinstance(child, Node):
                if (tag is None or child.tag == tag) and (cls is None or cls in child.classes):
                    found.append(child)
                found.extend(child.find_all(tag, cls))
        return found

    def find(self, tag=None, cls=None):
        found = self.find_all(tag, cls)
        return found[0] if found else None


class _TreeBuilder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#document", [])
        self.current = self.root

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.current)
        self.current.children.append(node)
        if tag not in VOID_TAGS:
            self.current = node

    def handle_startendtag(self, tag, attrs):
        self.current.children.append(Node(tag, attrs, self.current))

    def handle_endtag(self, tag):
        node = self.current
        while node is not self.root and node.tag != tag:
            node = node.parent
        if node is not self.root:
            self.current = node.parent

    def handle_data(self, data):
        self.current.children.append(data)


def page(path):
    """Parsed DOM of a built page; `path` is a site path like "", "people/" or "publication/2026-oakland/"."""
    if path not in _pages:
        with open(os.path.join(public_dir(), path, "index.html"), encoding="utf-8") as fh:
            builder = _TreeBuilder()
            builder.feed(fh.read())
        _pages[path] = builder.root
    return _pages[path]


def resolves(url):
    """True if an internal URL (absolute or root-relative, with the subpath) points at a built file."""
    if url.startswith(BASE_URL):
        url = BASE_PATH + url[len(BASE_URL):]
    if not url.startswith(BASE_PATH):
        return False
    rel = url[len(BASE_PATH):].split("#")[0].split("?")[0]
    target = os.path.join(public_dir(), rel)
    if os.path.isdir(target):
        target = os.path.join(target, "index.html")
    return os.path.isfile(target)


def css_compact():
    """All compiled CSS, lower-cased with whitespace removed, so assertions ignore minifier spacing."""
    global _css
    if _css is None:
        folder = os.path.join(public_dir(), "css")
        text = ""
        for name in sorted(os.listdir(folder)):
            if name.endswith(".css"):
                with open(os.path.join(folder, name), encoding="utf-8") as fh:
                    text += fh.read()
        _css = re.sub(r"\s+", "", text.lower())
    return _css


def _media_blocks(query):
    css = css_compact()
    needle = "@media" + re.sub(r"\s+", "", query.lower())
    blocks, i = [], css.find(needle)
    while i != -1:
        start = css.index("{", i)
        depth, k = 0, start
        while True:
            if css[k] == "{":
                depth += 1
            elif css[k] == "}":
                depth -= 1
                if depth == 0:
                    break
            k += 1
        blocks.append(css[start + 1:k])
        i = css.find(needle, k)
    return blocks


def css_rules(selector, media=None):
    """Declarations of every rule whose selector list contains `selector` (whitespace-insensitive),
    optionally only inside `@media <media>` blocks such as "(max-width: 767.98px)"."""
    wanted = re.sub(r"\s+", "", selector.lower())
    sources = _media_blocks(media) if media else [css_compact()]
    found = []
    for src in sources:
        for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", src):
            if wanted in m.group(1).split(","):
                found.append(m.group(2))
    return ";".join(found)


def png_info(path):
    """(width, height, colour type) from a PNG header; colour type 6 is RGBA."""
    with open(path, "rb") as fh:
        head = fh.read(26)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError(f"{path} is not a PNG")
    return int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big"), head[25]


def newest_post_titles(n):
    """Titles of the n newest non-draft posts in content/post, by front-matter date."""
    posts = []
    root = os.path.join(ROOT, "content", "post")
    for name in os.listdir(root):
        path = os.path.join(root, name, "index.md")
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8") as fh:
            front = fh.read().split("---")[1]
        if re.search(r"(?m)^draft:\s*true", front):
            continue
        title = re.search(r"(?m)^title:\s*(.+)$", front).group(1).strip().strip("'\"")
        date = re.search(r"(?m)^date:\s*['\"]?([0-9T:\-+]+)", front).group(1)
        posts.append((date, title))
    return [title for _, title in sorted(posts, reverse=True)[:n]]
