# Managed artifacts

`artifact.copyTo(absolutePath)` never overwrites an existing destination. Managed and render artifacts download into a private temporary file beside the destination, verify the file's size and SHA-256, and then publish it with an exclusive hard link. A file created by another process during the download is preserved and publication fails. Existing destinations are rejected before downloading.

When the filesystem explicitly reports that hard links are unsupported (`ENOTSUP`, `EOPNOTSUPP` or `ENOSYS`), the SDK exclusively creates the destination and copies the already verified local content through its open descriptor. This fallback is visible while copying and may leave an incomplete new destination if copying fails. Inspect that file before removing it or retry with a new destination. Permission errors, cross-device errors and existing files do not trigger the fallback; support for every removable or network filesystem is not implied.

Error cleanup only removes private staging files. It never deletes the caller's destination pathname, which another process may have replaced. Successful publication verifies that the destination still identifies the verified file. An unavailable file identity or a replaced destination fails verification.
