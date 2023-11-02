"""Privacy module for Theengs Gateway.

This module is used to resolve resolvable private addresses (RPAs) if you know their
corresponding identity resolving keys (IRKs).
"""
from __future__ import annotations

from base64 import b64decode

from Cryptodome.Cipher import AES

_MSB_MASK = 0b11000000
_MSB_RPA = 0b01000000


def resolve_private_address(address: str, irk: str) -> bool:
    """Return `True` if the address can be resolved with the IRK."""
    rpa = bytes.fromhex(address.replace(":", ""))
    # Format of a resolvable private address:
    # MSB                                          LSB
    # 01 Random part of prand      Hash value
    # <-   prand (24 bits)  -><-   hash (24 bits)   ->
    if rpa[0] & _MSB_MASK != _MSB_RPA:
        # Address is not an RPA
        return False

    prand = rpa[:3]
    hash_value = rpa[3:]
    try:
        # Suppose the key is in hex format
        key = bytes.fromhex(irk)[::-1]
    except ValueError:
        # If that doesn't work, try to decode it as Base64 format
        key = b64decode(irk)[::-1]
    cipher = AES.new(key, AES.MODE_ECB)
    localhash = cipher.encrypt(b"\x00" * 13 + prand)

    if localhash[13:] != hash_value:
        # 24 bits of local hash don't match the RPA's hash
        return False

    return True
