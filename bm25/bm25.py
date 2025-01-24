from numba import njit
import numpy as np
import threading
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
from nltk import word_tokenize, data as nltk_data, download as nltk_download
import os
from queue import Queue
from .radix import RadixTree

def _safety_import_():
    # Check whether imported modules work fine
    ## nltk ##
    # set environ variable
    os.environ['NLTK_DATA'] = os.path.join(os.getcwd(), "support","nltk_data")
    try:
        nltk_data.find(os.path.join(os.environ['NLTK_DATA'], "tokenizers", "punkt_tab"))
        print("Requirement punkt_tab is found.")
    except LookupError:
        print(f"punkt_tab is not found at {os.environ['NLTK_DATA']}, Downloading")
        _status = nltk_download("punkt_tab", download_dir=os.path.join(os.environ['NLTK_DATA'], "tokenizers", "punkt_tab"))
        if _status:
            print("punkt_tab is downloaded")
        else:
            print("Unable to download punkt_tab")
    finally:
        nltk_data.path.append(os.environ['NLTK_DATA'])

@dataclass
class Word:
    """Contains name of the word, its frequency and inverse frequency across documents"""
    name: str = ""
    freq: list = field(default_factory=list) 
    doc: list = field(default_factory=list)
    doclen: list = field(default_factory=list)
    idf: int = 0
    bm25: list = field(default_factory=list)
    
class BM25:
    def __init__(self, file_ls:list=[]):
        self.files = file_ls
        # Key: token, Value: Word
        self.words = {}
        self.words_queue = Queue()
        self.rt = RadixTree()
        self.word_pos = []
        self.WORKER_THREADS = 10
        self.total_gathered = 0
        self.rem_specials = lambda w: ''.join([c for c in w if c.isalnum()])
        self.rem_special_words = lambda w: w.isalnum()
        self.CACHE_PATH = "./support/cache"
        
    def collect_words_from_queue(self, event):
        while not event.is_set():        
            words, doc, doclen = self.words_queue.get()
            if words==None:
                self.words_queue.task_done()
                break
            try:
                for word in words.keys():
                    self.words[word] = self.words.get(word, Word(name=word))
                    self.words[word].freq += [words[word]]
                    self.words[word].doc += [doc]
                    self.words[word].doclen += [doclen]
                self.total_gathered+=1
            except Exception as e:
                print("Gathernig didn't work for doc: ", doc, " due to: ", e)
            finally:
                self.words_queue.task_done()
        print("Finished queue execution")
        return

    def ext_metrics(self, file_path):
        vec_rem_special_words = np.vectorize(self.rem_special_words)
        vec_rem_sp = np.vectorize(self.rem_specials)
        file_name = file_path.split("\\")[-1]
        # print("Extracting metrics from file: ", file_name)
        with open(file_path, encoding="utf-8") as file:
            # Store words and its count
            words={}
            # Read file
            data = file.read()
            # Tokenize entire text into words
            word_ls = np.array(word_tokenize(data)) 
            doclen = len(word_ls)
            # Remove all non-alnum characters
            word_ls = word_ls[vec_rem_special_words(word_ls)]
            # Remove special characters within the words
            word_ls = vec_rem_sp(word_ls)
            # Count all the unique words in the count
            unique_words, counts = np.unique(word_ls, return_counts=True)
            # Assign each word and its count in the return var
            for index,word in enumerate(unique_words):
                word = word.lower()
                words[word] = int(counts[index])
            # print("Extracting finished for: ", file_name)
            self.words_queue.put((words, file_name, doclen))
            return True
        
    def ext_docs(self):
        # Create a thread to execute the gathering of words from queue and its counts
        thread_event = threading.Event()
        thread = threading.Thread(target = self.collect_words_from_queue, args=(thread_event,))
        thread.start()
        # Execute multiple threads
        with ThreadPoolExecutor(self.WORKER_THREADS) as executor:
            results = executor.map(self.ext_metrics, self.files)
        if not (sum(results) == len(self.files)):
            print("Not all files are executed properly")
        print("Extracted metrics for all files")
        # To exit from thread function's loop
        self.words_queue.put((None,None,None))
        # To wait until all elements are processed in queue
        self.words_queue.join()
        thread_event.set()
        print("Completed prrocessing from queue")
        thread.join()
        if(self.total_gathered == len(self.files)):
            print("Gathered words from all files and its counts.")

    def __idf(self, qi:str, N:int):
        # Calculting inverse document frequency
        nqi = len(self.words.get(qi.lower(), Word()).doc)
        return np.log((N-nqi+0.5)/(nqi+0.5)+1)
    
    def __bm25(self, qi:int, i:int, d:int, k1:float, b:float, N:int, davgl:float):
        # Calculating BM25 score for each qi
        # For each qi(that is word 'i' in the query) score is calculated
        # later at the time of retreival, scores of each qi is summed up
        fqi = self.words[qi.lower()].freq[i]
        idf = self.words[qi.lower()].idf
        return (idf*fqi*(k1+1)/(fqi + k1*(1-b+b*d/davgl)))
    
    
    def calc_scores(self, k1, b):
        # self.words contains words as keys and Word(name, freq:list, doc:list, doclen:list, bm25:list, idf:float) as values
        # For faster calculations, intialize array with numpy
        arr = np.array(list(self.words.values()))
        # Calculate idf for each words and BM25 for each words w.r.t each documents
        def idf_bm25_calc(word_obj):
            qi = word_obj.name.lower()
            doclen = word_obj.doclen
            N =  len(self.files)
            freq = word_obj.freq
            word_obj.idf = float(self.__idf(qi,N))
            word_obj.bm25 = [round(self.__bm25(qi, i, doclen[i], k1, b, N, sum(doclen)/len(doclen)),5) for i,f in enumerate(freq)]
            return None
        idf_bm25_calc_vec = np.vectorize(idf_bm25_calc)
        idf_bm25_calc_vec(arr)
    def store_index(self):
        import pickle
        # store the values in a file which is suitable for fast retreival and updating the data
        self.rt.insert(list(self.words.keys()))
        # Initialize position for the words
        # with open("./sample_words", "w", encoding="utf-8") as file:
            # file.write("\n".join(list(self.words.keys())))
        self.rt.get_pos()
        # As of now we will store the tree as object file using pickle
        try:
            if not os.path.exists(self.CACHE_PATH):
                os.mkdir(self.CACHE_PATH)
            with open(f"{self.CACHE_PATH}/radix_words.pickle", "wb") as file:
                pickle.dump(self.rt, file, pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            print("Error in saving words as radix tree: ",e)
        # store list 
        word_obj_ls = ['']*len(self.words)
        # convert list to string
        conv_ls = lambda l: ','.join([str(s) for s in l])
        # get position of each word in lexicographical order 
        for word in self.words.keys():
            is_retreived, pos = self.rt.search(word=word)
            # print("word: ", word, " position: ",pos)
            if is_retreived:
                word_obj = self.words[word]
                content = f"{conv_ls(word_obj.freq)}|{conv_ls(word_obj.doc)}|{conv_ls(word_obj.doclen)}|{word_obj.idf}|{conv_ls(word_obj.bm25)}"
                word_obj_ls[pos-1] = content
            else:
                print(word)

        with open(f"{self.CACHE_PATH}/words.meta", "w") as file:
            file.write("\n".join(word_obj_ls))
        # To find the actual position of the content in file
        word_ls_pos = [0]
        for index, content in enumerate(word_obj_ls):
            word_ls_pos.append(word_ls_pos[index] + len(content) + 2)
        with open(f"{self.CACHE_PATH}/word_position.pickle", "wb") as file:
            pickle.dump(word_ls_pos, file, pickle.HIGHEST_PROTOCOL)

    def load_word_tree(self):
        import pickle
        # load radix tree and word position object
        rt_fd = open(f"{self.CACHE_PATH}/radix_words.pickle", "rb")
        word_pos_fd = open(f"{self.CACHE_PATH}/word_position.pickle", "rb")
        self.rt = pickle.load(file=rt_fd)
        self.word_pos = pickle.load(file=word_pos_fd) 
        rt_fd.close()
        word_pos_fd.close()

    def get_score(self, query:str) -> dict[str, int]:
        self.load_word_tree()
        words = word_tokenize(query)
        words = list(filter(self.rem_special_words, words))
        words = [self.rem_specials(word) for word in words]
        self.score = {}
        prop_file = open(f"{self.CACHE_PATH}/words.meta","rt")
        prop_fd = prop_file.fileno()
        for word in words:
            is_retrieved, position = self.rt.search(word)
            # print("word: ", word, " position: ",position)
            if is_retrieved:
                begin_pos = self.word_pos[position-1] 
                end_pos = self.word_pos[position]
                # print("begin: ", begin_pos, "end: ", end_pos)
                os.lseek(prop_fd, begin_pos, os.SEEK_SET)
                prop_data = os.read(prop_fd, end_pos-begin_pos).decode("utf-8").rstrip("\n").rstrip("\r").split("|")
                prop_bm25 = prop_data[-1].split(",")
                # print(prop_data)
                # assign or add to the score for each document
                for index,doc in enumerate(prop_data[1].split(",")):
                    self.score[doc] = self.score.get(doc, 0) + float(prop_bm25[index])
        prop_file.close()            
        # print(self.score)
        return self.score

    def topk(self, k:int, score:dict) -> str:
        sort_val = sorted(score.items(), key = lambda item: item[1], reverse=True)
        for index in range(k):
            yield sort_val[index][0]
        

