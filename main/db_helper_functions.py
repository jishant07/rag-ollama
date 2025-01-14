import string
import random

def reference_id_generator():
    reference_id = ""
    corpus = string.ascii_lowercase + string.ascii_uppercase
    for _ in range(15):
        reference_id = reference_id + \
            corpus[random.randrange(0, len(corpus)-1)]
    return reference_id