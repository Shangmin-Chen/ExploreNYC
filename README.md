# 🗽 ExploreNYC - AI Event Explorer

The Event Explorer Bot is an AI-powered agent designed to uncover and personalize NYC's hidden and mainstream events, from underground art shows to discounted museum visits.

Built with **LangGraph** and **Streamlit** for an intuitive, conversational experience that helps you discover the perfect NYC events based on your preferences.

## ✨ Features

- 🤖 **AI-Powered Recommendations**: Chat with an intelligent agent that understands your preferences
- 🎭 **Comprehensive Event Discovery**: Find everything from underground art shows to mainstream attractions
- 🎯 **Personalized Filtering**: Filter by category, location, budget, accessibility needs, and more
- 📊 **Event Analytics**: Visualize event trends and statistics
- 🗺️ **Interactive Maps**: See events plotted on NYC maps
- 💬 **Natural Language Interface**: Ask questions like "Find jazz clubs in the Village this weekend"
- ♿ **Accessibility Support**: Filter for wheelchair accessible venues and other accessibility features

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Cohere API key (for AI features)

### Installation

1. **Clone and navigate to the repository:**
   ```bash
   git clone <your-repo-url>
   cd ExploreNYC
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   # Copy the example environment file
   cp env.example .env
   
   # Edit .env with your API keys
   nano .env  # or use your preferred editor
   ```

4. **Add your Cohere API key to `.env`:**
   ```
   COHERE_API_KEY=your_cohere_api_key_here
   ```

5. **Run the application:**
   ```bash
   streamlit run app.py
   ```

6. **Open your browser** to `http://localhost:8501`

## 🛠️ Configuration

### Required API Keys

- **Cohere API Key**: Required for AI chat functionality
  - Get yours at: https://dashboard.cohere.ai/api-keys
  - Add to `.env` as `COHERE_API_KEY=your_key_here`

### Optional API Keys

- **LangChain API Key**: For enhanced tracing and monitoring
- **NYC Open Data API Token**: For accessing official NYC event data
- **Eventbrite API Key**: For Eventbrite event integration
- **Meetup API Key**: For Meetup event integration

## 🎯 Usage

### Basic Usage

1. **Start the app** with `streamlit run app.py`
2. **Set your preferences** in the sidebar (categories, budget, neighborhoods)
3. **Chat with the AI** using natural language:
   - "Find underground art shows this weekend"
   - "What's happening in Brooklyn tonight under $20?"
   - "Show me family-friendly outdoor events"
4. **Explore results** with detailed event cards and maps

### Advanced Features

- **Custom Date Ranges**: Use the advanced search filters
- **Save Favorites**: Save events you're interested in
- **View Statistics**: See trending categories and popular neighborhoods
- **Accessibility Filters**: Find venues that meet your accessibility needs

## 📁 Project Structure

```
ExploreNYC/
├── app.py                     # Main Streamlit application
├── config.py                  # Configuration and settings
├── langchain_integration.py   # LangGraph AI agent implementation
├── requirements.txt           # Python dependencies
├── env.example               # Complete environment variables template
├── env.minimal               # Minimal environment template
├── utils/
│   ├── __init__.py
│   ├── event_utils.py        # Event processing utilities
│   └── ui_components.py      # Streamlit UI components
└── README.md                 # This file
```

## 🧩 Architecture

### Core Components

1. **Streamlit Frontend** (`app.py`)
   - Modern, responsive UI with custom CSS
   - Chat interface for natural language queries
   - Interactive sidebar for preferences
   - Event cards, maps, and statistics

2. **LangGraph Integration** (`langchain_integration.py`)
   - AI agent with state management and workflow control
   - Event search tools and recommendation engine
   - Graph-based conversation flow and context management

3. **Utilities** (`utils/`)
   - **Event Processing**: Data filtering, sorting, and statistics
   - **UI Components**: Reusable Streamlit components

### Data Flow

1. User sets preferences in sidebar
2. User asks question in chat interface
3. LangGraph workflow processes query with state management
4. Event search tools find relevant events
5. Results are filtered and personalized based on preferences
6. Events are displayed with rich UI components

## 🔧 Customization

### Adding New Event Sources

1. Create a new tool in `langchain_integration.py`
2. Implement the event search API integration
3. Update the event processor to handle the new data format

### Extending AI Capabilities

1. Add new tools to the `EventExplorerAgent`
2. Update the system prompt for new behaviors
3. Extend the conversation memory for better context

### UI Customization

1. Modify CSS in `app.py` for styling changes
2. Add new components in `utils/ui_components.py`
3. Update the layout in the main application

## 🐛 Troubleshooting

### Common Issues

**"Cohere API key not found" error:**
- Ensure you've created a `.env` file (copy from `env.example`)
- Check that `COHERE_API_KEY` is set correctly
- Restart the Streamlit app after adding the key

**App won't start:**
- Check Python version (3.8+ required)
- Install dependencies: `pip install -r requirements.txt`
- Check for port conflicts (default: 8501)

**No events showing:**
- Currently using mock data for demonstration
- Integrate real APIs by updating `langchain_integration.py`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

Need help? Here are some resources:

- **Issues**: Open a GitHub issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check the code comments for detailed explanations

## 🚗 Roadmap

- [ ] Real-time event data integration
- [ ] User authentication and saved preferences
- [ ] Social features (sharing, reviews)
- [ ] Mobile app version
- [ ] Integration with calendar apps
- [ ] Advanced AI features (image recognition, sentiment analysis)

---

**Built with ❤️ in NYC** | Powered by LangGraph, Cohere & Streamlit
