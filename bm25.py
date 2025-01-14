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
                word = word.lower()
                words[word] = self.words.get(word, [])
                words[word].append(counts[index])
            return words
    def ext_docs(self):
        # Create a thread to execute collection of words and its counts
        thread = threading.Thread(target = self.collect_words, daemon=True).start()
        # Execute multiple threads
        with ThreadPoolExecutor(self.WORKER_THREADS) as executor:
            results = executor.map(self.ext_metrics, *self.files)
    def __idf(self, qi:str, N:int):
        # Calculting inverse document frequency
        nqi = len(self.words.get(qi.lower(), Word()).doc)
        return np.log((N-nqi+0.5)/(nqi+0.5)+1)
    def __bm25(self, qi:int, d:int, k1:float, b:float, N:int, davgl:float):
        # Calculating BM25 score for each qi
        # For each qi(that is word 'i' in the query) score is calculated
        # later at the time of retreival, scores of each qi is summed up
        word_ls = self.words.keys()
        fqi = self.words[qi.lower()].freq[d] if qi in word_ls else 0
        idf = self.words[qi.lower()].idf if qi in word_ls else 0
        return idf*fqi*(k1+1)/(fqi + k1*(1-b+b*d/davgl))
    def store_index(self):
        # store the values in a file which is suitable for fast retreival and 
    def calc_scores(self, k1, b):
        # self.words contains words as keys and Word(name, freq:list, doc:list, doclen:list, bm25:list, idf:float) as values
        # For faster calculations, intialize array with numpy
        arr = np.array(self.words.values())
        # Calculate idf for each words and BM25 for each words w.r.t each documents
        def idf_bm25calc(word_obj):
            qi = word_obj.name.lower()
            doclen = word_obj.doclen
            N =  len(self.files)
            freq = word_obj.freq
            word_obj.idf = self.__idf(qi,N)
            word_obj.bm25 = [self.__bm25(qi, doclen[i], k1, b, N, avg(doclen)) for i,f in freq]
            return None
        idf_bm25_calc_vec = np.vectorize(idf_bm25_calc)
        idf_bm25_calc_vec(arr)
        
        
