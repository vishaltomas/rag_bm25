# Retrieval Augmented Generation for LLMs
<p>Retrieval Augmented Generation is a technique used for retrieving relevant documents based on a query and supply the relevant contents of the documents to a generator for answering the query.
For the retrieval there are mainly two types sparse retrieval and dense retrieval mechanisms. Sparse retrieval uses sparse vector representations for query and documents. Dense retrieval uses embeddings 
for representing the query and documents.
As below shown currently the retrieval is based on sparse mechanism. BM25 score is used to retrieve the relevant documents based on the query provided by the user.
  
![rag_bm25_80](https://github.com/user-attachments/assets/dc1e7d46-ddf3-4e13-a7b6-a2a05f2683b9)

  ## Usage
  
  ```python
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

```

</p>
