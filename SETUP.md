# Setup Guide

## Basic Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the app:
```bash
streamlit run synthetic_data_app.py
```

3. Open your browser to `http://localhost:8501`

## Using Your Own API Key

Enter your OpenAI API key in the configuration section at the top of the page. The key is stored in your browser session only and cleared when you close the tab.

Get an API key: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

## Demo Mode (For Presentations)

If you want to provide your API key for others to use (like at a conference or demo), create a secrets file:

Create `.streamlit/secrets.toml`:
```toml
DEMO_API_KEY = "sk-your-api-key-here"
DEMO_MODE_ENABLED = "true"
```

Your key stays on the server and is never exposed to users. They'll see "Demo Mode Active" and can use the app immediately.

To turn it off later:
```toml
DEMO_MODE_ENABLED = "false"
```

## Deploying to Streamlit Cloud

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo and deploy
4. Add secrets in app settings (same format as above)

## Cost Control

Set spending limits on your OpenAI account:
- Go to [platform.openai.com/account/limits](https://platform.openai.com/account/limits)
- Set a monthly budget ($20-50 recommended for demos)
- Enable usage alerts

## Using Virtual Environments

Recommended for cleaner dependency management:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Troubleshooting

**"Client.init() got an unexpected keyword argument 'proxies'"**
- Update OpenAI library: `pip install openai --upgrade`

**"Invalid API key"**
- Check your key at [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- Make sure there are no extra spaces

**App won't start**
- Check Python version (3.9+ required)
- Try reinstalling: `pip install -r requirements.txt --force-reinstall`
