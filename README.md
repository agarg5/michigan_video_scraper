# Overview

This project processes video metadata and performs automated transcription of video content. It is designed to run at scale while avoiding repeated work, handling transient failures, and supporting controlled concurrency.

The core workflow is:

1. **Fetch a batch of videos** from the database or another upstream source.
2. **Skip videos already processed**, using database lookups to avoid redundant work.
3. **Transcribe videos in parallel**, with a configurable concurrency limit.
4. **Stream video files directly from their URLs in memory**, avoiding temporary disk usage.
5. **Retry a failed transcription once**, then record persistent failure logs for later inspection.
6. **Store successful transcripts** back into the database.

---

## Architecture

### Components

* **Fetcher**: Retrieves a list of video metadata entries that need transcription.
* **Processor**: Orchestrates transcription, deduplication, retries, and error handling.
* **Transcriber**: Streams the video from its remote URL and sends audio data to the transcription model.
* **Database Layer**: Stores transcripts, failure states, and tracks which videos are already processed.
* **Concurrency Manager**: Uses a thread pool to parallelize transcription with a maximum number of simultaneous workers.

---

## Concurrency

Parallel execution is implemented through a thread pool. You can configure `MAX_WORKERS` to control how many videos are processed at once. This ensures predictable resource usage and prevents overload conditions.

---

## Error Handling and Retries

Each transcription is attempted up to two times:

1. Initial attempt
2. One retry on failure

If both attempts fail, the system records the error in a persistent storage table so these items can be examined or retried separately later.

---

## Avoiding Redundant Work

Before processing, the system checks whether a transcript for the given video already exists in the database. If found, the video is skipped.

This allows safe reruns of the job without duplicating effort.

---

## In-memory Transcription Workflow

The system avoids writing video files to disk. Instead:

1. The video is streamed from its URL into memory.
2. The audio portion is sent to the transcription endpoint.

This reduces I/O overhead and avoids disk storage concerns.

---

## Extensibility

The system is modular and can be extended in several directions:

* Adding a message queue if needed for distributed scaling
* Supporting different transcription backends
* Adding structured logs or metrics
* Incorporating batch processing or scheduled execution

---

## Running the System

1. Configure your API keys and database URL in the environment.
2. Adjust `MAX_WORKERS` based on your resource constraints.
3. Run the main processing script, which will fetch unprocessed videos and begin parallel transcription.

All failures and results are logged for inspection.
