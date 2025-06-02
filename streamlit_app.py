import streamlit as st
import re
from datetime import datetime
from rag_service import rag_service
from api_client import api_client

# Page configuration
st.set_page_config(
    page_title="Cyfuture Customer Support Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        padding: 1rem 0;
        border-bottom: 2px solid #A23B72;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .user-message {
        background-color: #E3F2FD;
        border-left: 4px solid #2196F3;
    }
    .bot-message {
        background-color: #F1F8E9;
        border-left: 4px solid #4CAF50;
    }
    .complaint-card {
        background-color: #FFF3E0;
        border-left: 4px solid #FF9800;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .success-message {
        background-color: #E8F5E8;
        border-left: 4px solid #4CAF50;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .error-message {
        background-color: #FFEBEE;
        border-left: 4px solid #F44336;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    if 'complaint_context' not in st.session_state:
        st.session_state.complaint_context = {
            'name': None,
            'phone_number': None,
            'email': None,
            'complaint_details': None,
            'collecting_complaint': False
        }
    
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello! I'm your Cyfuture customer support assistant. I can help you file complaints or retrieve complaint details. How can I assist you today?"
            }
        ]

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number format"""
    # Remove any non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    return len(digits_only) >= 10

def extract_missing_fields(context):
    """Check which fields are missing for complaint creation"""
    missing = []
    if not context['name']:
        missing.append('name')
    if not context['phone_number']:
        missing.append('phone number')
    if not context['email']:
        missing.append('email address')
    if not context['complaint_details']:
        missing.append('complaint details')
    return missing

def update_complaint_context(user_input, context):
    """Update complaint context based on user input"""
    # Extract contact information
    contact_info = rag_service.extract_contact_info(user_input)
    
    # Update email if found and not already set
    if 'email' in contact_info and not context['email']:
        if validate_email(contact_info['email']):
            context['email'] = contact_info['email']
    
    # Update phone if found and not already set
    if 'phone_number' in contact_info and not context['phone_number']:
        if validate_phone(contact_info['phone_number']):
            context['phone_number'] = contact_info['phone_number']
    
    # Update name if it looks like a name (simple heuristic)
    if not context['name']:
        # If the input is short and doesn't contain typical complaint words, it might be a name
        words = user_input.strip().split()
        if len(words) <= 3 and len(user_input) < 50:
            complaint_keywords = ['complaint', 'issue', 'problem', 'delayed', 'damaged', '@', 'phone', 'number']
            if not any(keyword in user_input.lower() for keyword in complaint_keywords):
                # Check if it's not an email or phone number
                if not re.search(r'@|^\d+$', user_input):
                    context['name'] = user_input.strip()
    
    # Update complaint details if it's descriptive
    if not context['complaint_details'] and len(user_input) > 20:
        if any(keyword in user_input.lower() for keyword in ['order', 'delivery', 'service', 'product', 'issue', 'problem']):
            context['complaint_details'] = user_input.strip()

def create_complaint_from_context(context):
    """Create complaint using collected context"""
    complaint_data = {
        "name": context['name'],
        "phone_number": context['phone_number'],
        "email": context['email'],
        "complaint_details": context['complaint_details']
    }
    
    result = api_client.create_complaint(complaint_data)
    return result

def format_complaint_details(complaint):
    """Format complaint details for display"""
    formatted_date = datetime.fromisoformat(complaint['created_at'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
    
    return f"""
**Complaint ID:** {complaint['complaint_id']}  
**Name:** {complaint['name']}  
**Phone:** {complaint['phone_number']}  
**Email:** {complaint['email']}  
**Details:** {complaint['complaint_details']}  
**Created At:** {formatted_date}
"""

def handle_user_message(user_input):
    """Process user message and generate appropriate response"""
    context = st.session_state.complaint_context
    
    # Check if user wants to query complaint details
    if rag_service.is_complaint_query_intent(user_input):
        print("input", user_input)
        complaint_id = rag_service.extract_complaint_id(user_input)
        print("complaint id : ", complaint_id)
        if complaint_id:
            result = api_client.get_complaint(complaint_id)
            if 'error' in result:
                return f"I couldn't find a complaint with ID {complaint_id}. Please check the ID and try again."
            else:
                return f"Here are the details for complaint {complaint_id}:\n\n{format_complaint_details(result)}"
        else:
            return "Please provide the complaint ID you'd like me to look up."
    
    # Check if user wants to file a complaint
    if rag_service.is_complaint_filing_intent(user_input) or context['collecting_complaint']:
        context['collecting_complaint'] = True
        
        # Update context with any information from the current message
        update_complaint_context(user_input, context)
        
        # Check what information is still missing
        missing_fields = extract_missing_fields(context)
        
        if missing_fields:
            # Ask for the next missing field
            if 'name' in missing_fields:
                return "I'm sorry to hear about your issue. To help you file a complaint, I'll need some information. Could you please provide your full name?"
            elif 'phone number' in missing_fields:
                return f"Thank you, {context['name']}. What is your phone number?"
            elif 'email address' in missing_fields:
                return "Got it. Please provide your email address."
            elif 'complaint details' in missing_fields:
                return "Thanks. Could you please provide more details about your complaint?"
        else:
            # All information collected, create the complaint
            result = create_complaint_from_context(context)
            
            if 'error' in result:
                return f"I apologize, but there was an error creating your complaint: {result['error']}. Please try again or contact our support team directly."
            else:
                # Reset the complaint context
                st.session_state.complaint_context = {
                    'name': None,
                    'phone_number': None,
                    'email': None,
                    'complaint_details': None,
                    'collecting_complaint': False
                }
                return f"Your complaint has been successfully registered! Your complaint ID is: **{result['complaint_id']}**. You'll hear back from our team soon. Is there anything else I can help you with?"
    
    # Generate general response using RAG
    return rag_service.generate_response(user_input, context, st.session_state.conversation_history)

def main():
    """Main Streamlit application"""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🤖 Cyfuture Customer Support Chatbot</h1>', unsafe_allow_html=True)
    
    # Sidebar with information
    with st.sidebar:
        st.header("ℹ️ How I Can Help")
        st.markdown("""
        **File a Complaint:**
        - Tell me about your issue
        - I'll collect your details step by step
        - Get a unique complaint ID
        
        **Check Complaint Status:**
        - Provide your complaint ID
        - Get complete complaint details
        
        **General Support:**
        - Ask questions about our services
        - Get help with common issues
        """)
        
        st.header("📋 Current Session")
        context = st.session_state.complaint_context
        if context['collecting_complaint']:
            st.write("**Filing Complaint - Progress:**")
            st.write(f"✅ Name: {context['name'] or '❌ Missing'}")
            st.write(f"✅ Phone: {context['phone_number'] or '❌ Missing'}")
            st.write(f"✅ Email: {context['email'] or '❌ Missing'}")
            st.write(f"✅ Details: {'✅ Provided' if context['complaint_details'] else '❌ Missing'}")
        
        # Clear conversation button
        if st.button("🔄 Clear Conversation"):
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "Hello! I'm your Cyfuture customer support assistant. I can help you file complaints or retrieve complaint details. How can I assist you today?"
                }
            ]
            st.session_state.complaint_context = {
                'name': None,
                'phone_number': None,
                'email': None,
                'complaint_details': None,
                'collecting_complaint': False
            }
            st.session_state.conversation_history = []
            st.rerun()
    
    # Main chat interface
    st.header("💬 Chat")
    
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message bot-message"><strong>Assistant:</strong> {message["content"]}</div>', unsafe_allow_html=True)
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Add to conversation history for RAG context
        st.session_state.conversation_history.append({"role": "user", "content": prompt})
        
        # Display user message
        st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {prompt}</div>', unsafe_allow_html=True)
        
        # Generate and display assistant response
        with st.spinner("Thinking..."):
            response = handle_user_message(prompt)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.conversation_history.append({"role": "assistant", "content": response})
        
        # Display assistant response
        st.markdown(f'<div class="chat-message bot-message"><strong>Assistant:</strong> {response}</div>', unsafe_allow_html=True)
        
        # Rerun to update the display
        st.rerun() 

if __name__ == "__main__":
    main()
