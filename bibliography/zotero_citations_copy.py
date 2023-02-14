# Philip Bailey
# 29 Jan 2020
# Script to generate markdown file listing of citations within a Zotero library
# https://pyzotero.readthedocs.io/en/latest/
# -------------------------------------------------------------
import argparse
from pyzotero import zotero


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
    items = zot.top(limit=50)
    # Reverse sort by date
    items = sorted(items, key=lambda d: (d["meta"]["parsedDate"].split('-')[0], d['data']['creators'][0]['lastName'] ), reverse=True)
    formatted_citations = []
    for item in items:

        authors = ''
        if 'creators' in item['data']:
            authors = '; '.join(['{}, {}'.format(author['lastName'], author['firstName']) for author in item['data']['creators'] if author['creatorType'] != "editor"])
    
        date = item['meta']['parsedDate'].split('-')[0] if 'parsedDate' in item['meta'] else ''

        if 'url' in item['data'] and len(item['data']['url']) > 0:
            title = '[{}]({})'.format(item['data']['title'], item['data']['url'])
        else:
            title = item['data']['title']

        pub = ''
        if 'publicationTitle' in item['data']:
            pub = item['data']['publicationTitle']
        elif 'publisher' in item['data']:
            pub = item['data']['publisher']
        
        if pub != '':
            pub += ". "

        doi = ''
        if 'DOI' in item['data']:
            if item['data']['DOI'] != '':
                doi = 'DOI: [{0}](https://doi.org/{0})'.format(item['data']['DOI'])

        citation = '{} {}. {}. {}{}'.format(
            authors,
            date,
            title,
            pub,
            doi)

        formatted_citations.append(citation)


    with open(output_path, 'w+') as f:
        f.write('---\nlayout: page\ntitle: Bibliografi\n---\n\n')
        f.write("# DH-lab bibliografi\n")
        f.write("*Sortert ny --> gammel*\n\n\n")
        [f.write(c + '\n\n') for c in formatted_citations]

    print('Process complete.', len(formatted_citations), 'citations written to', output_path)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('library', help='Library ID', type=str)
    parser.add_argument('library_type', help='Library type: group or user', type=str)
    parser.add_argument('api_key', help='Zotero API key', type=str)
    parser.add_argument('output_path', help='Output file path where citations will be written', type=str)
    args = parser.parse_args()

    generate_citations(args.library, args.library_type, args.api_key, args.output_path)


if __name__ == '__main__':
    main()
