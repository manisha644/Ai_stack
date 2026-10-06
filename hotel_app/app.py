````python
import csv
import io
import json
import math
import re
import urllib.request
import urllib.error

import streamlit as st
import chromadb


# ============================================================
# CONFIGURATION
# ============================================================

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b"

CHROMA_PATH = "./bizmind_chroma"
COLLECTION_NAME = "sales_data"

st.set_page_config(
    page_title="BizMind AI",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# CHROMADB
# ============================================================

@st.cache_resource
def load_chromadb():

    client = chromadb.PersistentClient(
        path=CHROMA_PATH
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    return client, collection


chroma_client, collection = load_chromadb()


# ============================================================
# SIMPLE LOCAL TEXT EMBEDDING
# No sentence-transformers / torch / torchvision required
# ============================================================

def text_embedding(text, size=256):

    vector = [0.0] * size

    words = re.findall(
        r"[a-zA-Z0-9]+",
        text.lower()
    )

    if not words:
        return vector

    for word in words:

        value = 0

        for character in word:
            value = (
                value * 31
                + ord(character)
            ) % size

        vector[value] += 1.0

    length = math.sqrt(
        sum(x * x for x in vector)
    )

    if length > 0:

        vector = [
            x / length
            for x in vector
        ]

    return vector


# ============================================================
# OLLAMA
# ============================================================

def ask_ollama(prompt):

    data = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(data).encode("utf-8"),
        headers={
            "Content-Type": "application/json"
        }
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=180
        ) as response:

            result = json.loads(
                response.read().decode("utf-8")
            )

            return result.get(
                "response",
                "No response received from Ollama."
            )

    except urllib.error.URLError:

        return (
            "❌ Cannot connect to Ollama.\n\n"
            "Please make sure Ollama is running "
            "and the model is installed.\n\n"
            "Run:\n"
            "ollama pull llama3.2:3b"
        )

    except Exception as error:

        return f"❌ Ollama error: {error}"


# ============================================================
# CSV READING
# ============================================================

def read_csv(uploaded_file):

    content = uploaded_file.getvalue().decode(
        "utf-8-sig"
    )

    reader = csv.DictReader(
        io.StringIO(content)
    )

    rows = []

    for row in reader:

        clean_row = {}

        for key, value in row.items():

            if key:

                clean_key = key.strip()

                if value is None:
                    clean_value = ""
                else:
                    clean_value = value.strip()

                clean_row[
                    clean_key
                ] = clean_value

        rows.append(clean_row)

    return rows


# ============================================================
# FIND COLUMN
# ============================================================

def find_column(row, names):

    if not row:
        return None

    for wanted_name in names:

        for key in row.keys():

            if key.lower().strip() == wanted_name.lower():

                return key

    return None


# ============================================================
# NUMBER CONVERSION
# ============================================================

def number(value):

    try:

        text = str(value)

        text = text.replace(
            ",",
            ""
        )

        text = text.replace(
            "₹",
            ""
        )

        text = text.replace(
            "$",
            ""
        )

        text = text.replace(
            "€",
            ""
        )

        text = text.replace(
            "£",
            ""
        )

        return float(
            text.strip()
        )

    except:

        return 0.0


# ============================================================
# SALES ANALYSIS
# ============================================================

def analyze_sales(rows):

    if not rows:

        return {
            "revenue": 0.0,
            "profit": 0.0,
            "quantity": 0.0,
            "products": {},
            "regions": {}
        }

    first_row = rows[0]

    sales_column = find_column(
        first_row,
        [
            "sales",
            "revenue",
            "amount",
            "total_sales"
        ]
    )

    profit_column = find_column(
        first_row,
        [
            "profit",
            "net_profit"
        ]
    )

    quantity_column = find_column(
        first_row,
        [
            "quantity",
            "qty",
            "units"
        ]
    )

    product_column = find_column(
        first_row,
        [
            "product",
            "product_name",
            "item"
        ]
    )

    region_column = find_column(
        first_row,
        [
            "region",
            "area",
            "location",
            "zone"
        ]
    )

    total_revenue = 0.0
    total_profit = 0.0
    total_quantity = 0.0

    products = {}
    regions = {}

    for row in rows:

        if sales_column:

            sales = number(
                row.get(
                    sales_column,
                    0
                )
            )

        else:

            sales = 0.0

        if profit_column:

            profit = number(
                row.get(
                    profit_column,
                    0
                )
            )

        else:

            profit = 0.0

        if quantity_column:

            quantity = number(
                row.get(
                    quantity_column,
                    0
                )
            )

        else:

            quantity = 0.0

        if product_column:

            product = row.get(
                product_column,
                "Unknown"
            )

        else:

            product = "Unknown"

        if region_column:

            region = row.get(
                region_column,
                "Unknown"
            )

        else:

            region = "Unknown"

        product = (
            product.strip()
            if product
            else "Unknown"
        )

        region = (
            region.strip()
            if region
            else "Unknown"
        )

        total_revenue += sales
        total_profit += profit
        total_quantity += quantity

        if product not in products:

            products[product] = {
                "sales": 0.0,
                "profit": 0.0,
                "quantity": 0.0
            }

        products[product]["sales"] += sales
        products[product]["profit"] += profit
        products[product]["quantity"] += quantity

        if region not in regions:

            regions[region] = {
                "sales": 0.0,
                "profit": 0.0
            }

        regions[region]["sales"] += sales
        regions[region]["profit"] += profit

    return {
        "revenue": total_revenue,
        "profit": total_profit,
        "quantity": total_quantity,
        "products": products,
        "regions": regions
    }


# ============================================================
# CREATE BUSINESS DOCUMENTS
# ============================================================

def create_documents(stats):

    documents = []
    ids = []

    summary = (
        "Business summary. "
        f"Total revenue is {stats['revenue']:.2f}. "
        f"Total profit is {stats['profit']:.2f}. "
        f"Total quantity sold is {stats['quantity']:.2f}."
    )

    documents.append(summary)
    ids.append("summary")

    for product, data in stats["products"].items():

        document = (
            f"Product {product}. "
            f"Sales are {data['sales']:.2f}. "
            f"Profit is {data['profit']:.2f}. "
            f"Quantity sold is {data['quantity']:.2f}."
        )

        documents.append(document)

        ids.append(
            "product_" + str(len(ids))
        )

    for region, data in stats["regions"].items():

        document = (
            f"Region {region}. "
            f"Sales are {data['sales']:.2f}. "
            f"Profit is {data['profit']:.2f}."
        )

        documents.append(document)

        ids.append(
            "region_" + str(len(ids))
        )

    return documents, ids


# ============================================================
# STORE DATA IN CHROMADB
# ============================================================

def store_in_chromadb(stats):

    documents, ids = create_documents(
        stats
    )

    embeddings = []

    for document in documents:

        embeddings.append(
            text_embedding(document)
        )

    try:

        existing = collection.get()

        existing_ids = existing.get(
            "ids",
            []
        )

        if existing_ids:

            collection.delete(
                ids=existing_ids
            )

    except Exception:
        pass

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings
    )


# ============================================================
# SEARCH BUSINESS DATA
# ============================================================

def search_business_data(question):

    question_vector = text_embedding(
        question
    )

    try:

        result = collection.query(
            query_embeddings=[
                question_vector
            ],
            n_results=5
        )

        documents = result.get(
            "documents",
            [[]]
        )

        if documents:

            return documents[0]

    except Exception:

        pass

    return []


# ============================================================
# MONEY FORMAT
# ============================================================

def money(value):

    return f"₹{value:,.2f}"


# ============================================================
# MAIN UI
# ============================================================

st.title(
    "📊 BizMind AI"
)

st.subheader(
    "AI-Powered Sales Intelligence System"
)

st.write(
    "Upload your business sales CSV and "
    "ask questions about your business."
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header(
        "⚙️ Settings"
    )

    st.write(
        "AI Model"
    )

    st.code(
        OLLAMA_MODEL
    )

    st.write(
        "Vector Database"
    )

    st.code(
        "ChromaDB"
    )

    st.write(
        "Embedding"
    )

    st.code(
        "Local Python embedding"
    )


# ============================================================
# FILE UPLOAD
# ============================================================

uploaded_file = st.file_uploader(
    "📁 Upload Sales CSV",
    type=["csv"]
)


if uploaded_file:

    try:

        rows = read_csv(
            uploaded_file
        )

        if not rows:

            st.error(
                "❌ The CSV file is empty."
            )

            st.stop()

        stats = analyze_sales(
            rows
        )

        store_in_chromadb(
            stats
        )

        st.success(
            f"✅ Loaded {len(rows)} sales records."
        )

    except Exception as error:

        st.error(
            f"❌ Error reading CSV: {error}"
        )

        st.stop()


    # ========================================================
    # BUSINESS OVERVIEW
    # ========================================================

    st.header(
        "📈 Business Overview"
    )

    col1, col2, col3, col4 = st.columns(4)

    margin = 0.0

    if stats["revenue"] != 0:

        margin = (
            stats["profit"]
            / stats["revenue"]
        ) * 100

    col1.metric(
        "💰 Revenue",
        money(
            stats["revenue"]
        )
    )

    col2.metric(
        "📈 Profit",
        money(
            stats["profit"]
        )
    )

    col3.metric(
        "📦 Quantity",
        f"{stats['quantity']:,.0f}"
    )

    col4.metric(
        "📊 Profit Margin",
        f"{margin:.2f}%"
    )


    # ========================================================
    # PRODUCT PERFORMANCE
    # ========================================================

    st.header(
        "🛒 Product Performance"
    )

    product_data = []

    for product, data in stats[
        "products"
    ].items():

        product_data.append(
            {
                "Product": product,
                "Sales": round(
                    data["sales"],
                    2
                ),
                "Profit": round(
                    data["profit"],
                    2
                ),
                "Quantity": round(
                    data["quantity"],
                    2
                )
            }
        )

    product_data.sort(
        key=lambda item: item["Sales"],
        reverse=True
    )

    if product_data:

        st.table(
            product_data
        )

    else:

        st.info(
            "No product information found."
        )


    # ========================================================
    # REGION PERFORMANCE
    # ========================================================

    st.header(
        "🌍 Regional Performance"
    )

    region_data = []

    for region, data in stats[
        "regions"
    ].items():

        region_data.append(
            {
                "Region": region,
                "Sales": round(
                    data["sales"],
                    2
                ),
                "Profit": round(
                    data["profit"],
                    2
                )
            }
        )

    region_data.sort(
        key=lambda item: item["Sales"],
        reverse=True
    )

    if region_data:

        st.table(
            region_data
        )

    else:

        st.info(
            "No region information found."
        )


    # ========================================================
    # AUTOMATIC INSIGHTS
    # ========================================================

    st.header(
        "💡 Automatic Business Insights"
    )

    if stats["products"]:

        best_product = max(
            stats["products"].items(),
            key=lambda item: item[1]["sales"]
        )

        highest_profit_product = max(
            stats["products"].items(),
            key=lambda item: item[1]["profit"]
        )

        lowest_product = min(
            stats["products"].items(),
            key=lambda item: item[1]["sales"]
        )

        st.write(
            "🔥 **Best-selling product:** "
            + str(best_product[0])
        )

        st.write(
            "💰 **Highest-profit product:** "
            + str(highest_profit_product[0])
        )

        st.write(
            "⚠️ **Lowest-selling product:** "
            + str(lowest_product[0])
        )


    if stats["regions"]:

        best_region = max(
            stats["regions"].items(),
            key=lambda item: item[1]["sales"]
        )

        st.write(
            "🌍 **Best-performing region:** "
            + str(best_region[0])
        )


    # ========================================================
    # AI ASSISTANT
    # ========================================================

    st.header(
        "🤖 Ask BizMind AI"
    )

    question = st.text_area(
        "Ask a question about your sales:",
        placeholder=(
            "Example: Which product should "
            "we promote?"
        )
    )

    if st.button(
        "✨ Ask AI"
    ):

        if not question.strip():

            st.warning(
                "Please enter a question."
            )

        else:

            with st.spinner(
                "Analyzing business data..."
            ):

                context = search_business_data(
                    question
                )

                if context:

                    context_text = "\n".join(
                        context
                    )

                else:

                    context_text = (
                        "No matching business "
                        "information was found."
                    )

                prompt = f"""
You are BizMind AI,
a business sales intelligence assistant.

Answer the user's question using ONLY
the business information provided below.

Do not invent numbers.

Business information:

{context_text}

User question:

{question}

Give a clear and simple business answer.

When possible, structure the answer as:

Finding:
Reason:
Recommendation:
"""

                answer = ask_ollama(
                    prompt
                )

            st.subheader(
                "💡 AI Recommendation"
            )

            st.write(
                answer
            )

            if context:

                with st.expander(
                    "🔍 Business data used by AI"
                ):

                    for item in context:

                        st.write(
                            "• " + item
                        )


else:

    st.info(
        "👆 Upload a CSV file to start."
    )

    st.markdown(
        """
### CSV Example

Your CSV can look like this:

```text
Date,Product,Region,Sales,Quantity,Profit
2026-01-01,Laptop,South,75000,3,12000
2026-01-02,Phone,North,45000,5,7000
2026-01-03,Tablet,East,30000,4,5000
````

### Required columns

* Product
* Sales

### Optional columns

* Date
* Region
* Quantity
* Profit
  """
  )

