from ragas import evaluate
from ragas.metrics import answer_correctness
from datasets import Dataset
from ragas.run_config import RunConfig
import asyncio

import pandas as pd 

class Ragas_Evaluation:
    def __init__(self,dataset, evaluate_llm,embedding):
        self.data = dataset
        self.llm = evaluate_llm
        self.embedding = embedding
    print("Preparing the Data For the Evaluation part ")
    def data_prepare (self):
        print("It call the data preparation funcation successfully")
        self.data['Video__ID'] = [f"Evaluate video {i}" for i in range(len(self.data))]
        eval_data = Dataset.from_dict({
            'user_input': self.data['Video__ID'].tolist(),
            'response':self.data['analysis'].tolist(),
            'ground_truth': self.data['ground_truth'].tolist()
        })
        print("data evaluation is happened now returning the eval_data")
        return eval_data
    
    async def run_evaluation(self, run_config, batch_size: int = 5, delay_seconds: int = 60):
        print("It call the run_evaluation funcation successfully")
        
        eval_data = self.data_prepare()
        full_results_df_list = []
        
        # Manually loop over the data in batches
        for i in range(0, len(eval_data), batch_size):
            # Select the current batch
            batch_data = eval_data.select(range(i, min(i + batch_size, len(eval_data))))
            
            print(f"\nProcessing batch {i // batch_size + 1}: rows {i} to {i + len(batch_data) - 1}")
        print("It call the run_evaluation funcation successfully")
        # defining the LLm part into this 

        
        eval_data = self.data_prepare()
        print("The eval_data give to me successfull")
        print(f"calling the user__input of eval that dataset {eval_data['user_input'][:2]}")
        print(f"calling the response of eval data {eval_data['response'][:2]}")
        print(f"calling the ground truth column of eval  {eval_data['ground_truth'][:2]}")

       
         
        result =  evaluate(
            dataset=eval_data,
            metrics=[answer_correctness],
            llm=self.llm,
            embeddings=self.embedding,
            run_config= RunConfig
        )
        full_results_df_list.append(result.to_pandas())
            
            # Forced delay using asyncio.sleep()
            # ONLY pause if there are more batches to process
        if i + len(batch_data) < len(eval_data):
            print(f"Quota safety delay: Sleeping for {delay_seconds} seconds to reset the 1-minute quota...")
            await asyncio.sleep(delay_seconds) # Pause for 60 seconds

        # Combine all batch results into a final DataFrame
        final_df = pd.concat(full_results_df_list, ignore_index=True)
        print("Evaluation happened successfully now returning the final results ")
        return final_df
    