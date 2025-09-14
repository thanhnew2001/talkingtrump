# Talking Trump - AI Video Call App

An AI-powered video call application featuring Donald Trump's voice and personality, built with Cloudflare Pages and Replicate AI.

## Features

- 🎥 **Video Interface**: Interactive video call experience
- 🎤 **Voice Recognition**: Speak naturally with speech-to-text
- 🗣️ **AI Voice Generation**: Trump's voice powered by Replicate AI
- 💬 **Chat History**: Persistent conversation memory
- 🎭 **Personality Traits**: Authentic Trump speaking patterns and traits
- 📱 **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Backend**: Cloudflare Pages Functions
- **AI Voice**: Replicate API (Tortoise TTS)
- **AI Text**: Replicate API (Meta Llama 3.1)
- **Speech Recognition**: Web Speech API
- **Deployment**: Cloudflare Pages

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/thanhnew2001/talkingtrump.git
cd talkingtrump
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Set Environment Variables

Create a `.env` file in the root directory:

```env
REPLICATE_API_TOKEN=your_replicate_api_token_here
NEWS_API_KEY=your_news_api_key_here
```

### 4. Deploy to Cloudflare Pages

1. Connect your GitHub repository to Cloudflare Pages
2. Set the following environment variables in Cloudflare Pages dashboard:
   - `REPLICATE_API_TOKEN`: Your Replicate API key
   - `NEWS_API_KEY`: Your NewsAPI key (optional)

### 5. Generate Greeting Audio Files (Optional)

```bash
# Set your Replicate API token
export REPLICATE_API_TOKEN="your_token_here"

# Run the greeting generator
python3 generate_greetings.py
```

## API Keys Required

| Variable | Value | Description |
|----------|-------|-------------|
| `REPLICATE_API_TOKEN` | `r8_...` | Your Replicate API key |
| `NEWS_API_KEY` | `...` | Your NewsAPI key (optional) |

## Project Structure

```
talkingtrump/
├── public/
│   ├── index.html          # Main application
│   ├── greetings/          # Generated greeting audio files
│   └── trump/             # Trump images
├── functions/
│   └── api/
│       ├── health.js      # Health check endpoint
│       └── trump-response.js # Main AI response API
├── generate_greetings.py  # Script to generate greeting audio
├── package.json
├── wrangler.toml
└── README.md
```

## Usage

1. **Start a Call**: Click "Start Call" to begin
2. **Speak or Type**: Use voice recognition or type your messages
3. **Chat with Trump**: Experience AI-powered conversations with Trump's personality
4. **View History**: Chat history is automatically saved and restored

## Features in Detail

### AI Personality
- Authentic Trump speaking patterns
- References to current events and politics
- Characteristic phrases and expressions
- Blames Biden administration for problems
- Claims expertise on various topics

### Voice Features
- High-quality voice synthesis using Tortoise TTS
- Custom Trump voice model
- Fallback to browser TTS if needed
- Microphone muting during AI responses

### Chat Features
- Persistent chat history in localStorage
- System message filtering
- Real-time conversation flow
- Clear chat history option

## Development

### Local Development

```bash
# Start development server
npm run dev
```

### Deployment

```bash
# Deploy to Cloudflare Pages
npm run deploy
```

## Environment Variables

Make sure these are set in Cloudflare Pages:
- `REPLICATE_API_TOKEN`: Your Replicate API key
- `SITE_URL`: Your deployed site URL (for reference audio)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Disclaimer

This is a demonstration project for educational purposes. The AI-generated content does not represent actual political views or statements.