# Flipkart Product Recommender Chatbot

An intelligent e-commerce chatbot built with Flask and LangChain that uses Retrieval Augmented Generation (RAG) to answer product-related queries based on Flipkart product reviews. The system leverages vector search with AstraDB, Groq's LLM for natural language understanding, and HuggingFace embeddings for semantic search.

## Features

- **RAG-based Q&A**: Answers product questions using real customer reviews
- **Conversational Memory**: Maintains chat history for context-aware responses
- **Vector Search**: Semantic search powered by AstraDB and HuggingFace embeddings
- **Modern Chat UI**: Responsive web interface with real-time messaging
- **Containerized Deployment**: Docker and Kubernetes ready
- **History-Aware Retrieval**: Rewrites queries based on conversation context

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   User      │────▶│  Flask App   │────▶│   RAG Chain     │
│  (Browser)  │     │   (app.py)   │     │ (LangChain)     │
└─────────────┘     └──────────────┘     └─────────────────┘
                              │                    │
                              ▼                    ▼
                       ┌──────────────┐     ┌─────────────────┐
                       │  Chat UI     │     │  AstraDB Vector │
                       │(index.html)  │     │     Store       │
                       └──────────────┘     └─────────────────┘
                                                     │
                              ┌────────────────────┘
                              ▼
                       ┌─────────────────┐
                       │  HuggingFace    │
                       │  Embeddings     │
                       │ (bge-base-en)   │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Groq LLM      │
                       │ (gpt-oss-20b)   │
                       └─────────────────┘
```

## Prerequisites

Before running this application, you'll need:

1. **API Accounts**:
   - [Groq](https://groq.com/) account with API key
   - [HuggingFace](https://huggingface.co/) account with API token
   - [DataStax AstraDB](https://www.datastax.com/astra) account with database

2. **Tools** (for local development):
   - Python 3.13+
   - [UV](https://github.com/astral-sh/uv) package manager
   - Docker (optional, for containerized deployment)
   - Kubernetes cluster (optional, for K8s deployment)

## Installation

### Local Development

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd flipkart-recommender
   ```

2. **Install dependencies with UV**:
   ```bash
   uv sync
   ```

3. **Set up environment variables** (see [Environment Variables](#environment-variables) section)

4. **Run the application**:
   ```bash
   uv run python app.py
   ```

5. **Access the chatbot**:
   Open your browser and navigate to `http://localhost:5000`

### Docker Deployment

1. **Build the Docker image**:
   ```bash
   docker build -t flipkart-recommender .
   ```

2. **Run the container**:
   ```bash
   docker run -p 5000:5000 --env-file .env flipkart-recommender
   ```

### Kubernetes Deployment

1. **Create a Kubernetes secret** with your environment variables:
   ```bash
   kubectl create secret generic flask-secret \
     --from-literal=GROQ_API_KEY=your_key \
     --from-literal=HUGGINGFACEHUB_API_TOKEN=your_token \
     --from-literal=HF_TOKEN=your_token \
     --from-literal=ASTRA_DB_API_ENDPOINT=your_endpoint \
     --from-literal=ASTRA_DB_APPLICATION_TOKEN=your_token \
     --from-literal=ASTRA_DB_KEYSPACE=your_keyspace
   ```

2. **Apply the Kubernetes manifests**:
   ```bash
   kubectl apply -f flask-k8s.yaml
   ```

3. **Access the service**:
   ```bash
   kubectl get svc flask-service
   ```

## Environment Variables

Create a `.env` file in the project root with the following variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | API key for Groq LLM service | Yes |
| `HUGGINGFACEHUB_API_TOKEN` | HuggingFace Hub API token | Yes |
| `HF_TOKEN` | HuggingFace token for model access | Yes |
| `ASTRA_DB_API_ENDPOINT` | AstraDB database API endpoint | Yes |
| `ASTRA_DB_APPLICATION_TOKEN` | AstraDB application token | Yes |
| `ASTRA_DB_KEYSPACE` | AstraDB keyspace/namespace | Yes |

## Usage

### Web Interface

Once the application is running, access the chatbot at `http://localhost:5000`. The interface provides:

- Real-time chat with the AI assistant
- Conversation history display
- Responsive design for mobile and desktop

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serves the chat UI |
| `/get` | POST | Send a message to the chatbot |

**Example API call**:
```bash
curl -X POST http://localhost:5000/get \
  -d "msg=What are the best features of this product?"
```

## Project Structure

```
flipkart-recommender/
├── app.py                    # Flask application entry point
├── Dockerfile                # Docker container configuration
├── flask-k8s.yaml           # Kubernetes deployment manifests
├── pyproject.toml           # Project dependencies (UV)
├── requirements.txt         # Alternative requirements file
├── data/
│   └── flipkart_product_review.csv  # Product review dataset
├── flipkart/
│   ├── __init__.py
│   ├── config.py           # Configuration management
│   ├── data_converter.py   # CSV to document conversion
│   ├── data_ingestion.py   # Vector store ingestion
│   └── rag_chain.py        # RAG pipeline implementation
├── static/
│   └── style.css           # Chat UI styling
├── templates/
│   └── index.html          # Chat interface template
└── utils/
    ├── __init__.py
    ├── custom_exceptions.py
    └── logger.py           # Logging utilities
```

## Data Format

The application expects a CSV file at `data/flipkart_product_review.csv` with the following columns:

- `product_title`: Name of the product
- `review`: Customer review text

Example:
```csv
product_title,review
"Wireless Bluetooth Headphones","Great sound quality and comfortable to wear..."
"Smart Watch","Battery life is amazing, tracks all my activities..."
```

## How It Works

1. **Data Ingestion**: Product reviews are converted to LangChain documents and stored in AstraDB with HuggingFace embeddings
2. **Query Processing**: User questions are rewritten using conversation history for better context
3. **Retrieval**: Relevant reviews are retrieved using vector similarity search
4. **Generation**: Groq's LLM generates answers based on retrieved context
5. **Response**: The answer is returned to the user via the chat interface

## Technologies Used

- **Flask**: Web framework
- **LangChain**: LLM orchestration and RAG pipeline
- **AstraDB**: Vector database for semantic search
- **Groq**: Fast LLM inference (openai/gpt-oss-20b)
- **HuggingFace**: Embeddings (BAAI/bge-base-en-v1.5)
- **Docker**: Containerization
- **Kubernetes**: Container orchestration
- **UV**: Modern Python package manager

## Acknowledgments

- Built with [LangChain](https://langchain.com/)
- Powered by [Groq](https://groq.com/) for fast LLM inference
- Vector storage by [DataStax AstraDB](https://www.datastax.com/astra)
