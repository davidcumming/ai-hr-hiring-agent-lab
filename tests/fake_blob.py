"""Small fake Azure Blob client surface for deterministic storage tests."""

from __future__ import annotations

from types import SimpleNamespace


class ResourceNotFoundError(Exception):
    """Named to match Azure's not-found exception class for backend handling."""


class FakeBlobDownload:
    def __init__(self, body: bytes) -> None:
        self._body = body

    def readall(self) -> bytes:
        return self._body


class FakeBlobClient:
    def __init__(self, blobs: dict[str, bytes], name: str) -> None:
        self._blobs = blobs
        self._name = name

    def upload_blob(self, data, overwrite: bool = False) -> None:
        if not overwrite and self._name in self._blobs:
            raise RuntimeError("blob already exists")
        if isinstance(data, str):
            body = data.encode("utf-8")
        else:
            body = bytes(data)
        self._blobs[self._name] = body

    def download_blob(self) -> FakeBlobDownload:
        if self._name not in self._blobs:
            raise ResourceNotFoundError(self._name)
        return FakeBlobDownload(self._blobs[self._name])


class FakeBlobContainerClient:
    def __init__(self) -> None:
        self.blobs: dict[str, bytes] = {}

    def get_blob_client(self, name: str) -> FakeBlobClient:
        return FakeBlobClient(self.blobs, name)

    def list_blobs(self, name_starts_with: str):
        return [
            SimpleNamespace(name=name)
            for name in sorted(self.blobs)
            if name.startswith(name_starts_with)
        ]
