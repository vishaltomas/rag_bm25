from bm25 import BM25
import os 

file_path = os.path.join(".","samples","web")
file_ls = []
for (path,dirs,files) in os.walk(file_path):
    for file in files:
        file_ls.append(os.path.join(path,file))
# extract all the documents in listed in the file_ls
# file_ls should contain the file path of the file
bm25 = BM25(file_ls=file_ls)
bm25.ext_docs()
# Calculate bm25 scores for each words w.r.t each document
bm25.calc_scores(k1=1.2, b=.75)
# Store radix tree of the words
bm25.store_index()
del bm25
# Start fresh from loading the written cache files
bm25 = BM25()
bm25.load_word_tree()
score = bm25.get_score("On a computer keyboard which letter on the same line is between C and B?")
print("\n----------\nTop K documents\n----------")
for doc in bm25.topk(k=7, score=score):
    print(doc)
