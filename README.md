# ExploreNYC

AI-powered NYC event discovery app using LangChain and real event data.

## Features

- **Real Event Data**: Fetches live events from Eventbrite and NYC Open Data
- **AI-Powered Search**: Uses Cohere and LangChain for intelligent event recommendations
- **Interactive Chat**: Natural language interface for finding events
- **Free to Use**: No paid subscriptions required

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Up Environment**
   ```bash
   cp env.example .env
   # Edit .env and add your COHERE_API_KEY
   ```

3. **Run the App**
   ```bash
   streamlit run app.py
   ```

## API Keys

- **Required**: `COHERE_API_KEY` - Get from [Cohere Dashboard](https://dashboard.cohere.ai/api-keys)
- **Optional**: `EVENTBRITE_API_KEY` - Get from [Eventbrite](https://www.eventbrite.com/platform/api-keys/) (free tier: 1,000 requests/day)
- **NYC Open Data**: No API key needed - completely free

## Event Sources

- **Eventbrite**: Commercial events, concerts, workshops, classes
- **NYC Open Data**: Public events, sports, community events, special events

## Tech Stack

- **Frontend**: Streamlit
- **AI**: Cohere, LangChain, LangGraph
- **Data**: Eventbrite API, NYC Open Data API
- **Language**: Python 3.8+

## License

MIT License