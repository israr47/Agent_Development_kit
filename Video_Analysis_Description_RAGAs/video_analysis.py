import asyncio
import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI
from datasets import Dataset
from ragas.llms import llm_factory, InstructorLLM, LangchainLLMWrapper
from evaluation_class.Evaluation import Ragas_Evaluation
from ragas.run_config import RunConfig
from dotenv import load_dotenv
import os
load_dotenv()

# Loading the model
api_key = os.getenv("GOOGLE_API_KEY")

config = {
    "model": "gemini-1.5-pro",  # or other model IDs
    "temperature": 0.4,
    "max_tokens": None,
    "top_p": 0.8,
    # For Vertex AI only:
    "project": "your-project-id",  # Required for Vertex AI
    "location": "us-central1",     # Required for Vertex AI
}



# importing the Datasets into 
def load_document(path: str):
    """Loading the data of csv file using pandas libarary 
    and which contain two columns and the videos_analysis and Ground_truth
    """
    dataset = pd.read_csv(path)
    # check for the columns in the dataset 
    excepted_col = ['analysis', 'ground_truth']
    #drop the missing values from the 
    dataset.dropna(subset=excepted_col, inplace=True)
    print("The dataset contain the following ")
    print(f"the number of columns contain is {list(dataset.columns)}")

    print(dataset.head(2))
    return dataset

print("Loading the Dataset")
data = load_document(path=r"C:\Users\PMLS\Desktop\Google_adk_ragas\Video_Analysis_Description_RAGAs\pitcher_analysis.csv")

print("after laoding the dataset")

from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(api_key=api_key, model="textembedding-gecko-001")
async def main():
    evaluator_llm = LangchainLLMWrapper(ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        max_retries=10, 
    #CRITICAL CHANGE: Increase the timeout (e.g., to 120 seconds)
        timeout=120
    ))

    rate_limit_config = RunConfig(
        max_workers=1,
        max_retries=5,
        timeout=120
    )
     

    print("Calling the evaluation class for evaluation part")
    ragas_evaluation = Ragas_Evaluation(dataset=data,evaluate_llm=evaluator_llm,embedding=embeddings)
    result = await ragas_evaluation.run_evaluation(
        run_config=rate_limit_config,
        batch_size=5,    # Process 5 rows at a time
        delay_seconds=60 # Wait 60 seconds between each batch
    )

    print("The result of the ragas evaluation ")
    print(result)

asyncio.run(main())


