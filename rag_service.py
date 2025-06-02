import openai
import re
from settings import *
from qdrant_client import QdrantClient
from openai import OpenAI
# from fastembed import TextEmbedding
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage

client = OpenAI(
    api_key=OPENAI_API_KEY
)
class RAGService:
    def __init__(self):
        self.client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_KEY)
        self.llm = ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model="gpt-3.5-turbo",
            temperature=0.7
        )
        
    def search_knowledge_base(self, query: str, limit: int = 3):
        """Search the knowledge base for relevant information"""
        try:
            # Create embedding for the query
            response = client.embeddings.create(
                input=query,
                model="text-embedding-3-small"
            )
            vectors = response.data[0].embedding
            
            
            # Search in Qdrant
            search_result = self.client.search(
                collection_name="customer_complaints_collection",
                query_vector=vectors,
                limit=limit
            )
            
            # Extract relevant text
            relevant_texts = []
            for result in search_result:
                relevant_texts.append(result.payload["text"])
            
            return relevant_texts
        except Exception as e:
            print(f"Error searching knowledge base: {e}")
            return []
    
    def extract_complaint_id(self, text: str):
        """Extract complaint ID from user query"""

        patterns =r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}\b'
        matches = re.findall(patterns, text)
        print(matches)
        if matches:
            return matches[0]
        return None
    
    def extract_contact_info(self, text: str):
        """Extract contact information from user input"""
        info = {}
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            info['email'] = email_match.group()
        
        # Extract phone number
        phone_patterns = [
            r'\b\d{10}\b',  # 10 digits
            r'\b\+?\d{1,3}[-.\s]?\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b',  # International format
        ]
        for pattern in phone_patterns:
            phone_match = re.search(pattern, text)
            if phone_match:
                info['phone_number'] = phone_match.group()
                break
        
        return info
    
    def generate_response(self, user_message: str, context: dict, conversation_history: list):
        """Generate chatbot response using RAG"""
        # Search knowledge base for relevant information
        relevant_docs = self.search_knowledge_base(user_message)
        
        # Prepare context for the prompt
        knowledge_context = "\n".join(relevant_docs) if relevant_docs else "No specific knowledge base information found."
        
        # Create system prompt
        system_prompt = f"""You are a helpful customer service chatbot for Cyfuture. Your role is to:
1. Help customers file complaints by collecting their details (name, phone, email, complaint details)
2. Provide information based on the knowledge base
3. Be empathetic and professional
4. Ask follow-up questions to collect missing information

Knowledge Base Context:
{knowledge_context}

Current conversation context:
- Name: {context.get('name', 'Not provided')}
- Phone: {context.get('phone_number', 'Not provided')}
- Email: {context.get('email', 'Not provided')}
- Complaint details: {context.get('complaint_details', 'Not provided')}

Guidelines:
- If the user wants to file a complaint, collect all required information step by step
- Be conversational and natural
- If asked about complaint details with an ID, indicate that you'll help retrieve the information
- Keep responses concise but helpful
"""

        # Create the prompt
        messages = [
            SystemMessage(content=system_prompt),
        ]
        
        # Add conversation history
        for msg in conversation_history[-5:]:  # Keep last 5 messages for context
            messages.append(HumanMessage(content=f"{msg['role']}: {msg['content']}"))
        
        # Add current message
        messages.append(HumanMessage(content=f"User: {user_message}"))
        
        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            return f"I apologize, but I'm having trouble processing your request right now. Please try again. Error: {str(e)}"
    
    def is_complaint_filing_intent(self, text: str):
        """Check if user wants to file a complaint"""
        complaint_keywords = [
            'complaint', 'complain', 'issue', 'problem', 'file a complaint',
            'report a problem', 'delayed', 'damaged', 'poor service',
            'not satisfied', 'unhappy', 'wrong', 'error'
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in complaint_keywords)
    
    def is_complaint_query_intent(self, text: str):
        """Check if user wants to query complaint details"""
        query_keywords = [
            'show details', 'check complaint', 'complaint status',
            'my complaint', 'complaint id', 'check status'
        ]
        
        text_lower = text.lower()
        has_query_intent = any(keyword in text_lower for keyword in query_keywords)
        print(has_query_intent)
        has_complaint_id = self.extract_complaint_id(text) is not None
        print(has_complaint_id)
        return has_query_intent or has_complaint_id

# Create global instance
rag_service = RAGService()
