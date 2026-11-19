#!/usr/bin/env python3
"""
Process a Claude data export into a migration package.

Ported from the processing engine of github.com/ukogan/claude-migration-assistant (MIT).

Usage:
  # Personal export (ZIP from Settings > Privacy > Export Data)
  python3 process_export.py --zip export.zip --out migration-package

  # Admin team export (folder with conversations.json, users.json, memories.json, projects.json)
  python3 process_export.py --admin-dir ./admin-export --list-users
  python3 process_export.py --admin-dir ./admin-export --user <uuid-or-email> --out migration-package

Outputs (in --out):
  summary.md, context-document.md, memory-import-script.txt,
  conversations/index.json, conversations/recent/*.md, conversations/archive/*.md,
  artifacts/index.json, artifacts/*,
  projects/ (admin mode only), memory-from-admin.md (admin mode, if present)
"""
import argparse
import json
import os
import re
import secrets
import sys
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

# ---------------------------------------------------------------- parsing

def normalize_sender(s):
    s = (s or "").lower()
    if s in ("human", "user"):
        return "human"
    if s in ("assistant", "bot", "claude"):
        return "assistant"
    if s in ("system", "tool"):
        return "system"
    return s or "human"


def parse_content_item(item):
    if not isinstance(item, dict):
        return None
    t = item.get("type")
    if t == "text":
        return {"type": "text", "text": item.get("text") or ""}
    if t == "thinking":
        return {"type": "thinking", "thinking": item.get("thinking") or item.get("text") or ""}
    if t == "tool_use":
        return {"type": "tool_use", "name": item.get("name") or "", "id": item.get("id") or "",
                "input": item.get("input") or {}}
    if t == "tool_result":
        return {"type": "tool_result", "name": item.get("name") or "",
                "content": item.get("content") or [], "is_error": item.get("is_error", False)}
    return item


def parse_message(obj):
    if not isinstance(obj, dict):
        return None
    author = obj.get("author") if isinstance(obj.get("author"), dict) else {}
    msg = {
        "uuid": obj.get("uuid") or obj.get("id") or "",
        "sender": normalize_sender(obj.get("sender") or obj.get("role") or author.get("role") or ""),
        "text": obj.get("text") or "",
        "content": [],
        "created_at": obj.get("created_at") or obj.get("createdAt") or "",
    }
    if msg["sender"] == "system":
        return None
    c = obj.get("content")
    if isinstance(c, list):
        msg["content"] = [x for x in (parse_content_item(i) for i in c) if x]
    elif isinstance(c, str):
        msg["content"] = [{"type": "text", "text": c}]
    if not msg["content"] and msg["text"]:
        msg["content"] = [{"type": "text", "text": msg["text"]}]
    if not msg["text"] and msg["content"]:
        msg["text"] = "\n".join(i.get("text", "") for i in msg["content"] if i.get("type") == "text")
    return msg


def parse_conversation(obj):
    if not isinstance(obj, dict):
        return None
    proj = obj.get("project") if isinstance(obj.get("project"), dict) else {}
    conv = {
        "uuid": obj.get("uuid") or obj.get("id") or "",
        "name": obj.get("name") or obj.get("title") or "Untitled",
        "created_at": obj.get("created_at") or obj.get("createdAt") or "",
        "updated_at": obj.get("updated_at") or obj.get("updatedAt") or obj.get("created_at") or "",
        "project_uuid": obj.get("project_uuid") or proj.get("uuid"),
        "chat_messages": [],
    }
    msgs = obj.get("chat_messages") or obj.get("messages") or obj.get("mapping") or []
    if isinstance(msgs, dict):  # mapping-style tree
        msgs = [n.get("message") for n in msgs.values() if isinstance(n, dict) and n.get("message")]
    conv["chat_messages"] = sorted(
        (m for m in (parse_message(x) for x in msgs) if m), key=lambda m: m["created_at"] or "")
    return conv


def parse_conversations(raw):
    if not isinstance(raw, list):
        sys.exit("Expected conversations to be a JSON array")
    convs = [c for c in (parse_conversation(x) for x in raw) if c]
    convs.sort(key=lambda c: c["updated_at"] or "", reverse=True)
    return convs


def message_text(msg):
    texts = [i.get("text", "") for i in msg.get("content", []) if i.get("type") == "text"]
    return "\n".join(texts) if texts else (msg.get("text") or "")


def has_artifacts(conv):
    return any(
        any(i.get("type") == "tool_use" and i.get("name") == "artifacts" for i in m["content"])
        or "<antArtifact" in (m.get("text") or "")
        for m in conv["chat_messages"])

# ---------------------------------------------------------------- readers

def read_export_zip(path):
    with zipfile.ZipFile(path) as z:
        names = [n for n in z.namelist() if not n.endswith("/")]
        target = next((n for n in names if n.split("/")[-1] == "conversations.json"), None)
        if not target:
            for n in names:
                if n.endswith(".json") and z.read(n)[:100].decode("utf-8", "ignore").strip().startswith("["):
                    target = n
                    break
        if not target:
            sys.exit("Could not find conversations.json in the ZIP. Is this a Claude data export?")
        return json.loads(z.read(target).decode("utf-8"))


def read_admin_dir(path):
    data = {"users": [], "conversations": [], "memories": [], "projects": []}
    for key in data:
        f = os.path.join(path, f"{key}.json")
        if os.path.exists(f):
            with open(f, encoding="utf-8") as fh:
                parsed = json.load(fh)
            if not isinstance(parsed, list):
                sys.exit(f"{key}.json should contain a JSON array")
            data[key] = parsed
        elif key == "conversations":
            sys.exit("conversations.json is required in the admin export folder")
        else:
            print(f"warning: optional {key}.json not found", file=sys.stderr)
    data["conversations"] = [c for c in data["conversations"]
                             if isinstance(c.get("account"), dict) and c["account"].get("uuid")]
    if not data["conversations"]:
        sys.exit("No conversations with account.uuid found. Is this an admin export?")
    return data


def build_user_list(data):
    counts = Counter(c["account"]["uuid"] for c in data["conversations"])
    known = {u.get("uuid") for u in data["users"]}
    out = [{"uuid": u.get("uuid"), "full_name": u.get("full_name") or "Unknown",
            "email_address": u.get("email_address") or "", "conversations": counts.get(u.get("uuid"), 0)}
           for u in data["users"]]
    out += [{"uuid": u, "full_name": "[Departed User]", "email_address": "", "conversations": n}
            for u, n in counts.items() if u not in known]
    return sorted(out, key=lambda u: -u["conversations"])


def filter_by_user(data, who):
    uuid = who
    for u in data["users"]:
        if who and who.lower() in ((u.get("email_address") or "").lower(), (u.get("uuid") or "").lower()):
            uuid = u["uuid"]
    convs = [c for c in data["conversations"] if c["account"]["uuid"] == uuid]
    mem = next((m.get("conversations_memory") for m in data["memories"] if m.get("account_uuid") == uuid), None)
    projs = [p for p in data["projects"] if isinstance(p.get("creator"), dict) and p["creator"].get("uuid") == uuid]
    return convs, mem, projs

# ---------------------------------------------------------------- artifacts

TYPE_TO_EXT = {"application/vnd.ant.react": "jsx", "text/html": "html", "text/css": "css",
               "text/javascript": "js", "text/x-python": "py", "text/python": "py",
               "text/markdown": "md", "text/plain": "txt", "image/svg+xml": "svg",
               "application/vnd.ant.mermaid": "mmd", "application/json": "json"}
LANG_TO_EXT = {"python": "py", "javascript": "js", "typescript": "ts", "jsx": "jsx", "tsx": "tsx",
               "html": "html", "css": "css", "sql": "sql", "bash": "sh", "shell": "sh", "ruby": "rb",
               "go": "go", "rust": "rs", "java": "java", "c": "c", "cpp": "cpp", "c++": "cpp",
               "json": "json", "yaml": "yaml", "yml": "yaml", "toml": "toml", "xml": "xml",
               "markdown": "md", "swift": "swift", "kotlin": "kt"}
ART_RE = re.compile(r"<antArtifact\s+([^>]*)>([\s\S]*?)</antArtifact>")


def ext_for(t, lang):
    if TYPE_TO_EXT.get(t):
        return TYPE_TO_EXT[t]
    if lang:
        l = lang.lower()
        if l in LANG_TO_EXT:
            return LANG_TO_EXT[l]
        if len(l) <= 5 and l.isalpha():
            return l
    return "txt"


def slugify(s, n=50):
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")[:n] or "untitled"


def attr(s, name):
    m = re.search(rf'{name}="([^"]*)"', s, re.I)
    return m.group(1) if m else None


def extract_artifacts(convs):
    arts = {}
    for conv in convs:
        for msg in conv["chat_messages"]:
            if msg["sender"] != "assistant":
                continue
            for it in msg["content"]:
                if it.get("type") != "tool_use" or it.get("name") != "artifacts" or not it.get("input"):
                    continue
                inp = it["input"]
                aid = inp.get("id") or inp.get("version_uuid") or "gen-" + secrets.token_hex(4)
                a = {"id": aid, "title": inp.get("title") or "Untitled", "type": inp.get("type") or "text/plain",
                     "language": inp.get("language"), "content": inp.get("content") or "",
                     "sourceConversationId": conv["uuid"], "sourceConversationName": conv["name"],
                     "timestamp": msg["created_at"], "extractionMethod": "structured"}
                prev = arts.get(aid)
                # Artifacts updated via "update"/"rewrite" commands may lack content; keep the fullest latest
                if not prev or (a["content"] and a["timestamp"] >= prev["timestamp"]):
                    arts[aid] = a
            for m in ART_RE.finditer(msg.get("text") or ""):
                ident = attr(m.group(1), "identifier")
                if not ident or ident in arts:
                    continue
                arts[ident] = {"id": ident, "title": attr(m.group(1), "title") or "Untitled",
                               "type": attr(m.group(1), "type") or "text/plain",
                               "language": attr(m.group(1), "language"), "content": m.group(2).strip(),
                               "sourceConversationId": conv["uuid"], "sourceConversationName": conv["name"],
                               "timestamp": msg["created_at"], "extractionMethod": "regex"}
    out = []
    for a in arts.values():
        a["extension"] = ext_for(a["type"], a["language"])
        a["fileName"] = f"{slugify(a['title'])}-{a['id'][:6]}.{a['extension']}"
        out.append(a)
    return out

# ---------------------------------------------------------------- generators

STOP_WORDS = set("""the a an is are was were be been being have has had do does did will would could should may
might shall can to of in for on with at by from as into through during before after above below between out off
over under again then once here there when where why how all each every both few more most other some such no not
only own same so than too very just because but and or if while about up down this that these those i me my we our
you your it its they them their what which who whom he she him her please thanks thank like want need know think
also well make use get go see new one two way thing much many right good bad first last long great little old big
high different small large next early young important public people time year years work still back even give day
help line turn keep show let say said look find come made take put tell try hand point end part start able sure
using used something don doesn didn won wouldn couldn shouldn isn aren wasn weren haven hasn hadn really actually
going yes yeah okay hey hi hello ok""".split())

TECH_TERMS = """react vue angular svelte nextjs next.js nuxt gatsby python javascript typescript rust golang java
kotlin swift ruby php scala elixir haskell clojure dart flutter node nodejs express fastapi django flask rails spring
docker kubernetes k8s terraform ansible pulumi aws lambda s3 ec2 dynamodb cloudfront sqs sns gcp azure firebase
supabase vercel netlify railway postgres postgresql mysql mongodb redis sqlite elasticsearch prisma drizzle sequelize
mongoose typeorm git github gitlab bitbucket ci/cd jenkins circleci tailwind tailwindcss css sass styled-components
emotion webpack vite esbuild rollup parcel turbopack graphql rest grpc websocket api oauth jwt llm gpt claude openai
anthropic langchain embeddings rag tensorflow pytorch scikit-learn pandas numpy jupyter testing jest pytest cypress
playwright selenium figma sketch storybook agile scrum kanban jira notion linear confluence stripe twilio sendgrid
auth0 clerk nginx apache caddy cloudflare markdown json yaml toml xml csv linux macos windows ubuntu debian vim
neovim vscode emacs cursor bash zsh powershell tmux sql nosql timeseries influxdb clickhouse bigquery kafka rabbitmq
nats celery prometheus grafana datadog sentry pagerduty""".split() + [
    "machine learning", "deep learning", "neural network", "vector database", "design system"]

PREF_PATTERNS = [
    (r"i (?:always |usually |prefer to |like to )([^.!?\n]{10,120})", "Preference"),
    (r"please (?:always |never |make sure to )([^.!?\n]{10,120})", "Instruction"),
    (r"i(?:'m| am) (?:a |an |the )([^.!?\n]{5,80})", "Identity"),
    (r"i work (?:at|for|on|with|in) ([^.!?\n]{5,80})", "Work"),
    (r"my (?:team|company|role|job|title|name) (?:is|are) ([^.!?\n]{5,80})", "Identity"),
]
MEMORY_PATTERNS = [
    r"i (?:always |usually |prefer to |like to )([^.!?\n]{10,180})",
    r"please (?:always |never |make sure to |remember to )([^.!?\n]{10,180})",
    r"i(?:'m| am) (?:a |an |the )([^.!?\n]{5,150})",
    r"i work (?:at|for|on|with|in) ([^.!?\n]{5,150})",
    r"my (?:team|company|role|job|title|name|stack|tech) (?:is|are|includes?) ([^.!?\n]{5,150})",
    r"i(?:'ve| have) been (?:working on|building|developing|using) ([^.!?\n]{5,150})",
    r"(?:call me|i go by|my name is) ([^.!?\n]{2,80})",
    r"i (?:use|prefer|rely on) ([^.!?\n]{3,100}) (?:for|to|when)",
]


def fmt_date(iso):
    if not iso:
        return "Unknown"
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).strftime("%b %-d, %Y")
    except ValueError:
        return iso


def human_messages(convs):
    for c in convs:
        for m in c["chat_messages"]:
            if m["sender"] == "human":
                yield c, message_text(m)


def context_document(convs):
    conv_terms = defaultdict(set)
    texts = []
    for c, t in human_messages(convs):
        texts.append(t)
        toks = re.sub(r"[^a-z0-9\s.#+-]", " ", t.lower()).split()
        conv_terms[c["uuid"]].update(x for x in toks if len(x) > 2 and x not in STOP_WORDS)
    tc = Counter(term for terms in conv_terms.values() for term in terms)
    topics = sorted(((t, n) for t, n in tc.items() if n >= 2 and n < len(convs) * 0.8), key=lambda x: -x[1])[:25]
    blob = " ".join(texts).lower()
    tech = sorted(((t, len(re.findall(rf"\b{re.escape(t)}\b", blob))) for t in TECH_TERMS), key=lambda x: -x[1])
    tech = [x for x in tech if x[1]][:30]
    prefs = {}
    for t in texts:
        for pat, kind in PREF_PATTERNS:
            for m in re.finditer(pat, t, re.I):
                fact = re.sub(r"[.!?]+$", "", m.group(1).strip())
                if not 10 <= len(fact) <= 150:
                    continue
                k = re.sub(r"\s+", " ", fact.lower())
                prefs.setdefault(k, {"text": m.group(0).strip(), "type": kind, "count": 0})["count"] += 1
    prefs = sorted(prefs.values(), key=lambda p: -p["count"])[:15]
    recent = [c for c in convs if len(c["chat_messages"]) > 4][:20]
    dates = sorted(c["created_at"] for c in convs if c["created_at"])

    L = ["# Migration Context Document", "",
         f"**Generated:** {datetime.now().date()}",
         f"**Source:** {len(convs)} conversations, {sum(len(c['chat_messages']) for c in convs)} messages",
         f"**Date range:** {fmt_date(dates[0] if dates else '')} to {fmt_date(dates[-1] if dates else '')}", "",
         "> Machine-generated from conversation text. It supplements but does not replace the",
         "> manual memory capture. Review and edit for accuracy before uploading to the new account.",
         "", "---", ""]
    if topics:
        L += ["## Frequently Discussed Topics", ""] + [f"- **{t}** - mentioned across {n} conversations" for t, n in topics] + [""]
    if tech:
        L += ["## Technologies and Tools", ""] + [f"- **{t}** ({n} mentions)" for t, n in tech] + [""]
    if prefs:
        L += ["## Detected Preferences and Patterns", ""] + [f'- [{p["type"]}] "{p["text"]}"' for p in prefs] + [""]
    if recent:
        L += ["## Recent Conversation Summaries", ""]
        for c in recent:
            first = next((message_text(m) for m in c["chat_messages"] if m["sender"] == "human"), "")
            L += [f"### {c['name']} ({fmt_date(c['updated_at'])})", f"*{len(c['chat_messages'])} messages*", ""]
            if first:
                L += [f"> {first[:200].replace(chr(10), ' ')}{'...' if len(first) >= 200 else ''}", ""]
    return "\n".join(L)


def memory_script(convs):
    facts = {}
    for _, t in human_messages(convs):
        for pat in MEMORY_PATTERNS:
            for m in re.finditer(pat, t, re.I):
                fact = re.sub(r"^[,.\s]+|[,.\s]+$", "", re.sub(r"\s+", " ", m.group(0))).strip()
                if not 10 <= len(fact) <= 200:
                    continue
                k = fact.lower()
                facts.setdefault(k, {"text": fact, "count": 0})["count"] += 1
    top = sorted(facts.values(), key=lambda f: -f["count"])[:30]
    if not top:
        return "# Memory Import Script\n\n# No strong preference patterns were detected.\n# Use the manual memory capture prompt instead.\n"
    head = ["# Memory Import Script", "#", "# Paste into a new conversation in the new account, 5-10 at a time.",
            "# Review each one -- skip any that are outdated or incorrect.", ""]
    return "\n".join(head + [f"Please remember: {f['text']}" for f in top]) + "\n"


def strip_artifact_tags(text):
    return ART_RE.sub(lambda m: "\n```\n" + m.group(2).strip() + "\n```\n", text)


def conversation_md(c):
    L = [f"# {c['name']}", "", f"**Created:** {fmt_date(c['created_at'])}",
         f"**Updated:** {fmt_date(c['updated_at'])}", f"**Messages:** {len(c['chat_messages'])}", "", "---", ""]
    for m in c["chat_messages"]:
        L += [f"## {'Human' if m['sender'] == 'human' else 'Claude'}", ""]
        wrote = False
        for it in m["content"]:
            if it.get("type") == "text" and it.get("text"):
                L += [strip_artifact_tags(it["text"]), ""]
                wrote = True
            elif it.get("type") == "tool_use" and it.get("name") == "artifacts" and it.get("input"):
                inp = it["input"]
                L += [f"**Artifact: {inp.get('title') or 'Untitled'}**", "```" + (inp.get("language") or ""),
                      (inp.get("content") or "").strip(), "```", ""]
                wrote = True
        if not wrote and m.get("text"):
            L += [strip_artifact_tags(m["text"]), ""]
        L.append("")
    return "\n".join(L)


def summary_md(convs, arts):
    dates = sorted(c["created_at"] for c in convs if c["created_at"])
    L = ["# Migration Summary", "", f"**Generated:** {datetime.now().date()}", "", "## Statistics", "",
         "| Metric | Value |", "|--------|-------|",
         f"| Total conversations | {len(convs)} |",
         f"| Total messages | {sum(len(c['chat_messages']) for c in convs)} |",
         f"| Conversations with artifacts | {sum(1 for c in convs if has_artifacts(c))} |",
         f"| Extracted artifacts | {len(arts)} |",
         f"| Date range | {fmt_date(dates[0] if dates else '')} to {fmt_date(dates[-1] if dates else '')} |",
         "", "## Top Conversations (by message count)", ""]
    for c in sorted(convs, key=lambda c: -len(c["chat_messages"]))[:10]:
        L.append(f"- **{c['name']}** ({len(c['chat_messages'])} messages, {fmt_date(c['updated_at'])})")
    L += ["", "## What Did NOT Transfer", "",
          "- Interactive artifact rendering (re-create in the new account)",
          "- Claude's synthesized memory (use the memory capture prompt)",
          "- Project structure (recreate manually)", "- Style preferences and feature toggles", ""]
    return "\n".join(L)


def safe_name(name, n=60):
    return re.sub(r"\s+", "-", re.sub(r"[^a-zA-Z0-9\s_-]", "", name or "untitled")).lower()[:n] or "untitled"


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def unique(path):
    base, ext = os.path.splitext(path)
    i = 2
    while os.path.exists(path):
        path = f"{base}-{i}{ext}"
        i += 1
    return path

# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--zip", help="personal export ZIP")
    src.add_argument("--admin-dir", help="folder of admin export JSON files")
    ap.add_argument("--user", help="admin mode: user uuid or email to extract")
    ap.add_argument("--list-users", action="store_true", help="admin mode: list users and exit")
    ap.add_argument("--out", default="migration-package")
    ap.add_argument("--recent-days", type=int, default=90)
    a = ap.parse_args()

    memory, projects = None, []
    if a.zip:
        raw = read_export_zip(a.zip)
    else:
        data = read_admin_dir(a.admin_dir)
        if a.list_users or not a.user:
            for u in build_user_list(data):
                print(f"{u['conversations']:>6}  {u['uuid']}  {u['full_name']}  {u['email_address']}")
            if not a.user:
                print("\nRe-run with --user <uuid or email>.", file=sys.stderr)
            return
        raw, memory, projects = filter_by_user(data, a.user)
        if not raw:
            sys.exit(f"No conversations found for user {a.user}")

    convs = parse_conversations(raw)
    arts = extract_artifacts(convs)
    out = a.out
    os.makedirs(out, exist_ok=True)

    cutoff = (datetime.now(timezone.utc) - timedelta(days=a.recent_days)).isoformat()
    index = []
    for c in convs:
        bucket = "recent" if (c["updated_at"] or c["created_at"]) >= cutoff else "archive"
        p = unique(os.path.join(out, "conversations", bucket, safe_name(c["name"]) + ".md"))
        write(p, conversation_md(c))
        index.append({"uuid": c["uuid"], "name": c["name"], "created_at": c["created_at"],
                      "updated_at": c["updated_at"], "message_count": len(c["chat_messages"]),
                      "has_artifacts": has_artifacts(c), "project_uuid": c["project_uuid"],
                      "file": os.path.relpath(p, out)})
    write(os.path.join(out, "conversations", "index.json"), json.dumps(index, indent=2))

    if arts:
        for art in arts:
            write(os.path.join(out, "artifacts", art["fileName"]), art["content"])
        write(os.path.join(out, "artifacts", "index.json"), json.dumps(
            [{k: v for k, v in art.items() if k != "content"} | {"contentLength": len(art["content"])} for art in arts],
            indent=2))

    if projects:
        write(os.path.join(out, "projects", "index.json"), json.dumps(
            [{"name": p.get("name"), "description": p.get("description") or "", "docsCount": len(p.get("docs") or [])}
             for p in projects], indent=2))
        for p in projects:
            d = os.path.join(out, "projects", safe_name(p.get("name")))
            readme = f"# {p.get('name')}\n\n"
            if p.get("description"):
                readme += p["description"] + "\n\n"
            if p.get("prompt_template"):
                readme += "## Custom Instructions\n\n" + p["prompt_template"] + "\n"
            write(os.path.join(d, "README.md"), readme)
            for doc in p.get("docs") or []:
                write(os.path.join(d, os.path.basename(doc.get("filename") or "doc.txt")), doc.get("content") or "")

    if memory:
        write(os.path.join(out, "memory-from-admin.md"), "# Memory (from admin export)\n\n" + memory + "\n")

    write(os.path.join(out, "summary.md"), summary_md(convs, arts))
    write(os.path.join(out, "context-document.md"), context_document(convs))
    write(os.path.join(out, "memory-import-script.txt"), memory_script(convs))

    print(f"Wrote {out}: {len(convs)} conversations, {len(arts)} artifacts, {len(projects)} projects"
          + (", admin memory" if memory else ""))


if __name__ == "__main__":
    main()
