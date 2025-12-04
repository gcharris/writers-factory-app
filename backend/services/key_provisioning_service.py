"""
Key Provisioning Service - Client-side key management for baked-in API keys

This service handles:
- Requesting provisioned keys from the key server
- Securely storing keys locally (encrypted)
- Key refresh and rotation
- Fallback to user-provided keys

The actual key server is a separate deployment (Phase 3B).
This service is the client that talks to it.

Architecture:
    ┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
    │  Writers Factory│────▶│  Key Server      │────▶│  AI Providers   │
    │  Desktop App    │     │  (external)      │     │  (DeepSeek etc) │
    └─────────────────┘     └──────────────────┘     └─────────────────┘
            │                       │
            │ 1. Request keys       │ 2. Validate license
            │    (with license ID)  │    Return encrypted keys
            │◀──────────────────────│
            │
            │ 3. Store keys locally (encrypted in SQLite)
            │ 4. Use for API calls

Usage:
    key_service = KeyProvisioningService()

    # Request keys from server (on first launch or refresh)
    result = await key_service.provision_keys(license_id="abc123")

    # Get a key for a provider
    api_key = key_service.get_key("deepseek")

    # Check key status
    status = key_service.get_provisioning_status()
"""

import os
import json
import logging
import hashlib
import base64
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict
from enum import Enum

import httpx
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# --- Logging ---
logger = logging.getLogger(__name__)

# --- Database Setup ---
WORKSPACE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "workspace")
os.makedirs(WORKSPACE_DIR, exist_ok=True)
KEYS_DB_PATH = os.path.join(WORKSPACE_DIR, "sessions.db")  # Share with other services
KEYS_DB_URL = f"sqlite:///{KEYS_DB_PATH}"

# SQLAlchemy setup
engine = create_engine(KEYS_DB_URL, echo=False)
KeysSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# --- Configuration ---
# Key server URL - will be configured for production
KEY_SERVER_URL = os.getenv("KEY_SERVER_URL", "https://api.writersfactory.app")

# Providers that can have baked-in keys (cheap providers)
BAKED_IN_PROVIDERS = [
    "deepseek",
    "qwen",
    "mistral",
    "zhipu",
    "kimi",
    "yandex",
]

# Providers that require user's own keys (expensive)
USER_KEY_PROVIDERS = [
    "anthropic",
    "openai",
    "gemini",
    "xai",
]

# Key refresh interval (7 days)
KEY_REFRESH_INTERVAL = timedelta(days=7)

# Offline grace period (30 days)
OFFLINE_GRACE_PERIOD = timedelta(days=30)


class ProvisioningStatus(Enum):
    """Status of key provisioning."""
    NOT_PROVISIONED = "not_provisioned"  # Never provisioned
    ACTIVE = "active"  # Keys are valid and working
    NEEDS_REFRESH = "needs_refresh"  # Keys work but should be refreshed
    EXPIRED = "expired"  # Keys expired, need new provisioning
    OFFLINE_GRACE = "offline_grace"  # Can't reach server but within grace period
    ERROR = "error"  # Provisioning failed


# --- Database Models ---
class ProvisionedKey(Base):
    """Encrypted API key from provisioning server."""
    __tablename__ = "provisioned_keys"

    id = Column(Integer, primary_key=True, autoincrement=True)
    provider = Column(String(50), nullable=False, unique=True, index=True)
    encrypted_key = Column(Text, nullable=False)  # Fernet encrypted
    provisioned_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "provider": self.provider,
            "provisioned_at": self.provisioned_at.isoformat() if self.provisioned_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
            "is_active": self.is_active,
        }


class ProvisioningRecord(Base):
    """Record of provisioning attempts."""
    __tablename__ = "provisioning_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    license_id = Column(String(100), nullable=True)
    machine_id = Column(String(100), nullable=False)
    provisioned_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    providers_provisioned = Column(Text, nullable=True)  # JSON list

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "license_id": self.license_id,
            "machine_id": self.machine_id,
            "provisioned_at": self.provisioned_at.isoformat() if self.provisioned_at else None,
            "success": self.success,
            "error_message": self.error_message,
            "providers_provisioned": json.loads(self.providers_provisioned) if self.providers_provisioned else [],
        }


# Create tables
Base.metadata.create_all(bind=engine)
logger.info(f"Key provisioning tables initialized in: {KEYS_DB_PATH}")


# --- Data Classes ---
@dataclass
class ProvisioningResult:
    """Result of a provisioning request."""
    success: bool
    status: ProvisioningStatus
    providers_provisioned: List[str]
    error_message: Optional[str] = None
    next_refresh: Optional[datetime] = None

    def to_dict(self) -> dict:
        result = asdict(self)
        result["status"] = self.status.value
        if self.next_refresh:
            result["next_refresh"] = self.next_refresh.isoformat()
        return result


@dataclass
class KeyStatus:
    """Status of provisioned keys."""
    status: ProvisioningStatus
    provisioned_providers: List[str]
    missing_providers: List[str]
    last_provisioned: Optional[datetime]
    next_refresh: Optional[datetime]
    offline_days_remaining: Optional[int]

    def to_dict(self) -> dict:
        result = {
            "status": self.status.value,
            "provisioned_providers": self.provisioned_providers,
            "missing_providers": self.missing_providers,
            "last_provisioned": self.last_provisioned.isoformat() if self.last_provisioned else None,
            "next_refresh": self.next_refresh.isoformat() if self.next_refresh else None,
            "offline_days_remaining": self.offline_days_remaining,
        }
        return result


# --- Encryption Utilities ---
class KeyEncryption:
    """
    Encrypt/decrypt API keys using machine-specific key derivation.

    Uses PBKDF2 with a machine-specific salt to derive a Fernet key.
    This ensures keys can only be decrypted on the same machine.
    """

    @staticmethod
    def _get_machine_id() -> str:
        """Get a unique machine identifier."""
        # Combine multiple sources for a stable machine ID
        import platform
        import uuid

        parts = [
            platform.node(),  # Hostname
            platform.machine(),  # Machine type
            str(uuid.getnode()),  # MAC address
        ]
        combined = "-".join(parts)
        return hashlib.sha256(combined.encode()).hexdigest()[:32]

    @staticmethod
    def _derive_key(machine_id: str) -> bytes:
        """Derive a Fernet key from machine ID."""
        # Use a fixed salt (app-specific) + machine ID
        app_salt = b"writers-factory-key-encryption-v1"
        salt = hashlib.sha256(app_salt + machine_id.encode()).digest()[:16]

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(machine_id.encode()))
        return key

    @classmethod
    def encrypt(cls, plaintext: str) -> str:
        """Encrypt a string."""
        machine_id = cls._get_machine_id()
        key = cls._derive_key(machine_id)
        f = Fernet(key)
        return f.encrypt(plaintext.encode()).decode()

    @classmethod
    def decrypt(cls, ciphertext: str) -> str:
        """Decrypt a string."""
        machine_id = cls._get_machine_id()
        key = cls._derive_key(machine_id)
        f = Fernet(key)
        return f.decrypt(ciphertext.encode()).decode()

    @classmethod
    def get_machine_id(cls) -> str:
        """Get the machine ID (for server requests)."""
        return cls._get_machine_id()


# --- Service Class ---
from backend.services.settings_service import settings_service

class KeyProvisioningService:
    """
    Manages provisioned API keys from the key server.
    
    Handles:
    - Requesting keys from server
    - Secure local storage
    - Key refresh and rotation
    - Fallback to env vars for development
    - Integration with SettingsService for user overrides
    """

    def __init__(self):
        self.server_url = KEY_SERVER_URL
        self.encryption = KeyEncryption()

    async def provision_keys(
        self,
        license_id: Optional[str] = None,
        force_refresh: bool = False,
    ) -> ProvisioningResult:
        """
        Request provisioned keys from the key server.

        Args:
            license_id: Optional license ID for validation
            force_refresh: Force refresh even if keys are valid

        Returns:
            ProvisioningResult with status and provisioned providers
        """
        machine_id = self.encryption.get_machine_id()

        # Check if we need to provision
        if not force_refresh:
            status = self.get_provisioning_status()
            if status.status == ProvisioningStatus.ACTIVE:
                return ProvisioningResult(
                    success=True,
                    status=ProvisioningStatus.ACTIVE,
                    providers_provisioned=status.provisioned_providers,
                    next_refresh=status.next_refresh,
                )

        # Request keys from server
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.server_url}/keys/provision",
                    json={
                        "machine_id": machine_id,
                        "license_id": license_id,
                        "requested_providers": BAKED_IN_PROVIDERS,
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    return await self._process_provisioning_response(data, machine_id, license_id)

                elif response.status_code == 401:
                    return ProvisioningResult(
                        success=False,
                        status=ProvisioningStatus.ERROR,
                        providers_provisioned=[],
                        error_message="Invalid license ID",
                    )

                elif response.status_code == 429:
                    return ProvisioningResult(
                        success=False,
                        status=ProvisioningStatus.ERROR,
                        providers_provisioned=[],
                        error_message="Rate limited - please try again later",
                    )

                else:
                    return ProvisioningResult(
                        success=False,
                        status=ProvisioningStatus.ERROR,
                        providers_provisioned=[],
                        error_message=f"Server error: {response.status_code}",
                    )

        except httpx.ConnectError:
            # Can't reach server - check offline grace period
            return self._handle_offline()

        except Exception as e:
            logger.error(f"Provisioning failed: {e}")
            return ProvisioningResult(
                success=False,
                status=ProvisioningStatus.ERROR,
                providers_provisioned=[],
                error_message=str(e),
            )

    async def _process_provisioning_response(
        self,
        data: Dict[str, Any],
        machine_id: str,
        license_id: Optional[str],
    ) -> ProvisioningResult:
        """Process successful provisioning response."""
        db: Session = KeysSessionLocal()
        try:
            provisioned = []
            expires_at = None

            if "expires_at" in data:
                expires_at = datetime.fromisoformat(data["expires_at"].replace("Z", "+00:00"))

            # Store each key
            for provider, key_data in data.get("keys", {}).items():
                api_key = key_data.get("api_key")
                if not api_key:
                    continue

                # Encrypt and store
                encrypted = self.encryption.encrypt(api_key)

                existing = db.query(ProvisionedKey).filter(
                    ProvisionedKey.provider == provider
                ).first()

                if existing:
                    existing.encrypted_key = encrypted
                    existing.provisioned_at = datetime.now(timezone.utc)
                    existing.expires_at = expires_at
                    existing.is_active = True
                else:
                    new_key = ProvisionedKey(
                        provider=provider,
                        encrypted_key=encrypted,
                        expires_at=expires_at,
                    )
                    db.add(new_key)

                provisioned.append(provider)

            # Record the provisioning
            record = ProvisioningRecord(
                license_id=license_id,
                machine_id=machine_id,
                success=True,
                providers_provisioned=json.dumps(provisioned),
            )
            db.add(record)
            db.commit()

            next_refresh = datetime.now(timezone.utc) + KEY_REFRESH_INTERVAL

            return ProvisioningResult(
                success=True,
                status=ProvisioningStatus.ACTIVE,
                providers_provisioned=provisioned,
                next_refresh=next_refresh,
            )

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to store provisioned keys: {e}")
            raise
        finally:
            db.close()

    def _handle_offline(self) -> ProvisioningResult:
        """Handle case when server is unreachable."""
        status = self.get_provisioning_status()

        if status.status == ProvisioningStatus.ACTIVE:
            # Keys still valid, just can't refresh
            return ProvisioningResult(
                success=True,
                status=ProvisioningStatus.OFFLINE_GRACE,
                providers_provisioned=status.provisioned_providers,
            )

        elif status.offline_days_remaining and status.offline_days_remaining > 0:
            return ProvisioningResult(
                success=True,
                status=ProvisioningStatus.OFFLINE_GRACE,
                providers_provisioned=status.provisioned_providers,
            )

        else:
            return ProvisioningResult(
                success=False,
                status=ProvisioningStatus.EXPIRED,
                providers_provisioned=[],
                error_message="Keys expired and unable to reach server",
            )

    def get_key(self, provider: str) -> Optional[str]:
        """
        Get an API key for a provider.

        Priority:
        1. Settings Service (User overrides from UI)
        2. Environment variable (for development/user override)
        3. Provisioned key from database
        4. None (provider not available)
        """
        # 1. Check Settings Service (User overrides)
        settings_key = f"agents.{provider}_api_key"
        user_key = settings_service.get(settings_key)
        if user_key and isinstance(user_key, str) and user_key.strip():
            return user_key.strip()

        # 2. Check env var (allows override if no user setting)
        env_var = f"{provider.upper()}_API_KEY"
        env_key = os.getenv(env_var)
        if env_key:
            return env_key

        # 3. Check provisioned keys
        db: Session = KeysSessionLocal()
        try:
            key_record = db.query(ProvisionedKey).filter(
                ProvisionedKey.provider == provider,
                ProvisionedKey.is_active == True,
            ).first()

            if key_record:
                # Check expiration
                if key_record.expires_at and key_record.expires_at < datetime.now(timezone.utc):
                    # Expired but might be in grace period
                    grace_end = key_record.expires_at + OFFLINE_GRACE_PERIOD
                    if datetime.now(timezone.utc) > grace_end:
                        return None

                # Decrypt and return
                try:
                    decrypted = self.encryption.decrypt(key_record.encrypted_key)

                    # Update last used
                    key_record.last_used_at = datetime.now(timezone.utc)
                    db.commit()

                    return decrypted
                except Exception as e:
                    logger.error(f"Failed to decrypt key for {provider}: {e}")
                    return None

            return None

        finally:
            db.close()

    def get_provisioning_status(self) -> KeyStatus:
        """Get current status of key provisioning."""
        db: Session = KeysSessionLocal()
        try:
            # Get all provisioned keys
            keys = db.query(ProvisionedKey).filter(
                ProvisionedKey.is_active == True
            ).all()

            provisioned = [k.provider for k in keys]
            missing = [p for p in BAKED_IN_PROVIDERS if p not in provisioned]

            # Determine status
            if not keys:
                return KeyStatus(
                    status=ProvisioningStatus.NOT_PROVISIONED,
                    provisioned_providers=[],
                    missing_providers=BAKED_IN_PROVIDERS,
                    last_provisioned=None,
                    next_refresh=None,
                    offline_days_remaining=None,
                )

            # Get latest provisioning time
            latest = max(k.provisioned_at for k in keys if k.provisioned_at)
            next_refresh = latest + KEY_REFRESH_INTERVAL if latest else None

            # Check if any keys are expired
            now = datetime.now(timezone.utc)
            expired_keys = [k for k in keys if k.expires_at and k.expires_at < now]

            if expired_keys:
                # Check grace period
                grace_end = max(k.expires_at for k in expired_keys) + OFFLINE_GRACE_PERIOD
                days_remaining = (grace_end - now).days

                if days_remaining <= 0:
                    return KeyStatus(
                        status=ProvisioningStatus.EXPIRED,
                        provisioned_providers=provisioned,
                        missing_providers=missing,
                        last_provisioned=latest,
                        next_refresh=None,
                        offline_days_remaining=0,
                    )
                else:
                    return KeyStatus(
                        status=ProvisioningStatus.OFFLINE_GRACE,
                        provisioned_providers=provisioned,
                        missing_providers=missing,
                        last_provisioned=latest,
                        next_refresh=next_refresh,
                        offline_days_remaining=days_remaining,
                    )

            # Check if refresh needed
            if next_refresh and next_refresh < now:
                return KeyStatus(
                    status=ProvisioningStatus.NEEDS_REFRESH,
                    provisioned_providers=provisioned,
                    missing_providers=missing,
                    last_provisioned=latest,
                    next_refresh=next_refresh,
                    offline_days_remaining=None,
                )

            return KeyStatus(
                status=ProvisioningStatus.ACTIVE,
                provisioned_providers=provisioned,
                missing_providers=missing,
                last_provisioned=latest,
                next_refresh=next_refresh,
                offline_days_remaining=None,
            )

        finally:
            db.close()

    def clear_provisioned_keys(self) -> bool:
        """Clear all provisioned keys (for testing/reset)."""
        db: Session = KeysSessionLocal()
        try:
            db.query(ProvisionedKey).delete()
            db.commit()
            logger.info("Cleared all provisioned keys")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to clear keys: {e}")
            return False
        finally:
            db.close()

    def get_available_providers(self) -> Dict[str, str]:
        """
        Get all available providers and their key sources.

        Returns dict of provider -> source ("provisioned", "env", "user", "none")
        """
        result = {}

        for provider in BAKED_IN_PROVIDERS + USER_KEY_PROVIDERS:
            # 1. Check Settings (User) - Priority 1
            settings_key = f"agents.{provider}_api_key"
            user_key = settings_service.get(settings_key)
            if user_key and isinstance(user_key, str) and user_key.strip():
                result[provider] = "user"
                continue

            # 2. Check Env - Priority 2
            env_var = f"{provider.upper()}_API_KEY"
            if os.getenv(env_var):
                result[provider] = "env"
                continue

            # 3. Check Provisioned - Priority 3
            if self.get_key(provider): # This calls get_key which checks DB
                # But get_key also checks env/settings, so we need to be careful.
                # Since we already checked env and settings above, if we get here
                # and get_key returns something, it MUST be from DB (or we missed something).
                # Actually, get_key checks DB last.
                
                # Let's check DB directly to be sure about source
                db: Session = KeysSessionLocal()
                try:
                    key_record = db.query(ProvisionedKey).filter(
                        ProvisionedKey.provider == provider,
                        ProvisionedKey.is_active == True,
                    ).first()
                    if key_record:
                        result[provider] = "provisioned"
                    else:
                        result[provider] = "none"
                finally:
                    db.close()
            else:
                result[provider] = "none"

        return result


# Singleton instance
key_provisioning_service = KeyProvisioningService()
