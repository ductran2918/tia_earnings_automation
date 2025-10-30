"""Configuration constants for the application."""

# File upload settings
MAX_FILE_SIZE_MB = 25

# LLM model settings
MODEL_NAME = "openai/gpt-oss-20b:free"
TEMPERATURE = 0.0
MAX_TOKENS = 50000  # Increased for comprehensive financial data extraction

# Page configuration
PAGE_TITLE = "TiA automated earnings reporting tool"
PAGE_ICON = "📊"
PAGE_LAYOUT = "wide"

# Authentication page constants
AUTH_QUESTION = "What is your favorite food?"
AUTH_ERROR_MESSAGE = "Sorry, we couldn't find your account. Have you registered for this tool? Please contact duc@techinasia.com for more information."
USER_VERIFY_FILE = "user_verify_question.json"

# Welcome page constants
WELCOME_TITLE_TEMPLATE = "Welcome, {name}, to Tech in Asia's earnings tracker tool"
COMPANY_TYPE_LABEL = "Please select the type of company you want to extract financials"
COMPANY_TYPE_OPTIONS = ["Public companies (Grab, Sea Group...)", "Private company (Glints, Shopback...)"]
NEXT_BUTTON_LABEL = "Next"
BACK_BUTTON_LABEL = "← Back to Selection"

# Public company page constants
PUBLIC_COMPANIES_LIST_FILE = "public_companies_list.json"
PUBLIC_COMPANY_DROPDOWN_LABEL = "Which public company do you need to extract data today?"
COMING_SOON_MESSAGE_TEMPLATE = "The extraction workflow for {company} is being developed"

# Private company page constants
COMPANY_HINT_LABEL = "Company Name"
COMPANY_HINT_PLACEHOLDER = "e.g., Grab Holdings, Sea Limited"
COMPANY_HINT_HELP = "Optional hint used to guide extraction"
UPLOAD_SUBHEADER = "Upload PDF"
UPLOAD_INFO_TEXT = "Upload a PDF report to begin extracting metrics."
UPLOAD_BUTTON_LABEL = "Extract Financial Data"
DOWNLOAD_BUTTON_LABEL = "Download JSON"
UPLOAD_WIDGET_LABEL = "Upload a financial PDF"
DOWNLOAD_FILENAME = "financial_data.json"