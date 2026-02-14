# Pitfalls Research

**Domain:** Web GUI for AI-Powered CLI Document Generation Tool
**Researched:** 2026-02-14
**Confidence:** HIGH

## Critical Pitfalls

### Pitfall 1: WebSocket Connection Drops During Long-Running LLM Tasks

**What goes wrong:**
Engineers start a document generation task that triggers multiple Claude API calls taking 2-5 minutes total. The WebSocket connection drops mid-stream due to network hiccup, laptop closure, or browser refresh. The frontend loses connection, but the backend continues processing and burning API tokens. The user sees a frozen UI, refreshes, and starts the same task again, creating duplicate processing and wasted Claude API costs. The original results are lost even though processing completed.

**Why it happens:**
Developers treat WebSocket connections as reliable channels and tightly couple task execution to the connection lifecycle. The natural inclination is to stream LLM responses directly through the WebSocket, which works perfectly in development (stable laptop, same network) but fails in production (changing networks, browser refreshes, laptops closing). Platform limitations exacerbate this: Heroku enforces a 30-second initial response timeout, Vercel's hobby tier allows only 10 seconds for serverless functions, and even paid plans max out at 5-13 minutes.

**How to avoid:**
Implement the separation of concerns pattern: decouple task execution from client connections. Use Redis Streams for persistent storage of each LLM response chunk as it's generated, Redis Pub/Sub for notifying connected clients of new chunks, and automatic reconnection logic on the client side that fetches all chunks from the last received position. This ensures generation always continues uninterrupted, clients can reconnect and receive all content without duplicates or missing chunks, and multiple clients can follow the same generation task.

Add heartbeat keepalive signals every 15 seconds to detect disconnects early and implement client-side reconnection with exponential backoff (starting at 1 second, max 30 seconds). Store task state server-side with a unique task ID so clients can resume by ID after reconnection.

**Warning signs:**
- "It works on my laptop but not for remote team members"
- Users report seeing "Connection lost" then restarting tasks
- CloudWatch/monitoring shows duplicate Claude API calls within minutes
- WebSocket connections in logs show frequent disconnects/reconnects
- Users ask "Can I close my laptop while this runs?"

**Phase to address:**
Phase 1 (Core Infrastructure). This is an architectural decision that must be made upfront. Retrofitting persistent task storage after building direct WebSocket streaming requires significant rework. The phase must deliver WebSocket manager with Redis-backed persistence and reconnection logic as a foundational service.

---

### Pitfall 2: Blocking FastAPI Event Loop with Synchronous File Operations

**What goes wrong:**
During file upload (reference documents) or document generation output (saving PDFs), developers use synchronous operations like `file.write()`, `shutil.copyfileobj()`, or `open().read()`. When an engineer uploads a 50MB reference document or the system generates a large technical document, the FastAPI worker thread blocks for several seconds. All other requests queue up. The entire application becomes unresponsive. Other team members trying to use the system see timeout errors. Under concurrent load (3-4 engineers working simultaneously), response times spike from 200ms to 20+ seconds.

**Why it happens:**
Most FastAPI tutorials and file upload examples use synchronous file I/O because it's simpler to understand and works fine for small files in demos. Developers don't realize that FastAPI runs on an async event loop, and any synchronous blocking operation blocks the entire worker. The "it works on my machine" effect happens because testing is typically done with small files and no concurrent load.

**How to avoid:**
Use `aiofiles` for all file operations. Replace `open()` with `aiofiles.open()`, use async context managers (`async with`), and await all read/write operations. For large file uploads, implement streaming with chunked processing rather than loading entire files into memory.

Specifically:
```python
# BAD - Blocks event loop
with open(filepath, 'wb') as f:
    shutil.copyfileobj(upload_file.file, f)

# GOOD - Non-blocking async I/O
async with aiofiles.open(filepath, 'wb') as f:
    while chunk := await upload_file.read(8192):
        await f.write(chunk)
```

Set file size limits (e.g., 100MB max) and validate them before processing. Implement upload progress tracking through separate endpoint polling rather than holding connections open. Real-world measurements show 40% throughput gain and 28% latency reduction (215ms P95) with async file operations.

**Warning signs:**
- API response times spike during file uploads
- Concurrent user requests queue behind file operations
- Single large file upload makes entire app unresponsive
- Logs show worker timeout warnings
- Team members report "the app freezes when someone uploads files"

**Phase to address:**
Phase 1 (Core Infrastructure). File handling patterns must be established from the start. Include in API endpoint implementation guidelines and enforce through code review. Create reusable utility functions for async file operations that all phases use.

---

### Pitfall 3: Claude API Rate Limits Without Retry-After Header Handling

**What goes wrong:**
The system makes multiple concurrent Claude API calls during document generation (analyzing requirements, generating content sections, reviewing outputs). When the team hits the API rate limit (50 requests/minute on Tier 1, 30,000 input tokens/minute), the API returns 429 errors. The naive implementation retries immediately or with simple exponential backoff, ignoring the `retry-after` header. This creates a thundering herd where all queued requests retry simultaneously, making the congestion worse. Engineers see "Rate limit exceeded" errors, document generation fails mid-process, and the system burns through retry attempts without recovering.

**Why it happens:**
Developers implement retry logic based on generic best practices (exponential backoff) without reading Claude API's specific error responses. The Claude API returns a `retry-after` header that specifies exactly how many seconds to wait, but this is ignored. When multiple concurrent tasks hit rate limits simultaneously, they all retry at the same time (synchronized by the same backoff algorithm), creating waves of retries that perpetuate the problem.

**How to avoid:**
Implement Claude-specific error handling that reads and respects the `retry-after` header as the primary recovery signal. Combine this with exponential backoff as a fallback when the header is missing. Add jitter (random variation) to prevent synchronized retries.

Production pattern:
```python
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

async def call_claude_with_retry(prompt):
    for attempt in range(5):
        try:
            response = await client.post("https://api.anthropic.com/v1/messages", ...)
            return response
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                retry_after = int(e.response.headers.get('retry-after', 0))
                if retry_after:
                    await asyncio.sleep(retry_after)
                else:
                    # Fallback: exponential backoff with jitter
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    await asyncio.sleep(wait_time)
            else:
                raise
```

Implement request queuing with rate limit tracking to prevent hitting limits in the first place. Monitor token usage across all team members and implement per-user or per-project quotas. Use circuit breakers to stop retrying when the system is clearly overloaded.

**Warning signs:**
- Repeated 429 errors in logs despite retry logic
- Document generation tasks fail with "rate limit" errors
- Multiple retry attempts happen within seconds of each other
- API costs spike due to failed requests counting toward quota
- Team reports "randomly fails during generation"

**Phase to address:**
Phase 1 (Core Infrastructure). The LLM provider abstraction layer must implement this correctly from the start. Create a shared `LLMClient` service that all phases use, with built-in rate limit handling, retry logic, and circuit breakers.

---

### Pitfall 4: Shared State Divergence Between CLI and Web Application

**What goes wrong:**
The CLI tool maintains project state in `.fds/project.yaml` using a synchronous Python data model. The web application needs concurrent access from multiple users, real-time updates, and WebSocket broadcasting. Developers duplicate the state management logic with subtle differences: the CLI uses file-based locking and immediate writes, the web app uses in-memory state with periodic saves, they handle validation differently, they parse YAML differently. A project created via CLI doesn't appear correctly in the web UI. Changes made in the web UI corrupt the CLI project structure. Two team members editing the same project simultaneously via web UI create race conditions. The CLI and web app drift into incompatible implementations.

**Why it happens:**
The temptation is to "quickly add a web layer" by creating new state management code rather than refactoring the existing CLI code to work in both contexts. The CLI was designed for single-user, single-process, synchronous file operations. The web app needs multi-user, multi-process, async operations. These seem incompatible, so developers create parallel implementations. The differences start small (async vs sync) but grow over time (different validation, different defaults, different error handling).

**How to avoid:**
Create a shared state management layer that both CLI and web use as a library. This layer provides:

1. **Abstract storage interface**: Implementations for file-based (CLI) and Redis/database (web)
2. **Unified validation**: Single source of truth for project schema
3. **Transactional updates**: Atomic operations that work across storage backends
4. **Event emission**: State changes emit events that web UI can subscribe to

The CLI imports this library and uses the file-based storage. The web app imports the same library and uses Redis storage. Both use identical validation and business logic.

```python
# Shared library (used by both CLI and web)
class ProjectState:
    def __init__(self, storage: StorageBackend):
        self.storage = storage

    async def update_phase(self, project_id: str, phase_data: PhaseData):
        # Validation (same for CLI and web)
        validated = PhaseSchema.validate(phase_data)
        # Atomic update (backend-agnostic)
        await self.storage.atomic_update(project_id, "phase", validated)
        # Event emission (CLI ignores, web broadcasts)
        await self.emit_event("phase_updated", project_id, validated)
```

Implement migration tools to convert existing CLI projects to web-compatible storage. Add integration tests that verify CLI and web operations produce identical results.

**Warning signs:**
- "Works in CLI but not in web" bug reports
- Data corruption when switching between CLI and web
- Duplicate validation logic in two places
- Different error messages for the same validation failure
- "Which version is right?" questions about state format

**Phase to address:**
Phase 1 (Core Infrastructure). This is foundational architecture. Attempting to retrofit shared state management after building separate implementations is extremely costly. The phase must deliver the shared state library and storage abstraction before building CLI compatibility features or web UI features.

---

### Pitfall 5: Unvalidated File Uploads with Content-Type Spoofing

**What goes wrong:**
Engineers upload reference documents (PDFs, Word docs, markdown) for the document generation system to reference. The validation checks only the `Content-Type` header from the HTTP request. A malicious or compromised file has `Content-Type: application/pdf` but contains executable code. The system accepts it, stores it, and potentially processes it with document parsing libraries. This creates security vulnerabilities: remote code execution through malicious PDFs, server-side request forgery through crafted documents, denial of service through ZIP bombs or billion laughs XML attacks. Reference files stored on the team server become attack vectors.

**Why it happens:**
The `Content-Type` header is sent by the client and trivially spoofed. Beginner tutorials validate file uploads by checking this header because it's simple and works for honest users. Developers don't realize that accepting user-supplied files is a severe security risk. The "it's just our team" mindset creates a false sense of security—one compromised laptop or malicious engineer can exploit the entire system.

**How to avoid:**
Implement defense-in-depth file validation:

1. **Magic number validation**: Read the first 8-16 bytes and verify they match expected file signatures using `python-magic`
2. **File extension whitelist**: Only accept `.pdf`, `.docx`, `.md`, `.txt` extensions
3. **Size limits**: Enforce maximum file size (e.g., 100MB) before reading content
4. **Filename sanitization**: Generate UUIDs for storage, never use client-provided filenames
5. **Sandboxed parsing**: Process uploaded files in isolated processes with resource limits
6. **Virus scanning**: Integrate ClamAV or similar for malware detection

```python
import magic
import uuid
from pathlib import Path

async def validate_and_store_upload(upload_file: UploadFile):
    # Size check first (before reading)
    upload_file.file.seek(0, 2)  # Seek to end
    size = upload_file.file.tell()
    upload_file.file.seek(0)  # Reset
    if size > 100 * 1024 * 1024:  # 100MB
        raise HTTPException(413, "File too large")

    # Read first chunk for magic number validation
    header = await upload_file.read(8192)
    mime = magic.from_buffer(header, mime=True)

    # Whitelist validation
    allowed_types = {
        'application/pdf': ['.pdf'],
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
        'text/markdown': ['.md'],
        'text/plain': ['.txt']
    }

    if mime not in allowed_types:
        raise HTTPException(400, f"File type {mime} not allowed")

    # Generate safe storage path
    storage_id = uuid.uuid4()
    extension = allowed_types[mime][0]
    storage_path = UPLOAD_DIR / f"{storage_id}{extension}"

    # Stream to disk (async, with size limit enforced)
    upload_file.file.seek(0)
    async with aiofiles.open(storage_path, 'wb') as f:
        await f.write(header)  # Write header we already read
        while chunk := await upload_file.read(8192):
            await f.write(chunk)

    return storage_id, mime
```

Store uploads in a directory outside the web server document root. Never serve uploaded files directly—always proxy through an endpoint that sets proper `Content-Disposition` headers.

**Warning signs:**
- File validation only checks `Content-Type` header
- Uploaded files stored with original filenames
- Upload directory is within static file serving path
- No file size limits enforced
- "What could go wrong?" attitude about team-only access

**Phase to address:**
Phase 2 (File Management). Must be implemented before allowing any file uploads. This is a security gate—the phase cannot be considered complete without proper upload validation. Include security review and penetration testing in phase verification.

---

### Pitfall 6: Missing Resumption Points for Interrupted AI Workflows

**What goes wrong:**
Document generation follows a multi-step workflow: analyze requirements → generate outline → generate sections → review/polish → compile PDF. Each step involves Claude API calls taking 30-120 seconds. An engineer starts generation, the process fails at step 3 (generate sections) due to rate limit, network error, or server restart. The system restarts the entire workflow from step 1, re-doing analysis and outline generation, wasting time and API tokens. There's no way to manually intervene mid-workflow to fix issues. If the engineer disagrees with the AI's analysis, they must complete the entire workflow before providing feedback.

**Why it happens:**
Developers design AI workflows as linear pipelines without checkpointing. The pattern is: `step1().then(step2).then(step3).then(step4)`. This works perfectly when everything succeeds but fails catastrophically on any error. Adding checkpointing later requires redesigning the workflow engine, migrating existing projects, and handling partial state. The effort seems excessive for "occasional failures," so it gets deferred until failure rates increase and user frustration peaks.

**How to avoid:**
Design workflows with explicit state machines and persistent checkpoints from the start. Each workflow step:

1. **Saves output to persistent storage** (database/Redis) before proceeding
2. **Records completion status** with timestamp and responsible agent
3. **Emits events** that web UI can display for progress tracking
4. **Supports manual override** allowing users to edit intermediate results
5. **Allows resumption** from any completed checkpoint

Implement workflow state as a table/document:

```python
WorkflowState = {
    "project_id": "uuid",
    "phase": "generation",
    "current_step": "generate_sections",
    "checkpoints": {
        "analyze_requirements": {
            "status": "completed",
            "completed_at": "2026-02-14T10:30:00Z",
            "output": {...},
            "tokens_used": 1250
        },
        "generate_outline": {
            "status": "completed",
            "completed_at": "2026-02-14T10:32:15Z",
            "output": {...},
            "tokens_used": 2100
        },
        "generate_sections": {
            "status": "in_progress",
            "started_at": "2026-02-14T10:33:00Z",
            "partial_output": {...}
        }
    },
    "can_resume_from": ["generate_outline", "analyze_requirements"]
}
```

Provide UI controls for: viewing checkpoint outputs, editing checkpoint results before continuing, manually retrying failed steps, and resuming from specific checkpoints.

Modern agentic workflow systems implement this via checkpointing that enables recovery and resumption of long-running processes by saving workflow states, with workflows that can start, pause, and resume statefully on demand. Some systems support human-in-the-loop controls where operators can trigger interrupt commands, take over browser control, and pass control back to the agent to continue from the current state.

**Warning signs:**
- "Failed at 90% complete, had to restart from scratch" complaints
- No way to see what the AI did at intermediate steps
- Total workflow time appears in single log entry (no step-by-step tracking)
- Users can't provide feedback until entire workflow completes
- Workflow code is single async function with no state persistence

**Phase to address:**
Phase 3 (Phase Orchestration). The workflow engine is the heart of phase execution. This must support checkpointing before implementing complex multi-step phase workflows. Include checkpoint recovery testing and manual intervention testing in phase verification.

---

### Pitfall 7: Server-Sent Events vs WebSockets Mismatch for One-Way Streaming

**What goes wrong:**
Developers implement real-time progress updates for LLM streaming using WebSockets because "WebSockets are for real-time communication." This creates unnecessary complexity: WebSocket connection management, bidirectional protocol overhead, connection state synchronization, binary framing overhead. The application only needs server-to-client streaming (LLM tokens, progress updates). The extra complexity of WebSockets creates more failure modes without providing value. More code to debug, more edge cases (client sends unexpected messages), higher resource usage per connection.

**Why it happens:**
WebSockets are the well-known "real-time web" technology. Developers reach for them instinctively when they see "real-time" in requirements. Server-Sent Events (SSE) are less well-known despite being simpler and more appropriate for one-way streaming. The React ecosystem has more WebSocket examples and libraries than SSE examples. Once the initial WebSocket implementation is built, the sunk cost fallacy prevents reconsidering.

**How to avoid:**
Use Server-Sent Events for one-way server-to-client streaming. SSE provides:

- Simpler HTTP-based protocol (no upgrade handshake)
- Automatic reconnection built into browser EventSource API
- Lower overhead than WebSocket framing
- Better compatibility with proxies and load balancers
- Text-based format (easier debugging)

Reserve WebSockets for scenarios requiring bidirectional communication (collaborative editing, chat with replies).

For LLM streaming, document generation progress, and phase timeline updates, SSE is superior:

```python
# FastAPI SSE endpoint
from sse_starlette.sse import EventSourceResponse

@app.get("/stream/generation/{task_id}")
async def stream_generation(task_id: str):
    async def event_generator():
        # Subscribe to Redis pub/sub for this task
        async for message in subscribe_to_task(task_id):
            yield {
                "event": "token",
                "data": message["content"],
                "id": message["sequence"]
            }

    return EventSourceResponse(event_generator())
```

```javascript
// React client
const eventSource = new EventSource(`/stream/generation/${taskId}`);

eventSource.onmessage = (event) => {
    setContent(prev => prev + event.data);
};

eventSource.onerror = (error) => {
    // Browser automatically reconnects with Last-Event-ID header
    console.log("Connection lost, reconnecting...");
};
```

The browser's EventSource API handles reconnection automatically, sending the `Last-Event-ID` header so the server can resume from the last received event. This eliminates custom reconnection logic.

Use WebSockets only when you genuinely need client-to-server messages during streaming (like pause/resume controls, user interruptions of AI workflows). For most document generation scenarios, SSE is simpler and more reliable.

**Warning signs:**
- WebSocket implementation but server never receives messages from client
- Complex WebSocket state management code
- Difficulty debugging connection issues
- Connection drops more frequently than expected
- "Why are we using WebSockets for this?" questions during code review

**Phase to address:**
Phase 1 (Core Infrastructure). Choose the streaming protocol early and build the real-time communication abstraction around it. If starting with WebSockets, plan migration path to SSE for one-way scenarios. Document which scenarios use which protocol.

---

### Pitfall 8: Ignoring Context Window Limits in Multi-Step Document Generation

**What goes wrong:**
Document generation accumulates context across multiple steps: requirements → outline → section 1 → section 2 → section 3 → review. Each step's output becomes input for the next step. By step 5, the prompt includes requirements + outline + all previous sections + current instructions, totaling 180K tokens. This exceeds Claude's context window (200K for Sonnet 4.5). The API call fails with "context_length_exceeded" error. The workflow crashes. Even when it fits, the massive context inflates costs: each generation step pays for all previous content as input tokens.

Developers either didn't track cumulative token usage or assumed "200K is plenty." Real documents with extensive requirements and reference materials exceed limits quickly. FDS/SDS documents include technical specifications, equipment lists, safety procedures—all context-heavy.

**Why it happens:**
The "conversation" mental model encourages appending everything to context. It works in ChatGPT UI where history is automatic. Developers replicate this pattern in programmatic workflows. Token counting seems tedious, so it's skipped until production failures. The nonlinear relationship between content length and token count makes estimation difficult (code/technical content has higher token density than natural language).

**How to avoid:**
Implement explicit context management with token budgeting:

1. **Token counting before API calls**: Use `anthropic.count_tokens()` to measure before sending
2. **Context windowing**: Keep only essential context from previous steps
3. **Summarization**: Compress previous outputs into summaries for subsequent steps
4. **Reference storage**: Store full content in database, pass only IDs and summaries to API
5. **Prompt engineering**: Use structured output formats that reduce token usage

```python
class ContextBudget:
    def __init__(self, max_tokens=190000):  # Leave 10K buffer
        self.max_tokens = max_tokens
        self.system_prompt_tokens = 0
        self.context_tokens = 0
        self.reserved_output_tokens = 4000

    def add_context(self, text: str, priority: int = 1):
        tokens = anthropic.count_tokens(text)
        if self.available_input_tokens() < tokens:
            if priority > 5:
                # High priority: summarize existing context
                self.context_tokens = self._summarize_context()
            else:
                raise ContextBudgetExceeded()
        self.context_tokens += tokens

    def available_input_tokens(self):
        return self.max_tokens - self.system_prompt_tokens - self.context_tokens - self.reserved_output_tokens
```

For document generation workflows:

- Step 1 (Requirements analysis): Input=requirements (15K), Output=structured analysis (3K)
- Step 2 (Outline): Input=requirements summary (2K) + analysis (3K), Output=outline (2K)
- Step 3 (Section 1): Input=outline (2K) + relevant requirements (5K), Output=section (4K)
- Step 4 (Section 2): Input=outline (2K) + section 1 summary (500), Output=section (4K)

Each step's context budget stays under 30K input tokens despite the document growing to 200K+ tokens total. Use prompt caching for repeated content (requirements, outlines) to reduce costs by 60-90%.

**Warning signs:**
- "context_length_exceeded" errors in production
- Token costs scaling quadratically with document length
- No token counting in code
- Each workflow step includes full conversation history
- Developers surprised by token counts on real documents

**Phase to address:**
Phase 3 (Phase Orchestration). Context management is critical for phase execution workflows. The phase orchestrator must implement context budgeting before running multi-step generation workflows. Include token usage monitoring and context budget enforcement.

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Store files on local filesystem instead of S3/object storage | Simple implementation, no cloud dependencies | Difficult to scale horizontally, no disaster recovery, manual backups | Acceptable for MVP if team server has reliable backup and single-instance deployment is sufficient |
| Use polling instead of SSE/WebSocket for progress updates | Simpler implementation, easier debugging | Higher server load, 3-10 second latency, feels unresponsive | Never acceptable—SSE is only marginally more complex and drastically better UX |
| Skip file validation beyond extension check | Fast upload processing | Security vulnerability, potential RCE | Never acceptable—validation is non-negotiable |
| Use in-memory state instead of Redis for session management | No Redis dependency, faster development | Lose state on server restart, can't scale horizontally | Acceptable for single-server prototype, must migrate before multi-user production |
| Hard-code Claude API client instead of LLM abstraction | Fewer abstractions, direct API usage | Locked to single provider, difficult to add local models | Never acceptable—abstraction is explicit requirement |
| Store task results only in memory, not persistent storage | Faster processing, simpler code | Loss of data on restart, no resumption capability | Never acceptable—resumption is core reliability requirement |
| Skip retry logic and rely on user to refresh | Faster initial implementation | Poor UX, wasted API calls, frustrated users | Never acceptable for production |
| Synchronous database queries with SQLAlchemy ORM | Familiar ORM patterns, more examples | Blocks event loop, poor performance | Acceptable only if using async SQLAlchemy properly from start |

## Integration Gotchas

Common mistakes when connecting to external services.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Claude API | Ignoring `retry-after` header in 429 responses | Parse header, sleep for specified duration before retry |
| Claude API | Not implementing prompt caching for repeated content | Enable caching on system prompts and reference documents, save 60-90% |
| Claude API | Assuming streaming always works | Handle streaming failures, fallback to non-streaming, store partial results |
| Redis Pub/Sub | Treating it as persistent message queue | Use Redis Streams for persistence, Pub/Sub only for notifications |
| Redis | Using string operations for complex state | Use Redis JSON or hash operations for structured data |
| File uploads | Trusting `Content-Type` header | Validate magic numbers with `python-magic` library |
| File uploads | Loading entire file into memory | Stream uploads in chunks with `aiofiles` |
| WebSockets | Not implementing heartbeat/keepalive | Send ping/pong every 15-30 seconds to detect dead connections |
| WebSockets | Coupling task execution to connection lifecycle | Store task state server-side, allow reconnection with task ID |
| SSE | Not setting `Last-Event-ID` for resumption | Include event IDs, track client position, allow resumption |
| Nginx reverse proxy | Default timeout too short for LLM streaming | Set `proxy_read_timeout 300s` and `proxy_send_timeout 300s` |
| systemd service | Not setting proper working directory | Set `WorkingDirectory` in service file to project root |
| systemd service | Not handling graceful shutdown | Implement `SIGTERM` handler to finish in-flight requests |

## Performance Traps

Patterns that work at small scale but fail as usage grows.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Synchronous file I/O in async endpoints | Slow response times, queued requests | Use `aiofiles` for all file operations | 2-3 concurrent users with file uploads |
| Loading full document history into memory | High memory usage, OOM crashes | Paginate history, lazy load content | Documents over 50-100 pages |
| Storing all reference files in single directory | Slow directory listings, filesystem limits | Use hashed subdirectories (e.g., `uploads/{first_2_chars}/{uuid}`) | 10K+ uploaded files |
| Separate API calls for each document section | High latency, rate limit issues | Batch operations where possible | Documents with 20+ sections |
| No connection pooling for database | Connection exhaustion, high latency | Configure SQLAlchemy pool: `pool_size=20, max_overflow=40` | 10+ concurrent users |
| Unbounded WebSocket connections | Memory exhaustion | Limit concurrent connections per user, implement timeouts | 50+ simultaneous connections |
| Storing large context in Redis strings | High memory usage, serialization overhead | Use Redis JSON or compress with gzip | Context over 100KB per session |
| No rate limiting per user | Single user can exhaust API quota | Implement per-user rate limits and quotas | Team of 5+ users |

## Security Mistakes

Domain-specific security issues beyond general web security.

| Mistake | Risk | Prevention |
|---------|------|------------|
| Serving uploaded files directly from upload directory | Path traversal, RCE if executable files uploaded | Store outside web root, proxy through endpoint with UUID lookup |
| Not sanitizing filenames before storage | Directory traversal via `../` in filename | Generate UUID-based filenames, ignore client-provided names |
| Trusting client-provided `Content-Type` | Malicious files bypass validation | Validate magic numbers with `python-magic` |
| No file size limits | DoS via massive uploads | Enforce limits before reading (check `Content-Length`), streaming validation |
| Storing API keys in project files | Keys leaked in version control | Use environment variables, separate secrets management |
| Logging full API requests/responses | API keys, sensitive data in logs | Redact sensitive fields, log only metadata |
| No authentication on internal endpoints | Unauthorized access from team network | Require authentication even on "internal" network |
| Sharing single Claude API key across all users | No usage attribution, quota issues | Implement per-user API keys or internal usage tracking |
| Storing documents without access control | Users can access other users' documents | Implement document ownership and access control |
| No input sanitization on document content | XSS in document preview, template injection | Sanitize markdown/HTML before rendering, use CSP headers |

## UX Pitfalls

Common user experience mistakes in this domain.

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| No progress indication during long LLM calls | Users think app is frozen, refresh and retry | Stream tokens as they arrive, show "Generating..." with current step |
| Losing work on connection drop | Frustration, distrust of system | Auto-save drafts, persist task state, allow resumption |
| No way to cancel long-running generation | Users forced to wait or kill browser | Provide cancel button, implement graceful cancellation |
| Generic "Error occurred" messages | Users don't know what to do | Specific messages: "Rate limit reached, retrying in 30s..." |
| No indication of API cost for operations | Bill shock, inefficient usage | Show estimated token usage before generation |
| Requiring full workflow restart after failure | Wasted time, repeated work | Allow resumption from checkpoints |
| No preview before final document generation | Surprises in output, wasted generations | Show outline and section previews, allow editing before full generation |
| Document preview doesn't match final output | Trust issues, confusion | Use same rendering pipeline for preview and final output |
| No diff view for document iterations | Hard to see what changed | Show diff between versions, highlight AI suggestions |
| Unclear which operations use CLI vs must use web | Confusion, workflow friction | Clear documentation, consider making CLI call web API |

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **WebSocket streaming**: Often missing reconnection logic—verify connection drop recovery and state resumption
- [ ] **File uploads**: Often missing magic number validation—verify `python-magic` validation, not just extension/Content-Type
- [ ] **Claude API integration**: Often missing retry-after header handling—verify 429 error response parsing
- [ ] **Long-running tasks**: Often missing checkpoint persistence—verify tasks survive server restart
- [ ] **Document generation**: Often missing token budget tracking—verify context window management
- [ ] **Error handling**: Often missing user-friendly messages—verify specific, actionable error text
- [ ] **Session management**: Often missing cleanup on logout—verify session expiration and Redis cleanup
- [ ] **File storage**: Often missing access control—verify user can't access other users' files
- [ ] **API cost tracking**: Often missing per-user attribution—verify usage monitoring and quota enforcement
- [ ] **Graceful shutdown**: Often missing in-flight request handling—verify systemd service handles SIGTERM properly
- [ ] **Context sharing**: Often missing CLI/web compatibility layer—verify projects work in both interfaces
- [ ] **Background tasks**: Often missing failure notifications—verify users are notified when background tasks fail
- [ ] **State synchronization**: Often missing conflict resolution—verify concurrent edits don't corrupt state

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| WebSocket connection loss | LOW | Client auto-reconnects with task ID, fetches missed chunks from Redis, resumes streaming |
| Blocking file I/O degrading performance | MEDIUM | Migrate to `aiofiles` incrementally, prioritize upload endpoints first, test under load |
| Rate limit exceeded | LOW | Wait for `retry-after` period, queued requests auto-retry, consider tier upgrade |
| Shared state divergence CLI/web | HIGH | Rebuild shared library, migrate existing projects, comprehensive integration testing |
| File upload security vulnerability | HIGH | Audit existing uploads, quarantine suspicious files, patch validation immediately |
| Lost task state on server restart | MEDIUM | Implement Redis persistence, replay partial results to user, offer manual retry |
| Context window exceeded | LOW | Implement summarization for next step, reduce context budget, cache summaries |
| Duplicate task execution on reconnect | MEDIUM | Add task deduplication by ID, check existing task before starting new one |
| Cost overrun from inefficient prompts | LOW | Enable prompt caching, optimize prompts, implement token budgets per user |
| State corruption from concurrent edits | MEDIUM | Implement optimistic locking, detect conflicts, prompt user to merge or retry |

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| WebSocket connection drops | Phase 1: Core Infrastructure | Drop connection mid-task, verify resumption without data loss |
| Blocking file I/O | Phase 1: Core Infrastructure | Upload 50MB file while making concurrent API requests, verify no latency spike |
| Claude API rate limits | Phase 1: Core Infrastructure | Trigger 429 error, verify retry-after header respected |
| Shared state CLI/web divergence | Phase 1: Core Infrastructure | Create project in CLI, verify appears correctly in web UI |
| File upload security | Phase 2: File Management | Upload file with spoofed Content-Type, verify rejection based on magic number |
| Missing resumption points | Phase 3: Phase Orchestration | Kill server mid-workflow, restart, verify resumption from checkpoint |
| SSE vs WebSocket mismatch | Phase 1: Core Infrastructure | Implement streaming with SSE for one-way, verify auto-reconnection |
| Context window limits | Phase 3: Phase Orchestration | Generate document with 200K+ total tokens, verify context budgeting |
| Synchronous DB queries | Phase 1: Core Infrastructure | Run DB query under load, verify no event loop blocking |
| No graceful shutdown | Phase 7: Deployment | Send SIGTERM during task execution, verify in-flight requests complete |
| Missing error messages | All phases | Trigger each error condition, verify user-friendly message displayed |
| No cost tracking | Phase 4: Document Preview | Run generation task, verify token usage displayed to user |

## Sources

### WebSocket & Real-Time Communication
- [FastAPI WebSockets Documentation](https://fastapi.tiangolo.com/advanced/websockets/)
- [How to Handle Large Scale WebSocket Traffic with FastAPI | Medium](https://hexshift.medium.com/how-to-handle-large-scale-websocket-traffic-with-fastapi-9c841f937f39)
- [FastAPI + WebSockets + React: Real-Time Features | Medium](https://medium.com/@suganthi2496/fastapi-websockets-react-real-time-features-for-your-modern-apps-b8042a10fd90)
- [WebSockets vs Server-Sent Events | Ably](https://ably.com/blog/websockets-vs-sse)
- [SSE vs WebSockets: Comparing Real-Time Protocols | SoftwareMill](https://softwaremill.com/sse-vs-websockets-comparing-real-time-communication-protocols/)
- [Building Real-Time AI Chat Infrastructure | Render](https://render.com/articles/real-time-ai-chat-websockets-infrastructure)
- [How to Build LLM Streams That Survive Reconnects | Upstash](https://upstash.com/blog/resumable-llm-streams)

### FastAPI Background Tasks & Performance
- [Background Tasks - FastAPI](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [Handling Long-Running Tasks in FastAPI | DataScienceTribe](https://www.datasciencebyexample.com/2023/08/26/handling-long-running-tasks-in-fastapi-python/)
- [Managing Background Tasks in FastAPI | Leapcell](https://leapcell.io/blog/managing-background-tasks-and-long-running-operations-in-fastapi)
- [FastAPI Background Tasks | Sentry](https://sentry.io/answers/fastapi-background-tasks-and-middleware/)

### File Upload Security
- [Uploading Files Using FastAPI: A Complete Guide | Better Stack](https://betterstack.com/community/guides/scaling-python/uploading-files-using-fastapi/)
- [Building a Secure File Upload API in FastAPI | Mahdi Abu Tafish](https://noone-m.github.io/2025-12-10-fastapi-file-upload/)
- [Upload files in FastAPI with file validation | Medium](https://medium.com/@jayhawk24/upload-files-in-fastapi-with-file-validation-787bd1a57658)

### Claude API Integration & Cost Optimization
- [Claude API Rate Limits Documentation](https://docs.claude.com/en/api/rate-limits)
- [How to Fix Claude API 429 Rate Limit Error | AI Free API](https://www.aifreeapi.com/en/posts/fix-claude-api-429-rate-limit-error)
- [Claude API Rate Limits: Production Scaling Guide | HashBuilds](https://www.hashbuilds.com/articles/claude-api-rate-limits-production-scaling-guide-for-saas)
- [Prompt Caching: 60% Cost Reduction in LLM Applications | Medium](https://medium.com/tr-labs-ml-engineering-blog/prompt-caching-the-secret-to-60-cost-reduction-in-llm-applications-6c792a0ac29b)
- [LLM Cost Optimization: 80% Reduction Guide | Koombea](https://ai.koombea.com/blog/llm-cost-optimization)
- [Anthropic Claude API Pricing 2026 | MetaCTO](https://www.metacto.com/blogs/anthropic-api-pricing-a-full-breakdown-of-costs-and-integration)

### State Management & Architecture
- [State Management in 2026 | Nucamp](https://www.nucamp.co/blog/state-management-in-2026-redux-context-api-and-modern-patterns)
- [FastAPI State Variables Explained | Medium](https://medium.com/algomart/fastapi-state-variables-explained-the-right-way-to-share-global-data-across-your-app-6de4d1435b22)
- [FastAPI Sessions Documentation](https://jordanisaacs.github.io/fastapi-sessions/)
- [Command Line Interface Guidelines](https://clig.dev/)

### AI Workflow & Resumption
- [The 2026 Guide to Agentic Workflow Architectures | Stack AI](https://www.stack-ai.com/blog/the-2026-guide-to-agentic-workflow-architectures)
- [Agent-User Interaction Protocol | Via](https://ridewithvia.com/resources/agent-user-interaction-protocol-when-the-frontend-got-an-ai-protocol)
- [AgentWorkflow Guide | LlamaIndex](https://www.llamaindex.ai/blog/introducing-agentworkflow-a-powerful-system-for-building-ai-agent-systems)

### Production Deployment
- [Deploy FastAPI with Gunicorn and Nginx | Vultr](https://docs.vultr.com/how-to-deploy-a-fastapi-application-with-gunicorn-and-nginx-on-ubuntu-2404)
- [FastAPI Hosting: Deploy on Ubuntu Server | PloyCloud](https://ploy.cloud/blog/fastapi-hosting-deployment-guide-2025/)
- [FastAPI Best Practices for Production 2026 | FastLaunchAPI](https://fastlaunchapi.dev/blog/fastapi-best-practices-production-2026)
- [Preparing FastAPI for Production | Medium](https://medium.com/@ramanbazhanau/preparing-fastapi-for-production-a-comprehensive-guide-d167e693aa2b)

### Monitoring & Logging
- [Logging + LLM + FastAPI | Medium](https://medium.com/@alejandro7899871776/logging-llm-fastapi-69fe88e01a4d)
- [FastAPI Middleware Patterns: Logging, Metrics, Error Handling 2026 | Johal.in](https://johal.in/fastapi-middleware-patterns-custom-logging-metrics-and-error-handling-2026-2/)
- [Building Observable LLM Agents with OpenTelemetry | Medium](https://engineering.teknasyon.com/from-prompts-to-metrics-building-observable-llm-agents-using-fastapi-opentelemetry-prometheus-359d3132d92b)

---
*Pitfalls research for: Web GUI for AI-Powered CLI FDS/SDS Document Generation*
*Researched: 2026-02-14*
*Confidence: HIGH - Based on official documentation, production guides, and 2026 best practices*
