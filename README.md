# Synthetic Data Generator

A web application for generating realistic synthetic datasets using OpenAI's language models. Built with Streamlit for presentations and demonstrations at the Microsoft AI event.

## Features

- Generate synthetic data from natural language descriptions
- Support for multiple OpenAI models (GPT-4o, o1-preview, GPT-4-Turbo, etc.)
- Export to CSV, JSON, Excel, TSV, Parquet, and TOON formats
- Convert between formats after generation
- Built-in data preview and statistics

## Quick Start

Install dependencies:
```bash
pip install -r requirements.txt
```

Run the app:
```bash
streamlit run synthetic_data_app.py
```

The app will open in your browser at `http://localhost:8501`

## Usage

1. Enter your OpenAI API key in the configuration section at the top
2. Describe the data you want to generate
3. Optionally provide a sample record
4. Choose the number of records and output format
5. Click generate and download your data

Example prompt:
```
Generate customer data with name, email, age (18-80), city, 
and purchase_amount ($10-$5000)
```


## Deployment

### Streamlit Cloud

1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Deploy

To add your API key for demo mode:
- Go to your app settings
- Add secrets in the Secrets section
- Use the same format as shown above

### Local Development

The app uses session state to manage API keys temporarily. Keys are never stored permanently.

## File Formats

- **CSV** - Standard comma-separated values
- **JSON** - Structured data format
- **XLSX** - Excel spreadsheet
- **TSV** - Tab-separated values
- **Parquet** - Columnar storage format
- **TOON** - Simple custom format (id,name,value)

## Requirements

- Python 3.9+
- streamlit >= 1.31.0
- pandas >= 2.1.4
- openai >= 1.30.0
- openpyxl >= 3.1.2
- pyarrow >= 15.0.0

## Cost Management

When using demo mode, set spending limits on your OpenAI account to control costs:
1. Visit [platform.openai.com/account/limits](https://platform.openai.com/account/limits)
2. Set a monthly budget
3. Enable usage alerts

Typical costs for a presentation with 20-30 demos: $1-3


## License

MIT

## Author

Built for the Microsoft Synthetic Data presentation by Namash Aggarwal
