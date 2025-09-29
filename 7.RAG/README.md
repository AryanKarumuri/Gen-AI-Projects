# RAG (Retrieval-Augmented Generation) Resources

This folder contains various resources and implementations related to Retrieval-Augmented Generation (RAG).

## Prerequisites: Understanding Text Splitting

Before diving into RAG implementations, it's crucial to understand text splitting. The effectiveness of a RAG system heavily depends on how documents are split into chunks. Poor text splitting can lead to:
- Loss of context in responses
- Irrelevant retrievals
- Missed important information
- Increased costs due to inefficient token usage

Familiarize yourself with different text splitting approaches (character-based, token-based, semantic, or special-purpose) as they significantly impact RAG performance. To learn more about text splitting:
- [Text-Splitters](https://github.com/AryanKarumuri/Gen-AI-Projects/tree/main/7.RAG/Text-Splitters/Text-Splitters.ipynb): Comprehensive guide and examples of different text splitting strategies

## Implementations

- [Basic RAG](https://github.com/AryanKarumuri/Gen-AI-Projects/tree/main/7.RAG/basic_rag.ipynb): Introduction to RAG and its basic implementation.
- [RAG with FlashReranker](https://github.com/AryanKarumuri/Gen-AI-Projects/tree/main/7.RAG/rag_with_flashreranking.ipynb): Advanced RAG implementation utilizing FlashReranker for enhanced ranking efficiency.
- [RAG_with_MultiQueryRetriever](https://github.com/AryanKarumuri/Gen-AI-Projects/blob/main/7.RAG/rag_with_multiquery_retreiver.ipynb): Implementation of RAG with MultiQueryRetriever to improve retrieval by generating diverse query variations for better context and answers.
- [RAG with Hybrid Retrievers and Reranker](https://github.com/AryanKarumuri/Gen-AI-Projects/tree/main/7.RAG/rag_with_hybrid_retriever_and_reranker.ipynb): Implementation of RAG using hybrid retrievers and a reranker for improved retrieval.
- [RAG with MergerRetriever and LongContextReorder](https://github.com/AryanKarumuri/Gen-AI-Projects/tree/main/7.RAG/rag_with_MergerRetriever_and_LongContextReorder.ipynb): Implementation of RAG using MergerRetriever and LongContextReorder for managing long and diverse contexts for improved output quality.

Explore these notebooks to understand different approaches and techniques used in RAG-based models.
