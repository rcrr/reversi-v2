#
# test_binio.py
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

#
#
# How to use the unit tests binio module.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests.
#
# time PERF=0 python3 -m unittest test.reversi.tools.test_binio
#

"""Unit tests for the binio module."""

import hashlib
import io
import os
import struct
import tempfile
import unittest

import numpy as np

import reversi.tools.binio as binio
from reversi.tools.binio import BinaryFormatError, BinaryReader, BinaryWriter
from test.reversi.paths import CUSTOM_TMP_BASE


class ScalarRoundTripTest(unittest.TestCase):
    """Each scalar type must survive a write/read round trip, at its bounds."""

    def _round_trip(self, write_name, read_name, values):
        buf = io.BytesIO()
        with BinaryWriter(buf) as w:
            writer = getattr(w, write_name)
            for v in values:
                writer(v)
        buf.seek(0)
        with BinaryReader(buf) as r:
            reader = getattr(r, read_name)
            for v in values:
                self.assertEqual(reader(), v)

    def test_u8(self):
        self._round_trip("write_u8", "read_u8", [0, 1, 127, 255])

    def test_i8(self):
        self._round_trip("write_i8", "read_i8", [-128, -1, 0, 127])

    def test_u16(self):
        self._round_trip("write_u16", "read_u16", [0, 1, 32768, 65535])

    def test_i16(self):
        self._round_trip("write_i16", "read_i16", [-32768, -1, 0, 32767])

    def test_u32(self):
        self._round_trip("write_u32", "read_u32", [0, 123456, 4_294_967_295])

    def test_i32(self):
        self._round_trip("write_i32", "read_i32", [-2_147_483_648, 0, 2_147_483_647])

    def test_u64(self):
        self._round_trip("write_u64", "read_u64", [0, 18_446_744_073_709_551_615])

    def test_i64(self):
        self._round_trip(
            "write_i64", "read_i64", [-9_223_372_036_854_775_808, 0, 9_223_372_036_854_775_807]
        )

    def test_f32(self):
        buf = io.BytesIO()
        with BinaryWriter(buf) as w:
            w.write_f32(3.5)  # exactly representable in float32
            w.write_f32(-0.0)
        buf.seek(0)
        with BinaryReader(buf) as r:
            self.assertEqual(r.read_f32(), 3.5)
            self.assertEqual(r.read_f32(), -0.0)

    def test_f64(self):
        buf = io.BytesIO()
        value = 2.718281828459045
        with BinaryWriter(buf) as w:
            w.write_f64(value)
        buf.seek(0)
        with BinaryReader(buf) as r:
            self.assertEqual(r.read_f64(), value)

    def test_f32_special_values(self):
        buf = io.BytesIO()
        with BinaryWriter(buf) as w:
            w.write_f32(float("nan"))
            w.write_f32(float("inf"))
            w.write_f32(float("-inf"))
        buf.seek(0)
        with BinaryReader(buf) as r:
            self.assertTrue(np.isnan(r.read_f32()))
            self.assertEqual(r.read_f32(), float("inf"))
            self.assertEqual(r.read_f32(), float("-inf"))

    def test_f64_special_values(self):
        buf = io.BytesIO()
        with BinaryWriter(buf) as w:
            w.write_f64(float("nan"))
            w.write_f64(float("inf"))
            w.write_f64(float("-inf"))
        buf.seek(0)
        with BinaryReader(buf) as r:
            self.assertTrue(np.isnan(r.read_f64()))
            self.assertEqual(r.read_f64(), float("inf"))
            self.assertEqual(r.read_f64(), float("-inf"))

    def test_f32_quantization(self):
        # 0.1 is not representable in float32: the read value must be the quantized float32, bit-exactly.
        buf = io.BytesIO()
        with BinaryWriter(buf) as w:
            w.write_f32(0.1)
        buf.seek(0)
        with BinaryReader(buf) as r:
            self.assertEqual(r.read_f32(), np.float32(0.1))


class StringTest(unittest.TestCase):
    def test_roundtrip_ascii(self):
        buf = io.BytesIO()
        with BinaryWriter(buf) as w:
            w.write_string("hello world")
        buf.seek(0)
        with BinaryReader(buf) as r:
            self.assertEqual(r.read_string(), "hello world")

    def test_roundtrip_multibyte_utf8(self):
        # Length must be measured in bytes, not characters.
        text = "città è caffè ☕ 日本語"
        buf = io.BytesIO()
        with BinaryWriter(buf) as w:
            w.write_string(text)
        buf.seek(0)
        with BinaryReader(buf) as r:
            self.assertEqual(r.read_string(), text)

    def test_empty_string(self):
        buf = io.BytesIO()
        with BinaryWriter(buf) as w:
            w.write_string("")
        buf.seek(0)
        with BinaryReader(buf) as r:
            self.assertEqual(r.read_string(), "")

    def test_byte_length_not_char_length(self):
        # "é" is one character but two bytes in UTF-8; the byte after it must still round-trip,
        # proving the length prefix counts bytes.
        buf = io.BytesIO()
        with BinaryWriter(buf) as w:
            w.write_string("é")
            w.write_u8(99)
        buf.seek(0)
        with BinaryReader(buf) as r:
            self.assertEqual(r.read_string(), "é")
            self.assertEqual(r.read_u8(), 99)

    def test_roundtrip_latin1(self):
        # A non-UTF-8 encoding must round-trip when used on both sides.
        text = "café à la mode"
        buf = io.BytesIO()
        with BinaryWriter(buf) as w:
            w.write_string(text, encoding="latin-1")
        buf.seek(0)
        with BinaryReader(buf) as r:
            self.assertEqual(r.read_string(encoding="latin-1"), text)


class ArrayTest(unittest.TestCase):
    DTYPES = [
        np.int8, np.uint8, np.int16, np.uint16,
        np.int32, np.uint32, np.int64, np.uint64,
        np.float32, np.float64,
    ]

    def _round_trip(self, arr):
        buf = io.BytesIO()
        with BinaryWriter(buf) as w:
            w.write_array(arr)
        buf.seek(0)
        with BinaryReader(buf) as r:
            out = r.read_array()
        self.assertEqual(out.dtype, arr.dtype)
        self.assertEqual(out.shape, arr.shape)
        self.assertTrue(np.array_equal(out, arr))
        return out

    def test_all_dtypes_1d(self):
        for dt in self.DTYPES:
            with self.subTest(dtype=dt):
                self._round_trip(np.arange(5).astype(dt))

    def test_multidimensional(self):
        self._round_trip(np.arange(24, dtype=np.float64).reshape(2, 3, 4))

    def test_empty_array(self):
        out = self._round_trip(np.array([], dtype=np.int32))
        self.assertEqual(out.size, 0)

    def test_zero_dimensional(self):
        self._round_trip(np.array(42, dtype=np.int64))

    def test_result_is_writable(self):
        # read_array must return an owned, writable array (not a buffer view).
        out = self._round_trip(np.arange(3, dtype=np.int32))
        out[0] = 123  # must not raise
        self.assertEqual(out[0], 123)

    def test_non_contiguous_input(self):
        # A transposed (F-contiguous) view must still be stored correctly.
        base = np.arange(6, dtype=np.int32).reshape(2, 3)
        self._round_trip(base.T)

    def test_big_endian_input_is_stored_little_endian(self):
        # A big-endian input must be converted to the canonical LE dtype.
        arr = np.arange(4, dtype=">i4")
        buf = io.BytesIO()
        with BinaryWriter(buf) as w:
            w.write_array(arr)
        buf.seek(0)
        with BinaryReader(buf) as r:
            out = r.read_array()
        self.assertEqual(out.dtype, np.dtype("<i4"))
        self.assertTrue(np.array_equal(out, arr))

    def test_unsupported_dtype_raises(self):
        buf = io.BytesIO()
        with BinaryWriter(buf) as w:
            with self.assertRaises(BinaryFormatError):
                w.write_array(np.array([1 + 2j], dtype=np.complex128))

    def test_unknown_type_code_raises(self):
        # A record with an unknown on-disk type code must raise.
        magic = struct.pack("<I", binio.DEFAULT_MAGIC)
        # type_code=99 (unknown), ndim=1, shape=(1,), 4 bytes of int32 payload
        payload = (struct.pack("<B", 99)
                   + struct.pack("<Q", 1)
                   + struct.pack("<Q", 1)
                   + b"\x00" * 4)
        frame = magic + payload + magic
        buf = io.BytesIO(frame)
        with BinaryReader(buf) as r:
            with self.assertRaises(BinaryFormatError):
                r.read_array()


class HeaderTest(unittest.TestCase):
    def test_roundtrip(self):
        buf = io.BytesIO()
        with BinaryWriter(buf) as w:
            w.write_header("my dataset", version=3)
            w.write_u32(7)
        buf.seek(0)
        with BinaryReader(buf) as r:
            header = r.read_header()
            self.assertEqual(header.description, "my dataset")
            self.assertEqual(header.version, 3)
            self.assertEqual(r.read_u32(), 7)

    def test_wrong_signature_raises(self):
        buf = io.BytesIO()
        with BinaryWriter(buf, signature=0xAAAAAAAA) as w:
            w.write_header("x", version=1)
        buf.seek(0)
        with BinaryReader(buf, signature=0xBBBBBBBB) as r:
            with self.assertRaises(BinaryFormatError):
                r.read_header()


class _OneByteAtATime:
    """
    A minimal file-object surrogate whose read(n) yields at most one byte per call (exercises the
    short-read stitching in _read_exact).
    """

    def __init__(self, data):
        self._buf = io.BytesIO(data)

    def read(self, n):
        return self._buf.read(min(n, 1))

    def close(self):
        self._buf.close()

    @property
    def closed(self):
        return self._buf.closed


class FramingTest(unittest.TestCase):
    def test_magic_mismatch_raises(self):
        # A reader configured with a different MAGIC must reject the stream.
        buf = io.BytesIO()
        with BinaryWriter(buf, magic=0x11111111) as w:
            w.write_u32(1)
        buf.seek(0)
        with BinaryReader(buf, magic=0x22222222) as r:
            with self.assertRaises(BinaryFormatError):
                r.read_u32()

    def test_wrong_read_order_detected(self):
        # Writing a string then reading it as a scalar: the frame's length prefix is consumed as the
        # "value", and the post-value MAGIC check then lands on the string payload and must fail
        # (framing protects against desync).
        buf = io.BytesIO()
        with BinaryWriter(buf) as w:
            w.write_string("x" * 100)
        buf.seek(0)
        with BinaryReader(buf) as r:
            with self.assertRaises(BinaryFormatError):
                r.read_u64()

    def test_truncated_file_raises(self):
        buf = io.BytesIO()
        with BinaryWriter(buf) as w:
            w.write_u64(123)
        truncated = buf.getvalue()[:-2]  # drop part of the trailing magic
        with BinaryReader(io.BytesIO(truncated)) as r:
            with self.assertRaises(BinaryFormatError):
                r.read_u64()

    def test_short_reads_are_stitched(self):
        # A stream whose read(n) returns fewer than n bytes at a time must be reassembled by the
        # reader's _read_exact.
        buf = io.BytesIO()
        with BinaryWriter(buf) as w:
            w.write_u64(1234)
        reader = BinaryReader(_OneByteAtATime(buf.getvalue()))
        try:
            self.assertEqual(reader.read_u64(), 1234)
        finally:
            reader.close()


class LayoutGoldenTest(unittest.TestCase):
    """
    The on-disk byte layout pinned against hand-built bytes: a writer/reader round-trip alone would
    be self-referential.
    """

    MAGIC = struct.pack("<I", binio.DEFAULT_MAGIC)

    def test_scalar_layout(self):
        buf = io.BytesIO()
        with BinaryWriter(buf) as w:
            w.write_u32(0x12345678)
        expected = self.MAGIC + struct.pack("<I", 0x12345678) + self.MAGIC
        self.assertEqual(buf.getvalue(), expected)

    def test_string_layout(self):
        buf = io.BytesIO()
        with BinaryWriter(buf) as w:
            w.write_string("ab")
        expected = self.MAGIC + struct.pack("<Q", 2) + b"ab" + self.MAGIC
        self.assertEqual(buf.getvalue(), expected)

    def test_header_layout(self):
        buf = io.BytesIO()
        with BinaryWriter(buf) as w:
            w.write_header("x", version=1)
        expected = (self.MAGIC
                    + struct.pack("<I", binio.DEFAULT_FILE_SIGNATURE)
                    + struct.pack("<I", 1)
                    + struct.pack("<Q", 1)
                    + b"x"
                    + self.MAGIC)
        self.assertEqual(buf.getvalue(), expected)


class Sha3_256SidecarTest(unittest.TestCase):
    """Tests for the standalone sidecar functions (checksum service off)."""

    @classmethod
    def setUpClass(cls):
        CUSTOM_TMP_BASE.mkdir(parents=True, exist_ok=True)

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.path = os.path.join(self.temp_dir.name, "data.bin")
        # checksum=False so no sidecar is auto-created; these tests drive the standalone
        # write_sha3_256_sidecar / verify_sha3_256_sidecar functions.
        with BinaryWriter(self.path, checksum=False) as w:
            w.write_header("integrity demo", version=1)
            w.write_array(np.arange(100, dtype=np.float64))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_write_and_verify(self):
        sidecar = binio.write_sha3_256_sidecar(self.path)
        self.assertTrue(os.path.exists(sidecar))
        self.assertTrue(binio.verify_sha3_256_sidecar(self.path))

    def test_sidecar_format_is_sha3_256sum_compatible(self):
        binio.write_sha3_256_sidecar(self.path)
        with open(self.path + ".SHA3-256", encoding="ascii") as f:
            line = f.readline().strip()
        digest, name = line.split("  ", 1)
        self.assertEqual(len(digest), 64)
        self.assertEqual(name, "data.bin")
        self.assertEqual(digest, binio.compute_sha3_256(self.path))

    def test_detects_corruption(self):
        binio.write_sha3_256_sidecar(self.path)
        # Flip one byte in the payload.
        with open(self.path, "r+b") as f:
            f.seek(20)
            original = f.read(1)
            f.seek(20)
            f.write(bytes([original[0] ^ 0xFF]))
        self.assertFalse(binio.verify_sha3_256_sidecar(self.path))

    def test_missing_sidecar_raises(self):
        with self.assertRaises(FileNotFoundError):
            binio.verify_sha3_256_sidecar(self.path)

    def test_malformed_sidecar_raises(self):
        with open(self.path + ".SHA3-256", "w", encoding="ascii") as f:
            f.write("not-a-digest  data.bin\n")
        with self.assertRaises(BinaryFormatError):
            binio.verify_sha3_256_sidecar(self.path)

    def test_write_empty_suffix_raises_and_content_intact(self):
        # An empty suffix points the sidecar at the content file itself: the call must be rejected
        # and the content must survive.
        with open(self.path, "rb") as f:
            before = f.read()
        with self.assertRaises(ValueError):
            binio.write_sha3_256_sidecar(self.path, suffix="")
        with open(self.path, "rb") as f:
            self.assertEqual(f.read(), before)

    def test_verify_empty_suffix_raises(self):
        binio.write_sha3_256_sidecar(self.path)
        with self.assertRaises(ValueError):
            binio.verify_sha3_256_sidecar(self.path, suffix="")


class AutoChecksumTest(unittest.TestCase):
    """The built-in incremental checksum service (checksum=True default)."""

    @classmethod
    def setUpClass(cls):
        CUSTOM_TMP_BASE.mkdir(parents=True, exist_ok=True)

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.path = os.path.join(self.temp_dir.name, "data.bin")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_sidecar_written_on_close(self):
        # No explicit sidecar call: it must appear automatically at close.
        with BinaryWriter(self.path) as w:
            w.write_header("auto", version=1)
            w.write_u32(7)
        self.assertTrue(os.path.exists(self.path + ".SHA3-256"))
        self.assertTrue(binio.verify_sha3_256_sidecar(self.path))

    def test_incremental_matches_reread(self):
        # The incrementally-computed digest must equal a full re-read.
        with BinaryWriter(self.path) as w:
            w.write_string("payload")
            w.write_array(np.arange(50, dtype=np.int64))
        with open(self.path + ".SHA3-256", encoding="ascii") as f:
            digest = f.readline().split()[0]
        self.assertEqual(digest, binio.compute_sha3_256(self.path))

    def test_disabled_writes_no_sidecar(self):
        with BinaryWriter(self.path, checksum=False) as w:
            w.write_u32(1)
        self.assertFalse(os.path.exists(self.path + ".SHA3-256"))

    def test_empty_checksum_suffix_raises_on_construction(self):
        # Fail fast, before the file is even opened (an empty suffix would clobber the content file
        # at close).
        with self.assertRaises(ValueError):
            BinaryWriter(self.path, checksum_suffix="")
        self.assertFalse(os.path.exists(self.path))

    def test_digest_property_on_file_object(self):
        # With a file object (no path) the digest is exposed, not a sidecar.
        buf = io.BytesIO()
        with BinaryWriter(buf) as w:
            w.write_u32(123)
            digest = w.sha3_256_hexdigest
        self.assertEqual(digest, hashlib.sha3_256(buf.getvalue()).hexdigest())

    def test_digest_property_raises_when_disabled(self):
        buf = io.BytesIO()
        with BinaryWriter(buf, checksum=False) as w:
            with self.assertRaises(ValueError):
                _ = w.sha3_256_hexdigest


class FullDocumentTest(unittest.TestCase):
    """End-to-end: header + mixed scalars + string + arrays, ordered read."""

    def test_mixed_document(self):
        buf = io.BytesIO()
        a32 = np.linspace(0, 1, 5, dtype=np.float32)
        a64 = np.arange(6, dtype=np.int64).reshape(2, 3)
        with BinaryWriter(buf) as w:
            w.write_header("mixed", version=2)
            w.write_string("payload")
            w.write_i16(-1000)
            w.write_u16(1000)
            w.write_f64(0.125)
            w.write_array(a32)
            w.write_array(a64)
        buf.seek(0)
        with BinaryReader(buf) as r:
            self.assertEqual(r.read_header(), ("mixed", 2))
            self.assertEqual(r.read_string(), "payload")
            self.assertEqual(r.read_i16(), -1000)
            self.assertEqual(r.read_u16(), 1000)
            self.assertEqual(r.read_f64(), 0.125)
            self.assertTrue(np.array_equal(r.read_array(), a32))
            self.assertTrue(np.array_equal(r.read_array(), a64))

class Lz4CompressionTest(unittest.TestCase):
    """Tests for the LZ4 whole-file compression feature (compressed=True)."""

    @classmethod
    def setUpClass(cls):
        CUSTOM_TMP_BASE.mkdir(parents=True, exist_ok=True)

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.path = os.path.join(self.temp_dir.name, "data_compressed.bin")
        self.uncompressed_path = os.path.join(self.temp_dir.name, "data_uncompressed.bin")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_roundtrip_with_path(self):
        a32 = np.linspace(0, 1, 100, dtype=np.float32)
        with BinaryWriter(self.path, compressed=True) as w:
            w.write_header("compressed", version=1)
            w.write_string("hello lz4")
            w.write_array(a32)

        self.assertTrue(os.path.exists(self.path))

        with BinaryReader(self.path, compressed=True) as r:
            header = r.read_header()
            self.assertEqual(header.description, "compressed")
            self.assertEqual(header.version, 1)
            self.assertEqual(r.read_string(), "hello lz4")
            out_arr = r.read_array()
            self.assertTrue(np.array_equal(out_arr, a32))

    def test_compression_actually_compresses(self):
        # Highly repetitive array to ensure compression is effective
        arr = np.zeros(10000, dtype=np.float64)
        arr[::100] = 1.0

        with BinaryWriter(self.path, compressed=True) as w:
            w.write_array(arr)

        with BinaryWriter(self.uncompressed_path, compressed=False) as w:
            w.write_array(arr)

        compressed_size = os.path.getsize(self.path)
        uncompressed_size = os.path.getsize(self.uncompressed_path)

        self.assertLess(compressed_size, uncompressed_size)

    def test_checksum_uses_compressed_bytes(self):
        arr = np.arange(1000, dtype=np.int32)
        with BinaryWriter(self.path, compressed=True) as w:
            w.write_header("chk", version=1)
            w.write_array(arr)

        self.assertTrue(os.path.exists(self.path + ".SHA3-256"))
        self.assertTrue(binio.verify_sha3_256_sidecar(self.path))

        # Verify the digest is for the compressed file, not the uncompressed payload
        with open(self.path + ".SHA3-256", encoding="ascii") as f:
            digest = f.readline().split()[0]
        self.assertEqual(digest, binio.compute_sha3_256(self.path))

    def test_roundtrip_with_file_object(self):
        buf = io.BytesIO()
        arr = np.arange(50, dtype=np.int32)
        with BinaryWriter(buf, compressed=True) as w:
            w.write_header("obj", version=2)
            w.write_array(arr)

        # We must reset to the beginning of the BytesIO for reading
        buf.seek(0)
        with BinaryReader(buf, compressed=True) as r:
            header = r.read_header()
            self.assertEqual(header.description, "obj")
            self.assertEqual(header.version, 2)
            out_arr = r.read_array()
            self.assertTrue(np.array_equal(out_arr, arr))

    def test_decompression_failure_raises(self):
        # Garbage that is not an LZ4 frame must raise BinaryFormatError.
        buf = io.BytesIO(b"this is not an LZ4 frame")
        with self.assertRaises(BinaryFormatError):
            BinaryReader(buf, compressed=True)

    def test_digest_property_spans_the_compressed_bytes(self):
        # Before close the compressed-mode digest is the empty-stream digest (the hash runs only at
        # close, over the compressed bytes); after close it is the digest of what the file object
        # now holds.
        buf = io.BytesIO()
        writer = BinaryWriter(buf, compressed=True)
        writer.write_array(np.arange(100, dtype=np.int32))
        self.assertEqual(writer.sha3_256_hexdigest, hashlib.sha3_256(b"").hexdigest())
        writer.close()
        self.assertEqual(writer.sha3_256_hexdigest, hashlib.sha3_256(buf.getvalue()).hexdigest())


if __name__ == "__main__":
    unittest.main()
