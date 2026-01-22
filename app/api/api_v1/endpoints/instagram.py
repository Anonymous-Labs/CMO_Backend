import secrets
from typing import Any

import requests
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models
from app.api import deps
from app.core.config import settings

router = APIRouter()


@router.get("/oauth/url")
def get_instagram_oauth_url(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """Get the Instagram OAuth authorization URL"""
    if not settings.META_APP_ID:
        raise HTTPException(status_code=500, detail="Meta app not configured")

    # Generate a state parameter for security
    state = secrets.token_urlsafe(32)

    # Store state in database or cache for verification later
    # For now, we'll skip this for simplicity

    base_url = "https://www.facebook.com/v18.0/dialog/oauth"
    params = {
        "client_id": settings.META_APP_ID,
        "redirect_uri": settings.META_REDIRECT_URI,
        "scope": "instagram_basic,instagram_content_publish,pages_show_list,pages_read_engagement",
        "response_type": "code",
        "state": state,
    }

    auth_url = f"{base_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"

    return {"authorization_url": auth_url}


@router.post("/oauth/callback")
def handle_instagram_oauth_callback(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    code: str,
) -> Any:
    """Handle the Instagram OAuth callback and exchange code for access token"""
    if not settings.META_APP_ID or not settings.META_APP_SECRET:
        raise HTTPException(status_code=500, detail="Meta app not configured")

    # Exchange code for access token
    token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
    token_data = {
        "client_id": settings.META_APP_ID,
        "client_secret": settings.META_APP_SECRET,
        "redirect_uri": settings.META_REDIRECT_URI,
        "code": code,
    }

    try:
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        token_data = token_response.json()

        access_token = token_data.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to get access token")

        # Get user's pages to find Instagram Business account
        pages_url = f"https://graph.facebook.com/v18.0/me/accounts?access_token={access_token}"
        pages_response = requests.get(pages_url)
        pages_response.raise_for_status()
        pages_data = pages_response.json()

        instagram_account = None
        for page in pages_data.get("data", []):
            page_id = page["id"]
            page_access_token = page["access_token"]

            # Check if this page has an Instagram Business account
            ig_url = f"https://graph.facebook.com/v18.0/{page_id}?fields=instagram_business_account&access_token={page_access_token}"
            ig_response = requests.get(ig_url)
            if ig_response.status_code == 200:
                ig_data = ig_response.json()
                if "instagram_business_account" in ig_data:
                    ig_account_id = ig_data["instagram_business_account"]["id"]

                    # Get Instagram account details
                    ig_details_url = f"https://graph.facebook.com/v18.0/{ig_account_id}?fields=username,account_type&access_token={page_access_token}"
                    ig_details_response = requests.get(ig_details_url)
                    ig_details_response.raise_for_status()
                    ig_details = ig_details_response.json()

                    instagram_account = {
                        "id": ig_account_id,
                        "username": ig_details.get("username"),
                        "account_type": ig_details.get("account_type"),
                        "page_id": page_id,
                        "page_access_token": page_access_token,
                        "user_access_token": access_token,
                    }
                    break

        if not instagram_account:
            raise HTTPException(status_code=400, detail="No Instagram Business account found")

        # Store the Instagram account connection in database
        # For now, we'll just return the account info
        # In a real implementation, you'd store this securely

        return {
            "id": instagram_account["id"],
            "username": instagram_account["username"],
            "account_type": instagram_account["account_type"],
            "connected_at": "2025-01-22T00:00:00Z",  # Would be actual timestamp
        }

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Instagram API error: {str(e)}")


@router.get("/status")
def get_instagram_connection_status(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """Get the current Instagram connection status"""
    # In a real implementation, you'd check the database
    # For now, we'll return null to indicate not connected
    return None


@router.delete("/disconnect")
def disconnect_instagram(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """Disconnect the Instagram account"""
    # In a real implementation, you'd remove the connection from database
    return {"message": "Instagram account disconnected"}


@router.post("/publish")
def publish_to_instagram(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    post_id: int,
    caption: str,
    hashtags: str,
) -> Any:
    """Publish a post to Instagram"""
    # In a real implementation, you'd:
    # 1. Get the stored Instagram tokens
    # 2. Create a media container
    # 3. Publish the post
    # For now, we'll just simulate success

    raise HTTPException(status_code=501, detail="Instagram publishing not yet implemented")
