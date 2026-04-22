# MAX PAY Payment Integration API

A production-ready Flask REST API for integrating Max Pay payment processing into your restaurant ordering system.

## 🚀 Features

- ✅ Create payment requests with Max Pay
- ✅ Handle payment webhooks with signature verification
- ✅ Secure HMAC SHA256 signature validation
- ✅ Environment-based configuration
- ✅ Comprehensive error handling and logging
- ✅ Production-ready code structure

## 📁 Project Structure

```
/
├── maxpay_main.py          # Flask application with API endpoints
├── config.py               # Configuration and environment variables
├── services/
│   ├── __init__.py
│   └── maxpay.py          # Max Pay API integration service
├── utils/
│   ├── __init__.py
│   └── security.py        # Webhook signature verification
└── README_MAXPAY.md       # This file
```

## 🔧 Setup Instructions

### 1. Set Environment Variables

Create a `.env` file or set these environment variables in Replit Secrets:

```bash
# Required - Max Pay API Credentials
MAX_API_KEY=your_max_api_key_here
MAX_MERCHANT_ID=your_merchant_id_here
MAX_WEBHOOK_SECRET=your_webhook_secret_here

# Required - Max Pay API URL (replace with real URL when you get it)
MAX_API_URL=https://api.maxpay.example.com/v1/payments

# Optional - Your domain URLs
SUCCESS_URL=https://yourdomain.com/payment/success
CANCEL_URL=https://yourdomain.com/payment/cancel

# Optional - Flask settings
SECRET_KEY=your-secret-key-here
DEBUG=False
```

### 2. Install Dependencies

The following packages will be installed automatically:
- Flask (web framework)
- python-dotenv (environment variables)
- requests (HTTP client)

### 3. Run on Replit

Simply click the **Run** button in Replit, or execute:

```bash
python maxpay_main.py
```

The API will start on `http://0.0.0.0:5000`

## 📡 API Endpoints

### 1. Health Check

**GET /**

Check if the API is running.

**Response:**
```json
{
  "status": "running",
  "service": "Max Pay Integration API",
  "version": "1.0.0"
}
```

### 2. Create Payment

**POST /create-payment**

Create a new payment request with Max Pay.

**Request Body:**
```json
{
  "order_id": "12345",
  "amount": 129.90
}
```

**Success Response (200):**
```json
{
  "payment_url": "https://maxpay.com/checkout/abc123...",
  "order_id": "12345",
  "amount": 129.90,
  "transaction_id": "txn_xyz789"
}
```

**Error Response (400/500):**
```json
{
  "error": true,
  "message": "Error description here"
}
```

### 3. Webhook Handler

**POST /webhook/max**

Receives payment notifications from Max Pay.

**Expected Payload from Max Pay:**
```json
{
  "orderId": "12345",
  "transactionId": "txn_xyz789",
  "status": "approved",
  "amount": 129.90
}
```

**Signature Verification:**
- Max Pay should send a signature in one of these headers:
  - `X-Max-Signature`
  - `X-Signature`
  - `Signature`
  - `Max-Signature`

**Status Values:**
- `approved` - Payment successful → Prints "ORDER PAID"
- `declined` - Payment declined → Prints "ORDER FAILED"
- `error` - Payment processing error → Prints "ORDER FAILED"

**Response (Always 200):**
```json
{
  "status": "received",
  "order_id": "12345"
}
```

## 🧪 Testing

### Test with cURL

**Create Payment:**
```bash
curl -X POST http://localhost:5000/create-payment \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "TEST001",
    "amount": 99.99
  }'
```

**Simulate Webhook (Approved):**
```bash
curl -X POST http://localhost:5000/webhook/max \
  -H "Content-Type: application/json" \
  -H "X-Max-Signature: your_test_signature" \
  -d '{
    "orderId": "TEST001",
    "transactionId": "txn_test_123",
    "status": "approved",
    "amount": 99.99
  }'
```

**Simulate Webhook (Declined):**
```bash
curl -X POST http://localhost:5000/webhook/max \
  -H "Content-Type: application/json" \
  -d '{
    "orderId": "TEST001",
    "transactionId": "txn_test_124",
    "status": "declined",
    "amount": 99.99
  }'
```

### Test with Postman

1. Import the following endpoints into Postman:
   - **POST** `http://localhost:5000/create-payment`
   - **POST** `http://localhost:5000/webhook/max`

2. Set headers:
   ```
   Content-Type: application/json
   ```

3. Use the JSON bodies from the cURL examples above

## 🔐 Security Features

- **HMAC SHA256** signature verification for webhooks
- **Constant-time** signature comparison (prevents timing attacks)
- **Environment-based** secrets (never hardcoded)
- **Request validation** on all endpoints
- **Error logging** without exposing sensitive data

## 🔄 Integration with Max Pay

### Step 1: Get Your Credentials

Contact Max Pay to obtain:
1. **API Key** (for authenticating API requests)
2. **Merchant ID** (your unique merchant identifier)
3. **Webhook Secret** (for verifying webhook signatures)
4. **API URL** (the actual Max Pay API endpoint)

### Step 2: Configure Webhook URL

In your Max Pay merchant dashboard:
1. Set webhook URL to: `https://yourdomain.com/webhook/max`
2. Enable webhook events for payment status changes
3. Note the webhook signature method (should be HMAC SHA256)

### Step 3: Update Environment Variables

Replace the placeholder values in `.env` or Replit Secrets with your real credentials.

## 📝 Customization

### Database Integration

To save payment status to your database, modify `maxpay_main.py` in the webhook handler:

```python
if status == 'approved':
    # Add your database update logic here
    from models import Order
    order = Order.query.filter_by(id=order_id).first()
    if order:
        order.payment_status = 'paid'
        order.transaction_id = transaction_id
        db.session.commit()
```

### Email Notifications

Add email sending in the webhook handler:

```python
if status == 'approved':
    send_payment_confirmation_email(order_id, amount)
```

### Custom Success/Cancel URLs

You can pass dynamic URLs per order:

In `services/maxpay.py`, modify the `create_payment` method to accept optional URLs:

```python
def create_payment(self, order_id: str, amount: float, 
                   success_url: str = None, cancel_url: str = None):
    payload = {
        'merchantId': self.merchant_id,
        'amount': amount,
        'currency': 'ILS',
        'orderId': order_id,
        'successUrl': success_url or self.success_url,
        'cancelUrl': cancel_url or self.cancel_url
    }
    # ... rest of the code
```

## 🐛 Troubleshooting

### Missing Environment Variables

If you see: `Missing required environment variables`

**Solution:** Set all required variables in Replit Secrets:
- `MAX_API_KEY`
- `MAX_MERCHANT_ID`
- `MAX_WEBHOOK_SECRET`

### Payment URL Not Returned

If you get: `Payment URL not found in Max Pay response`

**Possible causes:**
1. Invalid API URL (still using placeholder)
2. Invalid credentials
3. Max Pay API response format different than expected

**Solution:** Check Max Pay's actual API response format and update `services/maxpay.py` accordingly.

### Webhook Signature Verification Fails

If webhooks are rejected with `Invalid signature`

**Solution:**
1. Verify `MAX_WEBHOOK_SECRET` matches Max Pay dashboard
2. Check which header Max Pay uses for signatures
3. Confirm Max Pay uses HMAC SHA256 (not SHA1 or other methods)

### Network Timeout

If you get timeout errors:

**Solution:**
1. Check `MAX_API_URL` is correct
2. Verify your server can reach Max Pay (firewall/network)
3. Increase timeout in `services/maxpay.py` if needed

## 📞 Support

For Max Pay API documentation and support:
- Contact Max Pay technical support
- Check Max Pay developer portal
- Review Max Pay API documentation

## 🔄 Production Checklist

Before going live:

- [ ] Set all environment variables with real values
- [ ] Replace `MAX_API_URL` with actual Max Pay endpoint
- [ ] Test with Max Pay sandbox/test environment
- [ ] Configure webhook URL in Max Pay dashboard
- [ ] Test webhook signature verification
- [ ] Add database integration for order tracking
- [ ] Implement email notifications
- [ ] Set up monitoring and error alerts
- [ ] Enable HTTPS (required for production)
- [ ] Review and test error handling
- [ ] Load test the API
- [ ] Set `DEBUG=False` in production

## 📄 License

This integration code is provided as-is for use with Max Pay payment processing.

---

**Built with ❤️ for restaurant ordering systems**
