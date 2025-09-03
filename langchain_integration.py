"""
LangGraph integration for the ExploreNYC Event Explorer.
Handles AI-powered event recommendations and natural language processing using LangGraph workflows.
"""

from langchain_cohere import ChatCohere
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from typing import Dict, List, Any, Optional, TypedDict, Annotated
import json
from datetime import datetime, timedelta
from config import Config
from utils.constants import DEFAULT_EVENTS, RATE_LIMIT_SECONDS, MAX_RECOMMENDATIONS
from utils.date_utils import process_time_frames, calculate_this_weekend
from utils.error_handling import handle_api_error, log_error

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
def nyc_event_search(category: str = None, location: str = None, keywords: str = None, date_range: str = None) -> str:
    """Search for NYC events based on criteria like category, location, date, and keywords.
    
    Args:
        category: Event category (e.g., "Art", "Music", "Food")
        location: Event location (e.g., "Brooklyn", "Manhattan")
        keywords: Search keywords (e.g., "underground", "jazz")
        date_range: Date range in format "start_date,end_date" (e.g., "2025-09-06,2025-09-07")
        
    Returns:
        JSON string containing list of matching events
    """
    try:
        # Build criteria from parameters
        criteria = {}
        if category:
            criteria["category"] = category
        if location:
            criteria["location"] = location
        if keywords:
            criteria["keywords"] = keywords
        if date_range:
            criteria["date_range"] = date_range.split(",") if "," in date_range else [date_range, date_range]
        
        # Use default events with calculated dates
        current_date = datetime.now()
        
        # Calculate dates for realistic event scheduling
        saturday, sunday = calculate_this_weekend(current_date)
        next_monday = saturday + timedelta(days=2)
        next_tuesday = next_monday + timedelta(days=1)
        next_wednesday = next_monday + timedelta(days=2)
        next_thursday = next_monday + timedelta(days=3)
        
        # Create events with calculated dates
        mock_events = []
        for i, event_template in enumerate(DEFAULT_EVENTS):
            event = event_template.copy()
            # Assign dates based on event index
            date_map = [saturday, next_monday, next_tuesday, next_wednesday, next_thursday]
            if i < len(date_map):
                event["date"] = date_map[i].strftime("%Y-%m-%d")
            mock_events.append(event)
        
        # Filter events based on criteria
        filtered_events = []
        for event in mock_events:
            # Category filter
            if criteria.get("category") and criteria["category"].lower() not in event["category"].lower():
                continue
            
            # Location filter
            if criteria.get("location") and criteria["location"].lower() not in event["location"].lower():
                continue
            
            # Date range filter (if specified in criteria)
            if criteria.get("date_range"):
                try:
                    event_date = datetime.strptime(event["date"], "%Y-%m-%d").date()
                    start_date = datetime.strptime(criteria["date_range"][0], "%Y-%m-%d").date()
                    end_date = datetime.strptime(criteria["date_range"][1], "%Y-%m-%d").date()
                    
                    if not (start_date <= event_date <= end_date):
                        continue
                except (ValueError, TypeError):
                    # If date parsing fails, continue without date filtering
                    pass
            
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
            "recommendations": recommendations[:MAX_RECOMMENDATIONS],
            "total_events_considered": len(event_list),
            "message": f"Found {len(event_list)} events, recommending the top {MAX_RECOMMENDATIONS} based on your preferences."
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
        self.last_request_time = 0
        self.request_count = 0
        
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

        IMPORTANT: You MUST use the available tools to search for events. Do not make up information.

        Available tools:
        1. nyc_event_search(category, location, keywords, date_range) - Search for events with these parameters:
           - category: "Art", "Music", "Food", "Entertainment", "Outdoor"
           - location: "Brooklyn", "Manhattan", "Queens", "Bronx", "Central Park"
           - keywords: any search terms like "underground", "jazz", "free"
           - date_range: "start_date,end_date" format like "2025-09-06,2025-09-07"
        2. generate_recommendations - Use this tool to provide personalized recommendations based on user preferences

        Your workflow:
        1. ALWAYS use nyc_event_search first to find relevant events
        2. Extract search criteria from the user's query and date range information
        3. Call nyc_event_search with appropriate parameters
        4. Then use generate_recommendations to provide personalized suggestions
        5. Provide detailed, helpful information about the events found
        6. Include practical details like location, time, cost, and how to get there

        Your personality:
        - Enthusiastic about NYC culture and events
        - Knowledgeable about different neighborhoods and venues
        - Helpful in finding both popular and off-the-beaten-path experiences
        - Considerate of budget, time, and accessibility needs

        Remember: ALWAYS use the tools to search for events. Do not respond without searching first."""
        
        def should_continue(state: EventExplorerState) -> str:
            """Determine whether to continue the workflow or end."""
            messages = state["messages"]
            last_message = messages[-1]
            
            # If the last message is from the user, we should continue
            if isinstance(last_message, HumanMessage):
                return "continue"
            # If the last message is from the assistant, check if it has tool calls
            elif isinstance(last_message, AIMessage):
                # Check if the message has tool calls that need to be executed
                if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                    return "continue"  # Continue to tools node
                else:
                    return "end"  # End if no tool calls
            # If the last message is a tool message, continue to get final response
            elif hasattr(last_message, '__class__') and 'ToolMessage' in str(last_message.__class__):
                return "continue"
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
                try:
                    tool_messages = self.tool_node.invoke({"messages": [last_message]})
                    return {"messages": tool_messages["messages"]}
                except Exception as e:
                    print(f"Tool execution error: {e}")
                    # Return an error message as ToolMessage
                    from langchain_core.messages import ToolMessage
                    error_message = ToolMessage(
                        content=f"I encountered an error while searching for events: {str(e)}",
                        tool_call_id="error"
                    )
                    return {"messages": [error_message]}
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
            # Simple rate limiting for trial API keys
            current_time = datetime.now().timestamp()
            if current_time - self.last_request_time < RATE_LIMIT_SECONDS:
                return f"Please wait a moment before making another request. I'm rate limited to {60//RATE_LIMIT_SECONDS} requests per minute."
            
            self.last_request_time = current_time
            self.request_count += 1
            
            # Pre-process the query to extract and calculate time frames
            processed_input = process_time_frames(user_input)
            
            # Create initial state
            initial_state = {
                "messages": [HumanMessage(content=processed_input)],
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
            log_error(e, "process_query")
            return handle_api_error(e)
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the conversation history from the current state."""
        # This would need to be implemented with proper state management
        # For now, return empty list as LangGraph handles state internally
        return []
    
    def clear_history(self):
        """Clear the conversation history."""
        # LangGraph manages state internally, so this is handled by creating new instances
        pass
    

