from numba import njit
import numpy as np
import threading
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import nltk
import os

def _safety_import_():
    # Check whether imported modules work fine
    ## nltk ##
    # set environ variable
    os.environ['NLTK_DATA'] = os.path.join(os.getcwd(), "support","nltk_data")
    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        print("Punkt is not downloaded, Downloading")
        _status = nltk.download("punkt", download_dir=os.environ['NLTK_DATA'])
        if _status:
            print("Punkt is downloaded")
        else:
            print("Unable to download punkt")

@dataclass
class Word:
    """Contains name of the word its frequency and inverse frequency across documents"""
    name: str
    freq: int = 0
    ifreq: int = 0 
    
class BM25:
    def __init__(self, num_docs, file_ls):
        self.num_docs = num_docs
        self.files = file_ls
        # Key: token, Value: Word
        self.words = {}
        self.WORKER_THREADS = 10
    def collect_words(self):
    def ext_metrics(self, file_path):
        rem_specials = lambda w: [c for c in w if w.isalnum()]
        vec_rem_sp = np.vectorize(rem_specials)
        with open(file_path) as file:
            # Store words and its count
            words={}
            # Read file
            data = file.read()
            # Tokenize entire text into words
            word_ls = np.array(nltk.word_tokenize(data))
            # Remove all non-alnum characters
            word_ls = wordls[word_ls.isalnum()]
            # Remove special characters within the words
            word_ls = vec_rem_sp(word_ls)
            # Count all the unique words in the count
            unique_words, counts = np.unique(word_ls, return_counts=True)
            # Assign each word and its count in the return var
            for index,word in enumerate(unique_words):
                words[word] = self.words.get(word, [])
                words[word].append(counts[index])
            return words
    def ext_docs(self):
        # Create a thread to execute collection of words and its counts
        thread = threading.Thread(target = self.collect_words, daemon=True).start()
        # Execute multiple threads
        with ThreadPoolExecutor(self.WORKER_THREADS) as executor:
            results = executor.map(self.ext_metrics, *self.files)
    def idf(self, qi, N):
        pass
    def bm25(self, qi, d, k1, b):
        pass    
