from __future__ import annotations

import time

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from jose import jwk, jwt


def _generate_rsa_keypair() -> tuple[str, str]:
    """Gera um par RSA novo e retorna (private_pem, public_pem)."""
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode()
    public_pem = key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    return private_pem, public_pem


def _jwk_for(public_pem: str, kid_value: str) -> dict:
    jwk_dict = jwk.construct(public_pem, algorithm="RS256").to_dict()
    jwk_dict["kid"] = kid_value
    jwk_dict["use"] = "sig"
    return jwk_dict


@pytest.fixture(scope="session")
def rsa_keypair() -> tuple[str, str]:
    """Retorna (private_pem, public_pem) de um par RSA gerado pra testes."""
    return _generate_rsa_keypair()


@pytest.fixture(scope="session")
def rsa_keypair_2() -> tuple[str, str]:
    """Segundo par RSA, distinto do primeiro — simula a chave nova numa rotação."""
    return _generate_rsa_keypair()


@pytest.fixture
def kid() -> str:
    return "test-kid-001"


@pytest.fixture
def kid_2() -> str:
    return "test-kid-002"


@pytest.fixture
def jwks_body(rsa_keypair: tuple[str, str], kid: str) -> dict:
    _, public_pem = rsa_keypair
    return {"keys": [_jwk_for(public_pem, kid)]}


@pytest.fixture
def jwks_body_rotation(
    rsa_keypair: tuple[str, str],
    kid: str,
    rsa_keypair_2: tuple[str, str],
    kid_2: str,
) -> dict:
    """JWKS com 2 chaves simultâneas — chave atual + chave anterior, como o Janus expõe durante rotação."""
    _, public_pem_1 = rsa_keypair
    _, public_pem_2 = rsa_keypair_2
    return {"keys": [_jwk_for(public_pem_1, kid), _jwk_for(public_pem_2, kid_2)]}


def make_token(
    rsa_keypair: tuple[str, str],
    kid: str,
    *,
    sub: str = "user-1",
    email: str = "user@example.com",
    role: str = "user",
    authorized_systems: list[str] | None = None,
    issuer: str = "janus",
    audience: str = "janus",
    expires_in: int = 3600,
) -> str:
    private_pem, _ = rsa_keypair
    now = int(time.time())
    claims = {
        "sub": sub,
        "jti": "jti-1",
        "email": email,
        "role": role,
        "authorized_systems": authorized_systems or [],
        "iss": issuer,
        "aud": audience,
        "iat": now,
        "exp": now + expires_in,
    }
    return jwt.encode(claims, private_pem, algorithm="RS256", headers={"kid": kid})
