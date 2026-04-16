import httpx
import aiofiles
from pathlib import Path


class MinerUService:
    """
    Wraps the MinerU API for document parsing (PDF/DOCX -> Markdown).
    For .md files, returns content directly without calling the API.
    """

    def __init__(self, api_key: str | None = None, base_url: str = "https://mineru.net/api/v4"):
        self.api_key = api_key
        self.base_url = base_url

    async def parse_file(self, file_path: str) -> str:
        path = Path(file_path)
        suffix = path.suffix.lower()

        # Markdown files: read directly
        if suffix == ".md":
            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                return await f.read()

        # PDF/DOCX: call MinerU API
        if not self.api_key:
            raise ValueError("MinerU API key not configured")

        async with aiofiles.open(file_path, "rb") as f:
            file_bytes = await f.read()

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self.base_url}/extract/file",
                headers={"Authorization": f"Bearer {self.api_key}"},
                files={"file": (path.name, file_bytes, "application/octet-stream")},
                data={"output_format": "markdown"},
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("markdown", "")
