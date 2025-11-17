import numpy as np
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from ragas import EvaluationDataset
from ragas import evaluate
from ragas.llms import LangchainLLMWrapper

llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.4)


sample_docs = [
    "Albert Einstein proposed the theory of relativity, which transformed our understanding of time, space, and gravity.",
    "Marie Curie was a physicist and chemist who conducted pioneering research on radioactivity and won two Nobel Prizes.",
    "Isaac Newton formulated the laws of motion and universal gravitation, laying the foundation for classical mechanics.",
    "Charles Darwin introduced the theory of evolution by natural selection in his book 'On the Origin of Species'.",
    "Ada Lovelace is regarded as the first computer programmer for her work on Charles Babbage's early mechanical computer, the Analytical Engine.",
    "Nikola Tesla made groundbreaking contributions to the development of alternating current (AC) electrical systems and wireless communication.",
    "Galileo Galilei improved the telescope and made key astronomical discoveries that supported the heliocentric model of the solar system.",
    "Stephen Hawking developed theories on black holes and cosmology, including Hawking radiation, deepening our understanding of the universe.",
    "Rosalind Franklin’s X-ray diffraction images were crucial in discovering the double-helix structure of DNA.",
    "Alan Turing laid the groundwork for computer science and artificial intelligence with his concept of the Turing Machine."
]


class RAG:
    def __init__(self, model):
        self.llm = ChatGoogleGenerativeAI(model=model)
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.doc_embeddings = None
        self.docs = None

    def load_documents(self, documents):
        """Load documents and compute their embeddings."""
        self.docs = documents
        self.doc_embeddings = self.embeddings.embed_documents(documents)

    def get_most_relevant_docs(self, query):
        """Find the most relevant document for a given query."""
        if not self.docs or not self.doc_embeddings:
            raise ValueError("Documents and their embeddings are not loaded.")

        query_embedding = self.embeddings.embed_documents(query)
        similarities = [
            np.dot(query_embedding, doc_emb)
            / (np.linalg.norm(query_embedding) * np.linalg.norm(doc_emb))
            for doc_emb in self.doc_embeddings
        ]
        most_relevant_doc_index = np.argmax(similarities)
        return [self.docs[most_relevant_doc_index]]

    
    

rag = RAG(model="gemini-1.5-pro")
rag.load_documents(sample_docs)
query = "Who is known as the first computer programmer?"
relevant_docs = rag.get_most_relevant_docs(query)
answer = rag.generate_answer(query, relevant_docs)

sample_queries = [
    "Who introduced the theory of relativity?",
    "Who was the first computer programmer?",
    "What did Isaac Newton contribute to science?",
    "Who won two Nobel Prizes for research on radioactivity?",
    "What is the theory of evolution by natural selection?"
]

expected_responses = [
    "Albert Einstein proposed the theory of relativity, which transformed our understanding of time, space, and gravity.",
    "Ada Lovelace is regarded as the first computer programmer for her work on Charles Babbage's early mechanical computer, the Analytical Engine.",
    "Isaac Newton formulated the laws of motion and universal gravitation, laying the foundation for classical mechanics.",
    "Marie Curie was a physicist and chemist who conducted pioneering research on radioactivity and won two Nobel Prizes.",
    "Charles Darwin introduced the theory of evolution by natural selection in his book 'On the Origin of Species'."
]
dataset = []

for query,ground_truth in zip(sample_queries,expected_responses):

    relevant_docs = rag.get_most_relevant_docs(query)
    dataset.append(
        {
            "user_input":query,
            "retrieved_contexts":relevant_docs,
            "reference":ground_truth
        }
    )

evaluation_dataset = EvaluationDataset.from_list(dataset)




evaluator_llm = LangchainLLMWrapper(llm)
from ragas.metrics import LLMContextRecall, Faithfulness, FactualCorrectness

result = evaluate(dataset=evaluation_dataset,metrics=[LLMContextRecall(), Faithfulness(), FactualCorrectness()],llm=evaluator_llm)
result
