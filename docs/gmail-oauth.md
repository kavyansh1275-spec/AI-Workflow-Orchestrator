# Gmail OAuth connection

The Orchestrator uses Google's OAuth 2.0 flow instead of asking clients for Gmail passwords.

## Environment

Set:

- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REDIRECT_URI` (default: `http://localhost:8000/api/connections/gmail/callback`)

The connection requests only `https://www.googleapis.com/auth/gmail.send`, which is sufficient for sending mail on the connected user's behalf.

## Flow

1. Create a Google OAuth client in Google Cloud and configure the consent screen.
2. The Orchestrator creates a one-time `state` value and redirects the client to Google.
3. The client grants the requested Gmail permission.
4. Google redirects back to the configured callback with an authorization code.
5. The backend exchanges that code for OAuth tokens.
6. The refresh token must be stored encrypted in a production connection store; never commit it to Git.
7. Workflows reference the connection by `connection_id`, not by a password or raw secret.

The current code provides the OAuth URL/state and connection metadata foundation. Token exchange and encrypted persistent token storage should be enabled before production use.
