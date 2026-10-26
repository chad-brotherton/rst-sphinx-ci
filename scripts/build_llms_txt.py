"""Generate llms.txt, llms-full.txt, and a Markdown copy of each page.

Build the HTML docs with sphinx-build first, then run this script. Pass
--html if the HTML isn't in docs/build/html.

The script reads everything from the built site. It takes the page order and
section names from the table of contents on index.html, and each page's URL
from its canonical link, which Sphinx adds when html_baseurl is set in
conf.py. It writes its output into the HTML folder, next to the pages, so the
files are published with the site:

- llms.txt: an index of the docs in the format described at llmstxt.org.
- <page>.html.md: a Markdown copy of each page, which llms.txt links to.
- llms-full.txt: every page's Markdown in one file.
"""

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag
from markdownify import MarkdownConverter

DEFAULT_HTML = Path(__file__).resolve().parent.parent / "docs" / "build" / "html"

# Table of contents sections that llms.txt lists under its Optional heading.
# By the llmstxt.org convention, an agent can skip those links to save context.
OPTIONAL_SECTIONS = {"About these docs"}


@dataclass
class Page:
    """One page of the built site, converted to Markdown."""

    title: str
    url: str
    description: str
    markdown: str

    @property
    def markdown_url(self) -> str:
        return self.url + ".md"


def _code_language(pre: Tag) -> str:
    # Sphinx wraps each code block in <div class="highlight-LANGUAGE">.
    for parent in pre.parents:
        for cls in parent.get("class", []):
            if cls.startswith("highlight-"):
                language = cls.removeprefix("highlight-")
                return "python" if language == "default" else language
    return ""


def _to_markdown(article: Tag) -> str:
    converter = MarkdownConverter(
        heading_style="ATX",
        bullets="-",
        code_language_callback=_code_language,
        escape_underscores=False,
    )
    markdown = converter.convert_soup(article)
    markdown = re.sub(r"[ \t]+\n", "\n", markdown)
    return re.sub(r"\n{3,}", "\n\n", markdown).strip() + "\n"


def _first_sentence(text: str) -> str:
    text = " ".join(text.split())
    match = re.match(r"(.+?[.!?])(\s|$)", text)
    return match.group(1) if match else text


def _read_html(path: Path) -> BeautifulSoup:
    if not path.is_file():
        sys.exit(f"build_llms_txt: {path} doesn't exist. Build the HTML first.")
    return BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")


def _canonical_url(soup: BeautifulSoup, path: Path) -> str:
    link = soup.find("link", rel="canonical")
    if link is None:
        sys.exit(f"build_llms_txt: {path.name} has no canonical link. Set html_baseurl in conf.py.")
    return link["href"]


def _article(soup: BeautifulSoup, path: Path) -> Tag:
    article = soup.select_one("article.bd-article")
    if article is None:
        sys.exit(f"build_llms_txt: {path.name} has no <article class='bd-article'>.")
    # Drop the anchor links on headings and the [source] links on API entries.
    for element in article.select("a.headerlink"):
        element.decompose()
    for element in article.select("span.viewcode-link"):
        (element.find_parent("a") or element).decompose()
    for link in article.find_all("a"):
        link.attrs.pop("title", None)
    # Turn admonition titles such as "Warning" into a bold "Warning:" label.
    for title in article.select("p.admonition-title"):
        label = soup.new_tag("strong")
        label.string = title.get_text(strip=True) + ":"
        title.clear()
        title.append(label)
    return article


def read_page(path: Path) -> Page:
    """Convert one built HTML page to a Page."""
    soup = _read_html(path)
    url = _canonical_url(soup, path)
    article = _article(soup, path)

    heading = article.find("h1")
    if heading is None:
        sys.exit(f"build_llms_txt: {path.name} has no title.")
    title = heading.get_text(strip=True)
    paragraph = heading.find_next("p")
    description = _first_sentence(paragraph.get_text()) if paragraph else ""

    # Make links absolute, so they work wherever the Markdown is read.
    for link in article.find_all("a", href=True):
        link["href"] = urljoin(url, link["href"])

    return Page(title, url, description, _to_markdown(article))


def read_sections(html_dir: Path) -> tuple[str, str, str, list[tuple[str, list[str]]]]:
    """Read the site name, summary, base URL, and table of contents from index.html.

    Returns:
        The site name, the summary paragraph, the index page's URL, and a list
        of (section name, [page file names]) pairs in table-of-contents order.
    """
    path = html_dir / "index.html"
    soup = _read_html(path)
    index_url = _canonical_url(soup, path)
    article = _article(soup, path)

    name = article.find("h1").get_text(strip=True)
    summary = " ".join(article.find("p").get_text().split())

    sections = []
    for wrapper in article.select("div.toctree-wrapper"):
        caption = wrapper.select_one("span.caption-text")
        pages = [link["href"] for link in wrapper.select("li.toctree-l1 > a.reference.internal")]
        sections.append((caption.get_text(strip=True) if caption else "Docs", pages))
    if not sections:
        sys.exit("build_llms_txt: index.html has no table of contents.")
    return name, summary, index_url, sections


def build(html_dir: Path) -> list[Path]:
    """Write llms.txt, llms-full.txt, and the per-page Markdown into html_dir.

    Returns:
        The paths of every file written.
    """
    name, summary, index_url, sections = read_sections(html_dir)
    full_url = urljoin(index_url, "llms-full.txt")

    index_lines = [
        f"# {name}",
        "",
        f"> {summary}",
        "",
        "Each link below points to a Markdown copy of a page. "
        f"The full text of every page is in [llms-full.txt]({full_url}).",
    ]
    optional_lines = []
    full_parts = [f"# {name}\n\n> {summary}\n"]
    written = []

    for section, files in sections:
        lines = index_lines if section not in OPTIONAL_SECTIONS else optional_lines
        if section not in OPTIONAL_SECTIONS:
            lines += ["", f"## {section}", ""]
        for file_name in files:
            page = read_page(html_dir / file_name)
            markdown_path = html_dir / (file_name + ".md")
            markdown_path.write_text(page.markdown, encoding="utf-8")
            written.append(markdown_path)
            lines.append(f"- [{page.title}]({page.markdown_url}): {page.description}")
            # Put the source URL under each page's title in llms-full.txt.
            title_line, _, body = page.markdown.partition("\n")
            full_parts.append(f"{title_line}\n\nSource: {page.url}\n{body}")

    if optional_lines:
        index_lines += ["", "## Optional", ""] + optional_lines

    for file_name, text in (
        ("llms.txt", "\n".join(index_lines) + "\n"),
        ("llms-full.txt", "\n".join(full_parts)),
    ):
        path = html_dir / file_name
        path.write_text(text, encoding="utf-8")
        written.append(path)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--html",
        type=Path,
        default=DEFAULT_HTML,
        help=f"the built HTML folder (default: {DEFAULT_HTML})",
    )
    args = parser.parse_args()
    for path in build(args.html):
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
