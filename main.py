from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup
import httpx

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/api/outline")
async def outline(country: str):
    # Build the Wikipedia URL
    url = f"https://en.wikipedia.org/wiki/{country.replace(' ', '_')}"
    # Fetch the page asynchronously
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
    if r.status_code != 200:
        raise HTTPException(404, f"Wikipedia page not found: {url}")

    # Parse HTML
    soup = BeautifulSoup(r.text, "html.parser")
    # Remove the Table of Contents to avoid duplicate "Contents" heading
    toc = soup.find("div", id="toc")
    if toc:
        toc.decompose()
    # Scope to bodyContent if present
    content = soup.find("div", id="bodyContent") or soup
    # Extract all headings H1 through H6
    headings = content.find_all(["h1","h2","h3","h4","h5","h6"])

    # Build Markdown outline
    md_lines = ["## Contents", "", f"# {country}", ""]
    for h in headings:
        level = int(h.name[1])  # heading level from tag name
        indent = "  " * (level - 1)
        text = h.get_text(strip=True)
        md_lines.append(f"{indent}{'#'*level} {text}")

    outline_md = "\n".join(md_lines)
    return {"outline": outline_md}
