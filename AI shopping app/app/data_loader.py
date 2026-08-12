"""
Data Loader Module
Handles auto-loading of all data sources (policies, products, orders)
into the RAG knowledge base at startup. Also provides order/product
lookup functions and order intent detection.
"""

import re
import pandas as pd
from typing import Optional
from app.config import PRODUCTS_CSV, ORDERS_CSV, POLICIES_TXT

# ---------------------------------------------------------------------------
# Module-level DataFrames (loaded once at startup)
# ---------------------------------------------------------------------------
_products_df: Optional[pd.DataFrame] = None
_orders_df: Optional[pd.DataFrame] = None

PRODUCT_EMBED_LIMIT = 5000
PRODUCT_BATCH_SIZE = 500


# ---------------------------------------------------------------------------
# Data Loading Functions
# ---------------------------------------------------------------------------

def load_policies(file_path=None) -> tuple:
    """
    Parse retail_polocies.txt into Q&A sections.
    Supports both ALL CAPS headers and markdown ## / ### headers.
    Each ### sub-question becomes its own document, prefixed with its
    parent ## section name for context.

    Returns:
        (documents, metadata) ready for ingestion
    """
    file_path = file_path or str(POLICIES_TXT)
    print(f"  Loading policies from {file_path}...")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    sections = []
    current_section = []
    current_parent = ""  # Track the ## parent heading

    for line in content.split("\n"):
        stripped = line.strip()

        # Skip decorative lines (---, empty)
        if stripped == "---" or stripped == "":
            continue

        # Detect ## parent heading (e.g., "## SHIPPING & DELIVERY")
        if stripped.startswith("## "):
            # Save previous section
            if current_section:
                sections.append("\n".join(current_section).strip())
            current_parent = stripped.lstrip("# ").strip()
            current_section = [stripped]

        # Detect ### sub-question (e.g., "### How long does delivery take?")
        elif stripped.startswith("### "):
            # Save previous section
            if current_section:
                sections.append("\n".join(current_section).strip())
            # Start new section with parent context
            if current_parent:
                current_section = [f"[{current_parent}]", stripped]
            else:
                current_section = [stripped]

        # Legacy: ALL CAPS lines (for backward compatibility)
        elif stripped.isupper() and stripped and not stripped.startswith("#"):
            if current_section:
                sections.append("\n".join(current_section).strip())
            current_parent = stripped
            current_section = [stripped]

        else:
            current_section.append(stripped)

    # Don't forget the last section
    if current_section:
        sections.append("\n".join(current_section).strip())

    documents = []
    metadata = []
    for idx, section in enumerate(sections):
        if section.strip():
            documents.append(section)
            # Use first line as label
            first_line = section.split("\n")[0].strip("# ").strip("[]")
            metadata.append({
                "source": "policies",
                "section_index": idx,
                "question": first_line[:100],
            })

    print(f"  Loaded {len(documents)} policy sections")
    return documents, metadata


def load_products_for_embedding(csv_path=None, limit=PRODUCT_EMBED_LIMIT) -> tuple:
    """
    Read products CSV and build condensed summaries for embedding.
    Also stores the full DataFrame for later lookups.

    Returns:
        (documents, metadata) for embedding into ChromaDB
    """
    global _products_df

    csv_path = csv_path or str(PRODUCTS_CSV)
    print(f"  Loading products from {csv_path}...")

    _products_df = pd.read_csv(csv_path, low_memory=False)
    total_rows = len(_products_df)
    print(f"  Total products in CSV: {total_rows}")

    # Build condensed summary strings for embedding (only key fields)
    documents = []
    metadata = []

    subset = _products_df.head(limit)
    for idx, row in subset.iterrows():
        name = str(row.get("product_name", "")).strip()
        manufacturer = str(row.get("manufacturer", "")).strip()
        price = str(row.get("price", "")).strip()
        category = str(row.get("amazon_category_and_sub_category", "")).strip()
        rating = str(row.get("average_review_rating", "")).strip()
        stock = str(row.get("number_available_in_stock", "")).strip()

        # Skip rows with no product name
        if not name or name == "nan":
            continue

        summary = f"{name} | {manufacturer} | {price} | {category} | Rating: {rating} | Stock: {stock}"
        documents.append(summary)

        uniq_id = str(row.get("uniq_id", ""))
        metadata.append({
            "source": "products",
            "uniq_id": uniq_id,
            "row_index": int(idx),
        })

    print(f"  Prepared {len(documents)} product summaries for embedding (limit: {limit})")
    return documents, metadata


def load_orders(csv_path=None) -> pd.DataFrame:
    """
    Load orders CSV into a pandas DataFrame (no embedding).
    Orders are looked up by exact order_id, not semantic search.
    """
    global _orders_df

    csv_path = csv_path or str(ORDERS_CSV)
    print(f"  Loading orders from {csv_path}...")

    _orders_df = pd.read_csv(csv_path)
    print(f"  Loaded {len(_orders_df)} orders")
    return _orders_df


# ---------------------------------------------------------------------------
# Lookup Functions
# ---------------------------------------------------------------------------

def lookup_order(order_id: str) -> Optional[dict]:
    """Look up a specific order by order_id. Returns dict or None."""
    if _orders_df is None:
        return None

    matches = _orders_df[_orders_df["order_id"] == order_id]
    if matches.empty:
        return None

    row = matches.iloc[0]
    return row.to_dict()


def lookup_product(uniq_id: str) -> Optional[dict]:
    """Look up a product by uniq_id. Returns dict or None."""
    if _products_df is None:
        return None

    matches = _products_df[_products_df["uniq_id"] == uniq_id]
    if matches.empty:
        return None

    row = matches.iloc[0]
    return row.to_dict()


# ---------------------------------------------------------------------------
# Order Intent Detection
# ---------------------------------------------------------------------------

# Keywords that indicate a PERSONAL order question (needs order ID)
_ORDER_PERSONAL_KEYWORDS = [
    "my order", "my delivery", "my shipment", "my package",
    "order status", "delivery status", "shipping status",
    "where is my", "track my", "tracking",
    "is my order", "has my order", "was my order",
    "my billing address", "my shipping address",
    "my payment", "when will i receive",
    "order delivered", "order shipped",
]

# Keywords that indicate GENERAL ordering questions (answered by policies, NOT order lookup)
_ORDER_GENERAL_KEYWORDS = [
    "how to order", "how do i order", "how can i order",
    "place an order", "placing an order",
    "can i order", "cancel an order", "cancel my order",
    "return policy", "exchange policy", "refund policy",
    "shipping cost", "shipping fee", "delivery time",
    "how long", "payment method",
]

# UUID pattern for order IDs
ORDER_ID_PATTERN = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    re.IGNORECASE,
)


def detect_order_intent(query: str) -> bool:
    """
    Check if the query is about a PERSONAL order (needs order ID lookup).
    Returns False for general policy questions about ordering.
    """
    query_lower = query.lower()

    # If query contains an order ID, it's definitely an order lookup
    if ORDER_ID_PATTERN.search(query):
        return True

    # Check if it's a general ordering question first (higher priority)
    for kw in _ORDER_GENERAL_KEYWORDS:
        if kw in query_lower:
            return False

    # Check for personal order keywords
    for kw in _ORDER_PERSONAL_KEYWORDS:
        if kw in query_lower:
            return True

    return False


def extract_order_id(text: str) -> Optional[str]:
    """Extract a UUID-format order ID from text. Returns the ID or None."""
    match = ORDER_ID_PATTERN.search(text)
    return match.group(0) if match else None


def format_order_for_context(order: dict) -> str:
    """Format an order dict into a readable context string for the LLM."""
    return f"""Order Details:
- Order ID: {order.get('order_id', 'N/A')}
- Category: {order.get('category', 'N/A')}
- Price: ${order.get('price', 'N/A')}
- Quantity: {order.get('quantity', 'N/A')}
- Order Date: {order.get('order_date', 'N/A')}
- Shipping Date: {order.get('shipping_date', 'N/A')}
- Delivery Status: {order.get('delivery_status', 'N/A')}
- Payment Method: {order.get('payment_method', 'N/A')}
- Shipping Address: {order.get('shipping_address', 'N/A')}
- Billing Address: {order.get('billing_address', 'N/A')}
- Customer Segment: {order.get('customer_segment', 'N/A')}"""


# ---------------------------------------------------------------------------
# Auto-Load at Startup
# ---------------------------------------------------------------------------

def auto_load_knowledge_base(rag_pipeline):
    """
    Called at startup. Loads all 3 data sources:
    1. Policies -> embed into ChromaDB
    2. Products -> embed condensed summaries in batches
    3. Orders -> load into pandas DataFrame (no embedding)
    """
    print("\n" + "=" * 60)
    print("AUTO-LOADING KNOWLEDGE BASE")
    print("=" * 60)

    # 1. Load and embed policies
    print("\n[1/3] Loading store policies...")
    policy_docs, policy_meta = load_policies()
    rag_pipeline.ingest_documents_batched(
        documents=policy_docs,
        metadata=policy_meta,
        batch_size=50,
        id_prefix="policy",
    )
    print(f"  Ingested {len(policy_docs)} policy documents")

    # 2. Load and embed products (batched to save RAM)
    print("\n[2/3] Loading product catalog...")
    product_docs, product_meta = load_products_for_embedding()
    rag_pipeline.ingest_documents_batched(
        documents=product_docs,
        metadata=product_meta,
        batch_size=PRODUCT_BATCH_SIZE,
        id_prefix="product",
    )
    print(f"  Ingested {len(product_docs)} product summaries")

    # 3. Load orders (DataFrame only, no embedding)
    print("\n[3/3] Loading orders database...")
    load_orders()

    # Summary
    stats = rag_pipeline.get_collection_stats()
    print("\n" + "=" * 60)
    print(f"KNOWLEDGE BASE READY")
    print(f"  ChromaDB documents: {stats['document_count']}")
    print(f"  Orders in memory: {len(_orders_df) if _orders_df is not None else 0}")
    print(f"  Products in memory: {len(_products_df) if _products_df is not None else 0}")
    print("=" * 60 + "\n")
