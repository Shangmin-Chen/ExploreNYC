# 🗽 ExploreNYC - AI-Powered Event Discovery

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28.0+-red.svg)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/langchain-0.1.0+-green.svg)](https://langchain.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Discover NYC's hidden gems and mainstream events with AI-powered recommendations**

ExploreNYC is an intelligent event discovery application that uses artificial intelligence to help users find amazing events in New York City. Built with Streamlit and powered by LangChain and Cohere, it provides personalized event recommendations through natural language conversations.

## ✨ Features

### 🤖 AI-Powered Discovery
- **Natural Language Interface**: Chat with an AI assistant to find events
- **Intelligent Recommendations**: Personalized suggestions based on your preferences
- **Smart Query Processing**: Understands complex requests like "Find underground art shows this weekend"

### 📊 Real-Time Event Data
- **NYC Open Data API**: Integrates with NYC Open Data for official events
- **Live Event Information**: Real-time data from official sources
- **Comprehensive Coverage**: From mainstream events to hidden gems

### 🎯 Personalized Experience
- **User Preferences**: Set your interests, budget, and location preferences
- **Smart Filtering**: AI-powered filtering based on your criteria
- **Interactive UI**: Beautiful, responsive interface with quick action buttons

### 🗺️ NYC-Focused
- **Neighborhood Support**: Search by specific NYC neighborhoods
- **Local Insights**: AI trained on NYC culture and venues
- **Free Public Events**: Access to NYC Open Data events (no API key required)

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Internet connection for API access
- Cohere API key (free tier available)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ExploreNYC.git
   cd ExploreNYC
   ```

2. **Set up environment**
   ```bash
   # Copy the example environment file
   cp env.example .env
   
   # Edit .env and add your API keys
   nano .env
   ```

3. **Install dependencies**
   ```bash
   # Using the smart startup script (recommended)
   python run.py
   
   # Or manually
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   # Using the startup script
   python run.py
   
   # Or directly with Streamlit
   streamlit run app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:8501` to start exploring NYC events!

## 🔑 API Keys Setup

### Required: Cohere API Key
1. Visit [Cohere Dashboard](https://dashboard.cohere.ai/api-keys)
2. Sign up for a free account
3. Generate an API key
4. Add it to your `.env` file:
   ```
   COHERE_API_KEY=your_cohere_api_key_here
   ```

### Optional: LangChain API Key
1. Visit [LangChain Smith](https://smith.langchain.com/)
2. Sign up for tracing and monitoring
3. Add it to your `.env` file:
   ```
   LANGCHAIN_API_KEY=your_langchain_api_key_here
   ```

**Note**: NYC Open Data API is completely free and requires no API key.

## 🏗️ Architecture

### Core Components

```
ExploreNYC/
├── app.py                 # Main Streamlit application
├── run.py                 # Smart startup script
├── config.py              # Configuration management
├── langchain_integration.py # AI agent and LangGraph workflows
├── services/              # API service integrations
│   ├── event_service.py   # Unified event service
│   └── nyc_open_data_service.py # NYC Open Data integration
└── utils/                 # Utility modules
    ├── constants.py       # Application constants
    ├── date_utils.py      # Date/time utilities
    ├── error_handling.py  # Error handling utilities
    ├── event_utils.py     # Event processing utilities
    └── ui_components.py   # UI components
```

### Technology Stack

- **Frontend**: Streamlit
- **AI/ML**: LangChain, LangGraph, Cohere
- **Data Sources**: NYC Open Data API
- **Language**: Python 3.8+
- **Dependencies**: See `requirements.txt`

## 🎮 Usage

### Basic Usage

1. **Start the application** using `python run.py`
2. **Set your preferences** in the sidebar (categories, budget, neighborhoods)
3. **Chat with the AI** using natural language:
   - "Find art galleries this weekend"
   - "Show me free events in Brooklyn"
   - "What's happening tonight in Manhattan?"

### Advanced Features

- **Quick Suggestions**: Use the quick action buttons for common searches
- **Preference Filtering**: Set detailed preferences for personalized results
- **Time-based Searches**: Ask for events by specific time frames
- **Location-specific**: Search by neighborhood or borough

### Example Queries

```
"Find underground music venues in Williamsburg this weekend"
"Show me free art events in Manhattan"
"What food festivals are happening this month?"
"Find family-friendly activities in Queens"
"Any jazz concerts tonight?"
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `COHERE_API_KEY` | Yes | Cohere API key for AI functionality |
| `LANGCHAIN_API_KEY` | No | LangChain API key for tracing |
| `LANGCHAIN_TRACING_V2` | No | Enable LangChain tracing (true/false) |

### Application Settings

Key settings can be modified in `config.py`:

```python
# AI Model Configuration
DEFAULT_MODEL = "command-r-plus"  # Cohere model
MAX_TOKENS = 1000
TEMPERATURE = 0.7

# Rate Limiting
RATE_LIMIT_SECONDS = 6  # 6 seconds between requests
```

## 🛠️ Development

### Project Structure

- **`app.py`**: Main Streamlit application with UI logic
- **`run.py`**: Smart startup script with dependency management
- **`config.py`**: Centralized configuration management
- **`langchain_integration.py`**: AI agent and workflow orchestration
- **`services/`**: API integrations and data sources
- **`utils/`**: Utility functions and helper modules

### Adding New Features

1. **New Event Sources**: Add services in `services/` directory
2. **UI Components**: Add reusable components in `utils/ui_components.py`
3. **AI Tools**: Add new tools in `langchain_integration.py`
4. **Configuration**: Update `config.py` for new settings

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all functions
- Document all public functions and classes
- Use descriptive variable and function names

## 🧪 Testing

### Manual Testing

1. **Start the application**: `python run.py`
2. **Test basic functionality**: Try different queries
3. **Test error handling**: Try invalid inputs
4. **Test preferences**: Set different user preferences

### Automated Testing

```bash
# Run basic validation
python -c "from config import Config; print('Config loaded successfully')"

# Test service initialization
python -c "from services.event_service import EventService; print('Services working')"

# Test AI integration
python -c "from langchain_integration import EventExplorerAgent; print('AI agent ready')"
```

## 🐛 Troubleshooting

### Common Issues

1. **"Cohere API Key Missing"**
   - Ensure your `.env` file exists and contains a valid Cohere API key
   - Check that the key is not a placeholder value

2. **"No event services available"**
   - Verify at least one API key is configured
   - Check your internet connection

3. **"Streamlit not found"**
   - Run `pip install -r requirements.txt`
   - Or use the smart startup script: `python run.py`

4. **"Port 8501 already in use"**
   - Stop other Streamlit applications
   - Or specify a different port: `streamlit run app.py --server.port 8502`

### Debug Mode

Enable debug logging by setting environment variables:

```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=your_key_here
```

## 📊 Performance

### Rate Limiting

- **Cohere API**: 6 seconds between requests (10 requests/minute)
- **NYC Open Data**: 1 second between requests

### Optimization Tips

- Use the async search methods for better performance
- Cache frequently accessed data
- Implement request batching for multiple queries

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** following the code style guidelines
4. **Add tests** for new functionality
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to the branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/ExploreNYC.git
cd ExploreNYC

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp env.example .env
# Edit .env with your API keys

# Run the application
python run.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Cohere** for providing the AI language models
- **LangChain** for the AI framework and tools
- **Streamlit** for the web application framework
- **NYC Open Data** for free public event data
- **NYC** for being an amazing city with endless events to discover!

## 📞 Support

- **Documentation**: Check this README and inline code documentation
- **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/yourusername/ExploreNYC/issues)
- **Discussions**: Join the conversation on [GitHub Discussions](https://github.com/yourusername/ExploreNYC/discussions)

## 🗺️ Roadmap

### Upcoming Features

- [ ] **Event Favorites**: Save and manage favorite events
- [ ] **Calendar Integration**: Export events to calendar apps
- [ ] **Social Features**: Share events with friends
- [ ] **Mobile App**: Native mobile application
- [ ] **Advanced Analytics**: Event trend analysis
- [ ] **Multi-City Support**: Expand beyond NYC

### Version History

- **v1.0.0** (Current): Initial release with core functionality
- **v0.9.0**: Beta release with basic AI integration
- **v0.8.0**: Alpha release with NYC Open Data integration

---

**Made with ❤️ in NYC** | **ExploreNYC © 2024**

*Discover the city that never sleeps, one event at a time.*