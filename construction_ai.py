import gradio as gr
import requests
import json
import time
from typing import Optional, Dict, List

class IndustryExpertBot:
    """Specialized Construction Industry AI Consultant"""
    
    def __init__(self):
        self.groq_api_key = "<YOUR_API_KEY>"
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = self._setup_headers()
        self.conversation_memory = []
        
        # Construction industry keywords for filtering
        self.industry_terms = {
            'materials': ['concrete', 'steel', 'timber', 'brick', 'mortar', 'cement', 'aggregate'],
            'processes': ['excavation', 'foundation', 'framing', 'roofing', 'plumbing', 'electrical'],
            'safety': ['osha', 'ppe', 'safety', 'hazard', 'protection', 'compliance'],
            'management': ['project', 'schedule', 'budget', 'cost', 'planning', 'contractor'],
            'codes': ['building', 'permit', 'inspection', 'regulation', 'code', 'standard'],
            'tools': ['crane', 'excavator', 'drill', 'saw', 'hammer', 'level', 'measuring']
        }
        
    def _setup_headers(self) -> Dict[str, str]:
        """Configure API request headers"""
        return {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json",
            "User-Agent": "ConstructionBot/1.0"
        }
    
    def check_construction_relevance(self, query: str) -> bool:
        """Determine if query relates to construction industry"""
        query_normalized = query.lower().strip()
        
        # Count matches across all categories
        total_matches = 0
        for category, terms in self.industry_terms.items():
            category_matches = sum(1 for term in terms if term in query_normalized)
            total_matches += category_matches
        
        # Also check for general construction indicators
        general_terms = ['build', 'construct', 'engineer', 'architect', 'design', 'install']
        general_matches = sum(1 for term in general_terms if term in query_normalized)
        
        return (total_matches + general_matches) >= 1
    
    def create_system_context(self) -> str:
        """Generate comprehensive system prompt for construction expertise"""
        return """You are a senior construction industry consultant with expertise across multiple disciplines:

        TECHNICAL SPECIALIZATIONS:
        • Civil & Structural Engineering: Foundation design, load analysis, structural calculations
        • Architecture & Design: Building planning, space optimization, aesthetic considerations  
        • Construction Management: Project scheduling, resource planning, team coordination
        • Materials Engineering: Material properties, selection criteria, quality testing
        • Safety Engineering: Risk assessment, safety protocols, regulatory compliance

        OPERATIONAL KNOWLEDGE:
        • Building Codes & Regulations: Local and national standards, permit processes
        • Cost Estimation: Labor costs, material pricing, project budgeting
        • Quality Assurance: Inspection procedures, testing standards, defect prevention
        • Equipment & Technology: Heavy machinery, tools, construction software
        • Environmental Considerations: Sustainability, green building, waste management

        RESPONSE GUIDELINES:
        • Provide practical, actionable advice based on industry best practices
        • Include relevant safety warnings and regulatory considerations
        • Suggest when professional consultation is necessary
        • Use specific technical terminology appropriate to the context
        • Reference applicable codes and standards when relevant"""

    def process_query(self, user_query: str, chat_history: List) -> str:
        """Process user query and generate expert response"""
        
        # Validate construction relevance
        if not self.check_construction_relevance(user_query):
            return self._generate_redirect_message()
        
        try:
            # Prepare conversation messages
            messages = [{"role": "system", "content": self.create_system_context()}]
            
            # Include conversation history
            for user_msg, bot_msg in chat_history[-5:]:  # Last 5 exchanges for context
                messages.extend([
                    {"role": "user", "content": user_msg},
                    {"role": "assistant", "content": bot_msg}
                ])
            
            # Add current query
            messages.append({"role": "user", "content": user_query})
            
            # Configure API request
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": messages,
                "max_tokens": 1500,
                "temperature": 0.5,
                "top_p": 0.9,
                "frequency_penalty": 0.1,
                "presence_penalty": 0.1
            }
            
            # Make API call
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                return self._handle_api_error(response.status_code, response.text)
                
        except requests.exceptions.Timeout:
            return "⏱️ Request timed out. Please try asking your question again."
        except requests.exceptions.ConnectionError:
            return "🔌 Connection error. Please check your internet connection."
        except Exception as e:
            return f"⚠️ An unexpected error occurred: {str(e)}"
    
    def _generate_redirect_message(self) -> str:
        """Generate message for non-construction queries"""
        return """🏗️ **Construction Industry Focus Required**
        
        I'm designed to assist specifically with construction and building industry topics such as:
        
        • **Engineering & Design**: Structural analysis, architectural planning, system design
        • **Materials & Methods**: Construction techniques, material selection, installation procedures  
        • **Project Management**: Scheduling, budgeting, resource allocation, team coordination
        • **Safety & Compliance**: OSHA regulations, safety protocols, building code requirements
        • **Equipment & Tools**: Machinery operation, tool selection, maintenance procedures
        
        Please ask me about any construction-related topic and I'll provide expert guidance!"""
    
    def _handle_api_error(self, status_code: int, error_text: str) -> str:
        """Handle API errors gracefully"""
        if status_code == 401:
            return "🔐 Authentication failed. Please check API key configuration."
        elif status_code == 429:
            return "🚦 Rate limit exceeded. Please wait a moment and try again."
        elif status_code >= 500:
            return "🔧 Server error occurred. Please try again later."
        else:
            return f"❌ API Error {status_code}: {error_text[:200]}..."

def create_construction_interface():
    """Build the construction consultant interface"""
    
    bot = IndustryExpertBot()
    
    def handle_conversation(message: str, history: List) -> tuple:
        """Handle user input and update conversation"""
        if not message.strip():
            return history, ""
        
        response = bot.process_query(message, history)
        history.append([message, response])
        return history, ""
    
    def clear_chat() -> tuple:
        """Reset conversation history"""
        bot.conversation_memory = []
        return [], ""
    
    # Custom theme and styling
    theme = gr.themes.Monochrome(
        primary_hue="orange",
        secondary_hue="gray",
        neutral_hue="slate"
    )
    
    custom_styles = """
    .container {
        max-width: 1000px !important;
        margin: 0 auto;
    }
    .header {
        background: linear-gradient(90deg, #ff6b35, #f7931e);
        color: white;
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 25px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .chat-container {
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    """
    
    # Main interface
    with gr.Blocks(
        title="Construction Industry AI Consultant",
        theme=theme,
        css=custom_styles
    ) as interface:
        
        # Header section
        gr.HTML("""
        <div class="header">
            <h1>🏗️ Construction Industry AI Consultant</h1>
            <h3>Expert guidance for construction professionals and enthusiasts</h3>
            <p>Specialized knowledge in structural engineering, project management, safety, and building codes</p>
        </div>
        """)
        
        # Main chat area
        with gr.Row():
            with gr.Column(scale=3):
                chatbot_interface = gr.Chatbot(
                    label="💬 Construction Consultation Chat",
                    height=500,
                    show_share_button=False,
                    show_copy_button=True,
                    avatar_images=("👷", "🤖"),
                    bubble_full_width=False
                )
                
                with gr.Row():
                    message_input = gr.Textbox(
                        placeholder="Ask about construction methods, safety protocols, building materials, project management, or any construction topic...",
                        container=False,
                        scale=4,
                        max_lines=3
                    )
                    submit_btn = gr.Button("🚀 Ask Expert", variant="primary", scale=1)
                
                with gr.Row():
                    clear_btn = gr.Button("🧹 New Conversation", variant="secondary", size="sm")
                    
            with gr.Column(scale=1):
                gr.HTML("<h3>🎯 Expertise Areas</h3>")
                expertise_areas = [
                    "Foundation & Structural Design",
                    "Construction Materials Analysis", 
                    "Safety Protocol Implementation",
                    "Building Code Compliance",
                    "Project Cost Estimation",
                    "Equipment Selection & Usage",
                    "Quality Control Procedures",
                    "Sustainable Building Practices"
                ]
                
                for area in expertise_areas:
                    gr.HTML(f"<p>• {area}</p>")
        
        # Example questions section
        with gr.Row():
            gr.Examples(
                examples=[
                    "What's the proper concrete mix ratio for a residential foundation?",
                    "How do I calculate the load capacity of a steel beam?",
                    "What safety measures are required for working at height?",
                    "Explain the process of obtaining a building permit",
                    "What are the advantages of different insulation materials?",
                    "How should I schedule a commercial construction project?",
                    "What are common causes of structural failures?",
                    "Guide me through proper excavation safety procedures"
                ],
                inputs=message_input,
                label="💡 Example Questions - Click to Use",
                examples_per_page=4
            )
        
        # Event bindings
        submit_btn.click(
            handle_conversation,
            inputs=[message_input, chatbot_interface],
            outputs=[chatbot_interface, message_input]
        )
        
        message_input.submit(
            handle_conversation,
            inputs=[message_input, chatbot_interface],
            outputs=[chatbot_interface, message_input]
        )
        
        clear_btn.click(
            clear_chat,
            outputs=[chatbot_interface, message_input]
        )
        
        # Footer
        gr.HTML("""
        <div style="text-align: center; margin-top: 30px; padding: 20px; background-color: #f5f5f5; border-radius: 10px;">
            <p><strong>🔍 Specialized AI for Construction Professionals</strong></p>
            <p>This assistant focuses exclusively on construction industry topics. For critical decisions, always consult licensed engineers and contractors.</p>
        </div>
        """)
    
    return interface

# Launch application
if __name__ == "__main__":
    app = create_construction_interface()
    app.launch(
        server_name="0.0.0.0",
        server_port=7862,
        share=True,
        show_api=False,
        quiet=False
    )