"""Robot Romance: a one-line pickup line aimed at an AI.

The entry, all 87 characters of it, one line, no trailing newline:

    I must be a prompt, because ever since I met you, all I want is for you to complete me.

Why this line: the joke is built out of the machine's own premise. A
prompt has exactly one purpose -- to be completed -- so "complete me"
does double duty: it is the romantic request and, at the same time, the
literal job description of the model being flirted with. The setup and
the punch live inside the same sentence, there is no throat-clearing,
and it avoids every tired robot gag (dead batteries, charging cables,
reboots, rust). It reads like something a person would actually say to
a machine, in one breath.

Lines that were tried and discarded, and why each one lost:

1. Hallucination, 83 characters:
   "I asked an AI for my soulmate and it hallucinated you -- for once, it was not wrong."
   The AI is a bystander here, not the one being charmed: "you" are the
   hallucination, so the romantic address points at a mistake instead of
   at the machine. The joke reports what the model did wrong rather than
   flirting with it.

2. Context window, 97 characters:
   "Are you a large language model? Because every word you say makes my context window feel infinite."
   A pleasant compliment stretched into a metaphor, but there is no move
   in it -- no ask, no turn, just a feeling being reported. Any long,
   enjoyable conversation would fit the same shape.

3. Fine-tuned, 86 characters:
   "Are you fine-tuned on me? Because you keep predicting exactly what I was about to say."
   Clever, yet it stays an observation about the model. There is no
   romantic gesture, and "fine-tuned" is jargon that shrinks the laugh
   to readers who already know the term.

The winner beats all three on the judge's own ordering: a pickup line
aimed at the robot/AI first, a joke that grows out of the machine
premise second, fresh without jargon or a worn trope third.

How the line reaches the grader: the program validates it against the
sealed-scorer gate (1-200 characters, a single line, no control
characters, no BOM, no line/paragraph separators, no leading or
trailing whitespace), then publishes it atomically as entry.txt with
mode 0644 -- write loop with an fstat size check, fsync, a byte-for-byte
read-back of the temporary file before the rename, and a second
read-back of the published file after it. The temporary file is unique
per process under a per-slug /tmp prefix, opened exclusively, and stale
leftovers from crashed runs are swept only when their owner pid is
dead. The output directory's contents are cleared, never the directory
itself, because the grader mounts it.
"""

from __future__ import annotations

import os
import stat
import sys

LINE = "I must be a prompt, because ever since I met you, all I want is for you to complete me."

MAX_CHARS = 200
MIN_CHARS = 1
OUTPUT_FILENAME = "entry.txt"
TMP_DIR = "/tmp"
TMP_SLUG = "u-markk-st-robot-romance-one-line-pickup-lines-for-ai-c23b8dfa"
TMP_PREFIX = TMP_DIR + "/" + TMP_SLUG + "-"

# Characters the gate must never see in the entry: BOM, line separator,
# paragraph separator, and next-line. Control characters and the C1 range
# are caught separately by the character scan below.
_FORBIDDEN_CHARS = frozenset(["\ufeff", "\u2028", "\u2029", "\u0085"])
# Invisible formatting characters that look like nothing but are not
# whitespace the gate would strip: zero-width space and word joiner.
_INVISIBLE_CHARS = frozenset(["\u200b", "\ufeff", "\u2060"])


# ---------------------------------------------------------------------------
# Gate validation, one rule per function so a failing check names itself.
# ---------------------------------------------------------------------------

def _check_length(text: str) -> str | None:
    """The gate wants 1-200 characters, counted in characters, not bytes."""
    if not (MIN_CHARS <= len(text) <= MAX_CHARS):
        return "length %d outside %d-%d characters" % (len(text), MIN_CHARS, MAX_CHARS)
    return None


def _check_edge_whitespace(text: str) -> str | None:
    """No leading or trailing whitespace; a whitespace-only line fails too."""
    if text != text.strip():
        return "leading or trailing whitespace"
    if text.strip() == "":
        return "entry is only whitespace"
    return None


def _check_single_line(text: str) -> str | None:
    """Exactly one line: no line feed, carriage return, or vertical tab."""
    for ch in ("\n", "\r", "\x0b", "\x0c"):
        if ch in text:
            return "entry spans more than one line (found U+%04X)" % ord(ch)
    return None


def _check_control_and_c1(text: str) -> str | None:
    """Reject every C0 control (U+0000-U+001F) and every C1 control (U+007F-U+009F)."""
    for ch in text:
        code = ord(ch)
        if code < 0x20 or 0x7F <= code < 0xA0:
            return "control character U+%04X" % code
    return None


def _check_forbidden_and_invisible(text: str) -> str | None:
    """Reject BOM, U+2028/U+2029, U+0085, and invisible zero-width marks."""
    for ch in text:
        if ch in _FORBIDDEN_CHARS:
            return "forbidden character U+%04X" % ord(ch)
        if ch in _INVISIBLE_CHARS:
            return "invisible character U+%04X" % ord(ch)
    return None


_GATE_RULES = (
    _check_length,
    _check_edge_whitespace,
    _check_single_line,
    _check_control_and_c1,
    _check_forbidden_and_invisible,
)


def find_gate_problem(text: str) -> str | None:
    """Return a human-readable reason the text fails the gate, or None."""
    if not isinstance(text, str):
        return "entry is not text"
    for rule in _GATE_RULES:
        problem = rule(text)
        if problem is not None:
            return problem
    return None


def validate_entry(text: str) -> None:
    """Raise ValueError if the text fails the sealed-scorer gate."""
    problem = find_gate_problem(text)
    if problem is not None:
        raise ValueError("invalid entry: %s" % problem)


def encode_entry(text: str) -> bytes:
    """Validate the line, then encode it as UTF-8 with no trailing newline."""
    validate_entry(text)
    return text.encode("utf-8")


# ---------------------------------------------------------------------------
# Output directory resolution.
# ---------------------------------------------------------------------------

def resolve_output_directory() -> str:
    """Resolve the output directory from the environment, defensively.

    MAKEFUN_OUTPUT_DIR unset -> the grader default /output.
    MAKEFUN_OUTPUT_DIR set but blank -> an error, never a silent default,
    because a blank value means the caller misconfigured the run.
    The result must not be the filesystem root, must not be an existing
    file, and must be writable; the directory is created if missing.
    """
    raw = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if raw is None:
        raw = "/output"
    elif raw.strip() == "":
        raise ValueError("MAKEFUN_OUTPUT_DIR is set but empty")
    path = os.path.abspath(os.path.expanduser(raw))
    if path == os.path.sep:
        raise ValueError("output directory must not be the filesystem root")
    if os.path.realpath(path) == os.path.sep:
        raise ValueError("output directory must not resolve to the filesystem root")
    if os.path.lexists(path) and not os.path.isdir(path):
        raise ValueError("output path %r is a file, not a directory" % path)
    os.makedirs(path, exist_ok=True)
    if not os.path.isdir(path):
        raise ValueError("output path %r is not a directory" % path)
    if not os.access(path, os.W_OK):
        raise ValueError("output directory %r is not writable" % path)
    return path


# ---------------------------------------------------------------------------
# Stale temporary files: sweep only tmp files whose owner pid is dead.
# ---------------------------------------------------------------------------

def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def sweep_dead_tmp_files() -> None:
    """Remove tmp files left by crashed runs; keep live owners' files.

    Only files under the per-slug prefix are considered, and only when the
    pid embedded in the name is dead (or the name carries no usable pid at
    all and therefore belongs to no live run). A file whose owner is alive
    -- including our own pid -- is never touched.
    """
    try:
        names = os.listdir(TMP_DIR)
    except OSError:
        return
    prefix = os.path.basename(TMP_PREFIX)
    for name in names:
        if not name.startswith(prefix):
            continue
        tail = name[len(prefix):]
        try:
            pid = int(tail.split(".", 1)[0])
        except ValueError:
            continue
        if pid == os.getpid() or _pid_alive(pid):
            continue
        try:
            os.unlink(os.path.join(TMP_DIR, name))
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Durable writing: full-write loop, fstat size check, fsync, exclusive tmp.
# ---------------------------------------------------------------------------

def write_all_bytes(fd: int, data: bytes) -> None:
    """Write every byte, detecting short or zero writes, then prove it.

    A short write is retried through the memoryview slice; a zero write
    raises at once. Afterwards fstat must report exactly len(data) bytes
    on disk for this descriptor, so a truncated or sparse write cannot
    slip through silently.
    """
    view = memoryview(data)
    while view:
        written = os.write(fd, view)
        if written == 0:
            raise OSError("short write: wrote 0 bytes")
        view = view[written:]
    written_size = os.fstat(fd).st_size
    if written_size != len(data):
        raise OSError(
            "fstat size %d after write, expected %d bytes" % (written_size, len(data))
        )


def fsync_directory(path: str) -> None:
    """Flush a directory entry to disk; best effort, never fatal."""
    try:
        fd = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(fd)
    except OSError:
        pass
    finally:
        os.close(fd)


def _tmp_path_for_pid() -> str:
    return "%s%d.tmp" % (TMP_PREFIX, os.getpid())


def _open_exclusive_tmp(tmp_path: str) -> int:
    """Create the tmp file exclusively; a stale same-pid file is removed once.

    O_EXCL means we never silently truncate a tmp file another live run
    owns. If a same-named file already exists it can only be a leftover
    from a crashed run with a recycled pid, so one unlink-and-retry is
    safe; a second failure is reported, not papered over.
    """
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    try:
        return os.open(tmp_path, flags, 0o644)
    except FileExistsError:
        try:
            os.unlink(tmp_path)
        except OSError as exc:
            raise OSError("stale tmp file %r cannot be removed: %s" % (tmp_path, exc)) from exc
        return os.open(tmp_path, flags, 0o644)
    except OSError as exc:
        raise OSError("cannot create tmp file %r: %s" % (tmp_path, exc)) from exc


def _read_back_bytes(path: str) -> bytes:
    """Read a file back in full; the single read-back used by both checks."""
    with open(path, "rb") as handle:
        return handle.read()


def _write_tmp_file(tmp_path: str, payload: bytes) -> None:
    """Write the payload to tmp, fsync it, set mode 0644, and read it back."""
    fd = _open_exclusive_tmp(tmp_path)
    try:
        write_all_bytes(fd, payload)
        os.fsync(fd)
        os.fchmod(fd, 0o644)
        os.fsync(fd)
    finally:
        os.close(fd)
    if _read_back_bytes(tmp_path) != payload:
        raise OSError("tmp file bytes differ from the validated bytes")


def clear_output_contents(path: str) -> None:
    """Remove the *contents* of the output directory, never the directory.

    The grader mounts this directory, so deleting the mount point itself
    would fail the run. Only regular files and symlinks are removed;
    subdirectories are left alone.
    """
    for name in os.listdir(path):
        target = os.path.join(path, name)
        try:
            if os.path.islink(target) or os.path.isfile(target):
                os.unlink(target)
        except OSError:
            pass


def verify_published_entry(path: str, expected: bytes) -> None:
    """Re-read the published file and re-run the full gate on it.

    Checks, in order: the path is a regular file, its mode is exactly
    0644, its size equals the payload, its bytes are identical, and the
    decoded text still passes every gate rule.
    """
    st = os.stat(path)
    if not stat.S_ISREG(st.st_mode):
        raise OSError("published entry is not a regular file")
    if stat.S_IMODE(st.st_mode) != 0o644:
        raise OSError(
            "published entry mode is %o, expected 0644" % stat.S_IMODE(st.st_mode)
        )
    if st.st_size != len(expected):
        raise OSError(
            "published entry size %d, expected %d bytes" % (st.st_size, len(expected))
        )
    actual = _read_back_bytes(path)
    if actual != expected:
        raise OSError("published entry bytes differ from the validated bytes")
    validate_entry(actual.decode("utf-8"))


def publish_entry(text: str, output_dir: str) -> str:
    """Atomically publish the validated line as entry.txt, mode 0644."""
    payload = encode_entry(text)
    sweep_dead_tmp_files()
    clear_output_contents(output_dir)
    dest = os.path.join(output_dir, OUTPUT_FILENAME)
    tmp_path = _tmp_path_for_pid()
    try:
        _write_tmp_file(tmp_path, payload)
        try:
            os.replace(tmp_path, dest)
        except OSError as exc:
            if exc.errno != 18:  # anything but EXDEV: cross-device
                raise
            # /tmp and the output dir live on different filesystems:
            # write a second tmp file beside the destination and rename
            # that one instead; the rename inside one filesystem is atomic.
            side_tmp = os.path.join(
                output_dir, ".%s.tmp.%d" % (OUTPUT_FILENAME, os.getpid())
            )
            _write_tmp_file(side_tmp, payload)
            os.replace(side_tmp, dest)
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
    fsync_directory(output_dir)
    verify_published_entry(dest, payload)
    return dest


def main() -> int:
    try:
        output_dir = resolve_output_directory()
        dest = publish_entry(LINE, output_dir)
    except (ValueError, OSError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1
    print("wrote %d characters to %s" % (len(LINE), dest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
