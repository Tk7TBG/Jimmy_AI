# from random import choice, randint
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import GPT4AllEmbeddings

import ollama


from langchain_core.prompts import PromptTemplate
# from langchain_community.llms import Ollama
from langchain_ollama import OllamaLLM
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import RetrievalQA
# Here I just need to ask the AI to give me a response cuz the infinite loop is abstracted by the discord api and async python
messages=[]

loader = PyPDFLoader("./Testdocument.pdf")
data = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
all_splits = text_splitter.split_documents(data)

embeddings = GPT4AllEmbeddings(device="cpu")
vectorstore = Chroma.from_documents(documents=all_splits, embedding=embeddings)

template = """
Use the following pieces of context to answer the question at the end.
If you don't know the answer, just say that you don't know,
Answer in three sentences maximum, keeping it concise.
{context}
Question: {question}
Answer:"""
QA_CHAIN_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=template,
)

# Set up the LLM with the Ollama model
llm = OllamaLLM(model="llama3:8b")
# , callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(),
    chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
)

def get_response(user_input: str) -> str:
    # Replace all of this logic with our own
    # lowered: str = user_input.lower()                                                                       # This contains a log of messages from the conversation

    message={"role":"user","content":f"{user_input}"} # THis is the input                # Create a new message
    if message["content"] == "quit": 
        return "Goodbye!"     
                                           # Break the loop if the message is 'quit
    messages.append(message)       # This is the input history 


    if user_input.lower().startswith("query: "):
            query = user_input[len("query: "):]
            try:
                # Use the RetrievalQA chain for PDF-related queries
                result = qa_chain({"query": query})
                response_content = result.get("result", "I couldn't find an answer.")
                return response_content
            except Exception as e:
                print(f"Error: {e}")
                response_content = "Sorry, there was an error processing your request."    
                                                    # Append message to the log
    else:
        try:                                            
            stream=ollama.chat(model="llama3:8b",messages=messages,stream=True)                 # Call the Ollama server and return a stream
            ai_response=[]                                                                      # This contains AI Response chunks
            for chunk in stream:                                                                # Iterate through the stream
                content=chunk["message"]["content"]                                             # Get the content from the server response
                ai_response.append(content)                                                     # Append the content to the AI Response
                print(content,end='',flush=True)                                               # Print each chunk in the stream
                full_response = "".join(ai_response)
            messages.append({"role": "assistant", "content": full_response})
            return full_response  
        except Exception as e:
            print(f"Error: {e}")
            return "Sorry, there was an error processing your request."