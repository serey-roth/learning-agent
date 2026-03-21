from dataclasses import dataclass, field

MAX_HISTORY_TURNS = 6
RECENT_QUERIES_LIMIT = 6

@dataclass
class SessionState:
    history: list[dict] = field(default_factory=list)
    recent_queries: list[str] = field(default_factory=list)

    def add(self, role: str, content: str) -> None:
        self.history.append({"role": role, "content": content})
        if len(self.history) > MAX_HISTORY_TURNS * 2:
            self.history = self.history[-(MAX_HISTORY_TURNS * 2):]

    def add_query(self, query: str) -> None:
        self.recent_queries.append(query)
        if len(self.recent_queries) > RECENT_QUERIES_LIMIT:
            self.recent_queries = self.recent_queries[-RECENT_QUERIES_LIMIT:]