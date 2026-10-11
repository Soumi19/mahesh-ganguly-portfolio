# Automatic publication discovery — setup

This site uses GitHub Actions (daily 04:20 UTC) to search for new works and commit changes to `data/publications.json`. Homepage, Publications and Media load that JSON automatically. No paid server is required.

## Setup
1. Upload ALL files, including hidden `.github/workflows/publications.yml`, to the **root** of your GitHub Pages repository.
2. GitHub → Settings → Actions → General → Workflow permissions: **Read and write permissions** (if permitted by repository settings).
3. GitHub → Actions → **Discover Mahesh Ganguly publications** → **Run workflow**.
4. Open the run logs and inspect `data/publications.json` and `data/publication-review.json`.
5. Optional but strongly recommended: add the **correct verified** OpenAlex Author ID or ORCID in GitHub → Settings → Secrets and variables → Actions → **Variables** as `MAHESH_OPENALEX_AUTHOR_ID` or `MAHESH_ORCID`. Do not guess an author ID; verify publications belong to the same person.

## How discovery works
- Google News RSS searches name mentions; publisher page must explicitly credit Mahesh Ganguly in author metadata to auto-publish. Some Google News links or publisher sites cannot be read and will be missed.
- OpenAlex with a verified author ID / ORCID automatically publishes associated academic records.
- Crossref finds author-name-matched academic works, and Google Books finds name-matched books. **These go to `data/publication-review.json`**, not the live site, until identity is verified.
- The BRICS reprint is linked to the original Hindustan Times article instead of counted as a separate original work.
- Publisher blocks, delayed indexing, missing author metadata, and other people with the same name prevent guaranteed completeness. Google Scholar cannot be reliably scraped directly.

## Review queue
For a confirmed work in `data/publication-review.json`, copy its entry to `data/publications.json`, change `verified` to `true`, then remove it from the review queue. Verify authorship and publication details first. The discovery script will not add duplicates by URL or closely matching title.

## Additional sources
A truly broad catalogue requires verified identifiers (ORCID/OpenAlex), publisher author-page feeds, and periodic human review. The code is extensible; no crawler can guarantee that it finds every publication across the internet.
