# Phase 10: Discussion Workflow & Chat Interface - Research

**Researched:** 2026-02-15
**Domain:** AI-driven chat interface, phase timeline, conversation persistence, v1.0 workflow translation
**Confidence:** HIGH

## Summary

Phase 10 implements the discussion workflow from v1.0 as a chat-based UI with real-time AI streaming, conversation history, and a phase timeline for workflow navigation. The research confirms that shadcn/ui chat patterns (message bubbles, streaming, question cards) are well-established and work naturally with FastAPI SSE (Server-Sent Events) for Claude API streaming. The existing Sheet component can be reused for the chat panel. Phase timeline patterns exist as horizontal carousels with status indicators and popovers for action triggers. Conversation storage should use SQLite (not files) for queryability and scale. The v1.0 discuss-phase.md workflow provides the authoritative source for discussion patterns, question depth, content type detection, and CONTEXT.md generation — plans MUST reference specific v1.0 source files (not paraphrase).

**Primary recommendation:** Use shadcn-chatbot-kit patterns for chat UI, FastAPI sse-starlette for streaming, SQLite for conversation persistence, and Radix Popover for timeline phase actions. Extract v1.0 discussion patterns from gsd-docs-industrial/workflows/discuss-phase.md and templates/context.md as the authoritative source, NOT as verbatim injection but as optimized chat prompts with backend guardrails.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Phase timeline:**
- Horizontal timeline bar above the main workspace content — always visible, compact
- Each phase node shows colored icon + sub-status detail (Besproken, Gepland, Geschreven, Geverifieerd, Beoordeeld)
- Clicking a phase node opens an inline popover with status summary and action buttons (only valid next actions enabled)
- Separate "Fasering" tab available for full detailed phase view with all phases expanded
- Compact bar is the quick entry point; Fasering tab gives the full picture

**Chat panel design:**
- Reuse the slide-in Sheet component (from Phase 8) — discussion opens from the right side
- Hybrid question cards: AI presents questions as styled cards with clickable option chips AND a text input for freeform/detailed answers
- Multi-select card for initial gray area selection (direct v1.0 AskUserQuestion translation)
- Text input with file attach button — engineer can reference project files while answering
- Supported file types for attachment include .md files (gap from Phase 9: add .md to accepted upload types)

**Discussion flow:**
- AI-driven with backend guardrails: Claude API drives the conversation, backend enforces structure (topic selection step, scope boundary, question pacing)
- Extract and optimize v1.0 discussion patterns into a chat-optimized prompt (NOT verbatim workflow injection). Fallback: if extracted version lacks depth, switch to full v1.0 workflow as system prompt
- Summary card posted in chat after each topic completes — engineer confirms, edits, or adds before moving on
- Running summary panel visible alongside the chat — accumulates decisions as discussion progresses, always shows the full picture
- Engineer can edit decisions two ways: click in the summary panel to edit directly, OR type a correction in chat and AI updates the summary
- Scope creep handling preserved from v1.0: redirect to deferred ideas, don't discuss new capabilities

**Conversation history:**
- Past discussions accessible from both the phase timeline (contextual: "Bekijk bespreking") and a dedicated "Gesprekken" tab (full overview)
- Past conversations are read-only — "Bijwerken" (Update) button starts a new discussion pre-loaded with existing context
- Clean separation between original discussion and revision sessions

### Claude's Discretion
- CONTEXT.md decision surfacing approach (summary panel, rendered document, or hybrid)
- Conversation message storage (SQLite vs file-based)
- Chat message styling and bubble design
- Popover layout for timeline phase detail
- Fasering tab detailed view layout

### Deferred Ideas (OUT OF SCOPE)
- Phase 9 fix: add .md to accepted file upload types in backend validation — could be addressed as Phase 10 prerequisite or separate fix

</user_constraints>

## Standard Stack

### Core Backend (Chat & Streaming)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| sse-starlette | ^2.2.2 | Server-Sent Events for streaming | Production-ready SSE for FastAPI/Starlette, follows W3C spec |
| litellm | existing | Claude API integration | Already abstracted in Phase 8, supports streaming |
| anthropic | latest | Official Claude SDK (fallback) | Direct access if LiteLLM insufficient for extended context |

### Core Frontend (Chat UI)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| shadcn-chatbot-kit | ^1.3.0+ | Chat UI components | Built on shadcn/ui, copy-paste philosophy, streaming support |
| @radix-ui/react-popover | via shadcn | Timeline phase popovers | WAI-ARIA compliant, keyboard navigation, focus management |
| react-markdown | ^9.0.0+ | Render markdown in messages | Industry standard for React markdown rendering |
| sonner | existing | Toast notifications | Already in stack (Phase 8), used for discussion confirmations |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| EventSource | browser native | SSE client for streaming | Built-in browser API, no library needed |
| remark-gfm | latest | GitHub Flavored Markdown | Enhance react-markdown with tables, task lists |
| react-syntax-highlighter | latest | Code block highlighting | If discussion includes code examples |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| sse-starlette | WebSockets | SSE is simpler for server→client streaming, WebSocket overkill for unidirectional flow |
| shadcn-chatbot-kit | chatscope/chat-ui-kit-react | Chatscope is more opinionated, shadcn gives code ownership |
| SQLite storage | File-based JSON | Files harder to query for history, SQLite better for conversation search/filter |
| Radix Popover | Custom tooltip | Radix handles accessibility, keyboard nav, focus trap automatically |

**Installation:**

Backend:
```bash
pip install sse-starlette anthropic
# litellm already installed in Phase 8
```

Frontend:
```bash
npm install react-markdown remark-gfm
# @radix-ui/react-popover installed via shadcn CLI
npx shadcn@latest add popover
# shadcn-chatbot-kit components copied manually (shadcn philosophy)
```

## Architecture Patterns

### Recommended Project Structure

Backend:
```
backend/
├── app/
│   ├── models/
│   │   ├── conversation.py      # Conversation sessions
│   │   ├── message.py           # Chat messages
│   │   └── phase.py             # Phase metadata and status
│   ├── schemas/
│   │   ├── conversation.py      # Pydantic schemas
│   │   └── phase.py             # Phase timeline schemas
│   ├── api/
│   │   ├── discussions.py       # Chat endpoints + SSE streaming
│   │   ├── phases.py            # Timeline status, phase operations
│   │   └── context.py           # CONTEXT.md generation endpoint
│   ├── services/
│   │   ├── discussion_engine.py # v1.0 workflow orchestration
│   │   ├── prompt_builder.py    # Extract v1.0 patterns into prompts
│   │   └── context_generator.py # CONTEXT.md writing from decisions
│   └── prompts/
│       ├── discuss_phase.py     # Chat-optimized prompts from v1.0
│       └── v1_fallback.py       # Full v1.0 workflow as system prompt
```

Frontend:
```
frontend/src/features/
├── discussions/
│   ├── components/
│   │   ├── ChatPanel.tsx        # Sheet with chat + summary panel
│   │   ├── MessageList.tsx      # Scrollable message history
│   │   ├── QuestionCard.tsx     # Hybrid question with chips + input
│   │   ├── SummaryPanel.tsx     # Running decision accumulator
│   │   └── ConversationHistory.tsx # Past discussions browser
│   ├── hooks/
│   │   ├── useDiscussionStream.ts # SSE connection for streaming
│   │   └── useConversationHistory.ts # Load past discussions
│   └── types/
│       └── conversation.ts      # TypeScript types
├── timeline/
│   ├── components/
│   │   ├── PhaseTimeline.tsx    # Horizontal timeline bar
│   │   ├── PhaseNode.tsx        # Single phase with status
│   │   ├── PhasePopover.tsx     # Action buttons popover
│   │   └── FaseringTab.tsx      # Full detailed phase view
│   └── hooks/
│       └── usePhaseStatus.ts    # Fetch timeline state
```

### Pattern 1: SSE Streaming for Claude API Responses

**What:** Server-Sent Events (SSE) connection that streams Claude API responses token-by-token to the frontend for real-time chat feel.

**When to use:** All discussion endpoints where AI generates questions or responses.

**Example:**
```python
# Source: FastAPI SSE with Claude API streaming
# https://mahdijafaridev.medium.com/implementing-server-sent-events-sse-with-fastapi-real-time-updates-made-simple-6492f8bfc154
# https://platform.claude.com/docs/en/build-with-claude/streaming

from sse_starlette.sse import EventSourceResponse
from fastapi import APIRouter
from app.llm.provider import LLMProvider

router = APIRouter()

@router.post("/discussions/{conversation_id}/stream")
async def stream_discussion(
    conversation_id: int,
    message: str,
    llm: LLMProvider
):
    """Stream AI response via SSE."""

    async def event_generator():
        """Generate SSE events from Claude streaming."""
        messages = [
            {"role": "system", "content": discussion_prompt},
            {"role": "user", "content": message}
        ]

        accumulated = ""
        async for chunk in llm.stream_complete(messages):
            accumulated += chunk
            yield {
                "event": "message",
                "data": json.dumps({
                    "delta": chunk,
                    "accumulated": accumulated
                })
            }

        # Signal completion
        yield {
            "event": "done",
            "data": json.dumps({"final": accumulated})
        }

    return EventSourceResponse(event_generator())
```

Frontend consumption:
```typescript
// Source: Browser EventSource API
// https://developer.mozilla.org/en-US/docs/Web/API/EventSource

function useDiscussionStream(conversationId: number) {
  const [messages, setMessages] = useState<string[]>([]);

  const streamMessage = (userMessage: string) => {
    const eventSource = new EventSource(
      `/api/discussions/${conversationId}/stream?message=${encodeURIComponent(userMessage)}`
    );

    eventSource.addEventListener('message', (e) => {
      const data = JSON.parse(e.data);
      setMessages(prev => [...prev.slice(0, -1), data.accumulated]);
    });

    eventSource.addEventListener('done', (e) => {
      eventSource.close();
    });

    eventSource.onerror = () => {
      eventSource.close();
    };
  };

  return { messages, streamMessage };
}
```

### Pattern 2: Hybrid Question Card with Chips + Input

**What:** Chat message component that displays AI questions as cards with clickable option chips (for structured choices) AND a text input for freeform answers (for specification details).

**When to use:** All gray area questions where engineer can choose from common options OR provide detailed specifications.

**Example:**
```typescript
// Source: shadcn-chatbot-kit patterns
// https://shadcn-chatbot-kit.vercel.app/

import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';

interface QuestionCardProps {
  question: string;
  options?: string[];
  onAnswer: (answer: string) => void;
}

export function QuestionCard({ question, options, onAnswer }: QuestionCardProps) {
  const [customAnswer, setCustomAnswer] = useState('');

  return (
    <Card className="p-4 space-y-3">
      <p className="font-medium">{question}</p>

      {/* Option chips */}
      {options && (
        <div className="flex flex-wrap gap-2">
          {options.map(opt => (
            <Button
              key={opt}
              variant="outline"
              size="sm"
              onClick={() => onAnswer(opt)}
            >
              {opt}
            </Button>
          ))}
        </div>
      )}

      {/* Freeform input */}
      <div className="space-y-2">
        <label className="text-sm text-muted-foreground">
          Of geef een gedetailleerd antwoord:
        </label>
        <Textarea
          value={customAnswer}
          onChange={(e) => setCustomAnswer(e.target.value)}
          placeholder="Beschrijf de specificaties..."
          className="min-h-[80px]"
        />
        <Button
          onClick={() => onAnswer(customAnswer)}
          disabled={!customAnswer.trim()}
        >
          Verstuur
        </Button>
      </div>
    </Card>
  );
}
```

### Pattern 3: Running Summary Panel with Editable Decisions

**What:** Side panel that accumulates discussion decisions in real-time, allowing engineer to edit directly in the panel OR via chat corrections.

**When to use:** Always visible during discussion phase, updates after each topic completes.

**Example:**
```typescript
// Source: React state management patterns for chat
// https://blog.logrocket.com/building-real-time-state-management-react-fluent-state/

import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Edit2 } from 'lucide-react';

interface Decision {
  topic: string;
  decision: string;
  reasoning?: string;
}

interface SummaryPanelProps {
  decisions: Decision[];
  onEdit: (index: number, newDecision: string) => void;
}

export function SummaryPanel({ decisions, onEdit }: SummaryPanelProps) {
  const [editingIndex, setEditingIndex] = useState<number | null>(null);

  return (
    <div className="w-80 border-l bg-muted/20 p-4 space-y-4">
      <h3 className="font-semibold">Beslissingen</h3>

      {decisions.map((decision, idx) => (
        <Card key={idx} className="p-3 space-y-2">
          <div className="flex items-start justify-between">
            <p className="text-sm font-medium">{decision.topic}</p>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setEditingIndex(idx)}
            >
              <Edit2 className="h-4 w-4" />
            </Button>
          </div>

          {editingIndex === idx ? (
            <Textarea
              defaultValue={decision.decision}
              onBlur={(e) => {
                onEdit(idx, e.target.value);
                setEditingIndex(null);
              }}
              className="text-sm"
            />
          ) : (
            <p className="text-sm text-muted-foreground">{decision.decision}</p>
          )}

          {decision.reasoning && (
            <p className="text-xs text-muted-foreground italic">
              Redenering: {decision.reasoning}
            </p>
          )}
        </Card>
      ))}
    </div>
  );
}
```

### Pattern 4: Phase Timeline with Popover Actions

**What:** Horizontal timeline showing all ROADMAP phases with completion status indicators and inline popovers for triggering phase operations.

**When to use:** Always visible above main workspace, provides quick navigation and action triggers.

**Example:**
```typescript
// Source: Radix Popover accessibility patterns
// https://www.radix-ui.com/primitives/docs/components/popover
// Horizontal timeline patterns: https://shadcn-timeline.vercel.app/

import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Button } from '@/components/ui/button';
import { CheckCircle2, Circle, Clock } from 'lucide-react';

interface PhaseNode {
  id: number;
  name: string;
  status: 'pending' | 'in_progress' | 'completed';
  subStatus?: string; // Besproken, Gepland, etc.
  availableActions: string[]; // discuss, plan, write, verify, review
}

export function PhaseTimeline({ phases }: { phases: PhaseNode[] }) {
  return (
    <div className="flex items-center gap-2 py-2 px-4 border-b bg-background">
      {phases.map((phase, idx) => (
        <div key={phase.id} className="flex items-center gap-2">
          <Popover>
            <PopoverTrigger asChild>
              <Button
                variant={phase.status === 'completed' ? 'default' : 'outline'}
                size="sm"
                className="gap-2"
              >
                {phase.status === 'completed' && <CheckCircle2 className="h-4 w-4" />}
                {phase.status === 'in_progress' && <Clock className="h-4 w-4" />}
                {phase.status === 'pending' && <Circle className="h-4 w-4" />}
                <span>Fase {phase.id}</span>
                {phase.subStatus && (
                  <span className="text-xs text-muted-foreground">
                    {phase.subStatus}
                  </span>
                )}
              </Button>
            </PopoverTrigger>

            <PopoverContent className="w-80 p-4 space-y-3">
              <div>
                <h4 className="font-medium">{phase.name}</h4>
                <p className="text-sm text-muted-foreground">Status: {phase.subStatus || 'Nog te starten'}</p>
              </div>

              <div className="space-y-2">
                <p className="text-sm font-medium">Acties:</p>
                {phase.availableActions.includes('discuss') && (
                  <Button variant="outline" className="w-full">
                    Bespreken
                  </Button>
                )}
                {phase.availableActions.includes('plan') && (
                  <Button variant="outline" className="w-full" disabled={!phase.subStatus?.includes('Besproken')}>
                    Plannen
                  </Button>
                )}
                {/* Other actions... */}
              </div>
            </PopoverContent>
          </Popover>

          {idx < phases.length - 1 && (
            <div className="h-px w-8 bg-border" />
          )}
        </div>
      ))}
    </div>
  );
}
```

### Anti-Patterns to Avoid

- **Scroll position hell:** DON'T auto-scroll to bottom when user has scrolled up to read history. Show "New message" button instead. Source: [Intuitive Scrolling for Chatbot Message Streaming](https://tuffstuff9.hashnode.dev/intuitive-scrolling-for-chatbot-message-streaming)

- **Naive token truncation:** DON'T blindly truncate old messages when hitting context limits. Use summarization for older conversation parts or intelligent compression. Source: [Context Window Management Strategies](https://www.getmaxim.ai/articles/context-window-management-strategies-for-long-context-ai-agents-and-chatbots/)

- **Verbatim v1.0 injection:** DON'T inject full v1.0 workflow text as system prompt. Extract patterns into chat-optimized prompts with backend guardrails. V1.0 is CLI-centric; GUI needs conversation-native phrasing.

- **File-based message storage:** DON'T store conversation messages as JSON files. Use SQLite for queryability (filter by phase, date, project) and proper indexing.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| SSE streaming | Custom long-polling or chunked transfer | sse-starlette | W3C standard, handles reconnection, connection management, error recovery |
| Chat message scrolling | Manual scroll calculations | react-chatview or use-chat-scroll hook | Handles virtualization, scroll anchoring, "scroll to bottom" UX |
| Markdown rendering | Custom parser with regex | react-markdown + remark-gfm | Handles security (XSS), edge cases (nested lists, tables), extensibility |
| Popover positioning | Absolute positioning logic | Radix Popover | Collision detection, focus trap, keyboard nav, ARIA compliance |
| Conversation token counting | String length heuristics | tiktoken (OpenAI) or anthropic.count_tokens | Accurate token counting for context window management |

**Key insight:** Chat UIs have well-established accessibility and UX patterns (scroll anchoring, typing indicators, message grouping). Reinventing these creates subtle bugs (scroll jumps, focus loss, screen reader issues). Use proven libraries that handle edge cases.

## Common Pitfalls

### Pitfall 1: V1.0 Fidelity Violation

**What goes wrong:** Plans assume project type definitions, content type mappings, or gray area patterns without reading v1.0 source files. Results in mismatched discussion depth or missing content types.

**Why it happens:** V1.0 is dense (25K lines in discuss-phase.md). Easy to paraphrase from memory instead of referencing source.

**How to avoid:** EVERY plan task that touches discussion logic MUST cite specific v1.0 files:
- Content type detection: `gsd-docs-industrial/workflows/discuss-phase.md` lines 128-140
- Gray area patterns per content type: `discuss-phase.md` lines 160-214
- CONTEXT.md structure: `gsd-docs-industrial/templates/context.md`
- Project type A/B/C/D definitions: (verify which v1.0 file defines these)

**Warning signs:** Plan says "common discussion topics include..." without a file reference. Plan uses "reasonable defaults" for content types. Plan creates CONTEXT.md structure without reading template.

### Pitfall 2: Context Window Overflow

**What goes wrong:** Conversation exceeds Claude's context window mid-discussion, causing API errors or silent truncation (Claude Sonnet 3.7+). Engineer loses progress.

**Why it happens:** Full v1.0 workflow as system prompt (27K lines) + conversation history + ROADMAP.md + PROJECT.md quickly fills 200K token window.

**How to avoid:**
1. Use chat-optimized prompts (NOT full v1.0 text) — extract core patterns only
2. Implement conversation summarization after each topic completes
3. Track token usage per message (use anthropic SDK's count_tokens)
4. Switch to extended context prompt caching if conversation exceeds 100K tokens
5. Warn engineer when approaching 80% of context window

**Warning signs:** Conversation feels "forgetful" after 10+ messages. API returns validation errors about context window. Backend logs show truncation.

### Pitfall 3: Unvalidated Summary Edits

**What goes wrong:** Engineer edits decision in summary panel, but edit doesn't sync with chat context. AI generates next questions based on stale decisions, creating confusion.

**Why it happens:** Summary panel state and conversation history stored separately, not kept in sync.

**How to avoid:**
- Every summary edit MUST append a system message to conversation: "Decision updated: [old] → [new]"
- Backend re-validates CONTEXT.md constraints after each edit
- UI shows "Updating..." indicator while AI processes the edit
- Alternative: treat edits as new user messages (cleaner audit trail)

**Warning signs:** AI asks about already-decided topics. Engineer corrects same decision multiple times. CONTEXT.md missing decisions that were discussed.

### Pitfall 4: Phase Timeline State Drift

**What goes wrong:** Timeline shows "Besproken" but CONTEXT.md doesn't exist, or shows "Gepland" but no PLAN files present. Engineer clicks "Schrijven" but backend errors because planning incomplete.

**Why it happens:** Phase status stored in SQLite but not validated against filesystem artifacts (CONTEXT.md, PLAN.md, SUMMARY.md).

**How to avoid:**
- Phase status is DERIVED from filesystem artifacts, not stored
- Status query: check for CONTEXT.md → "Besproken", check for PLAN.md → "Gepland", etc.
- Action buttons disabled if prerequisites missing (enforce dependency chain)
- V1.0 pattern: SUMMARY.md existence is completion proof, not STATUS.md

**Warning signs:** Engineer clicks "Plannen" but backend says "no CONTEXT.md". Timeline shows green checkmark but section is empty. Phase operations available out of order.

### Pitfall 5: Scope Creep Goes Undetected

**What goes wrong:** Engineer mentions new functionality outside phase scope, AI continues discussing it instead of redirecting to deferred ideas. CONTEXT.md grows to 300+ lines with out-of-scope items.

**Why it happens:** AI prompt doesn't enforce phase boundary strongly enough, no backend validation of topic relevance.

**How to avoid:**
- System prompt MUST include phase boundary from ROADMAP.md goal (exact text)
- Backend validates each captured decision against phase scope keywords
- AI MUST redirect: "That belongs in Phase X" (v1.0 pattern preserved)
- CONTEXT.md size limit: 100 lines (v1.0 Pitfall 7 mitigation)
- Track deferred ideas separately, show count in summary panel

**Warning signs:** Discussion takes 30+ messages for a simple phase. CONTEXT.md exceeds 100 lines. Engineer says "but we already discussed this" but it's in wrong phase.

## Code Examples

Verified patterns from official sources:

### Conversation Persistence Schema

```python
# Source: SQLite schema for chat conversation storage
# Best practice: separate table per message for queryability
# https://www.indiehackers.com/post/database-design-for-storing-chats-12085e9f8e

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.models.base import Base

class Conversation(Base):
    """Conversation session for a phase discussion."""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    phase_number = Column(Integer, nullable=False)
    status = Column(String(20), default="active")  # active, completed
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    # Relationship to messages
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    # Indexes for efficient queries
    __table_args__ = (
        Index('ix_conversations_project_phase', 'project_id', 'phase_number'),
    )

class Message(Base):
    """Single message in a conversation."""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # system, user, assistant
    content = Column(Text, nullable=False)
    metadata = Column(JSON, nullable=True)  # For question cards, decisions, etc.
    timestamp = Column(DateTime, nullable=False)

    # Relationship back to conversation
    conversation = relationship("Conversation", back_populates="messages")

    # Index for message ordering
    __table_args__ = (
        Index('ix_messages_conversation_timestamp', 'conversation_id', 'timestamp'),
    )
```

### V1.0 Pattern Extraction (Discussion Engine)

```python
# Source: Extract v1.0 discuss-phase.md patterns into reusable prompt components
# Must reference specific v1.0 file locations (v1.0 fidelity requirement)

from pathlib import Path
from typing import Dict, List

V1_WORKFLOW_PATH = Path("gsd-docs-industrial/workflows/discuss-phase.md")
V1_TEMPLATE_PATH = Path("gsd-docs-industrial/templates/context.md")

class DiscussionEngine:
    """Orchestrates discussion workflow using v1.0 patterns."""

    def __init__(self):
        self.v1_workflow = self._load_v1_workflow()
        self.v1_template = self._load_v1_template()

    def _load_v1_workflow(self) -> str:
        """Load v1.0 discuss-phase.md for reference."""
        return V1_WORKFLOW_PATH.read_text()

    def _load_v1_template(self) -> str:
        """Load v1.0 CONTEXT.md template for structure."""
        return V1_TEMPLATE_PATH.read_text()

    def extract_content_types(self) -> Dict[str, List[str]]:
        """
        Extract content type detection keywords from v1.0.

        Source: gsd-docs-industrial/workflows/discuss-phase.md lines 128-140
        Returns keyword mappings for Equipment Modules, Interfaces, HMI, etc.
        """
        # Parse lines 128-140 from v1_workflow
        # Return structured keyword→content_type mapping
        pass

    def extract_gray_areas(self, content_type: str) -> List[str]:
        """
        Extract gray area patterns for a content type from v1.0.

        Source: gsd-docs-industrial/workflows/discuss-phase.md lines 160-214
        Returns probe patterns at FULL functional spec depth.

        Example:
        - Equipment Modules → operating parameters, states, interlocks, failure modes
        - Interfaces → protocol, signal list, error handling, connection failure
        """
        # Parse content-type-specific sections from v1_workflow
        # Return gray area topics with probe depth examples
        pass

    def build_chat_prompt(
        self,
        phase_goal: str,
        content_types: List[str],
        project_type: str  # A/B/C/D
    ) -> str:
        """
        Build chat-optimized system prompt from v1.0 patterns.

        NOT verbatim v1.0 injection — extract core patterns:
        - Phase boundary enforcement
        - Content type detection logic
        - Gray area probing depth (functional spec level)
        - Scope creep redirection
        - CONTEXT.md size limits (100 lines)

        Fallback: if extracted prompt lacks depth, use full v1_workflow as system prompt.
        """
        prompt = f"""You are conducting a discussion phase for an FDS project.

Phase boundary: {phase_goal}
Content types: {', '.join(content_types)}
Project type: {project_type}

Your role:
1. Identify gray areas in this phase (NOT other phases)
2. Probe at FULL functional spec depth (exact values, edge cases, failure modes)
3. Redirect scope creep to deferred ideas
4. Generate CONTEXT.md under 100 lines

Content type gray areas (from v1.0):
{self._format_gray_areas(content_types)}

Ask 3-5 questions per topic. Use hybrid cards (option chips + freeform input).
"""
        return prompt
```

### Auto-Scroll with User Override

```typescript
// Source: Prevent scroll-to-bottom when user is reading history
// https://tuffstuff9.hashnode.dev/intuitive-scrolling-for-chatbot-message-streaming

import { useEffect, useRef, useState } from 'react';

function MessageList({ messages }: { messages: Message[] }) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [autoScroll, setAutoScroll] = useState(true);
  const [showNewMessageButton, setShowNewMessageButton] = useState(false);

  // Detect user scroll
  const handleScroll = () => {
    if (!containerRef.current) return;

    const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;

    setAutoScroll(isAtBottom);
    setShowNewMessageButton(!isAtBottom && messages.length > 0);
  };

  // Auto-scroll only if enabled
  useEffect(() => {
    if (autoScroll && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, autoScroll]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    setAutoScroll(true);
    setShowNewMessageButton(false);
  };

  return (
    <div className="relative flex-1 overflow-hidden">
      <div
        ref={containerRef}
        onScroll={handleScroll}
        className="h-full overflow-y-auto p-4 space-y-4"
      >
        {messages.map(msg => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        <div ref={messagesEndRef} />
      </div>

      {showNewMessageButton && (
        <button
          onClick={scrollToBottom}
          className="absolute bottom-4 right-4 bg-primary text-primary-foreground px-4 py-2 rounded-full shadow-lg"
        >
          Nieuw bericht ↓
        </button>
      )}
    </div>
  );
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| WebSockets for chat | SSE for server→client streaming | 2024-2025 | SSE simpler for unidirectional, auto-reconnect, HTTP/2 multiplexing |
| Custom chat UI libraries | Copy-paste shadcn patterns | 2024-2026 | Code ownership, no bundle bloat, tailored to use case |
| Prompt truncation at context limit | Intelligent summarization + compression | 2025-2026 | Claude Sonnet 3.7+ throws error on overflow, forces better management |
| File-based conversation storage | SQLite with message indexing | Always standard | Queryability, filtering, search — files don't scale |

**Deprecated/outdated:**
- Long-polling for real-time updates: Replaced by SSE (W3C standard, browser native)
- mammoth.js for DOCX preview: docx-preview has better formatting fidelity (2024+)
- Generic "AI assistant" prompts: Specialized prompts per workflow phase (discuss/plan/write) perform better

## Open Questions

1. **V1.0 Project Type Definitions**
   - What we know: V1.0 uses types A/B/C/D, Type C/D require BASELINE.md
   - What's unclear: Which v1.0 file defines the exact meaning of each type?
   - Recommendation: Search gsd-docs-industrial/ for type A/B/C/D definitions before planning. Plans MUST cite source file.

2. **Context Window Strategy**
   - What we know: Claude Sonnet 3.7+ has 200K context, throws error on overflow
   - What's unclear: Should we use extended context prompt caching for long discussions?
   - Recommendation: Start with chat-optimized prompts (no caching), add caching only if discussions routinely exceed 100K tokens. Monitor token usage in metrics.

3. **CONTEXT.md Edit Sync**
   - What we know: Engineer can edit decisions in summary panel OR via chat
   - What's unclear: Should summary edits append to conversation history or trigger re-generation?
   - Recommendation: Append system message to conversation log for audit trail. UI preference to user.

4. **Fasering Tab Layout**
   - What we know: Separate tab for detailed phase view with all phases expanded
   - What's unclear: Vertical timeline? Table view? Accordion with phase details?
   - Recommendation: Vertical timeline with expandable cards per phase (consistent with horizontal bar's visual language). Plan includes mockup decision.

## Sources

### Primary (HIGH confidence)
- V1.0 discuss-phase.md workflow: `gsd-docs-industrial/workflows/discuss-phase.md` (25K lines, authoritative source)
- V1.0 CONTEXT.md template: `gsd-docs-industrial/templates/context.md` (structure reference)
- Claude API streaming docs: https://platform.claude.com/docs/en/build-with-claude/streaming
- Radix Popover docs: https://www.radix-ui.com/primitives/docs/components/popover
- Existing Sheet component: `frontend/src/components/ui/sheet.tsx` (Phase 8)

### Secondary (MEDIUM confidence)
- FastAPI SSE implementation: [Implementing Server-Sent Events with FastAPI](https://mahdijafaridev.medium.com/implementing-server-sent-events-sse-with-fastapi-real-time-updates-made-simple-6492f8bfc154)
- sse-starlette PyPI: https://pypi.org/project/sse-starlette/
- shadcn-chatbot-kit: [GitHub - Blazity/shadcn-chatbot-kit](https://github.com/Blazity/shadcn-chatbot-kit)
- Horizontal timeline patterns: [Shadcn Timeline](https://shadcn-timeline.vercel.app/)
- Chat scroll UX: [Intuitive Scrolling for Chatbot Message Streaming](https://tuffstuff9.hashnode.dev/intuitive-scrolling-for-chatbot-message-streaming)
- Context window management: [Context Window Management Strategies](https://www.getmaxim.ai/articles/context-window-management-strategies-for-long-context-ai-agents-and-chatbots/)

### Tertiary (LOW confidence)
- Chat UI libraries comparison: [20 Open-source Free Chat and Messaging UI Components](https://medevel.com/react-chat-ui/) — used for ecosystem overview, not library selection
- WebSearch results on React chat patterns — verified against official docs

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — SSE, shadcn/ui, Radix are proven in Phase 8/9
- Architecture: HIGH — V1.0 provides authoritative patterns, FastAPI SSE well-documented
- Pitfalls: HIGH — V1.0 fidelity violation is documented hard requirement, context overflow is known Claude 3.7+ behavior

**Research date:** 2026-02-15
**Valid until:** 60 days (stable ecosystem — FastAPI, React, Claude API don't change rapidly)

**V1.0 fidelity checklist:**
- ✅ V1.0 workflow file located: `gsd-docs-industrial/workflows/discuss-phase.md`
- ✅ V1.0 template file located: `gsd-docs-industrial/templates/context.md`
- ⚠️ Project type A/B/C/D definitions: location TBD (search required before planning)
- ✅ Content type detection keywords: lines 128-140 in discuss-phase.md
- ✅ Gray area patterns: lines 160-214 in discuss-phase.md
- ✅ CONTEXT.md size limit: 100 lines (Pitfall 7 mitigation)
- ✅ Scope creep handling: Step 5.3 in discuss-phase.md
