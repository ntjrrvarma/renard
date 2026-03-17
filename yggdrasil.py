import chromadb
from chromadb.utils import embedding_functions
import uuid
from datetime import datetime


class Yggdrasil:
    """
    The World Tree — memory engine of the empire.
    Every agent draws from its roots.
    Every conversation becomes part of its branches.
    Renard is its first and primary user.
    """

    def __init__(self, agent_name: str):
        self.client = chromadb.PersistentClient(path="./memory")
        self.ef = embedding_functions.DefaultEmbeddingFunction()

        # each agent gets their own branch of the tree
        self.collection = self.client.get_or_create_collection(
            name=agent_name.lower().replace(" ", "_"),
            embedding_function=self.ef
        )

    def remember(self, user_msg: str, agent_reply: str, context: str = "general"):
        """Plant a new memory into the tree"""
        self.collection.add(
            documents=[
                f"Mr. R said: {user_msg}\n"
                f"Renard replied: {agent_reply}"
            ],
            metadatas=[{
                "timestamp": datetime.now().isoformat(),
                "context": context,
                "user_msg_preview": user_msg[:120]
            }],
            ids=[str(uuid.uuid4())]
        )

    def recall(self, query: str, n: int = 4) -> str:
        """Pull relevant memories from the tree"""
        total = self.count()

        if total == 0:
            return "No memories stored yet. This is the beginning."

        results = self.collection.query(
            query_texts=[query],
            n_results=min(n, total)
        )

        if not results["documents"][0]:
            return "Nothing relevant found in memory."

        memories = []
        for doc, meta in zip(
            results["documents"][0],
            results["metadatas"][0]
        ):
            date = meta["timestamp"][:16].replace("T", " at ")
            memories.append(f"[{date}]\n{doc}")

        return "\n\n---\n\n".join(memories)

    def count(self) -> int:
        return self.collection.count()

    def recent(self, n: int = 3) -> str:
        """Pull the most recent memories regardless of topic"""
        total = self.count()
        if total == 0:
            return "No memories yet."

        try:
            results = self.collection.get(
                include=["documents", "metadatas"],
                limit=min(n * 5, total)
            )
        except Exception:
            # fallback to semantic query when get is unavailable
            results = self.collection.query(
                query_texts=["recent conversation"],
                n_results=min(n, total)
            )

        docs = []
        metas = []
        if "documents" in results and results["documents"]:
            docs = results["documents"]
            metas = results.get("metadatas", [])

        if not docs:
            return "Nothing recent found."

        # output from query may be list-of-lists, flatten if necessary
        if isinstance(docs[0], list):
            docs = docs[0]
            metas = metas[0] if metas and isinstance(metas[0], list) else []

        ranked = []
        for doc, meta in zip(docs, metas):
            ts = meta.get("timestamp") if isinstance(meta, dict) else None
            try:
                ts_val = datetime.fromisoformat(ts) if ts else datetime.min
            except Exception:
                ts_val = datetime.min
            ranked.append((ts_val, doc, meta))

        ranked.sort(key=lambda item: item[0], reverse=True)
        top = ranked[:n]

        memories = []
        for ts_val, doc, meta in top:
            if isinstance(meta, dict) and "timestamp" in meta:
                date = meta["timestamp"][:16].replace("T", " at ")
            else:
                date = ts_val.strftime("%Y-%m-%d %H:%M")
            memories.append(f"[{date}]\n{doc}")

        return "\n\n---\n\n".join(memories)