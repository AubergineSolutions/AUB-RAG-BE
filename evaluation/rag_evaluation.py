import pandas as pd
import logging
from langchain_openai import ChatOpenAI
from rag_chatbot.services.vectorstore import get_vectorstore

from dotenv import load_dotenv
from datasets import Dataset

import pathlib
from langchain.chains import RetrievalQA
from ragas import evaluate
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import ContextUtilization, Faithfulness, AnswerRelevancy, BleuScore, ContextRecall
from ragas.cost import get_token_usage_for_openai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Input file path - can be changed to any file
input_file_path = "test_set/SalesQuestionsTest.csv"

# Load CSV
df = pd.read_csv(input_file_path)
load_dotenv()
# Initialize OpenAI Model
llm = ChatOpenAI(model_name="gpt-4o")

# Get vector store
vectorstore = get_vectorstore()

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
def evaluate_rag(input_path=input_file_path):
    dataset_records = []
    
    # Generate output file paths based on input file
    input_path_obj = pathlib.Path(input_path)
    output_dir = input_path_obj.parent
    filename_stem = input_path_obj.stem
    
    evaluation_results_path = output_dir / f"{filename_stem}_evaluation_results.csv"
    
    logger.info(f"Input file: {input_path}")
    logger.info(f"Results will be saved to: {evaluation_results_path}")

    for _, row in df.iterrows():
        question = row["Question"]
        expected_answer = row["Answer"]

        # Retrieve relevant documents
        retrieved_context = vectorstore.similarity_search(question, k=3)

        qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, return_source_documents=True)

        response = qa_chain.invoke({"query": question})

        # Extract answer and sources
        generated_answer = response["result"]

        # Append to dataset with the correct column names expected by RAGAS
        dataset_records.append({
            "question": question,
            "answer": generated_answer,  # Changed from "response" to "answer"
            "contexts": [doc.page_content for doc in retrieved_context],
            "ground_truth": expected_answer  # Added ground truths for evaluation
        })

    # Create dataset from records
    evaluation_dataset = Dataset.from_list(dataset_records)
    
    # Initialize LLM wrapper for RAGAS
    evaluator_llm = LangchainLLMWrapper(llm)

    # Run RAGAS evaluation with proper metrics
    results = evaluate(
        dataset=evaluation_dataset,
        metrics=[
            ContextUtilization(),
            AnswerRelevancy(),
            Faithfulness(),
            ContextRecall(),
            BleuScore()  # Added BLEU score from RAGAS
        ],
        llm=evaluator_llm,
        token_usage_parser=get_token_usage_for_openai
    )
    logger.info(f"Total Usage of token: {results.total_tokens()}")

    dataframe = results.to_pandas()
    
    # Calculate mean of numeric columns
    mean_values = dataframe.select_dtypes(include=['float64', 'int64']).mean()
    
    # Create a new row for the mean values
    mean_row = pd.DataFrame([mean_values], index=['Mean'])
    
    # Append the mean row to the dataframe
    dataframe = pd.concat([dataframe, mean_row])
    
    # Save the DataFrame to CSV using dynamic filenames
    dataframe.to_csv(evaluation_results_path, index=False)
    
    logger.info(f"Evaluation completed and saved to {evaluation_results_path}")



if __name__ == "__main__":
    evaluate_rag()
