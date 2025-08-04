# Bank Statement Processor API

This API processes bank statement PDFs using AI and returns structured JSON data for your Laravel application.

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your AI model:**
   ```bash
   python src/base_model/setup.py
   ```

3. **Start the API server:**
   ```bash
   python start_api.py
   ```

4. **Access API documentation:**
   - Interactive docs: http://localhost:8000/docs
   - Health check: http://localhost:8000/health/

## 🔐 Security

The API uses API key authentication. Your Laravel app needs to include the API key in requests:

**Method 1: Bearer Token (recommended)**
```
Authorization: Bearer bank-processor-api-key-2024
```

**Method 2: Custom Header (simpler)**
```
X-API-Key: bank-processor-api-key-2024
```

## 🔌 Laravel Integration

### 1. Health Check Endpoint

Check if the API is running:

```php
// Laravel Controller
$response = Http::withHeaders([
    'X-API-Key' => env('BANK_API_KEY')
])->get('http://localhost:8000/health/');

$data = $response->json();
// Returns: {"status": "healthy", "model_loaded": true, "version": "1.0.0"}
```

### 2. Process PDF File

Upload and process a bank statement PDF:

```php
// Laravel Controller
$response = Http::withHeaders([
    'X-API-Key' => env('BANK_API_KEY')
])->attach(
    'file', file_get_contents($pdfPath), 'statement.pdf'
)->post('http://localhost:8000/api/process-file-simple', [
    'customer_id' => 'CUST123'
]);

$result = $response->json();

if ($result['success']) {
    $bankData = $result['data'];
    // Process the structured bank statement data
    $bankName = $bankData['bank_name'];
    $accounts = $bankData['accounts'];
    foreach ($accounts as $account) {
        $transactions = $account['transactions'];
        // Save to your database
    }
}
```

### 3. Process Text Content

If you already have extracted text:

```php
// Laravel Controller
$response = Http::withHeaders([
    'Authorization' => 'Bearer ' . env('BANK_API_KEY')
])->post('http://localhost:8000/api/process-text', [
    'text_content' => $extractedText,
    'customer_id' => 'CUST123'
]);

$result = $response->json();
```

## 📊 Response Format

All endpoints return a consistent JSON structure:

```json
{
  "success": true,
  "message": "Bank statement processed successfully in 2.34 seconds",
  "data": {
    "bank_name": "Example Bank",
    "statement_period": {
      "start_date": "2024-01-01",
      "end_date": "2024-01-31"
    },
    "accounts": [
      {
        "account_number": "1234567890",
        "account_name": "John Doe",
        "currency": "USD",
        "opening_balance": 1000.00,
        "closing_balance": 1500.00,
        "transactions": [
          {
            "date": "2024-01-15",
            "description": "ATM Withdrawal",
            "debit": 100.00,
            "credit": null,
            "balance": 900.00,
            "note": null
          }
        ]
      }
    ],
    "processed_at": "2024-08-03T10:30:00",
    "processing_time_seconds": 2.34
  }
}
```

## 🛠️ Configuration

Update `.env` file:

```env
# API Configuration
API_SECRET_KEY="your-super-secret-key-change-this-in-production"
API_KEY="bank-processor-api-key-2024"
ALLOWED_ORIGINS="http://localhost,https://yourdomain.com"
API_HOST="0.0.0.0"
API_PORT=8000
```

## 🔍 Available Endpoints

- `GET /` - API information
- `GET /health/` - Basic health check
- `GET /health/detailed` - Detailed health information
- `POST /api/process-text` - Process text content
- `POST /api/process-file` - Process PDF file (Bearer auth)
- `POST /api/process-file-simple` - Process PDF file (Header auth)

## 🚀 Production Deployment

1. **Change security settings:**
   - Update `API_SECRET_KEY` to a strong random key
   - Update `API_KEY` to a secure random string
   - Set `ALLOWED_ORIGINS` to your Laravel app's domain

2. **Deploy with Docker:**
   ```bash
   docker build -t bank-statement-api .
   docker run -p 8000:8000 bank-statement-api
   ```

3. **Or run with production server:**
   ```bash
   pip install gunicorn
   gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

## 🐛 Error Handling

The API returns consistent error responses:

```json
{
  "success": false,
  "message": "Failed to process bank statement",
  "error": "Invalid file format"
}
```

Common error codes:
- `401` - Invalid API key
- `400` - Invalid request (bad file, missing data)
- `500` - Server error (model not loaded, processing failed)

## 📝 Laravel Environment Variables

Add to your Laravel `.env`:

```env
BANK_API_URL=http://localhost:8000
BANK_API_KEY=bank-processor-api-key-2024
```
