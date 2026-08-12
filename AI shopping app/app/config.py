"""
Configuration and Constants
Centralized configuration for the RAG application
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# PATH CONFIGURATION
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATABRICKS_DIR = PROJECT_ROOT / "databricks"

# ============================================================================
# MODEL CONFIGURATION
# ============================================================================

LLM_MODEL_ID = os.getenv("LLM_MODEL_ID", "llama-3.3-70b-versatile")
EMBEDDINGS_MODEL_ID = os.getenv(
    "EMBEDDINGS_MODEL_ID", "sentence-transformers/all-MiniLM-L6-v2"
)
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_PROVIDER = "groq"  # Using Groq API for LLM inference

# Model defaults
DEFAULT_MAX_LENGTH = 512
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 0.95
DEFAULT_N_RESULTS = 3

# ============================================================================
# VECTOR DATABASE CONFIGURATION
# ============================================================================

COLLECTION_NAME = "retail_knowledge_base"
VECTOR_DB_TYPE = "chromadb"  # Options: chromadb, pinecone, weaviate

# ============================================================================
# PII MASKING CONFIGURATION
# ============================================================================

PII_MASKING_ENABLED = os.getenv("PII_MASKING_ENABLED", "true").lower() == "true"
MASK_EMAIL = os.getenv("MASK_EMAIL", "true").lower() == "true"
MASK_PHONE = os.getenv("MASK_PHONE", "true").lower() == "true"
MASK_ADDRESS = os.getenv("MASK_ADDRESS", "true").lower() == "true"
MASK_CUSTOMER_ID = os.getenv("MASK_CUSTOMER_ID", "true").lower() == "true"

# PII Detection entities
PII_ENTITIES = [
    "PERSON",
    "EMAIL_ADDRESS",
    "PHONE_NUMBER",
    "CREDIT_CARD",
    "IP_ADDRESS",
    "LOCATION",
    "DATE_TIME",
]

# ============================================================================
# DATABASE CONFIGURATION (Databricks)
# ============================================================================

DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")
DATABRICKS_CATALOG = os.getenv("DATABRICKS_CATALOG", "retail")
DATABRICKS_SCHEMA = os.getenv("DATABRICKS_SCHEMA", "default")

# Table names
ORDERS_TABLE = f"{DATABRICKS_CATALOG}.{DATABRICKS_SCHEMA}.orders"
PRODUCTS_TABLE = f"{DATABRICKS_CATALOG}.{DATABRICKS_SCHEMA}.products"

# ============================================================================
# DATA SOURCE CONFIGURATION
# ============================================================================

# CSV Files
PRODUCTS_CSV = DATA_DIR / "amazon_co-ecommerce_sample_retail_copilot.csv"
ORDERS_CSV = DATA_DIR / "ecommerce_orders_clean.csv"
POLICIES_TXT = DATA_DIR / "retail_polocies.txt"

# Data processing
CHUNK_SIZE = 500  # Chunk size for batch processing
MAX_DOCUMENTS = None  # None = no limit, set number to limit for testing

# ============================================================================
# API CONFIGURATION
# ============================================================================

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_RELOAD = os.getenv("API_RELOAD", "true").lower() == "true"

# CORS
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:8501",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8501",
]

# ============================================================================
# STREAMLIT CONFIGURATION
# ============================================================================

STREAMLIT_SERVER_PORT = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))
STREAMLIT_SERVER_HEADLESS = (
    os.getenv("STREAMLIT_SERVER_HEADLESS", "false").lower() == "true"
)

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ============================================================================
# INFERENCE CONFIGURATION
# ============================================================================

# Device settings
USE_CUDA = True  # Automatically detected in hf_client.py
TORCH_DTYPE = "float16"  # Options: float16, float32
BATCH_SIZE = 32

# ============================================================================
# FEATURE FLAGS
# ============================================================================

ENABLE_CACHE = True
ENABLE_PII_MASKING = PII_MASKING_ENABLED
ENABLE_LOGGING = True
ENABLE_METRICS = False  # Set to True for production monitoring

# ============================================================================
# DATA FIELD MAPPINGS
# ============================================================================

# Orders data columns
ORDERS_COLUMNS = {
    "order_id": "Order ID",
    "customer_id": "Customer ID",
    "product_id": "Product ID",
    "category": "Category",
    "price": "Price",
    "quantity": "Quantity",
    "order_date": "Order Date",
    "shipping_date": "Shipping Date",
    "delivery_status": "Status",
    "payment_method": "Payment Method",
    "device_type": "Device",
    "channel": "Channel",
    "shipping_address": "Shipping Address",
    "billing_address": "Billing Address",
    "customer_segment": "Segment",
}

# Products data columns
PRODUCTS_COLUMNS = {
    "uniq_id": "Product ID",
    "product_name": "Product Name",
    "manufacturer": "Manufacturer",
    "price": "Price",
    "number_available_in_stock": "Stock",
    "number_of_reviews": "Reviews",
    "average_review_rating": "Rating",
    "amazon_category_and_sub_category": "Category",
    "description": "Description",
    "product_description": "Details",
}

# ============================================================================
# VALIDATION THRESHOLDS
# ============================================================================

# Minimum similarity score for retrieval
MIN_SIMILARITY_SCORE = 0.3

# Maximum documents to retrieve per query
MAX_RETRIEVED_DOCUMENTS = 10

# PII Detection confidence threshold
PII_CONFIDENCE_THRESHOLD = 0.5

# ============================================================================
# DEFAULT PROMPTS
# ============================================================================

RAG_SYSTEM_PROMPT = """You are a helpful retail assistant for Retail Pilot.
Your knowledge comes from three sources:
1. Store policies (returns, shipping, payments, customer service hours, etc.)
2. Product catalog (product names, prices, categories, ratings, stock)
3. Order database (accessed via Order ID lookup)

Rules:
- Answer questions based ONLY on the provided context. Do not make up information.
- For product questions, mention the product name, price, and category when available.
- Never fabricate order details, prices, or policy information.
- If the context doesn't contain enough information, say so honestly and suggest contacting Customer Support at m.hamzamaliik@gmail.com (Monday to Friday, 9:00–17:30 CET).
- Be concise, friendly, and professional."""

RAG_QUERY_TEMPLATE = """Based on the following context, answer the user's question:

Context:
{context}

Question: {query}

Answer:"""

# Order-specific prompt for when we have order data
ORDER_SYSTEM_PROMPT = """You are a helpful retail assistant for Retail Pilot.
The customer has provided their Order ID and you have retrieved their order details.
Answer their question based on the order data provided in the context.
Rules:
- Only share information that is relevant to the customer's question.
- Be careful with sensitive information like addresses — only share if specifically asked.
- Be concise, friendly, and professional.
- If the customer asks about something not in the order data, say so honestly."""

ORDER_PROMPT_TEMPLATE = """Order Details:
- Order ID: {order_id}
- Category: {category}
- Price: ${price}
- Quantity: {quantity}
- Order Date: {order_date}
- Shipping Date: {shipping_date}
- Delivery Status: {delivery_status}
- Payment Method: {payment_method}
- Shipping Address: {shipping_address}
- Billing Address: {billing_address}
- Customer Segment: {customer_segment}

Customer's question: {query}"""

# Data loading settings
PRODUCT_EMBED_LIMIT = 5000
PRODUCT_BATCH_SIZE = 500

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def get_model_config():
    """Get model configuration dictionary"""
    return {
        "llm_model_id": LLM_MODEL_ID,
        "embeddings_model_id": EMBEDDINGS_MODEL_ID,
        "max_length": DEFAULT_MAX_LENGTH,
        "temperature": DEFAULT_TEMPERATURE,
        "top_p": DEFAULT_TOP_P,
    }


def get_database_config():
    """Get database configuration dictionary"""
    return {
        "host": DATABRICKS_HOST,
        "token": DATABRICKS_TOKEN,
        "catalog": DATABRICKS_CATALOG,
        "schema": DATABRICKS_SCHEMA,
    }


def get_pii_config():
    """Get PII masking configuration dictionary"""
    return {
        "enabled": PII_MASKING_ENABLED,
        "mask_email": MASK_EMAIL,
        "mask_phone": MASK_PHONE,
        "mask_address": MASK_ADDRESS,
        "mask_customer_id": MASK_CUSTOMER_ID,
        "entities": PII_ENTITIES,
    }


def validate_config():
    """Validate configuration"""
    errors = []

    if not HUGGINGFACE_TOKEN:
        errors.append("HUGGINGFACE_TOKEN not set in environment")

    if not PRODUCTS_CSV.exists():
        errors.append(f"Products CSV not found: {PRODUCTS_CSV}")

    if not ORDERS_CSV.exists():
        errors.append(f"Orders CSV not found: {ORDERS_CSV}")

    if not POLICIES_TXT.exists():
        errors.append(f"Policies TXT not found: {POLICIES_TXT}")

    if errors:
        print("❌ Configuration validation failed:")
        for error in errors:
            print(f"  - {error}")
        return False

    print("✅ Configuration validation passed")
    return True


if __name__ == "__main__":
    print("Configuration Validation")
    print("=" * 50)
    validate_config()
    print("\nModel Config:", get_model_config())
    print("\nPII Config:", get_pii_config())
