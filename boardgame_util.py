from difflib import SequenceMatcher

SIMILARITY_THRESHOLD = 0.75

##
# utility methods
## 
def similar(a, b):
    sim_ratio = SequenceMatcher(None, a.lower(), b.lower()).ratio()
    return sim_ratio >= SIMILARITY_THRESHOLD
