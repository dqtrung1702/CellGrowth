"""
Seed hoặc cập nhật cấu hình social provider (Google) vào DB.
Usage:
  SOCIAL_CFG_KEY=supersecret \
  UAA_DATABASE_URI=postgresql://admin:admin@localhost:5432/dev?options=-c%20search_path=uaa \
  python -m scripts.seed_social_provider --provider google --client-id <id> --client-secret <secret> --redirect-uri http://localhost:8082/auth/google/callback --scopes "openid email profile"
"""
import argparse

from config import Config
from repositories.social_provider_repository import SocialProviderRepository
from utils.secret_cipher import encrypt_secret, master_key_from_env


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", required=True, help="google/facebook/zalo...")
    parser.add_argument("--client-id", required=True)
    parser.add_argument("--client-secret", required=True)
    parser.add_argument("--redirect-uri", required=True)
    parser.add_argument("--scopes", default="openid email profile")
    parser.add_argument("--enabled", action="store_true", default=True)
    parser.add_argument("--updated-by", default="seed_script")
    args = parser.parse_args()

    master = master_key_from_env()
    cipher = encrypt_secret(args.client_secret, master)
    repo = SocialProviderRepository()
    repo.upsert(
        provider=args.provider.lower(),
        client_id=args.client_id,
        client_secret_enc=cipher,
        redirect_uri=args.redirect_uri,
        scopes=args.scopes,
        enabled=args.enabled,
        updated_by=args.updated_by,
    )
    print(f"✅ upserted {args.provider} config (enabled={args.enabled})")


if __name__ == "__main__":
    main()
