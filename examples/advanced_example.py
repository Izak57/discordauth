#!/usr/bin/env python3
"""
Advanced Discord OAuth2 Example

This example demonstrates advanced features and best practices when using
the discordauth library, including:
- Error handling and retry logic
- Token expiration handling
- Multiple scope requests
- User data validation
- Logging and debugging

Prerequisites:
- A Discord application with multiple scopes configured
- Python logging knowledge (optional)

Usage:
    python advanced_example.py
"""

import logging
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Optional, Dict, Any
from discordauth import Application, Endpoint, DiscordToken, UserInfo
import httpx


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AdvancedDiscordAuth:
    """
    Advanced Discord OAuth2 handler with enhanced features.
    
    This class wraps the basic discordauth functionality with additional
    features like retry logic, token validation, and comprehensive error handling.
    """
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        """Initialize the advanced Discord auth handler."""
        self.app = Application(id=client_id, secret=client_secret)
        self.redirect_uri = redirect_uri
        self.logger = logger
        
        # Define available scopes with descriptions
        self.available_scopes = {
            "identify": "Basic account information",
            "email": "Email address",
            "guilds": "List of user's guilds",
            "guilds.join": "Join guilds on behalf of user",
            "guilds.members.read": "Read guild member info",
            "connections": "Linked third-party accounts",
            "role_connections.write": "Update role connection metadata"
        }
    
    def create_endpoint(self, scopes: list[str]) -> Endpoint:
        """
        Create an OAuth2 endpoint with scope validation.
        
        Args:
            scopes: List of Discord OAuth2 scopes to request
            
        Returns:
            Configured Endpoint instance
            
        Raises:
            ValueError: If any scope is invalid
        """
        # Validate scopes
        invalid_scopes = [scope for scope in scopes if scope not in self.available_scopes]
        if invalid_scopes:
            raise ValueError(f"Invalid scopes: {invalid_scopes}. Available: {list(self.available_scopes.keys())}")
        
        self.logger.info(f"Creating endpoint with scopes: {scopes}")
        for scope in scopes:
            self.logger.info(f"  - {scope}: {self.available_scopes[scope]}")
        
        return Endpoint(
            app=self.app,
            scopes=scopes,
            redirect_uri=self.redirect_uri
        )
    
    def exchange_with_retry(self, endpoint: Endpoint, code: str, max_retries: int = 3) -> Optional[DiscordToken]:
        """
        Exchange authorization code for token with retry logic.
        
        Args:
            endpoint: The OAuth2 endpoint
            code: Authorization code from Discord
            max_retries: Maximum number of retry attempts
            
        Returns:
            DiscordToken if successful, None if all retries failed
        """
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Attempting token exchange (attempt {attempt + 1}/{max_retries})")
                token = endpoint.exchange(code)
                self.logger.info(f"Token exchange successful! Expires in {token.expires_in} seconds")
                return token
                
            except httpx.HTTPStatusError as e:
                self.logger.error(f"Token exchange failed (attempt {attempt + 1}): {e.response.status_code} - {e.response.text}")
                
                # Don't retry on client errors (4xx)
                if 400 <= e.response.status_code < 500:
                    self.logger.error("Client error - not retrying")
                    break
                
                # Wait before retry (exponential backoff)
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    self.logger.info(f"Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    
            except Exception as e:
                self.logger.error(f"Unexpected error during token exchange: {e}")
                break
        
        self.logger.error("All token exchange attempts failed")
        return None
    
    def get_user_with_validation(self, endpoint: Endpoint, token: DiscordToken) -> Optional[UserInfo]:
        """
        Get user information with comprehensive validation.
        
        Args:
            endpoint: The OAuth2 endpoint
            token: Valid Discord token
            
        Returns:
            UserInfo if successful, None if failed
        """
        try:
            # Check if token has required scope
            if "identify" not in token.scopes:
                self.logger.error("Token missing 'identify' scope - cannot get user info")
                return None
            
            self.logger.info("Retrieving user information...")
            user = endpoint.get_user(token)
            
            # Validate user data
            if not user.id or not user.username:
                self.logger.error("Received incomplete user data from Discord")
                return None
            
            self.logger.info(f"Successfully retrieved user info for: {user.username}#{user.discriminator}")
            return user
            
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Failed to get user info: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error getting user info: {e}")
            return None
    
    def validate_token(self, token: DiscordToken) -> bool:
        """
        Validate token expiration and scope requirements.
        
        Args:
            token: Discord token to validate
            
        Returns:
            True if token is valid, False otherwise
        """
        # Note: This is a basic validation. In a real app, you'd want to
        # store the token creation timestamp and check against expires_in
        if not token.access_token:
            self.logger.error("Token has no access_token")
            return False
        
        if not token.scopes:
            self.logger.error("Token has no scopes")
            return False
        
        self.logger.info(f"Token validation passed. Scopes: {token.scopes}")
        return True
    
    def display_user_info(self, user: UserInfo, token: DiscordToken) -> None:
        """
        Display comprehensive user information.
        
        Args:
            user: User information from Discord
            token: Token used to retrieve the info
        """
        print("\n" + "="*50)
        print("USER INFORMATION")
        print("="*50)
        
        print(f"ID: {user.id}")
        print(f"Username: {user.username}#{user.discriminator}")
        
        if user.global_name:
            print(f"Display Name: {user.global_name}")
        
        print(f"Avatar URL: {user.avatar_url or 'No custom avatar'}")
        print(f"Banner URL: {user.banner_url or 'No banner'}")
        
        # Premium status
        premium_types = {0: "None", 1: "Nitro Classic", 2: "Nitro"}
        print(f"Premium Type: {premium_types.get(user.premium_type, user.premium_type)}")
        
        print(f"2FA Enabled: {'Yes' if user.mfa_enabled else 'No'}")
        print(f"Locale: {user.locale or 'Not specified'}")
        
        # Token information
        print(f"\nToken Scopes: {', '.join(token.scopes)}")
        print(f"Token Expires In: {token.expires_in} seconds")
        
        # Scope explanations
        print(f"\nScope Explanations:")
        for scope in token.scopes:
            description = self.available_scopes.get(scope, "Unknown scope")
            print(f"  - {scope}: {description}")


def main():
    """Demonstrate advanced Discord OAuth2 usage."""
    print("=== Advanced Discord OAuth2 Example ===\n")
    
    # Configuration
    CLIENT_ID = "your_discord_client_id_here"
    CLIENT_SECRET = "your_discord_client_secret_here"
    REDIRECT_URI = "http://localhost:8000/callback"
    
    # Initialize advanced auth handler
    auth_handler = AdvancedDiscordAuth(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
    
    # Example 1: Basic scope request
    print("1. Creating endpoint with basic scopes...")
    try:
        basic_endpoint = auth_handler.create_endpoint(["identify"])
        print(f"   ✓ Authorization URL: {basic_endpoint.url}")
    except ValueError as e:
        print(f"   ✗ Error: {e}")
        return
    
    # Example 2: Multiple scopes with validation
    print("\n2. Creating endpoint with multiple scopes...")
    try:
        advanced_scopes = ["identify", "email", "guilds"]
        advanced_endpoint = auth_handler.create_endpoint(advanced_scopes)
        print(f"   ✓ Advanced authorization URL generated")
        print(f"   ✓ Requested scopes: {advanced_scopes}")
    except ValueError as e:
        print(f"   ✗ Error: {e}")
        return
    
    # Example 3: Invalid scope handling
    print("\n3. Testing invalid scope handling...")
    try:
        auth_handler.create_endpoint(["identify", "invalid_scope"])
        print("   ✗ Should have failed!")
    except ValueError as e:
        print(f"   ✓ Correctly rejected invalid scope: {e}")
    
    # Example 4: Simulated token exchange with retry
    print("\n4. Token exchange with retry logic (simulated)...")
    print("   In a real scenario with an authorization code:")
    print("   ```python")
    print("   token = auth_handler.exchange_with_retry(endpoint, auth_code)")
    print("   if token:")
    print("       print('Token exchange successful!')")
    print("   else:")
    print("       print('All retry attempts failed')")
    print("   ```")
    
    # Example 5: Token validation
    print("\n5. Token validation example...")
    # Create a mock token for demonstration
    from discordauth import DiscordToken
    mock_token_data = {
        "access_token": "mock_token_12345",
        "token_type": "Bearer",
        "expires_in": 3600,
        "scope": "identify email"
    }
    mock_token = DiscordToken(**mock_token_data)
    
    is_valid = auth_handler.validate_token(mock_token)
    print(f"   Mock token validation: {'✓ Valid' if is_valid else '✗ Invalid'}")
    
    # Example 6: Available scopes information
    print("\n6. Available Discord OAuth2 scopes:")
    for scope, description in auth_handler.available_scopes.items():
        print(f"   - {scope}: {description}")
    
    print("\n=== Advanced Example Complete ===")
    print("\nKey features demonstrated:")
    print("- ✅ Scope validation and description")
    print("- ✅ Retry logic with exponential backoff") 
    print("- ✅ Comprehensive error handling")
    print("- ✅ Token validation")
    print("- ✅ Structured logging")
    print("- ✅ User data validation")
    
    print(f"\nTo use this in production:")
    print("1. Replace the CLIENT_ID and CLIENT_SECRET with real values")
    print("2. Implement proper token storage and refresh logic")
    print("3. Add rate limiting to prevent API abuse")
    print("4. Use HTTPS for your redirect URI")
    print("5. Validate all user inputs")


if __name__ == "__main__":
    main()