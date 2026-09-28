import jwt
import requests
from jwt.algorithms import RSAAlgorithm

COGNITO_REGION = "us-east-1"
COGNITO_USER_POOL_ID = "us-east-1_icqLr20CS"
COGNITO_CLIENT_ID = "4e1o6h4fote0icdvoflgb3pilu"

JWKS_URL = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}/.well-known/jwks.json"

def verify_cognito_token(id_token):
    # Get JWKS keys
    jwks = requests.get(JWKS_URL).json()
    headers = jwt.get_unverified_header(id_token)

    # Find the matching key
    key = next((k for k in jwks['keys'] if k['kid'] == headers['kid']), None)
    if not key:
        raise Exception("Public key not found in JWKS")

    # Build public key
    public_key = RSAAlgorithm.from_jwk(key)

    # Verify token
    claims = jwt.decode(
        id_token,
        public_key,
        algorithms=['RS256'],
        audience=COGNITO_CLIENT_ID,
        issuer=f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}"
    )
    return claims
