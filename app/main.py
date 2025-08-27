import streamlit as st
import pdfplumber
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import tempfile
import os


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
    
    except Exception as e:
        return {
            "page_count": 0,
            "has_text": False,
            "success": False,
            "error": str(e)
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
    
    except Exception as e:
        return f"Error reading page preview: {str(e)}"


def format_file_size(size_bytes: int) -> str:
    """Convert bytes to human-readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def main():
    st.set_page_config(
        page_title="Financial PDF Loader",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("Financial PDF Loader — Step 1: Upload")
    
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
                st.session_state.temp_file_path = str(temp_path)
                
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
                
                # Status box with temp file path
                st.subheader("Status")
                st.code(f"Temporary file saved to: {temp_path}")
                
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
                # Handle encrypted or corrupted PDFs
                if "encrypted" in str(e).lower() or "password" in str(e).lower():
                    st.warning("This PDF appears to be encrypted or password-protected. Please use an unprotected PDF.")
                elif "corrupted" in str(e).lower() or "invalid" in str(e).lower():
                    st.warning("This PDF file appears to be corrupted or invalid. Please try a different file.")
        
        else:
            st.info("No file uploaded yet. Use the uploader on the left to select a PDF file.")


if __name__ == "__main__":
    main()