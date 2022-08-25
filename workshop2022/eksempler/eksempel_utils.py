
from typing import Iterable
import pandas as pd 
import dhlab as dh
from datetime import datetime



def time_period_generator(start, end = datetime.today().year, interval=10): 
    for i in range(start, end, interval): 
        yield i, i+interval


def get_longest_param_list(parameters) -> tuple: 
    parameter, args = max(parameters.items(), key=lambda x: len(x[1]) if isinstance(x[1], list) else 0)
    return parameter, args


def corpora_from_sequence(param: str = None, args: list = None, **kwargs) -> list:
    """Construct a list of corpora from multiple values of a single parameter such as author or title."""
    corpus = dh.EmptyCorpus()
    for arg in args:
        kwargs[param] = arg
        corpus.add(dh.Corpus(**kwargs))
    return corpus
    
def corpus_distributed_over_time(from_year=1800, to_year=2000, **kwargs):
    """Construct a corpus while looping over intervals in a time period. 
    
    The intervals are calculated from the total time range, 
    in order to gather an even distribution of publications from the full time period. 
    """
    corpus = dh.EmptyCorpus()
    interval = 10 if (to_year-from_year) > 10 else 1
    for start in range(from_year, to_year, interval): 
        kwargs.update(from_year=start, to_year=start+interval)
        corpus.add(dh.Corpus(**kwargs))
    return corpus

    