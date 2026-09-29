import os
import io
import hashlib
from typing import BinaryIO, Optional, Tuple
from abc import ABC, abstractmethod
from app.config import settings

class StorageService(ABC):
    @abstractmethod
    def is_ready(self) -> bool:
        """Returns whether the configured storage backend is reachable and usable."""
        pass

    @abstractmethod
    def save_file(self, file_obj: BinaryIO, filename: str, content_type: Optional[str] = None) -> Tuple[str, str, int]:
        """Saves a file and returns (storage_path, sha256_checksum, byte_size)"""
        pass

    @abstractmethod
    def get_file_bytes(self, storage_path: str) -> bytes:
        """Retrieves raw bytes for a file"""
        pass

    @abstractmethod
    def get_file_stream(self, storage_path: str) -> BinaryIO:
        """Retrieves a readable binary stream for a file"""
        pass

    @abstractmethod
    def delete_file(self, storage_path: str) -> bool:
        """Deletes a file if it exists"""
        pass

    @abstractmethod
    def exists(self, storage_path: str) -> bool:
        """Checks if a file exists"""
        pass

class LocalStorageService(StorageService):
    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = os.path.abspath(base_dir or settings.LOCAL_STORAGE_DIR)
        os.makedirs(self.base_dir, exist_ok=True)

    def _get_full_path(self, storage_path: str) -> str:
        # Normalize and reject paths that escape the configured storage root.
        clean_path = storage_path.replace("\\", "/").lstrip("/")
        full_path = os.path.abspath(os.path.join(self.base_dir, clean_path))
        if os.path.commonpath((self.base_dir, full_path)) != self.base_dir:
            raise ValueError("Storage path escapes the configured storage directory.")
        return full_path

    def is_ready(self) -> bool:
        return os.path.isdir(self.base_dir) and os.access(self.base_dir, os.W_OK)

    def save_file(self, file_obj: BinaryIO, filename: str, content_type: Optional[str] = None) -> Tuple[str, str, int]:
        full_path = self._get_full_path(filename)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        hasher = hashlib.sha256()
        total_size = 0

        # Read in chunks to compute sha256 and write
        with open(full_path, "wb") as f:
            file_obj.seek(0)
            while chunk := file_obj.read(1024 * 1024): # 1MB chunks
                hasher.update(chunk)
                f.write(chunk)
                total_size += len(chunk)

        checksum = hasher.hexdigest()
        clean_rel_path = filename.replace("\\", "/").lstrip("/")
        return clean_rel_path, checksum, total_size

    def get_file_bytes(self, storage_path: str) -> bytes:
        full_path = self._get_full_path(storage_path)
        with open(full_path, "rb") as f:
            return f.read()

    def get_file_stream(self, storage_path: str) -> BinaryIO:
        full_path = self._get_full_path(storage_path)
        return open(full_path, "rb")

    def delete_file(self, storage_path: str) -> bool:
        full_path = self._get_full_path(storage_path)
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
                return True
            except OSError:
                return False
        return False

    def exists(self, storage_path: str) -> bool:
        return os.path.exists(self._get_full_path(storage_path))


class S3StorageService(StorageService):
    def __init__(self):
        try:
            from minio import Minio
            # Strip http:// or https:// from endpoint for minio client
            endpoint = settings.S3_ENDPOINT_URL.replace("http://", "").replace("https://", "").rstrip("/")
            self.client = Minio(
                endpoint,
                access_key=settings.S3_ACCESS_KEY,
                secret_key=settings.S3_SECRET_KEY,
                secure=settings.S3_SECURE
            )
            self.bucket_name = settings.S3_BUCKET_NAME
            # Ensure bucket exists
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
            self._available = True
        except Exception as e:
            # Fall back safely to local storage if MinIO is not running
            self._available = False
            self.local_fallback = LocalStorageService()

    @staticmethod
    def _clean_object_path(storage_path: str) -> str:
        clean_path = storage_path.replace("\\", "/").lstrip("/")
        if any(part == ".." for part in clean_path.split("/")):
            raise ValueError("Storage path contains a parent-directory segment.")
        return clean_path

    def save_file(self, file_obj: BinaryIO, filename: str, content_type: Optional[str] = None) -> Tuple[str, str, int]:
        if not self._available:
            return self.local_fallback.save_file(file_obj, filename, content_type)

        clean_path = self._clean_object_path(filename)
        file_obj.seek(0, io.SEEK_END)
        size = file_obj.tell()
        file_obj.seek(0)

        # Compute checksum
        hasher = hashlib.sha256()
        while chunk := file_obj.read(1024 * 1024):
            hasher.update(chunk)
        checksum = hasher.hexdigest()
        file_obj.seek(0)

        self.client.put_object(
            bucket_name=self.bucket_name,
            object_name=clean_path,
            data=file_obj,
            length=size,
            content_type=content_type or "application/octet-stream"
        )
        return clean_path, checksum, size

    def is_ready(self) -> bool:
        return self.client.bucket_exists(self.bucket_name) if self._available else self.local_fallback.is_ready()

    def get_file_bytes(self, storage_path: str) -> bytes:
        if not self._available:
            return self.local_fallback.get_file_bytes(storage_path)
        clean_path = self._clean_object_path(storage_path)
        response = self.client.get_object(self.bucket_name, clean_path)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    def get_file_stream(self, storage_path: str) -> BinaryIO:
        if not self._available:
            return self.local_fallback.get_file_stream(storage_path)
        clean_path = self._clean_object_path(storage_path)
        response = self.client.get_object(self.bucket_name, clean_path)
        # Read into in-memory bytes buffer for reliable random access/Polars reading
        data = response.read()
        response.close()
        response.release_conn()
        return io.BytesIO(data)

    def delete_file(self, storage_path: str) -> bool:
        if not self._available:
            return self.local_fallback.delete_file(storage_path)
        try:
            clean_path = self._clean_object_path(storage_path)
            self.client.remove_object(self.bucket_name, clean_path)
            return True
        except Exception:
            return False

    def exists(self, storage_path: str) -> bool:
        if not self._available:
            return self.local_fallback.exists(storage_path)
        try:
            clean_path = self._clean_object_path(storage_path)
            self.client.stat_object(self.bucket_name, clean_path)
            return True
        except Exception:
            return False

def get_storage() -> StorageService:
    if settings.STORAGE_BACKEND == "s3":
        try:
            return S3StorageService()
        except Exception:
            return LocalStorageService()
    return LocalStorageService()

storage_service = get_storage()
