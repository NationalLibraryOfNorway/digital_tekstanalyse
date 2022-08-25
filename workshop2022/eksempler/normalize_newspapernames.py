import pandas as pd

def get_normalized_names(s : pd.DataFrame):
    """Normalizes newspapernames for search in DHLAB-metadata. Lowers caps, normalizes æøå and strips punctuation.

    :param s: Paper names and party affiliation 
    :type s: pd.DataFrame
    :return: df with column of normalized names
    :rtype: _type_
    """
    
    normalized = []
    
    for ind, avis in s.iterrows():
        avis_formatted = (avis['avis'].lower()
                        .replace(' ', '')
                        .replace('æ', 'ae')
                        .replace('å', 'aa')
                        )
        avis_formatted = ''.join(ch for ch in avis_formatted if ch.isalnum())
        
        if 'ø' in avis['avis']:
            x1 = avis_formatted.replace('ø', 'o')
            x2 = avis_formatted.replace('ø', 'oe')
            
            normalized += [[avis['avis'], avis['parti'], x1], [avis['avis'], avis['parti'], x2]]
            
        else:
            normalized += [[avis['avis'], avis['parti'], avis_formatted]]
         
            
            
    return pd.DataFrame(normalized, columns=['avis', 'parti', 'normalisert'])