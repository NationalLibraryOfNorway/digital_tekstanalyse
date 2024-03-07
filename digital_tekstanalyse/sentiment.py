import logging
import numpy as np
import pandas as pd
import requests

from collections import Counter
from pathlib import Path
from typing import Generator, List, Union

import dhlab as dh
from dhlab.api.dhlab_api import concordance, get_chunks_para
from dhlab.constants import BASE_URL
from dhlab.nbtokenizer import tokenize


# File handling util functions
def load_corpus_from_file(file_path):
    """Load a Corpus object from an excel or csv file."""
    try:
        corpus = (
            dh.Corpus.from_df(pd.read_excel(file_path))
            if file_path.endswith(".xlsx")
            else dh.Corpus.from_csv(file_path)
        )
    except FileNotFoundError:
        print("The corpus file must be a .csv or .xlsx file: ", file_path)
        corpus = dh.Corpus()
    return corpus


def load_sentiment_terms(fpath: str = None) -> pd.Series:
    """Load a sentiment lexicon from a file path."""
    if fpath is None or not Path(fpath).exists:
        print("File not found: ", fpath)
    return pd.read_csv(fpath, names=["terms"])


def load_norsentlex() -> List[pd.Series]:
    """Load the sentiment lexicons from ``ǸorsentLex``.

    - Github repo [norsentlex](https://github.com/ltgoslo/norsentlex)
    - [Lexicon information in neural sentiment analysis:
    a multi-task learning approach](https://aclanthology.org/W19-6119) (Barnes et al., NoDaLiDa 2019)
    """
    fpath = "https://raw.githubusercontent.com/ltgoslo/norsentlex/master/Fullform/Fullform_{sentiment}_lexicon.txt"
    pos, neg = [
        load_sentiment_terms(fpath.format(sentiment=sent))
        for sent in ("Positive", "Negative")
    ]
    return pos, neg


# Helper functions
def make_list(value) -> list:
    """Turn a string or list into a list.

    :param value: Can be a list, a single valued string, a comma-separated string of values,
        or a multiline string of values separated by newline.
    """
    if isinstance(value, str):
        if value.__contains__("\n"):
            newlist = value.strip("\n").strip().split("\n")
        elif value.__contains__(","):
            newlist = value.split(",")
        else:
            newlist = [value]
        return [v.strip() for v in newlist]
    else:
        assert isinstance(value, list)
        return value


def strip_bold_annotation(text):
    return text.replace("<b>", "").replace("</b>", "")


def make_search_link(docid: str, search_term: str = None):
    """Create a URL to the online library view of the digital object, with the search term"""

    link = f"https://www.nb.no/items/{docid}"
    return link if search_term is None else f"{link}?searchText={search_term}"


def add_urls(df):
    df["url"] = df.apply(
        lambda row: make_search_link(row.loc["urn"], row.loc["word"]), axis=1
    )
    # urls = df.apply(make_link, axis=1)
    return df


def count_tokens(text):
    text = strip_bold_annotation(text)
    tokens = tokenize(text)
    newcoll = Counter([tok.lower() for tok in tokens if not tok == "..."])
    return pd.Series(newcoll.values(), index=newcoll.keys(), name="counts")


def strip_empty_cols(df: pd.DataFrame):
    """Remove columns without values from a dataframe."""
    return df.dropna(axis=1, how="all").fillna("")


def group_index_terms(df: pd.DataFrame) -> pd.DataFrame:
    """Group duplicate index terms, make them case-insensitive, and sum up their frequency counts."""
    if hasattr(df, "frame"):
        df = df.frame
    df = df.loc[df.index.str.isalpha()]
    df.index = df.index.str.lower()
    df = df.groupby(df.index).sum().to_frame("counts")
    return df


# Sentiment scoring functions: Number crunching


def count_terms_in_doc(
    urns: List[str],
    words: Union[list, str],
    docid_column="dhlabid"
):
    """Similar functionality as ``dhlab.api.dhlab_api.get_document_frequencies``,
    except the dataframe isn't pivoted.
    """
    params = {"urns": urns, "words": make_list(words), "cutoff": 0}
    cols = [docid_column, "word", "count", "urncount"]
    try:
        r = requests.post(f"{BASE_URL}/frequencies", json=params)
        r.raise_for_status
        result = r.json()
        df = pd.DataFrame(result, columns=cols)
    except requests.exceptions.JSONDecodeError as e:
        logging.error(f"Couldn't decode JSON object: {e}")
        logging.info(f"Returning empty dataframe instead of word counts")
        df = pd.DataFrame(columns=cols)

    df = df.drop("urncount", axis=1)
    #    df = pd.pivot_table(df, values="count", index="word", columns="urn").fillna(0)
    return df


def count_matching_tokens(token_counts: pd.DataFrame, terms: pd.Series) -> pd.DataFrame:
    """Combine word counts with a series of terms."""
    target_terms = terms.join(token_counts, how="inner", on="terms")
    return target_terms


def coll_sentiment(coll, word="barnevern", return_score_only=False):
    """Compute a sentiment score of positive and negative terms in `coll`.

    The collocations of the ``word`` are used to count occurrences of positive and negative terms.

    :param coll: a collocations dataframe or a dh.Corpus where ``word`` occurs.
    :param str word: a word to estimate sentiment scores for
    :param bool return_score_only: If True,
        return a tuple with the absolute counts for positive and negative terms.
    """
    if isinstance(coll, dh.Corpus):
        coll = coll.coll(word).frame

    coll = group_index_terms(coll)

    # Data import
    pos = load_sentiment_terms(sentiment="Positive")
    neg = load_sentiment_terms(sentiment="Negative")

    positive_counts = count_matching_tokens(coll, pos)
    negative_counts = count_matching_tokens(coll, neg)

    if return_score_only:
        return positive_counts.counts.sum(), negative_counts.counts.sum()

    neutral_counts = coll.join(
        pd.DataFrame(
            pd.concat([coll, negative_counts, positive_counts]).index.drop_duplicates(
                keep=False
            )
        ).set_index(0),
        how="inner",
    )

    positive_counts["sentiment"] = "pos"
    negative_counts["sentiment"] = "neg"
    neutral_counts["sentiment"] = "neutral"

    return pd.concat([positive_counts, negative_counts, neutral_counts])


def sentiment_by_place(
    cities=["Kristiansand", "Stavanger"],
    from_year=1999,
    to_year=2010
):

    for city in cities:
        lst = []
        for year in range(from_year, to_year):
            corpus = dh.Corpus(
                doctype="digavis", freetext=f"city: {city} year: {year}", limit=1000
            )
            pos, neg = coll_sentiment(corpus, "barnevern", return_score_only=True)

            lst.append(
                pd.DataFrame(
                    [[pos, neg, pos - neg]],
                    index=[year],
                    columns=["positive", "negative", "sum"],
                )
            )

        yield pd.concat(lst)


def score_sentiment(text, positive, negative):
    """Calculate a sentiment score for the ``text`` input."""
    context = count_tokens(text)
    sent_counts = [
        count_matching_tokens(context, sent_terms).counts.sum()
        if not context.empty
        else 0
        for sent_terms in (positive, negative)
    ]
    return sent_counts


def count_and_score_target_words(corpus: dh.Corpus, word: str):
    """Add word frequency and sentiment score for ``word`` in the given ``corpus``."""
    urnlist = corpus.corpus.urn.to_list()
    limit = 60 * len(urnlist)
    docid_column = "dhlabid"

    conc = concordance(urnlist, word, window=200, limit=limit)
    # FIXME: remove once concordance also returns dhlabid by default
    conc = conc.rename(columns={"docid": docid_column}).drop("urn", axis=1)

    word_freq = count_terms_in_doc(urnlist, [word])
    word_freq = word_freq.merge(
        conc, how="inner", left_on=docid_column, right_on=docid_column
    )

    pos, neg = load_norsentlex()

    word_freq[["positive", "negative"]] = word_freq.apply(
        lambda x: score_sentiment(x.conc, pos, neg), axis=1, result_type="expand"
    )
    word_freq["sentimentscore"] = word_freq["positive"] - word_freq["negative"]

    df = corpus.frame.merge(
        word_freq.drop(columns="conc"),
        how="inner",
        left_on=docid_column,
        right_on=docid_column,
    )
    df = strip_empty_cols(df)
    return df


def compute_sentiment_analysis(*args, **kwargs):
    """Compute sentiment score on the input data."""
    return count_and_score_target_words(*args, **kwargs)


# DUMPING GROUND

# Unnecessary function
def unpivot(frame):
    """Reshape a dataframe with multiple indexes.

    Util function copied from Pandas docs:
    https://pandas.pydata.org/pandas-docs/stable/user_guide/reshaping.html
    """
    N, K = frame.shape
    data = {
        "count": frame.to_numpy().ravel("F"),
        "urn": np.asarray(frame.columns).repeat(N),
        "word": np.tile(np.asarray(frame.index), K),
    }
    return pd.DataFrame(data, columns=["word", "urn", "count"])


# Unnecessary function
def count_terms(corpus: dh.Corpus, search_terms: str):
    """wrapper to undo the pivot in the get_document_frequencies function."""
    words = make_list(search_terms)
    count_matrix = corpus.count(words).frame
    flattened = unpivot(count_matrix)
    non_null_counts = flattened.loc[flattened["count"] != 0.0]
    return non_null_counts.reset_index(drop=True)


# Unnecessary function
def timestamp_generator(from_year: int, to_year: int) -> Generator:
    """Generate a timestamp per day in the period ``from_year``-``to_year``."""
    # range of timestamps
    timestamp_range = pd.date_range(start=f"{from_year}-01-01", end=f"{to_year}-12-31")

    for i in timestamp_range:
        date = "".join(str(i).split()[0].split("-"))
        yield date


def get_context_bow(urn, word):

    freq_col = "counts"
    token_col = "token"
    par_idx_col = "paragraph"

    # Get a dataframe with all paragraphs in a URN and their word counts
    chunks = get_chunks_para(urn)
    total = [
        {par_idx_col: i, token_col: token, freq_col: count}
        for i, para in enumerate(chunks)
        for token, count in para.items()
    ]
    df = pd.DataFrame(total)

    # Filter dataframe on the paragraphs that contain the search word
    df["lowercase"] = df[token_col].str.lower()
    matching_paragraphs = df[par_idx_col][df["lowercase"].str.match(word)]
    cdf = df[df.paragraph.isin(matching_paragraphs)]
    context = cdf[freq_col]
    context.index = cdf[token_col]
    context = group_index_terms(context)
    return context
