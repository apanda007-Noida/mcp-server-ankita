# Edge Cases and Corner Cases

This document outlines potential edge cases and corner cases for the Automated Weekly App Review Pulse system, grouped by architectural module. Identifying these upfront ensures robust error handling and failure recovery mechanisms.

---

## 1. Data Ingestion (Google Play Scraper)
* **Play Store DOM Changes**: Google frequently updates the Play Store web interface. If the DOM changes, the scraper could break, resulting in zero fetched reviews.
  - *Mitigation*: Implement alerts for "zero reviews fetched" to quickly identify broken scrapers.
* **IP Blocking / Rate Limiting**: Fetching hundreds or thousands of reviews may trigger Google's bot protection, leading to HTTP 429 (Too Many Requests) or CAPTCHA blocks.
  - *Mitigation*: Implement exponential backoff, request delays, and user-agent rotation.
* **Massive Volume Spikes**: A viral bug could result in 10,000+ reviews in a single week, potentially causing Out-Of-Memory (OOM) errors during local processing or exceeding LLM token limits.
  - *Mitigation*: Implement a hard cap/sampling strategy (e.g., process a maximum of 2,000 randomly sampled reviews per run if volume exceeds the threshold).
* **Non-English & "Hinglish" Reviews**: Users may write reviews in regional languages or mixed scripts (e.g., Hindi written in English script).
  - *Mitigation*: Decide whether to filter out non-English text or rely on multilingual embedding models and LLMs.
* **Empty / Emoji-Only Text**: Users leaving 1-star ratings with no text or just angry emojis.
  - *Mitigation*: Filter out reviews that contain less than 'N' alphanumeric characters before passing to the reasoning engine.

## 2. Reasoning & Analysis (Clustering & LLM)
* **PII Scrubbing Misses**: A user drops a highly sensitive piece of data (e.g., PAN card number, bank account number) in a review, and regex/NER scrubbers miss it.
  - *Mitigation*: Use aggressive, layered PII masking and instruct the LLM specifically to redact personal info in outputs.
* **Quote Validation Failures (Formatting/Unicode)**: The LLM extracts a real quote but alters smart quotes (`“` to `"`) or trims whitespace, causing the strict verbatim validation function to fail and reject the quote.
  - *Mitigation*: Use a fuzzy match string distance algorithm (like Levenshtein distance with a very tight threshold) or normalize strings before comparing.
* **LLM Token Context Exceeded**: Even after clustering, the summary prompt to the LLM exceeds the context window.
  - *Mitigation*: Chunk the clusters and run summarization in parallel, followed by a final map-reduce summarization step.
* **"Everything is Noise" (Clustering Failure)**: HDBSCAN classifies 95% of the reviews as noise (`Cluster -1`) because the feedback is too varied and lacks density.
  - *Mitigation*: Fallback to a broader clustering algorithm (like K-Means) if HDBSCAN fails to find dense groups.

## 3. Human-Visible Delivery (MCP Servers)
* **OAuth Credential Expiry**: The refresh tokens stored in the MCP server configurations expire, are revoked by Google Workspace admins, or require re-authentication.
  - *Mitigation*: Graceful failure reporting so developers are immediately pinged to re-authenticate the MCP server.
* **Google API Downtime**: Google Docs or Gmail APIs return 500/503 errors during the scheduled run.
  - *Mitigation*: Implement retry logic within the MCP tools. If it fails permanently, alert the admin without marking the weekly run as "Complete."
* **Idempotency Race Conditions / Network Timeouts**: The agent tells the Docs MCP to append the report. The Google API succeeds, but the network connection drops before the agent gets the `200 OK`. The agent retries, resulting in duplicate sections.
  - *Mitigation*: Ensure the Docs MCP tool checks the document for the exact `ISO Week Heading` *before* attempting the append on every single request.
* **Deep Link Anchor Instability**: Google Docs creates heading IDs automatically. If the heading format changes slightly, the deep link sent in the Gmail teaser might lead to the top of the document instead of the specific section.
  - *Mitigation*: Explicitly fetch the generated `headingId` from the Google Docs API response after appending, and use that specific ID to format the Gmail link.

## 4. Orchestration
* **Time Zone Mishaps (IST vs UTC)**: The cron job runs on UTC, but ISO week boundaries are calculated differently, or reviews are stamped with a different timezone, causing reviews to be double-counted or missed at the edges of the week.
  - *Mitigation*: Standardize all timestamps to UTC at the ingestion layer and only convert to IST for the final human-readable report.
* **Stuck Runs**: A run hangs indefinitely during the LLM summarization phase due to an API timeout that isn't caught.
  - *Mitigation*: Wrap the entire scheduled execution in a timeout wrapper (e.g., kill and alert if runtime > 30 minutes).
