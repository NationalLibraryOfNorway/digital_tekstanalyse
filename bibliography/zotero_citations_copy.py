# Philip Bailey
# 29 Jan 2020
# Script to generate markdown file listing of citations within a Zotero library
# https://pyzotero.readthedocs.io/en/latest/
# -------------------------------------------------------------
import argparse
from pyzotero import zotero
from datetime import datetime


def format_newspaper_article_citation(item: dict) -> str:
    """Harvard reference style for newspaper articles:

    Surname, Initial(s) (Year) Article Title, *Newspaper Title in italic*. Tilgjengelig fra: URL (Accessed: date).
    """
    elements = [
        format_creators(item.get("creators")),
        f"({format_date(item.get('date'))})",
        f'"{item.get("title")}",',
        f"*{item.get('publicationTitle')}*.",
        format_url(item),
    ]
    return elements


def format_thesis_citation(item) -> str:
    """Surname, Initial(s). (Year) Thesis Title in italic. Type of thesis. Institution."""
    elements = [
        format_creators(item.get("creators")),
        f"({format_date(item.get('date'))})",
        f"*{item.get('title')}*.",
    ]

    if thesis_type := item.get("thesisType"):
        elements.append(thesis_type + ".")

    if institution := item.get("university"):
        elements.append(institution + ".")

    elements.append(format_url(item))
    return elements


def format_book_section_citation(item: dict) -> str:
    """Harvard reference style for book sections:

    Surname, Initial(s). (Year) Title of chapter, in Surname of the editor(s), Initial(s) (ed.) Book title in italics. Edition. Place: Publisher, Page.
    """
    elements = [
        format_creators(item.get("creators")),
        f"({format_date(item.get('date'))})",
        f'"{item.get("title")}"',
    ]

    if editors := format_creators(item.get("creators"), creator_type="editor"):
        elements.append(f"in {editors} (ed.)")

    if book_title := item.get("bookTitle"):
        elements.append(f"*{book_title}*.")
    if edition := item.get("edition"):
        elements.append(edition)

    if (place := item.get("place")) and (publisher := item.get("publisher")):
        elements.append(f"{place}: {publisher},")

    if pages := item.get("pages"):
        elements.append(pages + ".")

    elements.append(format_url(item))

    return elements


def format_book_citation(item: dict) -> str:
    """Harvard reference style for books:

    Author surname, initial. (Year) *Book title*. Edition. Place: Publisher.
    """
    elements = []

    elements.append(format_creators(item.get("creators")))
    elements.append(f"({format_date(item.get('date'))})")
    elements.append(f"*{item.get('title')}*.")

    if edition := item.get("edition"):
        elements.append(edition + ".")

    if city := item.get("place"):
        elements.append(city + ":")

    if publisher := item.get("publisher"):
        elements.append(publisher + ".")

    elements.append(format_url(item))

    return elements


def format_article_citation(item: dict) -> str:
    """Harvard reference style for journal articles:

    Surname, Initial(s). (Year) Article title, Title of journal in italics, volume(number), page. doi (if applicable)
    Surname, Initial(s). (Year of Publication) Title of paper, Title of the conference in italics. Place and date of the conference. Place published: Publisher, Page.
    """
    elements = []

    elements.append(format_creators(item.get("creators")))
    elements.append(f"({format_date(item.get('date'))})")
    elements.append(f'"{item.get("title")}",')

    if proceedings := item.get("proceedingsTitle"):
        elements.append(f"*{proceedings}*,")

    if journal := item.get("publicationTitle"):
        elements.append(f"*{journal}*,")

    if (volume := item.get("volume")) and (issue := item.get("issue")):
        elements.append(f"{volume}({issue}),")

    if pages := item.get("pages"):
        elements.append(f"{pages}.")

    if doi := item.get("doi"):
        elements.append(f"doi:{doi}.")

    elements.append(format_url(item))

    return elements


def format_creators(authors: list, creator_type="author") -> str:
    """Format author names in Harvard reference style."""
    if not authors:
        return ""
    _authors = [
        f"{author['lastName']}, {author['firstName']}"
        for author in authors
        if author["creatorType"] == creator_type
    ]
    n_authors = len(_authors)
    match n_authors:
        case 1:
            authorlist = _authors[0]
        case 2:
            authorlist = " and ".join(_authors)
        case 3:
            authorlist = ", ".join(_authors[:2]) + ", og " + _authors[2]
        case _:
            authorlist = _authors[0] + " et al."
    return authorlist


def format_date(date: str, full: bool = False) -> str | None:
    """Format date in Harvard reference style."""
    try:
        if full:
            date = datetime.fromisoformat(date).strftime("%Y-%m-%d")
        else:
            date = datetime.fromisoformat(date).year
    except ValueError:
        date = date.split("-")[0]
    return date if date else ""


def format_url(data: dict) -> str | None:
    url = data.get("url")
    access_date = data.get("accessDate")
    if not url:
        return ""

    formatted_url = f"\nTilgjengelig fra: {url}"

    if access_date == "":
        return formatted_url

    date = format_date(access_date, full=True)
    formatted_url += f" (Hentet: {date})"
    return formatted_url


def generate_citations(library_id, library_type, api_key, output_path):
    """Call the Zotero API and retrieve all citations in a library.
    Format the citations and write them to a markdown file at the
    specified output path.

    Arguments:
        library_id {str} -- Zotero Library ID
        library_type {str} -- 'group' or 'user'
        api_key {str} -- personal Zotero API key. See user account settings in Zotero.
        output_path {str} -- File path where to write the markdown formatted citations.
    """

    zot = zotero.Zotero(library_id, library_type, api_key)
    items = [
        item
        for item in zot.collection_items("JWSHLR3R")
        if item["meta"].get("parsedDate") is not None
    ]

    # Reverse sort by date
    # items = sorted(items, key=lambda d: (d["meta"]["parsedDate"].split('-')[0], d['data']['creators'][0]['lastName'] ), reverse=True)
    items = sorted(
        items,
        key=lambda d: (
            d["meta"]["parsedDate"].split("-")[0],
            d["data"]["creators"][0]["lastName"],
        ),
        reverse=True,
    )
    formatted_citations = []
    # Format in reference style Harvard
    for item in items:
        data = item["data"]
        print(data)
        item_type = data["itemType"]

        match item_type:
            case "journalArticle" | "conferencePaper":
                citation_elements = format_article_citation(data)
            case "book":
                citation_elements = format_book_citation(data)
            case "thesis":
                citation_elements = format_thesis_citation(data)
            case "bookSection":
                citation_elements = format_book_section_citation(data)
            case "newspaperArticle":
                citation_elements = format_newspaper_article_citation(data)
            case _:
                # Notes or attachments are not interesting for citation
                print(f"Item type {item_type} not supported.")
                continue

        formatted_citation = " ".join(citation_elements)
        formatted_citations.append(formatted_citation)

    with open(output_path, "w+") as f:
        f.write("---\nlayout: page\ntitle: Bibliografi\n---\n\n")
        f.write("# DH-lab bibliografi\n")
        f.write("*Sortert ny --> gammel*\n\n\n")
        [f.write(c + "\n\n") for c in formatted_citations]

    print(
        "Process complete.",
        len(formatted_citations),
        "citations written to",
        output_path,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("library", help="Library ID", type=str)
    parser.add_argument("library_type", help="Library type: group or user", type=str)
    parser.add_argument("api_key", help="Zotero API key", type=str)
    parser.add_argument(
        "output_path", help="Output file path where citations will be written", type=str
    )
    args = parser.parse_args()

    generate_citations(args.library, args.library_type, args.api_key, args.output_path)


if __name__ == "__main__":
    main()
