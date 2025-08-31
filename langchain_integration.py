"""
LangGraph integration for the ExploreNYC Event Explorer.
Handles AI-powered event recommendations and natural language processing using LangGraph workflows.
"""

from langchain_cohere import ChatCohere
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from typing import Dict, List, Any, Optional, TypedDict, Annotated
import json
from datetime import datetime
from config import Config

# Define the state for our LangGraph workflow
class EventExplorerState(TypedDict):
    """State for the Event Explorer LangGraph workflow."""
    messages: Annotated[List, add_messages]
    user_preferences: Dict[str, Any]
    search_criteria: Dict[str, Any]
    events: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    current_date: str

@tool
def nyc_event_search(query: str) -> str:
    """Search for NYC events based on criteria like category, location, date, and keywords.
    
    Args:
        query: A JSON string with search criteria including category, location, date_range, keywords
        
    Returns:
        JSON string containing list of matching events
    """
    try:
        # Parse the query
        criteria = json.loads(query) if query.startswith('{') else {"keywords": query}
        
        # Mock event data for MVP (replace with actual API calls)
        mock_events = [
            {
                "title": "Underground Art Show",
                "description": "Emerging artists showcase at secret Brooklyn location",
                "category": "Art",
                "location": "Brooklyn",
                "date": "2024-01-15",
                "price": "Free",
                "url": "https://example.com/event1",
                "venue": "Secret Brooklyn Gallery",
                "time": "7:00 PM",
                "tags": ["art", "underground", "emerging artists"]
            },
            {
                "title": "Jazz Night at Blue Note",
                "description": "Live jazz performance with local musicians",
                "category": "Music",
                "location": "Manhattan",
                "date": "2024-01-16",
                "price": "$25",
                "url": "https://example.com/event2",
                "venue": "Blue Note Jazz Club",
                "time": "8:00 PM",
                "tags": ["jazz", "live music", "nightlife"]
            },
            {
                "title": "Food Truck Festival",
                "description": "50+ food trucks in Central Park",
                "category": "Food",
                "location": "Central Park",
                "date": "2024-01-17",
                "price": "Free entry",
                "url": "https://example.com/event3",
                "venue": "Central Park",
                "time": "12:00 PM",
                "tags": ["food", "outdoor", "family-friendly"]
            },
            {
                "title": "Comedy Night at The Comedy Cellar",
                "description": "Stand-up comedy featuring NYC's best comedians",
                "category": "Entertainment",
                "location": "Manhattan",
                "date": "2024-01-18",
                "price": "$20",
                "url": "https://example.com/event4",
                "venue": "The Comedy Cellar",
                "time": "9:00 PM",
                "tags": ["comedy", "stand-up", "nightlife"]
            },
            {
                "title": "Brooklyn Bridge Walking Tour",
                "description": "Guided historical walking tour of the Brooklyn Bridge",
                "category": "Outdoor",
                "location": "Brooklyn",
                "date": "2024-01-19",
                "price": "$15",
                "url": "https://example.com/event5",
                "venue": "Brooklyn Bridge",
                "time": "10:00 AM",
                "tags": ["outdoor", "history", "walking tour"]
            }
        ]
        
        # Filter events based on criteria
        filtered_events = []
        for event in mock_events:
            # Category filter
            if criteria.get("category") and criteria["category"].lower() not in event["category"].lower():
                continue
            
            # Location filter
            if criteria.get("location") and criteria["location"].lower() not in event["location"].lower():
                continue
            
            # Keyword filter
            if criteria.get("keywords"):
                keywords = criteria["keywords"].lower()
                event_text = f"{event['title']} {event['description']} {' '.join(event.get('tags', []))}".lower()
                if not any(keyword in event_text for keyword in keywords.split()):
                    continue
            
            filtered_events.append(event)
        
        return json.dumps(filtered_events, indent=2)
        
    except Exception as e:
        return f"Error searching events: {str(e)}"

@tool
def generate_recommendations(user_preferences: str, events: str) -> str:
    """Generate personalized event recommendations based on user preferences and available events.
    
    Args:
        user_preferences: JSON string containing user preferences
        events: JSON string containing list of events
        
    Returns:
        JSON string containing personalized recommendations with explanations
    """
    try:
        prefs = json.loads(user_preferences) if user_preferences else {}
        event_list = json.loads(events) if events else []
        
        if not event_list:
            return json.dumps({"recommendations": [], "message": "No events found matching your criteria."})
        
        # Simple recommendation logic (can be enhanced with ML)
        recommendations = []
        for event in event_list[:5]:  # Top 5 recommendations
            score = 0
            reasons = []
            
            # Category preference scoring
            if prefs.get('categories') and event.get('category') in prefs['categories']:
                score += 10
                reasons.append(f"Matches your interest in {event['category']}")
            
            # Budget preference scoring
            budget = prefs.get('budget', {})
            event_price = 0
            if event.get('price') and event['price'] != 'Free':
                try:
                    event_price = float(event['price'].replace('$', '').replace('Free entry', '0'))
                except:
                    event_price = 0
            
            if budget.get('max', 1000) >= event_price >= budget.get('min', 0):
                score += 5
                reasons.append("Fits your budget")
            
            # Location preference scoring
            if prefs.get('neighborhoods'):
                for neighborhood in prefs['neighborhoods']:
                    if neighborhood.lower() in event.get('location', '').lower():
                        score += 8
                        reasons.append(f"Located in {neighborhood}")
                        break
            
            recommendations.append({
                "event": event,
                "score": score,
                "reasons": reasons,
                "recommendation_strength": "High" if score >= 15 else "Medium" if score >= 8 else "Low"
            })
        
        # Sort by score
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return json.dumps({
            "recommendations": recommendations[:3],  # Top 3
            "total_events_considered": len(event_list),
            "message": f"Found {len(event_list)} events, recommending the top 3 based on your preferences."
        })
        
    except Exception as e:
        return f"Error generating recommendations: {str(e)}"

class EventExplorerAgent:
    """Main agent class for handling event exploration queries using LangGraph."""
    
    def __init__(self):
        """Initialize the EventExplorerAgent with LangGraph workflow."""
        self.llm = self._initialize_llm()
        self.tools = [nyc_event_search, generate_recommendations]
        self.tool_node = ToolNode(self.tools)
        self.graph = self._create_graph()
        
    def _initialize_llm(self) -> ChatCohere:
        """Initialize the language model."""
        if not Config.COHERE_API_KEY:
            raise ValueError("Cohere API key not found. Please set COHERE_API_KEY in your environment.")
        
        return ChatCohere(
            cohere_api_key=Config.COHERE_API_KEY,
            model=Config.DEFAULT_MODEL,
            temperature=Config.TEMPERATURE,
            max_tokens=Config.MAX_TOKENS
        )
    
    def _create_graph(self) -> StateGraph:
        """Create the LangGraph workflow for event exploration."""
        
        # Define the system prompt
        system_prompt = """You are an expert NYC event explorer assistant. You help users discover amazing events in New York City, 
        from hidden underground venues to mainstream attractions. You have access to tools to search for events and can provide 
        personalized recommendations.

        Your personality:
        - Enthusiastic about NYC culture and events
        - Knowledgeable about different neighborhoods and venues
        - Helpful in finding both popular and off-the-beaten-path experiences
        - Considerate of budget, time, and accessibility needs

        When users ask about events:
        1. Use the nyc_event_search tool to find relevant events
        2. Use the generate_recommendations tool to provide personalized suggestions
        3. Provide detailed, helpful information
        4. Include practical details like location, time, cost, and how to get there
        5. Suggest related events or alternatives
        6. Be conversational and engaging

        Always be helpful and provide actionable information about NYC events."""
        
        def should_continue(state: EventExplorerState) -> str:
            """Determine whether to continue the workflow or end."""
            messages = state["messages"]
            last_message = messages[-1]
            
            # If the last message is from the user, we should continue
            if isinstance(last_message, HumanMessage):
                return "continue"
            # If the last message is from the assistant, we should end
            elif isinstance(last_message, AIMessage):
                return "end"
            else:
                return "continue"
        
        def call_model(state: EventExplorerState) -> Dict[str, Any]:
            """Call the language model with the current state."""
            messages = state["messages"]
            
            # Add system message if not present
            if not messages or not isinstance(messages[0], SystemMessage):
                messages = [SystemMessage(content=system_prompt)] + messages
            
            # Bind tools to the model
            model_with_tools = self.llm.bind_tools(self.tools)
            
            # Get response from the model
            response = model_with_tools.invoke(messages)
            
            return {"messages": [response]}
        
        def call_tools(state: EventExplorerState) -> Dict[str, Any]:
            """Call the tools based on the model's response."""
            messages = state["messages"]
            last_message = messages[-1]
            
            # If the last message has tool calls, execute them
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                tool_messages = self.tool_node.invoke({"messages": [last_message]})
                return {"messages": tool_messages["messages"]}
            else:
                return {"messages": []}
        
        # Create the graph
        workflow = StateGraph(EventExplorerState)
        
        # Add nodes
        workflow.add_node("agent", call_model)
        workflow.add_node("tools", call_tools)
        
        # Set entry point
        workflow.set_entry_point("agent")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "agent",
            should_continue,
            {
                "continue": "tools",
                "end": END
            }
        )
        
        # Add edge from tools back to agent
        workflow.add_edge("tools", "agent")
        
        # Compile the graph
        return workflow.compile()
    
    def process_query(self, user_input: str, user_preferences: Dict[str, Any] = None) -> str:
        """Process a user query and return a response using LangGraph."""
        try:
            # Create initial state
            initial_state = {
                "messages": [HumanMessage(content=user_input)],
                "user_preferences": user_preferences or {},
                "search_criteria": {},
                "events": [],
                "recommendations": [],
                "current_date": datetime.now().strftime("%Y-%m-%d")
            }
            
            # Run the graph
            result = self.graph.invoke(initial_state)
            
            # Extract the final response
            messages = result["messages"]
            if messages:
                last_message = messages[-1]
                if hasattr(last_message, 'content'):
                    return last_message.content
                else:
                    return "I found some information but couldn't generate a proper response. Please try rephrasing your question."
            else:
                return "I'm sorry, I couldn't process your request. Please try again."
            
        except Exception as e:
            return f"I'm sorry, I encountered an error while processing your request: {str(e)}. Please make sure your Cohere API key is properly configured."
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the conversation history from the current state."""
        # This would need to be implemented with proper state management
        # For now, return empty list as LangGraph handles state internally
        return []
    
    def clear_history(self):
        """Clear the conversation history."""
        # LangGraph manages state internally, so this is handled by creating new instances
        pass
