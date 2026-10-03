#
# binio.py
#
# This file is part of the reversi program
# http://github.com/rcrr/reversi
# 
# Author Roberto Corradini mailto:rob_corradini@yahoo.it
# Copyright 2026 Roberto Corradini. All rights reserved.
#
# License
# 
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3, or (at your option) any
# later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA
# or visit the site <http://www.gnu.org/licenses/>.
#

"""
binio - minimal, C/Rust-interoperable binary I/O.

This module reads and writes flat binary files using only the standard
library (``struct``, ``hashlib``) plus ``numpy``. It is designed to be
trivially interoperable with C/Rust code using plain ``fwrite``/``fread``.

Design choices
--------------
* **Byte order**: fixed little-endian (``<``). A file written on any machine
  reads identically on any other machine, regardless of native endianness.
* **Framing**: every value is wrapped between two identical 32-bit MAGIC
  markers (one before, one after). The MAGIC is a *framing / version* check:
  if the reader is out of sync (wrong read order, version mismatch, truncation)
  it fails fast and loudly. It is NOT an integrity check of the payload bytes.
* **Integrity**: whole-file integrity is handled separately via a SHA3-256
  sidecar file (see ``write_sha3_256_sidecar`` / ``verify_sha3_256_sidecar``),
  written in the standard ``sha3_256sum`` format.
* **Ordered / manual**: there is no self-describing table of contents. The
  reader must call the read methods in the exact same order the writer used.
  This keeps the layout 100% predictable for the C/Rust side.

On-disk layout of each record
-----------------------------
Scalar (u8/i8/u32/i32/u64/i64/f32/f64)::

    [MAGIC u32][value][MAGIC u32]

String::

    [MAGIC u32][length u64][UTF-8 bytes ...][MAGIC u32]

    ``length`` is the number of *bytes* (UTF-8 encoded), not characters.

Numpy array::

    [MAGIC u32][type_code u8][ndim u64][shape[0] u64]...[shape[ndim-1] u64]
    [raw data, C-contiguous, little-endian][MAGIC u32]

    ``type_code`` is one of the TYPE_* constants below. Data is stored
    C-contiguous (row-major), little-endian, exactly ``prod(shape) * itemsize``
    bytes.

Example
-------
    >>> import numpy as np
    >>> with BinaryWriter("data.bin") as w:   # checksum=True by default
    ...     w.write_string("description")
    ...     w.write_u32(42)
    ...     w.write_f64(3.14159)
    ...     w.write_array(np.arange(10, dtype=np.int64))
    >>> # On close, data.bin.SHA3-256 was written automatically (no re-read).
    >>> assert verify_sha3_256_sidecar("data.bin")
    >>> with BinaryReader("data.bin") as r:
    ...     desc = r.read_string()
    ...     n = r.read_u32()
    ...     pi = r.read_f64()
    ...     arr = r.read_array()
"""

from __future__ import annotations

import hashlib
import io
import os
import struct
from collections import namedtuple

import numpy as np
import lz4.frame

__all__ = [
    'DEFAULT_MAGIC',
    'DEFAULT_FILE_SIGNATURE',
    'FileHeader',
    'BinaryFormatError',
    'BinaryWriter',
    'BinaryReader',
    'compute_sha3_256',
    'write_sha3_256_sidecar',
    'verify_sha3_256_sidecar',
]

# Result of BinaryReader.read_header().
FileHeader = namedtuple("FileHeader", ["description", "version"])

# Default framing marker. Little-endian bytes spell b"BIN1".
DEFAULT_MAGIC = 0x314E4942

# File-level signature stored inside the header record. Little-endian bytes
# spell b"BIOH". It identifies the file as a binio file and lets read_header()
# fail fast on a foreign or corrupted file.
DEFAULT_FILE_SIGNATURE = 0x484F4942

# Numpy dtype <-> on-disk type code. These integer codes are the contract
# shared with the C/Rust side; keep them stable across versions.
TYPE_INT8 = 1
TYPE_UINT8 = 2
TYPE_INT16 = 3
TYPE_UINT16 = 4
TYPE_INT32 = 5
TYPE_UINT32 = 6
TYPE_INT64 = 7
TYPE_UINT64 = 8
TYPE_FLOAT32 = 9
TYPE_FLOAT64 = 10

# Canonical dtype name -> type code.
_CODE_BY_NAME = {
    "int8": TYPE_INT8,
    "uint8": TYPE_UINT8,
    "int16": TYPE_INT16,
    "uint16": TYPE_UINT16,
    "int32": TYPE_INT32,
    "uint32": TYPE_UINT32,
    "int64": TYPE_INT64,
    "uint64": TYPE_UINT64,
    "float32": TYPE_FLOAT32,
    "float64": TYPE_FLOAT64,
}

# Type code -> little-endian numpy dtype.
_DTYPE_BY_CODE = {
    TYPE_INT8: np.dtype("<i1"),
    TYPE_UINT8: np.dtype("<u1"),
    TYPE_INT16: np.dtype("<i2"),
    TYPE_UINT16: np.dtype("<u2"),
    TYPE_INT32: np.dtype("<i4"),
    TYPE_UINT32: np.dtype("<u4"),
    TYPE_INT64: np.dtype("<i8"),
    TYPE_UINT64: np.dtype("<u8"),
    TYPE_FLOAT32: np.dtype("<f4"),
    TYPE_FLOAT64: np.dtype("<f8"),
}

# Pre-compiled struct formats (little-endian, standard sizes, no padding).
_MAGIC = struct.Struct("<I")
_U8 = struct.Struct("<B")
_I8 = struct.Struct("<b")
_U16 = struct.Struct("<H")
_I16 = struct.Struct("<h")
_U32 = struct.Struct("<I")
_I32 = struct.Struct("<i")
_U64 = struct.Struct("<Q")
_I64 = struct.Struct("<q")
_F32 = struct.Struct("<f")
_F64 = struct.Struct("<d")


class BinaryFormatError(Exception):
    """
    Raised when the data on disk does not match the expected format
    (e.g. a MAGIC marker mismatch, truncated file, or unknown type code).
    """
    pass


def _open_arg(file, mode):
    """
    Return (file_object, owns_it) for a path or an open binary file.

    Args:
        file: A path (str / os.PathLike) or an open binary file.
        mode (str): The open mode, used when ``file`` is a path.

    Returns:
        (file_object, owns_it): ``owns_it`` is True only when the file was
        opened here from a path.
    """
    if isinstance(file, (str, os.PathLike)):
        return open(file, mode), True
    return file, False


class BinaryWriter:
    """
    Write framed binary records. Accepts a path or an open binary file.

    When given a path it owns the file and closes it on ``close()`` / context
    exit; when given a file object it never closes it.

    Checksum service (``checksum=True`` by default): the SHA3-256 of the file is
    computed incrementally as data is written. On ``close()``, if the file was
    opened by path, a ``<path><checksum_suffix>`` sidecar is written from the
    in-memory digest -- no extra API call and no re-read of the file. When the
    target is a file object (no path), the digest is still available via the
    ``sha3_256_hexdigest`` property. With ``checksum=False`` no hashing happens;
    you may still create a sidecar afterwards with ``write_sha3_256_sidecar``.

    ``checksum_suffix`` must be non-empty: with an empty suffix the
    ``<path><suffix>`` sidecar would BE the content file, which ``close()``
    truncates and overwrites. Use ``checksum=False`` (not an empty suffix)
    to skip the sidecar. Raises ``ValueError`` if empty.

    Compression service (``compressed=True``): every write goes into an
    in-memory buffer; ``close()`` LZ4-frame-compresses it and flushes the
    result to the target. With ``checksum=True`` the digest is over the
    COMPRESSED bytes and the hash is updated only at ``close()``: before
    close, ``sha3_256_hexdigest`` is the empty-stream digest.
    """

    def __init__(
        self,
        file,
        *,
        magic: int = DEFAULT_MAGIC,
        signature: int = DEFAULT_FILE_SIGNATURE,
        checksum: bool = True,
        checksum_suffix: str = ".SHA3-256",
        compressed: bool = False,
    ):
        """
        Open the write target (a path or an open binary file) and configure
        the framing, the checksum service and the compression service.

        Args:
            file: A path (str / os.PathLike) or an open binary file.
            magic (int): The framing marker (``DEFAULT_MAGIC``).
            signature (int): The file signature stored in the header
                (``DEFAULT_FILE_SIGNATURE``).
            checksum (bool): When True (default), the SHA3-256 is computed
                incrementally and a sidecar is written on close (path-based
                targets only).
            checksum_suffix (str): The sidecar suffix appended to the path;
                must be non-empty.
            compressed (bool): When True, buffer all writes in memory,
                LZ4-frame-compress and flush on close.

        Raises:
            ValueError: If ``checksum_suffix`` is empty (the sidecar would BE
            the content file, which close truncates and overwrites).
        """
        if not checksum_suffix:
            raise ValueError(
                "checksum_suffix must be a non-empty string (an empty "
                "suffix would overwrite the content file on close; use "
                "checksum=False to disable the sidecar)")
        self._path = os.fspath(file) if isinstance(file, (str, os.PathLike)) else None
        self._actual_f = None
        self._compressed = compressed
        self.magic = magic
        self.signature = signature
        self._magic_bytes = _MAGIC.pack(magic)
        self._hash = hashlib.sha3_256() if checksum else None
        self._checksum_suffix = checksum_suffix
        self._closed = False

        if self._compressed:
            # Always write to an in-memory buffer first; the compression
            # happens at close.
            self._f = io.BytesIO()
            self._own = True
            # If a file object was passed, keep it: the compressed bytes are
            # written to it at close.
            if self._path is None:
                self._actual_f = file
        else:
            if self._path is not None:
                self._f = open(file, "wb")
                self._own = True
            else:
                self._f = file
                self._own = False

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    @property
    def sha3_256_hexdigest(self) -> str:
        """
        Return the SHA3-256 hex digest of everything written so far (the
        incremental hash; no re-read).

        In ``compressed`` mode the hash is updated only at ``close()`` over
        the compressed bytes: before close, the digest is the empty-stream
        digest.

        Raises:
            ValueError: If this writer was opened with ``checksum=False``.
        """
        if self._hash is None:
            raise ValueError("checksum service is disabled for this writer")
        return self._hash.hexdigest()

    def close(self):
        if self._closed:
            return
        self._closed = True
        try:
            if self._compressed:
                uncompressed_data = self._f.getvalue()
                compressed_data = lz4.frame.compress(uncompressed_data)

                if self._path is not None:
                    with open(self._path, "wb") as f_out:
                        f_out.write(compressed_data)
                elif self._actual_f is not None:
                    self._actual_f.write(compressed_data)

                if self._hash is not None:
                    self._hash.update(compressed_data)
            else:
                self._f.flush()

            if self._hash is not None and self._path is not None:
                sidecar = self._path + self._checksum_suffix
                name = os.path.basename(self._path)
                with open(sidecar, "w", encoding="ascii") as f:
                    f.write(f"{self._hash.hexdigest()}  {name}\n")
        finally:
            if self._own and hasattr(self._f, 'close') and not self._f.closed:
                self._f.close()

    # -- framing ---------------------------------------------------------

    def _write(self, data: bytes):
        """
        Write raw bytes and feed them to the incremental hash (if enabled).
        """
        self._f.write(data)
        if self._hash is not None and not self._compressed:
            self._hash.update(data)

    def _open_frame(self):
        self._write(self._magic_bytes)

    def _close_frame(self):
        self._write(self._magic_bytes)

    def _scalar(self, st: struct.Struct, value):
        self._open_frame()
        self._write(st.pack(value))
        self._close_frame()

    # -- header ----------------------------------------------------------

    def write_header(self, description: str, version: int, *, encoding: str = "utf-8"):
        """
        Write the file header:
        [MAGIC][signature u32][version u32][length u64][description bytes][MAGIC].

        Intended as the very first record of a file. ``version`` is an
        application-defined format version used to reject incompatible files.

        Args:
            description (str): The human-readable file description.
            version (int): The application-defined format version.
            encoding (str): The text encoding of ``description`` (default utf-8).
        """
        data = description.encode(encoding)
        self._open_frame()
        self._write(_U32.pack(self.signature))
        self._write(_U32.pack(version))
        self._write(_U64.pack(len(data)))
        self._write(data)
        self._close_frame()

    # -- scalars ---------------------------------------------------------

    def write_u8(self, value: int): self._scalar(_U8, value)
    def write_i8(self, value: int): self._scalar(_I8, value)
    def write_u16(self, value: int): self._scalar(_U16, value)
    def write_i16(self, value: int): self._scalar(_I16, value)
    def write_u32(self, value: int): self._scalar(_U32, value)
    def write_i32(self, value: int): self._scalar(_I32, value)
    def write_u64(self, value: int): self._scalar(_U64, value)
    def write_i64(self, value: int): self._scalar(_I64, value)
    def write_f32(self, value: float): self._scalar(_F32, value)
    def write_f64(self, value: float): self._scalar(_F64, value)

    # -- string ----------------------------------------------------------

    def write_string(self, value: str, *, encoding: str = "utf-8"):
        """
        Write a string as [MAGIC][length u64][bytes][MAGIC].

        ``length`` is the encoded byte count, NOT the character count.

        Args:
            value (str): The string to write.
            encoding (str): The text encoding (default utf-8).
        """
        data = value.encode(encoding)
        self._open_frame()
        self._write(_U64.pack(len(data)))
        self._write(data)
        self._close_frame()

    # -- numpy array -----------------------------------------------------

    def write_array(self, array: np.ndarray):
        """
        Write a numpy array as
        [MAGIC][type_code u8][ndim u64][shape... u64][data][MAGIC].

        The data is stored C-contiguous and little-endian, exactly
        ``prod(shape) * itemsize`` bytes; any input dtype is converted to its
        canonical little-endian dtype, and non-contiguous inputs are
        serialized in C order.

        Args:
            array (np.ndarray): The array to write.

        Raises:
            BinaryFormatError: If the dtype has no TYPE_* code (complex,
            bool, object, ...).
        """
        array = np.asarray(array)
        name = array.dtype.name
        code = _CODE_BY_NAME.get(name)
        if code is None:
            raise BinaryFormatError(f"unsupported array dtype: {name!r}")

        # Ensure little-endian dtype while preserving ndim (including 0-d).
        # tobytes(order="C") below serializes in C order for any memory layout,
        # so we must NOT use ascontiguousarray here (it promotes 0-d to 1-d).
        le_dtype = _DTYPE_BY_CODE[code]
        array = array.astype(le_dtype, copy=False)

        self._open_frame()
        self._write(_U8.pack(code))
        self._write(_U64.pack(array.ndim))
        for dim in array.shape:
            self._write(_U64.pack(dim))
        self._write(array.tobytes(order="C"))
        self._close_frame()


class BinaryReader:
    """
    Read framed binary records written by :class:`BinaryWriter`.

    Methods must be called in the same order the values were written. With
    ``compressed=True`` the whole file is LZ4-frame-decompressed into memory
    first.
    """

    def __init__(
        self,
        file,
        *,
        magic: int = DEFAULT_MAGIC,
        signature: int = DEFAULT_FILE_SIGNATURE,
        compressed: bool = False,
    ):
        """
        Open the read target (a path or an open binary file) and configure
        the framing.

        Args:
            file: A path (str / os.PathLike) or an open binary file.
            magic (int): The framing marker (``DEFAULT_MAGIC``).
            signature (int): The file signature expected in the header
                (``DEFAULT_FILE_SIGNATURE``).
            compressed (bool): When True, LZ4-frame-decompress the whole
                file into memory before reading.

        Raises:
            BinaryFormatError: If the LZ4 decompression fails
            (``compressed=True``).
        """
        self._compressed = compressed

        if self._compressed:
            f, own = _open_arg(file, "rb")
            # An in-memory file object (e.g. BytesIO) may not start at 0:
            # reset it.
            if not own and hasattr(f, 'seek'):
                f.seek(0)
            compressed_data = f.read()
            if own:
                f.close()
            try:
                uncompressed_data = lz4.frame.decompress(compressed_data)
            except Exception as e:
                raise BinaryFormatError(f"LZ4 decompression failed: {e}")
            self._f = io.BytesIO(uncompressed_data)
            self._own = True
        else:
            self._f, self._own = _open_arg(file, "rb")

        self.magic = magic
        self.signature = signature

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def close(self):
        if self._own and not self._f.closed:
            self._f.close()

    # -- low level -------------------------------------------------------

    def _read_exact(self, n: int) -> bytes:
        """
        Read exactly ``n`` bytes or raise; handles short reads.
        """
        buf = self._f.read(n)
        if len(buf) < n:
            chunks = [buf]
            remaining = n - len(buf)
            while remaining > 0:
                more = self._f.read(remaining)
                if not more:
                    raise BinaryFormatError(
                        f"unexpected EOF: wanted {n} bytes, got {n - remaining}"
                    )
                chunks.append(more)
                remaining -= len(more)
            buf = b"".join(chunks)
        return buf

    def _expect_magic(self, where: str):
        (value,) = _MAGIC.unpack(self._read_exact(_MAGIC.size))
        if value != self.magic:
            raise BinaryFormatError(
                f"MAGIC mismatch {where}: expected 0x{self.magic:08X}, "
                f"got 0x{value:08X} (wrong read order, version, or corruption)"
            )

    def _scalar(self, st: struct.Struct):
        self._expect_magic("before value")
        (value,) = st.unpack(self._read_exact(st.size))
        self._expect_magic("after value")
        return value

    # -- header ----------------------------------------------------------

    def read_header(self, *, encoding: str = "utf-8") -> FileHeader:
        """
        Read the file header written by :meth:`BinaryWriter.write_header`.

        Args:
            encoding (str): The text encoding of the stored description
                (default utf-8).

        Returns:
            FileHeader: (description, version).

        Raises:
            BinaryFormatError: If the signature does not match (foreign
            file).
        """
        self._expect_magic("before header")
        (sig,) = _U32.unpack(self._read_exact(_U32.size))
        if sig != self.signature:
            raise BinaryFormatError(
                f"file signature mismatch: expected 0x{self.signature:08X}, "
                f"got 0x{sig:08X} (not a binio file or wrong format)"
            )
        (version,) = _U32.unpack(self._read_exact(_U32.size))
        (length,) = _U64.unpack(self._read_exact(_U64.size))
        data = self._read_exact(length)
        self._expect_magic("after header")
        return FileHeader(description=data.decode(encoding), version=version)

    # -- scalars ---------------------------------------------------------

    def read_u8(self) -> np.uint8: return np.uint8(self._scalar(_U8))
    def read_i8(self) -> np.int8: return np.int8(self._scalar(_I8))
    def read_u16(self) -> np.uint16: return np.uint16(self._scalar(_U16))
    def read_i16(self) -> np.int16: return np.int16(self._scalar(_I16))
    def read_u32(self) -> np.uint32: return np.uint32(self._scalar(_U32))
    def read_i32(self) -> np.int32: return np.int32(self._scalar(_I32))
    def read_u64(self) -> np.uint64: return np.uint64(self._scalar(_U64))
    def read_i64(self) -> np.int64: return np.int64(self._scalar(_I64))
    def read_f32(self) -> np.float32: return np.float32(self._scalar(_F32))
    def read_f64(self) -> np.float64: return np.float64(self._scalar(_F64))

    # -- string ----------------------------------------------------------

    def read_string(self, *, encoding: str = "utf-8") -> str:
        """
        Read a string written by ``BinaryWriter.write_string``.

        Args:
            encoding (str): The text encoding of the stored bytes
                (default utf-8).

        Returns:
            str: The decoded string.
        """
        self._expect_magic("before string")
        (length,) = _U64.unpack(self._read_exact(_U64.size))
        data = self._read_exact(length)
        self._expect_magic("after string")
        return data.decode(encoding)

    # -- numpy array -----------------------------------------------------

    def read_array(self) -> np.ndarray:
        """
        Read an array written by ``BinaryWriter.write_array``.

        Returns:
            np.ndarray: An owned, writable C-contiguous little-endian array
            of the stored shape and dtype.

        Raises:
            BinaryFormatError: On an unknown on-disk type code.
        """
        self._expect_magic("before array")
        (code,) = _U8.unpack(self._read_exact(_U8.size))
        dtype = _DTYPE_BY_CODE.get(code)
        if dtype is None:
            raise BinaryFormatError(f"unknown array type code: {code}")

        (ndim,) = _U64.unpack(self._read_exact(_U64.size))
        shape = tuple(
            _U64.unpack(self._read_exact(_U64.size))[0] for _ in range(ndim)
        )

        count = 1
        for dim in shape:
            count *= dim
        raw = self._read_exact(count * dtype.itemsize)
        self._expect_magic("after array")

        return np.frombuffer(raw, dtype=dtype).reshape(shape).copy()


# --- whole-file SHA3-256 integrity (sidecar) -----------------------------


def compute_sha3_256(path, *, chunk_size: int = 1 << 20) -> str:
    """
    Return the hex SHA3-256 digest of the whole file at ``path``.

    Args:
        path: The file to hash.
        chunk_size (int): The read chunk size in bytes (default 1 MiB).

    Returns:
        str: The 64-character lowercase hex digest.
    """
    h = hashlib.sha3_256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk_size), b""):
            h.update(block)
    return h.hexdigest()


def write_sha3_256_sidecar(path, *, suffix: str = ".SHA3-256") -> str:
    """
    Write a ``<path><suffix>`` sidecar in ``sha3_256sum`` format.

    The line is ``"<hexdigest>  <basename>\\n"`` so the file is verifiable
    with the standard ``sha3_256sum -c`` tool from the same directory.

    Args:
        path: The content file to hash.
        suffix (str): The sidecar suffix; must be non-empty.

    Returns:
        str: The sidecar path.

    Raises:
        ValueError: If ``suffix`` is empty (the sidecar would be the content
        file itself, which would be overwritten).
    """
    if not suffix:
        raise ValueError(
            "suffix must be a non-empty string (an empty suffix would "
            "overwrite the content file)")
    digest = compute_sha3_256(path)
    sidecar = os.fspath(path) + suffix
    name = os.path.basename(os.fspath(path))
    with open(sidecar, "w", encoding="ascii") as f:
        f.write(f"{digest}  {name}\n")
    return sidecar


def verify_sha3_256_sidecar(path, *, suffix: str = ".SHA3-256") -> bool:
    """
    Recompute the file's SHA3-256 and compare it to its sidecar.

    Args:
        path: The content file to verify.
        suffix (str): The sidecar suffix; must be non-empty.

    Returns:
        bool: True if the digests match.

    Raises:
        FileNotFoundError: If the sidecar is missing.
        BinaryFormatError: If the sidecar is malformed.
        ValueError: If ``suffix`` is empty (it would read the content file
        as its sidecar).
    """
    if not suffix:
        raise ValueError(
            "suffix must be a non-empty string (an empty suffix would "
            "read the content file as its sidecar)")
    sidecar = os.fspath(path) + suffix
    with open(sidecar, "r", encoding="ascii") as f:
        line = f.readline().strip()
    expected = line.split(None, 1)[0] if line else ""
    if len(expected) != 64:
        raise BinaryFormatError(f"malformed sidecar: {sidecar!r}")
    return compute_sha3_256(path).lower() == expected.lower()

