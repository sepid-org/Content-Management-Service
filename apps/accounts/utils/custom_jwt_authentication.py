from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.settings import api_settings
from jwt import decode as jwt_decode, ExpiredSignatureError, InvalidTokenError


class CustomJWTAuthentication(JWTAuthentication):
    def get_validated_token(self, raw_token):
        try:
            # Decode token without signature verification
            unverified_payload = jwt_decode(
                raw_token,
                options={"verify_signature": False},
                algorithms=[api_settings.ALGORITHM],
            )

            # Check if "origin" claim is present and not null
            if unverified_payload.get("origin"):
                # Decode the token without expiration check
                return jwt_decode(
                    raw_token,
                    self.get_signing_key(),  # Use the signing key for decoding
                    algorithms=[api_settings.ALGORITHM],
                    options={"verify_exp": False},  # Skip expiration check
                )

            # If "origin" is null, use the default validation process
            return super().get_validated_token(raw_token)

        except ExpiredSignatureError:
            raise InvalidToken({"detail": "Token has expired."})
        except InvalidTokenError as e:
            raise InvalidToken({"detail": str(e)})

    def get_signing_key(self):
        """
        Retrieve the signing key from the settings.
        """
        return api_settings.SIGNING_KEY
