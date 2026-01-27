# Forge Playground

Document parsing and extraction playground with extensible parser architecture.

## Architecture

```
playground/
├── backend/          # FastAPI backend
├── frontend/          # Streamlit frontend
└── ...
```

### Backend Structure

- **api/**: FastAPI routes and schemas
- **application/**: Business logic services
- **core/**: Domain models and interfaces
- **infrastructure/**: Parser and storage implementations

## Getting Started

### Prerequisites

- Python 3.12+
- uv (recommended) or pip
- GPU (for enhance mode with Chandra parser)
- poppler-utils (for PDF to image conversion)
  - Ubuntu/Debian: `sudo apt-get install poppler-utils`
  - macOS: `brew install poppler`
  - Conda: `conda install -c conda-forge poppler`

### Backend Setup

```bash
cd backend
uv sync  # or: pip install -e .

# Run server
python main.py
# or
uvicorn main:app --reload
```

Backend will be available at `http://localhost:8000`

#### Parser Modes

- **basic**: Uses Docling parser (CPU/MPU compatible)
- **enhance**: Uses Chandra OCR parser (requires GPU)

#### GPU Requirements

For enhance mode (Chandra parser):
- CUDA-capable GPU
- ~20GB+ GPU memory recommended
- First run will download ~9GB model

### Frontend Setup

```bash
cd frontend
uv sync  # or: pip install -e .

# Run Streamlit
streamlit run app.py
```

Frontend will be available at `http://localhost:8501`

### Environment Variables

#### Backend (.env)

```env
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true
CORS_ORIGINS=["*"]
DEFAULT_PARSER=unstructured
UPLOAD_DIR=./uploads
```

#### Frontend (.env)

```env
API_BASE_URL=http://localhost:8000
```

## API Endpoints

### Documents

- `POST /api/v1/documents` - Upload document
- `GET /api/v1/documents/{document_id}` - Get document info
- `GET /api/v1/documents/{document_id}/pages/{page_number}` - Get page image

### Parse

- `POST /api/v1/documents/{document_id}/pages/{page_number}/parse` - Parse document page
  - Request body: `{"mode": "basic"}` or `{"mode": "enhance"}`
- `GET /api/v1/parsers` - List available parsers and modes

## Adding New Parsers

1. Create parser class in `backend/infrastructure/parsers/`:

```python
from infrastructure.parsers.base import BaseParser
from core.models.document import Document
from core.models.parse_result import ParseResult

class MyParser(BaseParser):
    def get_name(self) -> str:
        return "my_parser"
    
    def get_supported_formats(self) -> List[str]:
        return ["pdf", "png"]
    
    def _do_parse(self, document: Document) -> ParseResult:
        # Implementation
        pass
```

2. Register in `backend/infrastructure/parsers/__init__.py`:

```python
from infrastructure.parsers.my_parser import MyParser
ParserFactory.register("my_parser", MyParser)
```

3. Done! Parser is now available.

## Development

### Running Tests

```bash
cd backend
pytest
```

### Code Formatting

```bash
black .
ruff check .
```

## License

MIT
