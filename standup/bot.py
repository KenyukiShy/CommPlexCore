"""
standup/standup_bot.py — Arc Fleet Async Standup System

Async standups: M W F Su Tu Th Sa (daily)
Sync required:  Once/week near weekend (Friday + Sunday integration window)
Integration windows expand: week → month → 2mo → 3mo → biannual → annual

GoF Patterns:
  - Mediator:  StandupBot coordinates all team communication (no direct member-to-member)
  - Observer:  Members subscribe; bot notifies on standup time / deliverables due
  - Memento:   Each standup session captures state (checkins, blockers, commits)
  - Iterator:  Processes member responses in sequence
  - Template:  run_standup() defines the fixed flow; members fill in their slots

Team profiles:
  MSCS/ML Lead  (Kenyon)   — system design, GCP, Vertex, high-level architecture
  Kinda Skilled (Charles)  — API integrations, Twilio, Playwright
  Exposed/Learning (Justin)— QA, testing, documentation, low-code tools
  Theory-Smart  (4th)      — GoF patterns, prompt engineering, logic design

LLM Intermediary Mode:
  When --llm-mode is set, the bot:
    1. Sends each member a structured prompt via ntfy/Pushover
    2. Members reply by text/voice (via STT)
    3. LLM synthesizes a standup summary
    4. Summary pushed to all members
    5. Blockers extracted and assigned

Schedule (cron style):
    Monday:    09:00  Standup + Week Kickoff
    Tuesday:   09:00  Daily standup
    Wednesday: 09:00  Mid-week check + integration review
    Thursday:  09:00  Daily standup
    Friday:    09:00  Standup + Code Check-in + Week Review
    Saturday:  10:00  Integration window (async — lighter)
    Sunday:    10:00  Pre-week integration review + planning

Usage:
    python standup/standup_bot.py --run          # Run standup for today
    python standup/standup_bot.py --notify       # Send reminder push now
    python standup/standup_bot.py --summary      # Show last standup summary
    python standup/standup_bot.py --schedule     # Show upcoming schedule
    python standup/standup_bot.py --llm-review   # LLM code review request
    python standup/standup_bot.py --install-cron # Install cron jobs
"""

from __future__ import annotations
import os
import sys
import json
import logging
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# ── State file ────────────────────────────────────────────────────────────────
STANDUP_DIR  = Path("standup/sessions")
STANDUP_DIR.mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════════════
# TEAM MEMBER PROFILES
# ═══════════════════════════════════════════════════════

class TeamMember:
    """
    Profile for each team member.
    Used by StandupBot (GoF: Mediator) to route notifications.
    """
    def __init__(self, id: str, name: str, role: str, skill_level: str,
                 email: str = None, phone: str = None,
                 ntfy_topic: str = None, pushover_key: str = None,
                 fcm_token: str = None, timezone: str = "America/Chicago"):
        self.id            = id
        self.name          = name
        self.role          = role
        self.skill_level   = skill_level  # expert | skilled | learning | theory
        self.email         = email
        self.phone         = phone
        self.ntfy_topic    = ntfy_topic or f"arc-fleet-{id}"
        self.pushover_key  = pushover_key
        self.fcm_token     = fcm_token
        self.timezone      = timezone

    def to_dict(self) -> Dict:
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    def __repr__(self):
        return f"<TeamMember {self.name} [{self.role}/{self.skill_level}]>"


def load_team() -> List[TeamMember]:
    """Load team from environment or config."""
    return [
        TeamMember(
            id="kenyon", name="Kenyon Jones", role="Admin / Owner",
            skill_level="expert",
            email=os.getenv("ADMIN_EMAIL", "kjonesmle@gmail.com"),
            phone=os.getenv("SENDER_PHONE", "7018705235"),
            ntfy_topic=os.getenv("NTFY_TOPIC_KENYON", "arc-fleet-kenyon"),
            pushover_key=os.getenv("PUSHOVER_USER_KENYON", ""),
            fcm_token=os.getenv("FCM_TOKEN_KENYON", ""),
        ),
        TeamMember(
            id="charles", name="Charles", role="Integrator / Dev",
            skill_level="skilled",
            email=os.getenv("DEV_EMAIL_CHARLES", ""),
            ntfy_topic=os.getenv("NTFY_TOPIC_CHARLES", "arc-fleet-charles"),
            pushover_key=os.getenv("PUSHOVER_USER_CHARLES", ""),
            fcm_token=os.getenv("FCM_TOKEN_CHARLES", ""),
        ),
        TeamMember(
            id="justin", name="Justin", role="QA / Learning",
            skill_level="learning",
            email=os.getenv("DEV_EMAIL_JUSTIN", ""),
            ntfy_topic=os.getenv("NTFY_TOPIC_JUSTIN", "arc-fleet-justin"),
            pushover_key=os.getenv("PUSHOVER_USER_JUSTIN", ""),
            fcm_token=os.getenv("FCM_TOKEN_JUSTIN", ""),
        ),
        # 4th member (theory-smart) — fill in when known
        # TeamMember(id="theory", name="...", role="Prompt Engineer / Logic", skill_level="theory", ...),
    ]


# ═══════════════════════════════════════════════════════
# STANDUP SESSION — GoF Memento
# ═══════════════════════════════════════════════════════

class StandupSession:
    """
    GoF Memento — captures and restores standup state.
    Saved as JSON in standup/sessions/YYYY-MM-DD.json
    """

    def __init__(self, date: str = None, day_name: str = None,
                 session_type: str = "daily"):
        self.date         = date or datetime.now().strftime("%Y-%m-%d")
        self.day_name     = day_name or datetime.now().strftime("%A")
        self.session_type = session_type  # daily | integration | kickoff | review
        self.checkins:    Dict[str, Dict] = {}
        self.blockers:    List[str] = []
        self.decisions:   List[str] = []
        self.action_items: List[Dict] = []
        self.llm_summary: str = ""
        self.created_at:  str = datetime.now().isoformat()
        self.closed_at:   Optional[str] = None
        self.path = STANDUP_DIR / f"{self.date}.json"

    def add_checkin(self, member_id: str, done: str, doing: str,
                    blocked: str = None, mood: int = None):
        """Record a member's standup check-in."""
        self.checkins[member_id] = {
            "done":    done,
            "doing":   doing,
            "blocked": blocked or "",
            "mood":    mood,  # 1-5
            "ts":      datetime.now().isoformat(),
        }
        if blocked:
            self.blockers.append(f"{member_id}: {blocked}")

    def add_action(self, description: str, owner: str, due: str = None):
        self.action_items.append({
            "description": description,
            "owner":       owner,
            "due":         due or "next standup",
            "status":      "open",
        })

    def close(self, llm_summary: str = ""):
        self.closed_at  = datetime.now().isoformat()
        self.llm_summary = llm_summary

    def save(self):
        self.path.write_text(json.dumps(self.__dict__, indent=2, default=str))
        logger.info(f"[Standup] Session saved: {self.path}")

    @classmethod
    def load(cls, date: str) -> Optional["StandupSession"]:
        path = STANDUP_DIR / f"{date}.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text())
        session = cls.__new__(cls)
        session.__dict__.update(data)
        session.path = path
        return session

    @classmethod
    def today(cls) -> Optional["StandupSession"]:
        return cls.load(datetime.now().strftime("%Y-%m-%d"))

    def to_markdown(self) -> str:
        lines = [
            f"# Standup — {self.day_name} {self.date} [{self.session_type.upper()}]",
            "",
        ]
        for member_id, ci in self.checkins.items():
            lines += [
                f"## {member_id.title()}",
                f"**Done:** {ci.get('done', '—')}",
                f"**Doing:** {ci.get('doing', '—')}",
                f"**Blocked:** {ci.get('blocked') or 'Nothing'}",
                "",
            ]
        if self.blockers:
            lines += ["## Blockers", *[f"- {b}" for b in self.blockers], ""]
        if self.action_items:
            lines += ["## Action Items"]
            for a in self.action_items:
                lines.append(f"- [{a['owner']}] {a['description']} (due: {a['due']})")
            lines.append("")
        if self.llm_summary:
            lines += ["## LLM Summary", self.llm_summary, ""]
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════
# SCHEDULE — when standups happen
# ═══════════════════════════════════════════════════════

SCHEDULE = {
    "Monday":    {"time": "09:00", "type": "kickoff",     "sync": False},
    "Tuesday":   {"time": "09:00", "type": "daily",       "sync": False},
    "Wednesday": {"time": "09:00", "type": "midweek",     "sync": False},
    "Thursday":  {"time": "09:00", "type": "daily",       "sync": False},
    "Friday":    {"time": "09:00", "type": "review",      "sync": True},  # SYNC week review
    "Saturday":  {"time": "10:00", "type": "integration", "sync": False},
    "Sunday":    {"time": "10:00", "type": "planning",    "sync": True},  # SYNC pre-week
}

INTEGRATION_WINDOWS = [
    "Week 1",     # daily standups
    "Week 2",     # daily standups
    "Week 3-4",   # weekly integration (Friday/Sunday merge)
    "Month 2-3",  # bi-weekly integration
    "Month 4-6",  # monthly integration
    "Month 7-12", # bi-annual review
    "Year 2+",    # annual release cadence
]


# ═══════════════════════════════════════════════════════
# STANDUP BOT — GoF Mediator
# ═══════════════════════════════════════════════════════

class StandupBot:
    """
    GoF Mediator — coordinates all team standup communication.
    Members don't communicate directly; everything goes through the bot.

    LLM intermediary mode:
      - Bot sends structured prompt to each member
      - Member responds (text/voice)
      - LLM synthesizes summary
      - Summary distributed to team
    """

    STANDUP_PROMPT = """Arc Fleet Standup Check-in

Please answer briefly:
1. DONE: What did you complete since last standup?
2. DOING: What are you working on today?
3. BLOCKED: Anything blocking you? (or "nothing")
4. MOOD: Rate 1-5 (1=bad, 5=great)

Reply with your 4 answers numbered. Example:
1. Finished Playwright form-filler test
2. Setting up Bland.ai call script
3. Nothing
4. 4
"""

    LLM_SUMMARY_PROMPT = """You are the Arc Fleet project Standup Bot.
Summarize the following team check-ins into:
1. Key accomplishments (2-3 bullets)
2. Today's priorities (2-3 bullets)
3. Blockers that need attention (if any)
4. One line of encouragement for the team

Be concise. Use plain English. No fluff.

Check-ins:
{checkins}
"""

    def __init__(self):
        self.team = load_team()
        try:
            from modules.notifier import NotifierModule
            self._notifier = NotifierModule()
        except Exception:
            self._notifier = None

    def _notify_member(self, member: TeamMember, title: str, message: str,
                       priority: str = "high") -> bool:
        """Send notification to a specific member."""
        if not self._notifier:
            logger.warning(f"[Standup] No notifier. Would send to {member.name}: {title}")
            return False

        # Use member-specific ntfy topic if available
        try:
            from modules.notifier import NtfyBackend
            ntfy = NtfyBackend()
            if member.ntfy_topic:
                original = ntfy.topic
                ntfy.topic = member.ntfy_topic
                result = ntfy.send(title, message, priority=priority, tags=["clipboard"])
                ntfy.topic = original
                return result
        except Exception as e:
            logger.error(f"[Standup] Notify error for {member.name}: {e}")
        return False

    def send_standup_reminders(self, day: str = None) -> Dict[str, bool]:
        """Push standup reminder to all team members."""
        day = day or datetime.now().strftime("%A")
        schedule = SCHEDULE.get(day, {})
        session_type = schedule.get("type", "daily")
        is_sync = schedule.get("sync", False)

        sync_note = " — SYNC REQUIRED today" if is_sync else ""
        title   = f"📋 Arc Fleet Standup — {day}{sync_note}"
        message = self.STANDUP_PROMPT + (
            f"\n⚠️ This is a SYNC session — please be available at {schedule.get('time', '09:00')}."
            if is_sync else ""
        )

        results = {}
        for member in self.team:
            sent = self._notify_member(member, title, message)
            results[member.id] = sent
            logger.info(f"[Standup] Reminder → {member.name}: {'sent' if sent else 'FAILED'}")

        return results

    def llm_synthesize(self, session: StandupSession) -> str:
        """
        Use LLM to synthesize a standup summary from check-ins.
        GoF: Strategy — can swap Gemini / Claude / GPT here.
        """
        if not session.checkins:
            return "(No check-ins received)"

        checkin_text = ""
        for member_id, ci in session.checkins.items():
            checkin_text += (
                f"\n{member_id.upper()}:\n"
                f"  Done: {ci.get('done', '—')}\n"
                f"  Doing: {ci.get('doing', '—')}\n"
                f"  Blocked: {ci.get('blocked') or 'Nothing'}\n"
                f"  Mood: {ci.get('mood', '?')}/5\n"
            )

        prompt = self.LLM_SUMMARY_PROMPT.format(checkins=checkin_text)

        # Try Gemini first (GCP native), fallback to Claude API
        try:
            import vertexai
            from vertexai.generative_models import GenerativeModel
            project = os.getenv("GCP_PROJECT_ID", "arc-fleet-campaign")
            region  = os.getenv("GCP_REGION", "us-central1")
            vertexai.init(project=project, location=region)
            model   = GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.warning(f"[Standup LLM] Gemini failed ({e}), trying Claude API ...")

        try:
            import anthropic
            client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))
            msg = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}],
            )
            return msg.content[0].text
        except Exception as e:
            logger.error(f"[Standup LLM] Claude API failed: {e}")
            return "(LLM summary unavailable)"

    def run_standup(self, day: str = None, interactive: bool = False) -> StandupSession:
        """
        GoF Template Method — run today's standup.
        Steps: remind → collect → synthesize → distribute → save.
        """
        day = day or datetime.now().strftime("%A")
        schedule = SCHEDULE.get(day, {})
        session = StandupSession(session_type=schedule.get("type", "daily"), day_name=day)

        print(f"\n{'='*60}")
        print(f"  Arc Fleet Standup — {day} {session.date}")
        print(f"  Type: {session.session_type.upper()}")
        if schedule.get("sync"):
            print(f"  ⚠️  SYNC SESSION — synchronous participation required")
        print(f"{'='*60}\n")

        if interactive:
            # Interactive CLI check-in
            for member in self.team:
                print(f"\n--- {member.name} ({member.role}) ---")
                done    = input("  Done (since last standup): ").strip()
                doing   = input("  Doing today: ").strip()
                blocked = input("  Blocked? (Enter for 'nothing'): ").strip() or "nothing"
                mood_s  = input("  Mood 1-5: ").strip()
                mood    = int(mood_s) if mood_s.isdigit() else None
                session.add_checkin(member.id, done, doing, blocked, mood)

        # LLM synthesis
        if session.checkins:
            print("\n[LLM] Synthesizing standup summary ...")
            summary = self.llm_synthesize(session)
            session.close(summary)
            print(f"\n{summary}")

            # Distribute summary
            if self._notifier:
                self._notifier.alert_team(
                    f"Standup Summary — {day}",
                    summary[:500],
                )

        session.save()
        return session

    def llm_code_review(self, pr_description: str, files_changed: List[str] = None,
                         requester: str = None) -> str:
        """
        Request LLM code review. Notifies team + runs automated review.
        GoF: Memento — captures review state for async consumption.
        """
        prompt = f"""You are reviewing Arc Fleet code changes.
Apply GoF patterns, SOLID principles, and arc-fleet conventions.

PR: {pr_description}
Files: {', '.join(files_changed or ['(not specified)'])}

Review for:
1. GoF pattern compliance (Observer, Strategy, Proxy, etc.)
2. SOLID violations
3. Missing tests
4. Module registry compliance (does new code register in modules/__init__.py?)
5. Type hints and docstrings
6. Security (credentials in code?)

Format: PASS/WARN/FAIL for each, then 3-5 specific suggestions.
"""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))
            msg = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}],
            )
            review = msg.content[0].text
        except Exception as e:
            review = f"(LLM review unavailable: {e})"

        # Notify team
        if self._notifier:
            self._notifier.review_request(
                requester or "StandupBot",
                f"Code review ready: {pr_description[:80]}",
            )

        return review

    def print_schedule(self):
        """Show upcoming standup schedule."""
        print(f"\n{'='*60}")
        print("  Arc Fleet Standup Schedule")
        print(f"{'='*60}")
        today = datetime.now().strftime("%A")
        for day, info in SCHEDULE.items():
            marker = " ← TODAY" if day == today else ""
            sync   = " [SYNC]" if info.get("sync") else ""
            print(f"  {day:<12} {info['time']}  {info['type'].upper():<12}{sync}{marker}")
        print(f"\n  Integration Windows:")
        for i, w in enumerate(INTEGRATION_WINDOWS, 1):
            print(f"    {i}. {w}")
        print()

    def install_cron(self):
        """Install cron jobs for standup reminders."""
        script_path = Path(__file__).resolve()
        python      = sys.executable

        cron_entries = []
        for day, info in SCHEDULE.items():
            h, m = info["time"].split(":")
            # Convert day to cron day number (Mon=1 ... Sun=0)
            day_map = {
                "Monday": "1", "Tuesday": "2", "Wednesday": "3",
                "Thursday": "4", "Friday": "5", "Saturday": "6", "Sunday": "0"
            }
            dn = day_map[day]
            cron_entries.append(
                f"{m} {h} * * {dn} {python} {script_path} --notify "
                f">> /tmp/arc-fleet-standup.log 2>&1"
            )

        cron_block = "\n".join(cron_entries)
        print(f"\nAdd these lines to crontab (run 'crontab -e'):\n")
        print(cron_block)
        print(f"\nOr run:  (crontab -l; echo '{cron_entries[0]}') | crontab -")
        print(f"(Repeat for each day, or copy all at once)")

        try:
            result = subprocess.run(
                ["crontab", "-l"], capture_output=True, text=True
            )
            existing = result.stdout
            if "arc-fleet-standup" not in existing:
                new_cron = existing + "\n" + cron_block + "\n"
                proc = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE)
                proc.communicate(new_cron.encode())
                print("\n✓ Cron jobs installed!")
            else:
                print("\n⚠ Arc Fleet standup cron already exists. Edit manually if needed.")
        except Exception as e:
            print(f"\n⚠ Could not auto-install cron: {e}. Add manually.")


# ═══════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════

def cli():
    parser = argparse.ArgumentParser(description="Arc Fleet Standup Bot")
    parser.add_argument("--run",          action="store_true", help="Run today's standup (interactive)")
    parser.add_argument("--notify",       action="store_true", help="Send standup reminder push now")
    parser.add_argument("--summary",      action="store_true", help="Show last standup summary")
    parser.add_argument("--schedule",     action="store_true", help="Show standup schedule")
    parser.add_argument("--llm-review",   metavar="PR",        help="Request LLM code review")
    parser.add_argument("--install-cron", action="store_true", help="Install cron reminders")
    parser.add_argument("--day",          default=None,        help="Override day name")
    args = parser.parse_args()

    bot = StandupBot()

    if args.schedule:
        bot.print_schedule()
    elif args.notify:
        results = bot.send_standup_reminders(args.day)
        print(f"Reminders sent: {results}")
    elif args.run:
        session = bot.run_standup(args.day, interactive=True)
        print(f"\n✓ Session saved: {session.path}")
    elif args.summary:
        session = StandupSession.today()
        if session:
            print(session.to_markdown())
        else:
            print("No standup session found for today.")
    elif args.llm_review:
        review = bot.llm_code_review(args.llm_review)
        print(f"\nCode Review:\n{review}")
    elif args.install_cron:
        bot.install_cron()
    else:
        parser.print_help()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    cli()
