from numba import njit
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import  as_completed
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
    def ext_metrics(self, file_path):
        with open(file_path) as file:
            data = file.read()
            nltk.word_tokenize(data)
    def ext_docs(self):
        # Execute multiple threads
        with ThreadPoolExecutor(self.WORKER_THREADS) as executor:
            tasks = executor.map()
    def idf(self, qi, N):
        pass
    def bm25(self, qi, d, k1, b):
        pass    