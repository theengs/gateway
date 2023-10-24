"""Decryption module for Theengs Gateway.

This module adds decryptors for encrypted advertisements of a selection of
devices.
"""
from __future__ import annotations

import binascii
from abc import ABC, abstractmethod

from Cryptodome.Cipher import AES


class AdvertisementDecryptor(ABC):
    """Abstract class that represents a decryptor for advertisements."""

    @abstractmethod
    def compute_nonce(self, address: str, decoded_json: dict) -> bytes:
        """Compute the nonce for a specific address and JSON input."""

    @abstractmethod
    def decrypt(
        self,
        bindkey: bytes,
        address: str,
        decoded_json: dict,
    ) -> bytes:
        """Decrypt ciphertext from JSON input."""

    @abstractmethod
    def replace_encrypted_data(
        self,
        decrypted_data: bytes,
        data_json: dict,
        decoded_json: dict,
    ) -> None:
        """Replace the encrypted data by decrypted payload."""


class LYWSD03MMC_PVVXDecryptor(AdvertisementDecryptor):  # noqa: N801
    """Class for decryption of LYWSD03MMX PVVX encrypted advertisements."""

    def compute_nonce(self, address: str, decoded_json: dict) -> bytes:
        """Compute the nonce for a specific address and JSON input."""
        # The nonce consists of:
        # 6 bytes: device address in reverse
        # 1 byte : length of (service data + type and UUID)
        # 1 byte : "16" -> AD type for "Service Data - 16-bit UUID"
        # 2 bytes: "1a18" -> UUID 181a in little-endian
        # 1 byte : counter
        return binascii.unhexlify(
            "".join(
                [
                    reverse_address(address),
                    bytes([len(decoded_json["servicedata"]) // 2 + 3]).hex(),
                    "161a18",
                    decoded_json["ctr"],
                ],
            ),
        )

    def decrypt(
        self,
        bindkey: bytes,
        address: str,
        decoded_json: dict,
    ) -> bytes:
        """Decrypt ciphertext from JSON input with AES CCM."""
        nonce = self.compute_nonce(address, decoded_json)
        cipher = AES.new(bindkey, AES.MODE_CCM, nonce=nonce, mac_len=4)
        cipher.update(b"\x11")
        payload = bytes.fromhex(decoded_json["cipher"])
        mic = bytes.fromhex(decoded_json["mic"])
        return cipher.decrypt_and_verify(payload, mic)

    def replace_encrypted_data(
        self,
        decrypted_data: bytes,
        data_json: dict,
        decoded_json: dict,  # noqa: ARG002
    ) -> None:
        """Replace the encrypted data by decrypted payload."""
        data_json["servicedata"] = decrypted_data.hex()


class BTHomeV2Decryptor(AdvertisementDecryptor):
    """Class for decryption of BTHome v2 encrypted advertisements."""

    def compute_nonce(self, address: str, decoded_json: dict) -> bytes:
        """Compute the nonce for a specific address and JSON input."""
        # The nonce consists of:
        # 6 bytes: device address
        # 2 bytes: "d2fc" -> UUID fcd2 in little-endian
        # 1 byte : BTHome device info
        # 1 byte : counter
        return binascii.unhexlify(
            "".join(
                [
                    address.replace(":", ""),
                    "d2fc",  # UUID fcd2
                    decoded_json["servicedata"][:2],
                    decoded_json["ctr"],
                ],
            ),
        )

    def decrypt(
        self,
        bindkey: bytes,
        address: str,
        decoded_json: dict,
    ) -> bytes:
        """Decrypt ciphertext from JSON input with AES CCM."""
        nonce = self.compute_nonce(address, decoded_json)
        cipher = AES.new(bindkey, AES.MODE_CCM, nonce=nonce, mac_len=4)
        payload = bytes.fromhex(decoded_json["cipher"])
        mic = bytes.fromhex(decoded_json["mic"])
        return cipher.decrypt_and_verify(payload, mic)

    def replace_encrypted_data(
        self,
        decrypted_data: bytes,
        data_json: dict,
        decoded_json: dict,
    ) -> None:
        """Replace the encrypted data by decrypted payload."""
        # Clear encryption and MAC included bits in device info
        # See https://bthome.io/format/
        device_info = bytes.fromhex(decoded_json["servicedata"][:2])
        mask = 0b11111100
        masked_device_info = int.from_bytes(device_info, "big") & mask
        bthome_service_data = bytearray(masked_device_info.to_bytes(1, "big"))

        # Replace encrypted data by decrypted payload
        bthome_service_data.extend(decrypted_data)
        data_json["servicedata"] = bthome_service_data.hex()


_DECRYPTOR_MODELS = {
    "LYWSD03MMC/MJWSD05MMC_PVVX_ENCR": LYWSD03MMC_PVVXDecryptor,
    "SBBT_002C_ENCR": BTHomeV2Decryptor,
    "SBDW_002C_ENCR": BTHomeV2Decryptor,
    "SBMO_003Z_ENCR": BTHomeV2Decryptor,
}


class UnsupportedEncryptionError(Exception):
    """Exception raised when trying to decrypt an unsupported device."""


def create_decryptor(model_id: str) -> AdvertisementDecryptor:
    """Return the decryptor class for the given model ID."""
    if model_id not in _DECRYPTOR_MODELS:
        raise UnsupportedEncryptionError
    return _DECRYPTOR_MODELS[model_id]()  # type: ignore[abstract]


def reverse_address(address: str) -> str:
    """Reverse device address bytes and remove colons."""
    return "".join(address.split(":")[::-1])
