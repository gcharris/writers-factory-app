# Key Provisioning Server Task (Phase 3B)

> Server-side infrastructure for securely provisioning API keys to Writers Factory desktop app.

## Background

This task follows Phase 3A (completed), which built the client-side key provisioning service. The client is ready to:
1. Request keys from `https://api.writersfactory.app/keys/provision`
2. Store encrypted keys locally using machine-specific encryption
3. Track provisioning status and handle offline grace periods

**Related**: See `SETTINGS_SQUAD_REDESIGN.md` for full context on Squad-first onboarding.

## Requirements

### 1. Server Endpoint: `POST /keys/provision`

**Request:**
```json
{
  "license_id": "optional-license-key",
  "machine_id": "client-generated-machine-fingerprint",
  "app_version": "1.0.0"
}
```

**Response (Success):**
```json
{
  "success": true,
  "keys": {
    "deepseek": "encrypted-key-here",
    "qwen": "encrypted-key-here",
    "mistral": "encrypted-key-here",
    "zhipu": "encrypted-key-here",
    "kimi": "encrypted-key-here",
    "yandex": "encrypted-key-here"
  },
  "expires_at": "2025-01-15T00:00:00Z",
  "refresh_after": "2024-12-22T00:00:00Z"
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "invalid_license",
  "message": "License key not found or expired"
}
```

### 2. License Validation

For MVP (writers course):
- Accept a list of known email addresses or simple license codes
- No payment integration needed initially
- Track which users have provisioned keys

Post-MVP:
- Integrate with payment provider (Stripe, Gumroad, etc.)
- Validate subscription status
- Handle trial periods

### 3. Key Storage

Server must securely store API keys for:
- DeepSeek
- Qwen (Alibaba)
- Mistral
- Zhipu (GLM-4)
- Kimi (Moonshot AI)
- Yandex GPT

**Security Requirements:**
- Keys stored encrypted at rest
- Environment variables for master encryption key
- Keys never logged or exposed in errors
- Rate limiting per license/IP

### 4. Usage Tracking (Server-Side)

Track per-user usage to:
- Monitor costs across all users
- Detect abuse patterns
- Inform pricing decisions

**Data to track:**
- Tokens consumed per provider
- Estimated cost per user
- Request frequency
- Peak usage times

### 5. Key Rotation

- Support rotating individual provider keys without user action
- Notify clients when keys are refreshed
- Invalidate old keys after grace period

## Architecture Options

### Option A: AWS Lambda + DynamoDB
```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Desktop App    │────▶│  API Gateway     │────▶│  Lambda         │
│                 │     │  (HTTPS)         │     │  (Python)       │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                                                          ▼
                                                 ┌─────────────────┐
                                                 │  DynamoDB       │
                                                 │  (licenses,     │
                                                 │   usage)        │
                                                 └─────────────────┘
```

**Pros:** Serverless, scales automatically, pay-per-use
**Cons:** Cold starts, AWS complexity

### Option B: Cloudflare Workers + KV
```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Desktop App    │────▶│  Cloudflare      │────▶│  Worker         │
│                 │     │  Edge            │     │  (JS/TS)        │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                                                          ▼
                                                 ┌─────────────────┐
                                                 │  KV Store       │
                                                 │  + D1 (SQLite)  │
                                                 └─────────────────┘
```

**Pros:** Global edge, very fast, simple deployment
**Cons:** JavaScript/TypeScript only, KV eventually consistent

### Option C: Simple VPS + SQLite
```
┌─────────────────┐     ┌──────────────────┐
│  Desktop App    │────▶│  FastAPI on      │
│                 │     │  DigitalOcean/   │
└─────────────────┘     │  Fly.io          │
                        │  (SQLite)        │
                        └──────────────────┘
```

**Pros:** Simple, familiar Python, easy debugging
**Cons:** Single point of failure, manual scaling

### Recommendation for MVP

**Option B (Cloudflare Workers)** for:
- Fast global response times
- Free tier generous enough for MVP
- D1 (serverless SQLite) for relational data
- Easy secrets management

## Implementation Steps

### Phase 1: Basic Server (MVP)
- [ ] Set up Cloudflare Worker project
- [ ] Create `/keys/provision` endpoint
- [ ] Hardcode MVP license list (email addresses)
- [ ] Store API keys in Cloudflare secrets
- [ ] Return encrypted keys to valid licenses
- [ ] Deploy to `api.writersfactory.app`

### Phase 2: Usage Tracking
- [ ] Set up D1 database
- [ ] Create usage tracking tables
- [ ] Add `/usage/report` endpoint (client reports usage)
- [ ] Build simple admin dashboard

### Phase 3: License Management
- [ ] Create license generation system
- [ ] Add license revocation capability
- [ ] Build admin interface for license management

### Phase 4: Production Hardening
- [ ] Add rate limiting
- [ ] Implement key rotation
- [ ] Set up monitoring/alerting
- [ ] Add abuse detection

## Client Integration

The client (`key_provisioning_service.py`) is already implemented and expects:

1. **Endpoint**: `https://api.writersfactory.app/keys/provision`
2. **Method**: POST
3. **Headers**: `Content-Type: application/json`
4. **Body**: `{"license_id": "...", "machine_id": "..."}`

The client will:
- Call this endpoint on first launch or when keys expire
- Store returned keys encrypted locally
- Retry with exponential backoff on failure
- Work offline for 30 days using cached keys

## Security Checklist

- [ ] HTTPS only (Cloudflare provides this)
- [ ] API keys stored as Cloudflare secrets, never in code
- [ ] License validation before returning keys
- [ ] Rate limiting (100 requests/hour per IP)
- [ ] Machine ID tracking to detect key sharing
- [ ] Usage anomaly detection
- [ ] Audit logging for all key provisions

## Cost Estimation

**Cloudflare Workers (MVP):**
- Free tier: 100,000 requests/day
- Paid: $5/month for 10M requests

**API Key Costs (your responsibility):**
- DeepSeek: ~$0.14/M input tokens
- Qwen: Free tier generous
- Mistral: ~$0.15/M tokens
- Others: Varies

**Projected MVP Cost (50 users):**
- Server: $0 (free tier)
- API usage: $50-200/month depending on usage

## Open Questions

1. **Domain**: Use `api.writersfactory.app` or different subdomain?
2. **MVP License Format**: Simple codes like "WRITER-2024-ABC" or email-based?
3. **Usage Limits**: Should server enforce hard limits or just track?
4. **Admin Dashboard**: Build custom or use Cloudflare analytics?

---

*Created: November 2025*
*Status: Ready for Implementation*
*Depends On: Phase 3A (complete)*
*Assigned To: TBD (ID Agent)*
