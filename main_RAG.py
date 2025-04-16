import os
import re
import difflib
from docx import Document
import google.generativeai as genai
from dotenv import load_dotenv
import db.db

load_dotenv()
genai.configure(api_key=os.getenv("API_KEY"))

model = genai.GenerativeModel("gemini-2.0-flash")

def generate_rag_response(prompt):
    system_message = (
        "You are a helpful assistant. "
        "Answer the user's question using ONLY the following company documentation. "
        "If the answer is not found, say 'The information is not available in the document.'"
    )
    response = model.generate_content([system_message, prompt])
    return response.text.strip()

def generate_sql_only(prompt):
    sql_prompt = (
        "You are an expert SQL assistant. "
        "Given a natural language question, convert it into an SQL query for a table called 'orders' "
        "with columns: order_id, customer_name, order_date, amount. "
        "Do NOT return any explanation—only valid SQL."
        "Generate sql in MySql syntax."
    )
    response = model.generate_content([sql_prompt, prompt])
    return response.text.strip()

def load_chunks_from_docs(doc_path):
    doc = Document(doc_path)
    chunks = []
    for i, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        if text:
            if "Headquarters:" in text:
                text = text.replace("Headquarters:", "The company is located in")
            if "Company Name:" in text:
                text = text.replace("Company Name:", "The company name is")
            chunks.append({"chunk_id": i + 1, "content": text})
    return chunks

def find_most_accurate_chunks(query, chunks, top_n=3):
    scores = []
    for chunk in chunks:
        score = difflib.SequenceMatcher(None, query.lower(), chunk["content"].lower()).ratio()
        scores.append((score, chunk))
    sorted_chunks = sorted(scores, key=lambda x: x[0], reverse=True)
    return [c[1] for c in sorted_chunks[:top_n]]

def generate_rag_answer(query, chunks):
    top_chunks = find_most_accurate_chunks(query, chunks, top_n=3)
    knowledge = "\n".join([chunk["content"].replace("Company Name:", "The company is named") for chunk in top_chunks])
    prompt = f"""You are a helpful assistant.
Use ONLY the following company documentation to answer the user's question.
If the answer is not found, say 'The information is not available in the document.'

{knowledge}

Question: {query}
Answer:"""
    return generate_rag_response(prompt)


def detect_question_type(query):
    prompt = (
        "You are a smart assistant that classifies user queries.\n"
        "Determine whether the following question should be answered using:\n"
        "- 'sql' → if it requires querying a structured table called 'orders' with columns: order_id, customer_name, order_date, amount\n"
        "- 'rag' → if it requires company background information, documentation, or general company facts.\n\n"
        "Return only one word: 'sql' or 'rag'.\n\n"
        f"Question: {query}\n"
        "Type:"
    )
    response = model.generate_content(prompt)
    answer = response.text.strip().lower()
    return "sql" if "sql" in answer else "rag"


def clean_sql_query(sql_text):
    sql_pattern = re.search(r'```(?:sql)?\s*(.*?)```', sql_text, re.DOTALL)
    if sql_pattern:
        return sql_pattern.group(1).strip()
    return sql_text.strip()

def generate_answer(query, rag_chunks):
    q_type = detect_question_type(query)
    if q_type == "sql":
        return generate_sql_only(query)
    else:
        return generate_rag_answer(query, rag_chunks)


def test_question_classification():
    test_questions = {
        "What is the name of the company?": "rag",
        "Where is the company located?": "rag",
        "What is the company’s industry?": "rag",
        "When was the company founded?": "rag",
        "What services does the company offer?": "rag",
        "What is the total revenue?": "sql",
        "List all orders placed in 2024.": "sql",
        "Who spent the most?": "sql",
        "Is customer data shared with external parties?": "rag",
        "Which month had the highest total revenue?": "sql",
    }

    print("🧪 Running classification test...\n")
    for question, expected in test_questions.items():
        result = detect_question_type(question)
        status = "✅" if result == expected else "❌"
        print(f"{status} Q: '{question}' → Predicted: {result} | Expected: {expected}")

# Main loop
if __name__ == "__main__":
    doc_path = "data/NovaCart_RAG_Company_Info.docx"
    rag_chunks = load_chunks_from_docs(doc_path)

    while True:
        query = input("\n🔍 Ask a question (or type 'exit'): ")
        if query.lower() == "exit":
            break

        answer = generate_answer(query, rag_chunks)
        print(f"\n🤖 Answer:\n{answer}")

        query_type = detect_question_type(query)

        if query_type == "sql":
            try:
                cleaned_sql = clean_sql_query(answer)
                print(f"\n📊 Running SQL query:\n{cleaned_sql}")

                print("\n📋 Query results:")
                db.db.execute_query(cleaned_sql)
                print("\n✅ Query executed successfully!")

            except Exception as e:
                print(f"\n❌ SQL execution error: {str(e)}")



""" RAG:
🔹 Doğrudan içerikle birebir eşleşen:
	•	What is the name of the company? -->YARIM YAPIYOR
	•	Where is the company located? -->YAPIYOR
	•	What is the company’s industry?  -->YAPIYOR
	•	When was the company founded? -->YAPAMIYOR
	•	What services does the company offer? -->YAPAMIYOR

🔹 Daha çıkarım isteyen (kontrol soruları):
	•	Who is the target audience of the company?
	•	Is the company GDPR compliant?
	•	Where are data backups stored?
	•	What kind of analytics does the company provide?
	•	Is customer data shared with external parties?
	
	
	SQL:
	🔸 Basit sorgular:
	•	How many orders were placed in January?
	•	What is the total revenue?
	•	What is the average order amount?
	•	Who spent the most?
	•	What is the maximum order amount?

🔸 Gruplama + filtre isteyen:
	•	List customers who placed more than 2 orders.
	•	Which month had the highest total revenue?
	•	List all orders placed by Zeynep.
	•	Show all orders placed in 2024.
	•	List customers who spent more than 500 in total.
"""