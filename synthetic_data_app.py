import streamlit as st
import pandas as pd
import json
import io
import os
from openai import OpenAI
from typing import Optional
import re

# Page configuration
st.set_page_config(
    page_title="Synthetic Data Generator",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Clean, Working CSS with VISIBLE text
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .main .block-container {
        padding: 2rem;
        max-width: 1400px;
    }
    
    /* CRITICAL: Make all text DARK and VISIBLE */
    .stMarkdown, .stText, label, .stTextInput label, .stTextArea label, 
    .stNumberInput label, .stSelectbox label, p, span, div {
        color: #1f2937 !important;
    }
    
    /* Headers - White on gradient background */
    h1, h2, h3 {
        color: white !important;
        font-weight: 800 !important;
    }
    
    /* Input fields - white background, dark text */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        background-color: white !important;
        color: #1f2937 !important;
        border: 2px solid #e5e7eb !important;
        border-radius: 8px !important;
        padding: 10px !important;
        font-size: 14px !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        width: 100% !important;
        transition: all 0.3s !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6) !important;
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(245, 87, 108, 0.4) !important;
    }
    
    /* White cards with visible text */
    [data-testid="stVerticalBlock"] {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    /* Success/Error/Warning - high contrast */
    .stSuccess {
        background-color: #d1fae5 !important;
        color: #065f46 !important;
        border-left: 4px solid #10b981 !important;
    }
    
    .stError {
        background-color: #fee2e2 !important;
        color: #991b1b !important;
        border-left: 4px solid #ef4444 !important;
    }
    
    .stWarning {
        background-color: #fef3c7 !important;
        color: #92400e !important;
        border-left: 4px solid #f59e0b !important;
    }
    
    .stInfo {
        background-color: #dbeafe !important;
        color: #1e40af !important;
        border-left: 4px solid #3b82f6 !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #f9fafb !important;
        color: #1f2937 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    
    /* Hide branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 800 !important;
        color: #1f2937 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #6b7280 !important;
        font-weight: 600 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'generated_data' not in st.session_state:
    st.session_state.generated_data = None
if 'data_format' not in st.session_state:
    st.session_state.data_format = None
if 'preview_data' not in st.session_state:
    st.session_state.preview_data = None
if 'api_key' not in st.session_state:
    st.session_state.api_key = None

def get_demo_api_key():
    """Check if demo API key is available"""
    try:
        if 'DEMO_API_KEY' in st.secrets:
            demo_key = st.secrets['DEMO_API_KEY']
            demo_enabled = st.secrets.get('DEMO_MODE_ENABLED', 'true').lower() == 'true'
            if demo_enabled and demo_key and demo_key.strip():
                return demo_key
    except:
        pass
    
    env_key = os.getenv('DEMO_API_KEY')
    if env_key:
        return env_key
    
    return None

def parse_json_response(response_text: str) -> list:
    """Extract JSON from LLM response"""
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
        matches = re.findall(json_pattern, response_text)
        
        if matches:
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
        
        json_obj_pattern = r'\[\s*\{[\s\S]*\}\s*\]'
        obj_matches = re.findall(json_obj_pattern, response_text)
        
        if obj_matches:
            try:
                return json.loads(obj_matches[0])
            except json.JSONDecodeError:
                pass
        
        raise ValueError("Could not parse JSON from response")

def generate_synthetic_data(
    api_key: str,
    data_description: str,
    sample_data: Optional[str],
    num_records: int,
    model: str = "gpt-4o"
) -> list:
    """Generate synthetic data using OpenAI API"""
    
    client = OpenAI(api_key=api_key)
    
    prompt = f"""You are a synthetic data generation expert. Generate {num_records} realistic and diverse records based on the following requirements:

DATA DESCRIPTION:
{data_description}

"""
    
    if sample_data and sample_data.strip():
        prompt += f"""SAMPLE DATA/EXAMPLE:
{sample_data}

Use the sample data to understand the structure and format, but create NEW diverse data.

"""
    
    prompt += f"""INSTRUCTIONS:
1. Generate EXACTLY {num_records} records
2. Ensure data is realistic, diverse, and high-quality
3. Maintain consistency in data types and formats
4. Include appropriate variation and realistic patterns
5. Return ONLY a valid JSON array of objects
6. Each record should be a dictionary/object with consistent keys
7. Use realistic values - names, dates, numbers, categories should be believable
8. Add variety - don't repeat patterns too much

Return the data as a JSON array like this:
[
  {{"field1": "value1", "field2": "value2", ...}},
  {{"field1": "value1", "field2": "value2", ...}},
  ...
]

IMPORTANT: Return ONLY the JSON array, no explanations or markdown formatting."""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a synthetic data generation expert. You generate realistic, diverse, and high-quality datasets in JSON format. Always return valid JSON arrays."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        max_tokens=16000
    )
    
    response_text = response.choices[0].message.content
    data = parse_json_response(response_text)
    
    if not isinstance(data, list):
        raise ValueError("Generated data is not a list")
    
    if len(data) == 0:
        raise ValueError("No data was generated")
    
    return data

def convert_to_format(data: list, format: str) -> bytes:
    """Convert data to specified format"""
    df = pd.DataFrame(data)
    
    if format == "csv":
        return df.to_csv(index=False).encode('utf-8')
    elif format == "xlsx":
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Synthetic Data')
        return output.getvalue()
    elif format == "json":
        return json.dumps(data, indent=2).encode('utf-8')
    elif format == "tsv":
        return df.to_csv(index=False, sep='\t').encode('utf-8')
    elif format == "parquet":
        output = io.BytesIO()
        df.to_parquet(output, index=False)
        return output.getvalue()
    elif format == "toon":
        toon_output = []
        if len(data) > 0:
            all_keys = set()
            for record in data:
                all_keys.update(record.keys())
            keys = sorted(list(all_keys))
            
            toon_output.append(",".join(keys))
            
            for record in data:
                values = [str(record.get(key, "")) for key in keys]
                toon_output.append(",".join(values))
        
        return "\n".join(toon_output).encode('utf-8')
    else:
        raise ValueError(f"Unsupported format: {format}")

# Header
st.title("🔬 Synthetic Data Generator")
st.markdown("### Generate high-quality synthetic datasets powered by AI")
st.markdown("---")

# API Key Configuration Section (TOP OF PAGE)
st.subheader("⚙️ Configuration")

demo_key = get_demo_api_key()

col1, col2 = st.columns([2, 1])

with col1:
    if demo_key:
        st.success("✅ Demo Mode Active - Free to use!")
        st.info("A demo API key is provided. You can use the app immediately or enter your own key below.")
        
        use_own = st.checkbox("Use my own API key", value=False)
        
        if use_own:
            user_key = st.text_input(
                "Your OpenAI API Key",
                type="password",
                placeholder="sk-proj-...",
                help="Enter your OpenAI API key"
            )
            if user_key:
                st.session_state.api_key = user_key
                st.success("✅ Using your personal API key")
            else:
                st.session_state.api_key = demo_key
        else:
            st.session_state.api_key = demo_key
            
        # Add delete/clear option
        if use_own and st.session_state.api_key:
            if st.button("🗑️ Clear My API Key"):
                st.session_state.api_key = demo_key
                st.success("✅ Cleared! Using demo key now")
                st.rerun()
    else:
        st.warning("⚠️ No demo key available")
        st.info("Enter your OpenAI API key to use this app")
        
        user_key = st.text_input(
            "OpenAI API Key (Required)",
            type="password",
            placeholder="sk-proj-...",
            help="Get your API key from platform.openai.com/api-keys"
        )
        
        if user_key:
            st.session_state.api_key = user_key
            st.success("✅ API key provided")
            
            # Add delete option
            if st.button("🗑️ Clear API Key"):
                st.session_state.api_key = None
                st.info("API key cleared")
                st.rerun()
        else:
            st.session_state.api_key = None

with col2:
    model_choice = st.selectbox(
        "🤖 AI Model",
        ["gpt-4o", "gpt-4o-mini", "gpt-5", "gpt-5-mini"],
        help="Choose the AI model"
    )
    
    model_desc = {
        "gpt-4o": "⚡ Fast & powerful",
        "gpt-4o-mini": "💰 Affordable",
        "gpt-5": "🧠 Advanced reasoning",
        "gpt-5-mini": "💡 Efficient reasoning",
    }
    st.caption(model_desc.get(model_choice, ""))

st.markdown("---")

# Main Content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📝 Data Requirements")
    
    data_description = st.text_area(
        "What type of data do you need?",
        height=150,
        placeholder="Example: Generate customer data with name, email, age (18-80), city (major world cities), and purchase_amount ($10-$5000)",
        help="Describe your data requirements"
    )
    
    sample_data = st.text_area(
        "Sample Data or Example (Optional)",
        height=100,
        placeholder='{"name": "Jane Smith", "email": "jane@email.com", "age": 28, "city": "London", "purchase_amount": 245.50}',
        help="Provide an example"
    )

with col2:
    st.subheader("⚙️ Settings")
    
    num_records = st.number_input(
        "Number of Records",
        min_value=1,
        max_value=1000,
        value=50,
        step=10
    )
    
    output_format = st.selectbox(
        "Output Format",
        ["csv", "json", "xlsx", "tsv", "parquet", "toon"]
    )
    
    format_info = {
        "csv": "📊 Excel compatible",
        "json": "🔧 API friendly",
        "xlsx": "📈 Excel spreadsheet",
        "tsv": "📋 Tab-separated",
        "parquet": "🗄️ Big data format",
        "toon": "✨ Simplified format"
    }
    st.caption(format_info.get(output_format, ""))

# Generate Button
st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    generate_button = st.button("🚀 Generate Synthetic Data", use_container_width=True)

# Generate Data
if generate_button:
    if not st.session_state.api_key:
        st.error("❌ Please provide an OpenAI API key above in the Configuration section")
    elif not data_description.strip():
        st.error("❌ Please describe the type of data you need")
    else:
        with st.spinner(f"🔄 Generating {num_records} records using {model_choice}..."):
            try:
                data = generate_synthetic_data(
                    api_key=st.session_state.api_key,
                    data_description=data_description,
                    sample_data=sample_data,
                    num_records=num_records,
                    model=model_choice
                )
                
                file_data = convert_to_format(data, output_format)
                
                st.session_state.generated_data = file_data
                st.session_state.data_format = output_format
                st.session_state.preview_data = data
                
                st.success(f"✅ Successfully generated {len(data)} records!")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.session_state.generated_data = None

# Display Results
if st.session_state.generated_data:
    st.markdown("---")
    st.subheader("📦 Generated Data")
    
    # Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Records", len(st.session_state.preview_data))
    with col2:
        st.metric("Format", st.session_state.data_format.upper())
    with col3:
        size_kb = len(st.session_state.generated_data) / 1024
        st.metric("Size", f"{size_kb:.1f} KB")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Convert & Download
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        convert_format = st.selectbox(
            "🔄 Convert to different format:",
            ["csv", "json", "xlsx", "tsv", "parquet", "toon"],
            index=["csv", "json", "xlsx", "tsv", "parquet", "toon"].index(st.session_state.data_format),
            key="convert_format"
        )
    
    with col2:
        if st.button("🔄 Convert", use_container_width=True):
            try:
                converted_data = convert_to_format(st.session_state.preview_data, convert_format)
                st.session_state.generated_data = converted_data
                st.session_state.data_format = convert_format
                st.success(f"✅ Converted to {convert_format.upper()}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    with col3:
        file_ext = output_format if output_format else "txt"
        st.download_button(
            label="📥 Download",
            data=st.session_state.generated_data,
            file_name=f"synthetic_data.{st.session_state.data_format}",
            mime=f"application/{st.session_state.data_format}",
            use_container_width=True
        )
    
    # Preview
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("👀 Data Preview")
    
    if st.session_state.data_format == "toon":
        preview_text = st.session_state.generated_data.decode('utf-8')
        st.code(preview_text[:1000] + ("..." if len(preview_text) > 1000 else ""), language="text")
    elif st.session_state.data_format in ["csv", "xlsx", "tsv", "parquet"]:
        df = pd.DataFrame(st.session_state.preview_data)
        st.dataframe(df, use_container_width=True, height=400)
        
        with st.expander("📊 Data Statistics"):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Shape:**", df.shape)
                st.write("**Columns:**", list(df.columns))
            with col2:
                st.write("**Data Types:**")
                st.json(df.dtypes.astype(str).to_dict())
    else:
        st.json(st.session_state.preview_data[:5])
        if len(st.session_state.preview_data) > 5:
            st.info(f"Showing 5 of {len(st.session_state.preview_data)} records")

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <div style='text-align: center; color: white; padding: 1rem;'>
        <p>Powered by OpenAI • Built with Streamlit</p>
    </div>
""", unsafe_allow_html=True)
