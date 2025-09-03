import streamlit as st
import pdfplumber
from pathlib import Path
from datetime import datetime
from typing import Dict
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore


def save_temp_file(uploaded_file) -> Path:
    """Save uploaded file to temporary directory with timestamped filename."""
    # Ensure .tmp directory exists
    tmp_dir = Path(".tmp")
    tmp_dir.mkdir(exist_ok=True)
    
    # Create timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{uploaded_file.name}"
    tmp_path = tmp_dir / filename
    
    # Save uploaded bytes to temp file
    with open(tmp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return tmp_path


def get_pdf_info(pdf_path: Path) -> Dict:
    """Extract basic PDF information using pdfplumber."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            page_count = len(pdf.pages)
            has_text = False
            
            # Check if first page has extractable text
            if page_count > 0:
                first_page_text = pdf.pages[0].extract_text()
                has_text = bool(first_page_text and first_page_text.strip())
            
            return {
                "page_count": page_count,
                "has_text": has_text,
                "success": True
            }
    
    except Exception as exc:
        return {
            "page_count": 0,
            "has_text": False,
            "success": False,
            "error": f"{exc}"
        }


def read_page_preview(pdf_path: Path, page_idx: int = 0, max_chars: int = 300) -> str:
    """Extract text preview from specified page of PDF."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if page_idx >= len(pdf.pages):
                return "Page index out of range."
            
            page_text = pdf.pages[page_idx].extract_text()
            if not page_text or not page_text.strip():
                return "No extractable text on page 1."
            
            # Clean whitespace and limit length
            cleaned_text = " ".join(page_text.strip().split())
            if len(cleaned_text) <= max_chars:
                return cleaned_text
            else:
                return cleaned_text[:max_chars] + "..."
    
    except Exception as exc:
        return f"Error reading page preview: {exc}"


def extract_full_pdf_text(pdf_path: Path) -> str:
    """Extract all text from PDF as a single string."""
    try:
        full_text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                full_text += page_text + "\n\n"
        return full_text.strip()
    except Exception as exc:
        st.error(f"Error extracting PDF text: {exc}")
        return ""


def extract_financial_data_with_llm(pdf_text: str, api_key: str, company_hint: str = "", model_name: str = "gemini-1.5-flash", temperature: float = 0.0, max_tokens: int = 10000) -> Dict:
    """Extract financial data using Gemini LLM with structured prompt."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""You are a financial data extraction expert. Extract financial data from this annual financial statement text.

IMPORTANT INSTRUCTIONS:
1. Extract data for TWO YEARS (current year and previous year) - auto-detect the years from the content
2. Use RAW NUMBERS only (e.g., 1000000000 not 1B or 1000M)
3. Keep original currencies as mentioned in the financial statement
4. Use negative sign (-) for negative values/losses
5. Return null for missing data

EXTRACT THESE 7 METRICS FOR BOTH YEARS:

I. Income Statement (P&L) Metrics:
- Revenue (or Total Revenue, Net Revenue, Sales, Revenue and other income, etc.)
- Profit or Loss Before Income Tax (or Profit Before Tax, Income Before Tax, Pre-tax Income, etc.)
- Profit or Loss for the Year/After Income Tax (or Net Profit, Net Income, Net Loss, Profit After Tax, etc.)

II. Cash Flow Statement Metrics:
- Net Cash from Operating Activities (or Operating Cash Flow, Cash from Operations, etc.)
- Net Cash from Investing Activities (or Cash from Investments, Investing Cash Flow, etc.)
- Net Cash from Financing Activities (or Cash from Financing, Financing Cash Flow, etc.)
- Cash and Cash Equivalents at End of Year (or Cash at Year End, Total Cash, etc.)

REQUIRED JSON OUTPUT FORMAT:
{{
  "year_1": {{
    "year": "YYYY",
    "revenue": number_or_null,
    "profit_before_tax": number_or_null,
    "profit_after_tax": number_or_null,
    "net_cash_operating": number_or_null,
    "net_cash_investing": number_or_null,
    "net_cash_financing": number_or_null,
    "cash_end_of_year": number_or_null
  }},
  "year_2": {{
    "year": "YYYY",
    "revenue": number_or_null,
    "profit_before_tax": number_or_null,
    "profit_after_tax": number_or_null,
    "net_cash_operating": number_or_null,
    "net_cash_investing": number_or_null,
    "net_cash_financing": number_or_null,
    "cash_end_of_year": number_or_null
  }},
  "currencies": ["USD", "SGD"],
  "company_name": "extracted_company_name",
  "report_type": "Annual Report" or "10-K" or "Financial Statements"
}}

Company hint (if provided): {company_hint}

Financial Statement Text:
{pdf_text}

Respond with ONLY the JSON object, no additional text."""
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )
        )
        
        # Parse JSON response
        json_text = response.text.strip()
        # Remove any potential markdown code blocks
        if json_text.startswith('```json'):
            json_text = json_text[7:-3]
        elif json_text.startswith('```'):
            json_text = json_text[3:-3]
            
        return json.loads(json_text)
        
    except json.JSONDecodeError as exc:
        st.error(f"Failed to parse LLM response as JSON: {exc}")
        return {"error": "Invalid JSON response from LLM"}
    except Exception as exc:
        st.error(f"LLM extraction failed: {exc}")
        return {"error": f"LLM error: {exc}"}


def format_file_size(size_bytes: int) -> str:
    """Convert bytes to human-readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def initialize_firebase():
    """Initialize Firebase Admin SDK and return Firestore client."""
    try:
        # Check if Firebase is already initialized to avoid duplicate initialization
        if firebase_admin._apps:
            # Firebase already initialized, get existing app
            app = firebase_admin.get_app()
        else:
            # Load credentials path from environment variable
            credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
            
            if not credentials_path:
                st.error("❌ Firebase configuration error: FIREBASE_CREDENTIALS_PATH environment variable not found.")
                return None
            
            # Validate that the credentials file exists
            if not os.path.exists(credentials_path):
                st.error(f"❌ Firebase credentials file not found at: {credentials_path}")
                return None
            
            # Initialize Firebase Admin SDK with service account credentials
            cred = credentials.Certificate(credentials_path)
            app = firebase_admin.initialize_app(cred)
        
        # Return Firestore client instance
        db = firestore.client()
        return db
        
    except Exception as exc:
        st.error(f"❌ Firebase initialization failed: {exc}")
        return None


def main():
    # Load environment variables
    load_dotenv()
    
    st.set_page_config(
        page_title="Financial Data Extractor",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("Financial Data Extractor — LLM-Powered")
    
    # Configuration Panel (Sidebar) - User-facing inputs only
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Company name input (the only user-facing setting)
        company_hint = st.text_input(
            "Company Name",
            placeholder="e.g., Grab Holdings, Sea Limited",
            help="Enter the company name as it appears in financial reports (optional but recommended for validation)"
        )
        
        # Firebase Connection Test
        st.divider()
        st.subheader("🔥 Firebase Connection")
        
        if st.button("🔥 Test Firebase Connection", type="secondary"):
            with st.spinner("Testing Firebase connection..."):
                db = initialize_firebase()
                
                if db is not None:
                    try:
                        # Test a simple Firestore operation
                        collections = db.collections()
                        collection_names = [col.id for col in collections]
                        
                        st.success("✅ Firebase connected successfully!")
                        st.info(f"**Project:** financial-data-extractor")
                        st.info(f"**Collections found:** {len(collection_names)}")
                        
                        if collection_names:
                            st.text(f"Collections: {', '.join(collection_names[:5])}")
                        else:
                            st.text("No collections found (new project)")
                            
                    except Exception as exc:
                        st.success("✅ Firebase connected successfully!")
                        st.warning(f"Connection successful, but couldn't list collections: {exc}")
                        st.info("**Project:** financial-data-extractor")
                else:
                    st.error("❌ Firebase connection failed")
                    st.text("Check your credentials and environment variables.")
    
    # Internal configuration (hidden from users)
    api_key = os.getenv("GEMINI_API_KEY", "")
    model_name = "gemini-1.5-flash"  # Fixed model choice
    temperature = 0.0  # Fixed for consistent results
    max_tokens = 1024  # Fixed token limit
    
    # Validation (internal)
    if not api_key:
        st.error("❌ System configuration error: API key not found. Please contact administrator.")
        return
    
    # Initialize session state
    if 'uploaded_file_info' not in st.session_state:
        st.session_state.uploaded_file_info = None
    if 'temp_file_path' not in st.session_state:
        st.session_state.temp_file_path = None
    
    # Create two columns
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Upload PDF")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Upload a financial PDF",
            type=["pdf"],
            accept_multiple_files=False,
            help="Select a PDF file (max 25MB)"
        )
        
        # Clear button
        if st.button("Clear", type="secondary"):
            st.session_state.uploaded_file_info = None
            st.session_state.temp_file_path = None
            # Clean up temp file if it exists
            if st.session_state.temp_file_path and Path(st.session_state.temp_file_path).exists():
                try:
                    os.remove(st.session_state.temp_file_path)
                except:
                    pass
            st.rerun()
    
    with col2:
        st.subheader("File Information")
        
        if uploaded_file is not None:
            # Validate file size (25MB limit)
            file_size = uploaded_file.size
            if file_size > 25 * 1024 * 1024:  # 25MB in bytes
                st.error(f"File too large: {format_file_size(file_size)}. Maximum allowed size is 25MB.")
                return
            
            # Validate MIME type
            if uploaded_file.type != "application/pdf":
                st.error(f"Invalid file type: {uploaded_file.type}. Please upload a PDF file.")
                return
            
            try:
                # Save temporary file
                temp_path = save_temp_file(uploaded_file)
                st.session_state.temp_file_path = f"{temp_path}"
                
                # Display basic file info
                st.success("File uploaded successfully!")
                
                col2a, col2b = st.columns([1, 1])
                with col2a:
                    st.metric("File Name", uploaded_file.name)
                    st.metric("File Size", format_file_size(file_size))
                
                # Extract PDF information
                pdf_info = get_pdf_info(temp_path)
                
                with col2b:
                    if pdf_info["success"]:
                        st.metric("Page Count", pdf_info["page_count"])
                        st.metric("Has Text", "Yes" if pdf_info["has_text"] else "No")
                    else:
                        st.warning("Could not read PDF information")
                        st.error(f"Error: {pdf_info['error']}")
                
                # Show text preview if PDF was successfully processed
                if pdf_info["success"] and pdf_info["has_text"]:
                    st.subheader("Page 1 Preview")
                    preview_text = read_page_preview(temp_path)
                    st.text_area(
                        "First 300 characters:",
                        value=preview_text,
                        height=150,
                        disabled=True
                    )
                elif pdf_info["success"]:
                    st.subheader("Page 1 Preview")
                    st.info("No extractable text on page 1.")
                
                # Step 6: LLM-Based Financial Data Extraction
                if pdf_info["success"] and pdf_info["page_count"] > 0:
                    st.divider()
                    st.subheader("🤖 LLM Financial Data Extraction")
                    
                    if st.button("📊 Extract Financial Data", type="primary"):
                        with st.spinner("Extracting text from PDF..."):
                            pdf_text = extract_full_pdf_text(temp_path)
                        
                        if pdf_text:
                            with st.spinner(f"Analyzing with {model_name}..."):
                                financial_data = extract_financial_data_with_llm(
                                    pdf_text, api_key, company_hint, model_name, temperature, max_tokens
                                )
                            
                            if "error" not in financial_data:
                                st.success("✅ Financial data extracted successfully!")
                                
                                # Company name validation
                                company = financial_data.get("company_name", "")
                                if company and company_hint and company_hint.lower() in company.lower():
                                    st.success("✅ Company name matches your hint")
                                
                                # Display JSON output
                                st.subheader("📊 Extracted Financial Data")
                                st.json(financial_data)
                            
                            else:
                                st.error(f"❌ {financial_data['error']}")
                        else:
                            st.error("❌ Failed to extract text from PDF")
                
                # Status box with temp file path
                st.subheader("Status")
                st.code(f"Temporary file saved to: {temp_path}")
                
            except Exception as exc:
                st.error(f"Error processing file: {exc}")
                # Handle encrypted or corrupted PDFs
                if "encrypted" in f"{exc}".lower() or "password" in f"{exc}".lower():
                    st.warning("This PDF appears to be encrypted or password-protected. Please use an unprotected PDF.")
                elif "corrupted" in f"{exc}".lower() or "invalid" in f"{exc}".lower():
                    st.warning("This PDF file appears to be corrupted or invalid. Please try a different file.")
        
        else:
            st.info("No file uploaded yet. Use the uploader on the left to select a PDF file.")


if __name__ == "__main__":
    main()