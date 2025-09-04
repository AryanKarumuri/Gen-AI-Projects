# Required imports
import asyncio
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
from langgraph.checkpoint.mongodb import MongoDBSaver
from langchain.tools import Tool
from pymongo import MongoClient

# MongoDB Setup 
MONGO_URI = "" # MongoDB URI
DB_NAME = "msme"
USER_COLLECTION = "bot_users"
MEMORY_COLLECTION = "bot_long_term_memory"

print(" Connecting to MongoDB...")
db = MongoClient(MONGO_URI)[DB_NAME]

COLLECTIONS = db.list_collection_names()
print(f"Available number of collections: {len(COLLECTIONS)}")
#print(f"Collections: {COLLECTIONS}")

checkpoints_col = db[DB_NAME][USER_COLLECTION]
memory_col = db[DB_NAME][MEMORY_COLLECTION]

mongo_client = MongoClient(MONGO_URI)

# User Management
def check_or_create_user_id(user_id: str) -> str:
    existing = checkpoints_col.find_one({"thread_id": user_id})
    if existing:
        print(f"✅ Existing user found: {user_id}")
    else:
        print(f"🆕 New user created: {user_id}")
        checkpoints_col.insert_one({
            "thread_id": user_id,
            "checkpoint": {},
            "messages": [],
        })
    return user_id

# LLM Setup
OLLAMA_URL = "" # OLLAMA URL Endpoint
DEFAULT_MODEL = "llama3.1:8b"
model = ChatOllama(model=DEFAULT_MODEL, base_url=OLLAMA_URL)

# Memory Management Tools
def save_to_mongo_memory(input: str, user_id: str):
    memory_col.insert_one({
        "user_id": user_id,
        "content": input,
    })
    return "✅ Information saved to memory."

def search_mongo_memory(query: str, user_id: str):
    results = memory_col.find({
        "user_id": user_id,
        "content": {"$regex": query, "$options": "i"}
    })
    texts = [r["content"] for r in results]
    return "\n".join(texts) if texts else "No matching memory found."

# Memory Tools with user context
def create_manage_memory_tool(user_id):
    return Tool.from_function(
        name="save_to_memory",
        description="Use this tool to save important information from the conversation into memory.",
        func=lambda input: save_to_mongo_memory(input, user_id)
    )

def create_search_memory_tool(user_id):
    return Tool.from_function(
        name="search_memory",
        description="Use this tool to search the memory for relevant past information.",
        func=lambda input: search_mongo_memory(input, user_id)
    )


async def chat_loop():
    print("🤖 Welcome! Let's get started.")
    user_id = input("Enter your user ID (e.g., aryan01): ").strip()
    thread_id = check_or_create_user_id(user_id)

    # Setup tools with user-specific context
    manage_tool = create_manage_memory_tool(user_id)
    search_tool = create_search_memory_tool(user_id)
    tools = [manage_tool, search_tool]

    # Setup MongoDBSaver
    checkpointer = MongoDBSaver(
        client= mongo_client,
        mongo_uri=MONGO_URI,
        db_name=DB_NAME,
        collection_name=USER_COLLECTION
    )

    # Create the Agent
    agent_executor = create_react_agent(
        model=model,
        tools=tools,
        store=None,  # No vector store
        checkpointer=checkpointer
    )

    print(f"🧠 Using MongoDB memory space for: {thread_id}")
    print("👋 Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break

        try:
            result = await agent_executor.ainvoke(
                {"messages": [{"role": "user", "content": user_input}]},
                config={"configurable": {"thread_id": thread_id}}
            )

            reply = result["messages"][-1].content
            print(f"Bot: {reply}\n")

        except Exception as e:
            print(f"❌ Error: {e}\n")

# Run the chat loop
if __name__ == "__main__":
    asyncio.run(chat_loop())
