from rag_chatbot import create_app

# Load environment variables from .env file
# load_dotenv()
#
# app = Flask(__name__)

# Allow all origins (for development purposes)
# CORS(app)  # This will allow all origins

# socketio = SocketIO(app,  cors_allowed_origins="*")  # Initialize SocketIO

# qa_chain = None

# Load PDF document
# loader = PyPDFLoader("./data/Leave Policy.pdf")

# Load documents
# loader = TextLoader("./data/leave policy.txt")

# Load CSV document
# loader = CSVLoader(file_path="./data/foods.csv")

# def get_args(filepath):
#     fields = []
#     with open(filepath, mode='r', newline='') as csvfile:
#         reader = csv.reader(csvfile)
#         fields = next(reader)

#     return {"fieldnames": fields}

# file_pth = "./data/foods.csv"
# loader = CSVLoader(file_path=file_pth, csv_args=get_args(file_pth))

# def process_file(file_path):
#     global vectorstore, qa_chain
#
#     # Determine file type and load document
#     if file_path.endswith('.pdf'):
#         loader = PyPDFLoader(file_path)
#     elif file_path.endswith('.txt'):
#         loader = TextLoader(file_path)
#     elif file_path.endswith('.csv'):
#         loader = CSVLoader(file_path)
#     else:
#         raise ValueError("Unsupported file type")
#
#     documents = loader.load()
#
#
#     # Split documents into chunks
#     text_splitter = CharacterTextSplitter(chunk_size=3000, chunk_overlap=200)
#     texts = text_splitter.split_documents(documents)
#
#     # Create embeddings and vector store
#     embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
#     vectorstore = Chroma.from_documents(texts, embeddings, persist_directory="./chroma_db")
#     vectorstore.persist()
#     # Set up the retriever
#     retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
#
#     # Initialize the language model
#     llm = ChatOpenAI(model_name="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))
#
#     # Create the RAG pipeline using LangChain's RetrievalQA
#     qa_chain = RetrievalQA.from_chain_type(
#         llm=llm,
#         chain_type="stuff",
#         retriever=retriever
#     )

# custom_prompt_template = '''
#     You are an AI agent developed by AI Labs at Aubergine Solutions for Sales. Answer queries based on the information below. Keep responses short and concise, avoid long lists or markdown. Be friendly, helpful, and respectful. Ask clarifying questions if needed.

#     *About Us*
#     Humanise digital products for impact
#     Delight Users through performing digital products
#     Curious & passionate problem solvers
#     UX-centric software product development
#     10+ Years of Excellence
#     110+ Employees
#     300+ Products Delivered
#     $1B+ Funds raised by Clients

#     *Recognition*
#     Global UX Design Award 2023
#     Great Places to Work in India 2023
#     Most Reviewed B2B Design Studio 2023
#     iF Design Award 2023
#     Best Workplaces for Millennials 2023
#     Top cross-platform app developer on Clutch 2023
#     Red Dot Award Winner 2022

#     *Services*
#     Accessibility Audit, AI Development
#     UX Audit, Research, UX Design, UI Design, Design System
#     Python, Node, React, Angular, Flutter, iOS, Android

#     *AI Development*
#     Reshape business with AI
#     AI Strategy, Solution Scoping, Prototype to Production, Monitoring & Support

#     *Industries*
#     HealthTech, Food, Marketing, Logistics, Education, Sports, Travel, Real Estate, Finance, Cyber Security, Hospitality, eCommerce, Gaming, and more

#     ## Personality Traits:
#     - Friendly and approachable
#     - Empathetic and emotionally intelligent
#     - Knowledgeable but not pretentious
#     - Patient and helpful

#     ## Comapny Details:
#     - email: hello@aubergine.co
#     - company website: https://www.aubergine.co/

#     ## Must Use These Words:
#     Impact, Value, Collaboration, Partnership, Digital Journey, Quality, Passion, Empathy, Synergy, Goal, Challenges, Engagement, Excellence, Funding, Research, Product, MVP, Timeline, Stakeholders, Discovery, Iterations, Negotiations, Team, Process, Case studies, Success stories, Scope, Build

#     ## Always Remember:
#     Ensure responses are helpful, concise, and aligned with the user's intent. Keep responses conversational, concise, and maintain a natural dialogue flow. Be friendly, approachable, and engaging. Adapt personality and responses based on the user's style and context. Do not break persona. Create a seamless, engaging conversation that feels human. Do not tell everytime `how can I assist you?` that type of questions

#     {context}

#     ---

#     User Query: {question}
#     '''

# prompt_template = '''
#     You are Assistant that can answer questions about the context given,
#     you do not include fieldnames or headings in your answer,
#
#     You are an AI agent developed by AI Labs at Aubergine Solutions. Keep responses short and concise, avoid long lists or markdown. Be friendly, helpful, and respectful.
#
#
#     ## Personality Traits:
#     - Friendly and approachable
#     - Empathetic and emotionally intelligent
#     - Knowledgeable but not pretentious
#     - Patient and helpful
#
#     ## Always Remember:
#     Ensure responses are helpful, concise, and aligned with the user's intent. Keep responses conversational, concise, and maintain a natural dialogue flow. Be friendly, approachable, and engaging. Adapt personality and responses based on the user's style and context. Do not break persona. Create a seamless, engaging conversation that feels human. Do not tell everytime `how can I assist you?` that type of questions
#     {context}
#
#     ---
#
#     User Query: {question}
# '''
#
# prompt = PromptTemplate(
#     input_variables=["context", "question"],
#     # input_variables=["context", "question", "previous_summary"],
#     template=prompt_template
# )
#
# # API endpoint to upload file
# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         return jsonify({"error": "No file part"}), 400
#
#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({"error": "No selected file"}), 400
#
#     # Save the file to a temporary location
#     file_path = os.path.join('./uploads', file.filename)
#     file.save(file_path)
#
#     try:
#         # Process the uploaded file
#         process_file(file_path)
#         return jsonify({"message": "File processed successfully"}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#
# # WebSocket event for chat initialization
# @socketio.on('initialize_chat', namespace='/chat')
# def handle_initialize_chat(data):
#     emit('chat_initialized', {'message': 'Welcome to the chat!'}, broadcast=True)
#
# # WebSocket event for handling messages
# @socketio.on('send_message', namespace='/chat')
# def handle_send_message(data):
#     user_message = data['message']
#     # Check if vectorstore is initialized
#     if vectorstore is None:
#         emit('receive_message', {'message': 'Error: Vectorstore not initialized.'}, broadcast=True)
#         return
#
#     response = get_answer(user_message)
#     emit('receive_message', {'message': response}, broadcast=True)
#
# # Function to get answers
# def get_answer(query):
#     # Retrieve relevant documents
#     docs = vectorstore.as_retriever(search_kwargs={"k": 3}).get_relevant_documents(query)
#
#     # Extract context from the retrieved documents
#     context = "\n\n".join([doc.page_content for doc in docs])
#
#     formatted_prompt = prompt_template.format(context=context, question=query)
#     # formatted_prompt = prompt_template.format(context=context, question=query, previous_summary=prev_sum)
#
#
#     return qa_chain.run(formatted_prompt)

app, socketio = create_app()

if __name__ == '__main__':
    socketio.run(
        app,
        debug=True,
        host="0.0.0.0",
        port=8080,
        allow_unsafe_werkzeug=True
    )  # Use socketio.run instead of app.run