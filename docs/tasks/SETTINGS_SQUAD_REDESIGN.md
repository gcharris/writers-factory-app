# Settings & Squad Redesign Task

> Make Squad selection the first-time setup experience with baked-in API keys for affordable providers.

## Problem Statement

Current Settings flow is confusing:
1. User sees Settings tabs: Assistant, Squad, API Keys, AI Model, Voice, About
2. No clear guidance on where to start
3. API keys feel intimidating for non-technical writers
4. Local agent is slow and users don't understand why

## Solution: Squad-First Onboarding

### New First-Time Flow

```
1. App Launch (first time)
   ↓
2. Squad Wizard
   - Scan hardware (GPU, RAM, CPU)
   - Show 7 Squad presets with recommendations
   - Highlight which works best for their machine
   ↓
3. Squad Selection
   - User picks a Squad (or accepts recommendation)
   - Show price estimate (if any)
   ↓
4. Name Your Assistant (optional)
   - Fun personalization step
   - Default: "Muse" or similar
   ↓
5. Ready to Write!
   - Skip straight to main app
   - Settings available later for power users
```

### The 7 Squad Configurations

| Squad | Models | Monthly Cost | Target User |
|-------|--------|--------------|-------------|
| **Starter** | Llama 3.2 (local only) | $0 | Offline writers, privacy-focused |
| **Budget** | DeepSeek + Qwen | ~$2-5 | Cost-conscious, good quality |
| **Balanced** | Mistral + Claude Haiku | ~$10-20 | Best value for most writers |
| **Premium** | Claude Sonnet + GPT-4o | ~$30-50 | Professional authors |
| **Maximum** | Claude Opus + GPT-4 | ~$100+ | Production, publishing houses |
| **Hybrid** | Local + Cloud fallback | ~$5-10 | Privacy + power when needed |
| **Custom** | User picks each role | Varies | Power users |

### Baked-In API Keys (MVP Strategy)

**Providers to include keys for:**
- DeepSeek (cheap, high quality)
- Qwen (Alibaba, free tier generous)
- Mistral (European, good value)
- Kimi (Moonshot AI)
- Zhipu (GLM-4)
- Yandex (GPT alternative)

**User provides their own keys for:**
- Anthropic (Claude) - expensive, user pays directly
- OpenAI (GPT-4) - expensive, user pays directly

### Key Distribution Architecture

**Security: Never embed keys in app bundle!**

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Writers Factory│────▶│  Key Server      │────▶│  AI Providers   │
│  Desktop App    │     │  (Your backend)  │     │  (DeepSeek etc) │
└─────────────────┘     └──────────────────┘     └─────────────────┘
        │                       │
        │ 1. Request keys       │ 2. Validate license
        │    (with license ID)  │    Return encrypted keys
        │◀──────────────────────│
        │
        │ 3. Store keys locally (encrypted)
        │ 4. Use for API calls
```

**Implementation:**
1. App calls `https://api.writersfactory.app/keys/provision`
2. Server validates purchase/license
3. Server returns encrypted API keys for included providers
4. App stores keys in secure local storage (Tauri secure store)
5. Keys rotate periodically for security

### UI Changes Required

#### 1. New Component: `SquadWizard.svelte`
- Full-screen wizard overlay
- Hardware detection display
- Squad card grid with recommendations
- Price calculator
- "Get Started" CTA

#### 2. Modify: `SettingsModal.svelte`
- Remove Squad from main tabs (it becomes wizard-only for first-time)
- Add "Change Squad" button that re-opens wizard
- Simplify API Keys tab (only show user-provided keys)

#### 3. New Component: `HardwareScanner.svelte`
- Detect GPU (via Tauri system info)
- Detect RAM
- Detect CPU cores
- Return capability score

#### 4. Modify: Settings Tab Order
Current: Assistant, Squad, API Keys, AI Model, Voice, About
New: Assistant, AI Model, API Keys (advanced), Voice, About
(Squad accessed via wizard button, not tab)

### Backend Changes

#### 1. New Endpoint: `POST /squad/recommend`
```python
@app.post("/squad/recommend")
async def recommend_squad(hardware: HardwareInfo):
    """Analyze hardware and recommend best Squad."""
    # Score hardware capabilities
    # Return ranked Squad recommendations
    pass
```

#### 2. New Endpoint: `POST /keys/provision`
```python
@app.post("/keys/provision")
async def provision_keys(license: LicenseInfo):
    """Provision baked-in API keys for licensed users."""
    # Validate license
    # Return encrypted keys for included providers
    pass
```

#### 3. New Service: `key_provisioning_service.py`
- License validation
- Key encryption/decryption
- Key rotation logic
- Usage tracking (for cost management)

### Migration Path

**Existing Users:**
- Show wizard on next app launch
- Pre-select their current configuration
- "Keep Current" option available

**New Users:**
- Wizard is mandatory first step
- Can't skip to main app without selecting Squad

### Security Considerations

1. **Never ship keys in app binary** - Keys fetched at runtime
2. **Encrypt keys at rest** - Use Tauri's secure storage
3. **Rotate keys periodically** - Server can invalidate old keys
4. **Rate limit per user** - Prevent abuse of shared keys
5. **Monitor usage** - Track costs, detect anomalies
6. **License validation** - Only provision keys to valid licenses

### Success Metrics

- First-time setup completion rate > 90%
- Time to first AI response < 2 minutes
- Support tickets about "API keys" reduced 80%
- User satisfaction with onboarding (survey)

### Implementation Phases

**Phase 1: Squad Wizard UI** ✅ COMPLETE (pre-existing)
- [x] Create SquadWizard.svelte - `frontend/src/lib/components/Squads/SquadWizard.svelte`
- [x] Create HardwareScanner.svelte - `frontend/src/lib/components/Squads/HardwareStatusPanel.svelte`
- [x] Add first-time detection logic - in SquadWizard
- [x] Wire up to Settings - `frontend/src/lib/components/Settings/SettingsSquad.svelte`

**Phase 2: Backend Support** (partial - needs /squad/recommend endpoint)
- [ ] Add /squad/recommend endpoint
- [x] Add hardware analysis logic - exists in `/system/hardware`
- [x] Store Squad selection in settings - via settings_service

**Phase 3A: Key Provisioning Client** ✅ COMPLETE
- [x] Create `key_provisioning_service.py` - `backend/services/key_provisioning_service.py`
- [x] Machine-specific encryption using PBKDF2 + Fernet
- [x] SQLite storage for encrypted keys
- [x] Offline grace period (30 days)
- [x] Add client API endpoints - `/keys/provision`, `/keys/status`, `/keys/providers`
- [x] Create `SettingsKeyProvisioning.svelte` - UI for key status and provisioning

**Phase 3B: Key Provisioning Server** (separate task - see `KEY_SERVER_TASK.md`)
- [ ] Set up key provisioning server (AWS Lambda/Cloudflare Workers)
- [ ] Create server-side `/keys/provision` endpoint
- [ ] License validation logic
- [ ] Key rotation and revocation

**Phase 4: Usage Tracking (MVP Critical)** ✅ COMPLETE
- [x] Create `usage_tracking_service.py` - `backend/services/usage_tracking_service.py`
- [x] Add token counting to LLM service responses - pricing in service
- [x] Create cost estimation logic per provider - 10+ providers with pricing
- [x] Add `/usage/summary` and `/usage/record` endpoints - 6 endpoints added
- [x] Create `UsageIndicator.svelte` component - `frontend/src/lib/components/UsageIndicator.svelte`
- [x] Add threshold notification system - $5, $10, $25, $50 thresholds

**Phase 5: Polish**
- [ ] Add animations to wizard
- [ ] Add progress indicators
- [ ] Add "Why this recommendation?" explanations
- [ ] A/B test different Squad names/descriptions

---

## MVP Strategy (Writers Course)

The MVP will be tested with a writers course cohort. This provides real-world validation before public release.

### Business Model: Subscription
- Monthly subscription likely (to be validated during MVP)
- MVP users get free access in exchange for feedback
- Cost visibility is critical even when user isn't paying

### Token Usage Tracking

**Required Features:**
1. **Usage Counter** - Track tokens consumed per provider
2. **Cost Estimator** - Convert tokens to estimated $ spent
3. **Threshold Notifications** - Alert user when they pass configurable cost thresholds
4. **Dashboard Display** - Show running total in Settings or status bar

**Implementation:**

```python
# New service: usage_tracking_service.py
class UsageTrackingService:
    def record_usage(self, user_id: str, provider: str, tokens: int, cost: float):
        """Record API usage for a user."""
        pass

    def get_usage_summary(self, user_id: str) -> UsageSummary:
        """Get total usage and estimated cost."""
        pass

    def check_threshold(self, user_id: str) -> Optional[ThresholdAlert]:
        """Check if user has passed any cost thresholds."""
        pass
```

**Cost Thresholds (configurable):**
- $5 - Gentle reminder
- $10 - "You're using this a lot!"
- $25 - "Consider upgrading to your own API keys"
- $50 - Soft limit for MVP (may be enforced later)

**UI Component: `UsageIndicator.svelte`**
- Small badge in status bar or header
- Shows: "~$3.42 this month"
- Click to see breakdown by provider
- Color changes as thresholds approach (green → yellow → orange → red)

### MVP Relaxed Enforcement
- During MVP course, thresholds are advisory only
- No hard cutoffs (you're paying, so you see real costs)
- Data collected informs post-MVP pricing decisions

---

## Open Questions

1. ~~**Pricing model**: Does user pay monthly subscription, or one-time purchase with usage limits?~~ → **Subscription (likely)**
2. ~~**Usage limits**: How much can a user use baked-in keys before we cut them off?~~ → **Soft limits with notifications; hard limits TBD post-MVP**
3. **Offline grace period**: How long can app work offline before requiring key refresh?
4. **Key server hosting**: AWS Lambda? Cloudflare Workers? Self-hosted?

---

*Created: November 2025*
*Updated: November 2025 - Added MVP strategy and usage tracking*
*Status: Planning*
*Priority: High - Critical for user onboarding*
