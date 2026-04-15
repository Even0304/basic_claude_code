"""Session management for saving and loading conversations."""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from kimi_code.cost_tracker import CostSummary
from kimi_code.models import Message, ToolCall, ToolResult


@dataclass
class SessionMetadata:
    """Metadata about a saved session."""

    session_id: str
    created_at: str  # ISO format datetime
    updated_at: str  # ISO format datetime
    agent_name: str
    model: str
    total_turns: int
    total_tokens: int
    total_cost: float
    prompt: str  # First user message


class SessionManager:
    """Manages saving and loading conversation sessions."""

    def __init__(self, sessions_dir: Optional[Path] = None):
        """Initialize session manager.

        Args:
            sessions_dir: Directory to store sessions (default: ~/.kimi/sessions)
        """
        if sessions_dir is None:
            sessions_dir = Path.home() / ".kimi" / "sessions"

        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def save_session(
        self,
        session_id: str,
        messages: list[Message],
        agent_name: str,
        model: str,
        cost_summary: CostSummary,
        metadata: Optional[dict] = None,
    ) -> Path:
        """Save a session to disk.

        Args:
            session_id: Unique session identifier
            messages: Conversation messages
            agent_name: Name of the agent
            model: LLM model used
            cost_summary: Cost information
            metadata: Additional metadata

        Returns:
            Path to the saved session file
        """
        # Find first user message for prompt
        first_prompt = next(
            (msg.content for msg in messages if msg.role == "user"),
            "Unknown",
        )
        if isinstance(first_prompt, list):
            first_prompt = str(first_prompt)

        # Create session metadata
        now = datetime.now().isoformat()
        session_meta = SessionMetadata(
            session_id=session_id,
            created_at=now,
            updated_at=now,
            agent_name=agent_name,
            model=model,
            total_turns=len([m for m in messages if m.role == "user"]),
            total_tokens=cost_summary.total_tokens,
            total_cost=cost_summary.total_cost,
            prompt=str(first_prompt)[:200],
        )

        # Serialize messages
        messages_data = []
        for msg in messages:
            msg_dict = {
                "role": msg.role,
                "content": msg.content,
                "tool_calls": [asdict(tc) for tc in msg.tool_calls],
                "tool_results": [asdict(tr) for tr in msg.tool_results],
            }
            messages_data.append(msg_dict)

        # Create session file
        session_file = self.sessions_dir / f"{session_id}.json"
        session_data = {
            "metadata": asdict(session_meta),
            "messages": messages_data,
            "custom": metadata or {},
        }

        with open(session_file, "w") as f:
            json.dump(session_data, f, indent=2)

        return session_file

    def load_session(self, session_id: str) -> Optional[dict]:
        """Load a saved session.

        Args:
            session_id: Session identifier

        Returns:
            Session data or None if not found
        """
        session_file = self.sessions_dir / f"{session_id}.json"

        if not session_file.exists():
            return None

        try:
            with open(session_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading session {session_id}: {e}")
            return None

    def list_sessions(self) -> list[SessionMetadata]:
        """List all saved sessions.

        Returns:
            List of session metadata
        """
        sessions = []

        for session_file in self.sessions_dir.glob("*.json"):
            try:
                with open(session_file, "r") as f:
                    data = json.load(f)
                    meta_dict = data.get("metadata", {})
                    meta = SessionMetadata(**meta_dict)
                    sessions.append(meta)
            except Exception:
                pass

        # Sort by updated_at descending
        sessions.sort(key=lambda s: s.updated_at, reverse=True)
        return sessions

    def delete_session(self, session_id: str) -> bool:
        """Delete a saved session.

        Args:
            session_id: Session identifier

        Returns:
            True if deleted, False if not found
        """
        session_file = self.sessions_dir / f"{session_id}.json"

        if not session_file.exists():
            return False

        try:
            session_file.unlink()
            return True
        except Exception as e:
            print(f"Error deleting session {session_id}: {e}")
            return False

    def restore_messages(self, session_data: dict) -> list[Message]:
        """Restore messages from session data.

        Args:
            session_data: Session data from load_session

        Returns:
            List of Message objects
        """
        messages = []

        for msg_dict in session_data.get("messages", []):
            tool_calls = [
                ToolCall(**tc) for tc in msg_dict.get("tool_calls", [])
            ]
            tool_results = [
                ToolResult(**tr) for tr in msg_dict.get("tool_results", [])
            ]

            msg = Message(
                role=msg_dict["role"],
                content=msg_dict["content"],
                tool_calls=tool_calls,
                tool_results=tool_results,
            )
            messages.append(msg)

        return messages

    def format_session_info(self, session: SessionMetadata) -> str:
        """Format session info for display.

        Args:
            session: Session metadata

        Returns:
            Formatted string
        """
        created = datetime.fromisoformat(session.created_at)
        return (
            f"[{session.session_id}] {session.agent_name} | "
            f"Model: {session.model} | "
            f"Tokens: {session.total_tokens:,} | "
            f"Cost: ${session.total_cost:.4f} | "
            f"Created: {created.strftime('%Y-%m-%d %H:%M')} | "
            f"Prompt: {session.prompt[:50]}..."
        )
