# ARCHTICT — Arch Arena
### Think. Play. Build.

An original, browser-based Architecture Day quiz show with a persistent backend, a private host workspace, a public projector screen, and real-time mobile participation.

**Open the “Arch Arena” live preview to play.** The preview is a running application, not a static HTML mockup. For a real event, deploy it on your own persistent server or run it on the venue’s local network.

---

## Quick start

```bash
python -m pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8000 --workers 1
```

Open `http://localhost:8000` on the server computer.

For phones on the same Wi-Fi, open the host workspace using the server’s **LAN IP**, for example `http://192.168.1.50:8000`. The QR code uses that address. A phone cannot reach the server through `localhost`.

Docker deployment is also included:

```bash
docker compose up --build -d
```

Both the database and uploaded images have persistent Docker volumes.

## The four interfaces

| Interface | Location | Purpose |
|---|---|---|
| Host workspace | `/` | Board, teams, scoring, rules, event presets, and history |
| Question manager | Question library in the host sidebar | Create, edit, duplicate, delete, upload imagery, edit the final prompt |
| Projector | `/projector?room=ROOM-CODE` | Public board, questions, timer, scores, and results; no private answer before reveal |
| Participant | `/join?room=ROOM-CODE` | Join a team, submit answers, lock captain wagers, and follow scores |

Use **Presentation mode** and **Invite players** in the top bar rather than typing URLs.

## Included

- Original architectural visual identity: warm neutral surfaces, technical linework, muted photographic cards, and terracotta accents.
- **100 starter questions across 16 categories**, plus an editable final question.
- Balanced, randomized category boards: select 1–6 categories, with one question per enabled difficulty level in each category.
- 100–500 default question values; editable point values and question timers.
- Open answers, multiple choice, true/false, image identification, matching prompts, timelines, estimates, and host-judged drawing/design prompts.
- Original plan, section, elevation, structural, masonry, and landmark illustrations, plus photographic questions.
- Upload building photographs, campus images, event logos, and team logos.
- Up to eight customizable teams; one-person teams support individual competition.
- Separate audience leaderboard with server-scored answers and streak indicators.
- Host scoring, manual adjustments, steal percentage, random or manual double points, optional wrong-answer penalties, and a scoring activity log.
- Four once-per-team power-ups: Blueprint, +10 seconds, Site Analysis, and Team Huddle (+15 seconds).
- 60-second rapid fire, 60-second drawing, and two-minute design challenge.
- Secret final wagers, captain or offline-host entry, manual final judging, and winner celebration.
- QR joining and real Server-Sent Events synchronization.
- Pause/resume, configurable timers, final-five-second countdown, optional synthesized sounds, fullscreen, and mobile layouts.
- Multiple game sets, duplication of event setups, completed history, question-bank export, and results export including question-level response data.
- SQLite persistence, reconnect support, server-side answer filtering, session-based host authorization, request limits, upload validation, and cross-origin mutation protection.

## Host runbook

### 1. Prepare the event

1. Open **Event settings** and enter the event name, university, department, date, color, and optional acknowledgements.
2. Save the private **host recovery key**. Anyone holding this key controls your events. Do not put it on the projector or share it in the audience group.
3. Edit teams and colors in **Teams & players**. Default scores are zero.
4. Review the question library, difficulty, and reference information. Add local campus photographs and event-specific questions.
5. Use **Edit categories** on the board to select up to six categories.
6. Use **Final prompt** in the question library to review or replace the final challenge.

### 2. Set up the screens

- Use an **extended desktop**, not display mirroring.
- Put **Presentation mode** on the projector. Host controls and private answers belong on the host’s laptop.
- Enable fullscreen on the projector. Its board was tested at 1920×1080.
- Click the speaker control on each screen where sound should play. Browsers require interaction before allowing audio.
- Mute the host laptop if only projector audio should be heard.

The projector’s public API and event stream omit the correct answer and explanation before reveal, even if the projector window was opened from the host’s browser.

### 3. Welcome participants

Show **Invite players** or the projector lobby QR code. Players enter a nickname and select a team. Their browser retains an opaque, HTTP-only session cookie so that refreshing or reconnecting does not create a new identity.

Joining is optional: the host can run a complete team competition with no phones.

### 4. Play the board

1. Start the game or click a question value directly.
2. Select the answering team by clicking its score card or using the question’s team selector.
3. The timer starts when the question opens.
4. Use **Correct** to award team points and reveal the answer.
5. Use **Wrong / steal** before reveal to pass the opportunity to the next team. The default steal award is 50%.
6. Use **Reveal answer** if no team earns the question.
7. Choose **Next question** to return to the board.

**Team and audience scores are deliberately separate.** The host judges oral team answers. Audience players earn 100 points for a correct individual answer after reveal. Individual phone answers do not automatically add points to their selected team.

Open-answer audience grading uses normalized exact matching, not AI or semantic grading. Enter accepted alternatives separated by `|`. Conceptual answers, matching, long timelines, and design explanations are best judged as team responses by the host. Numeric estimates use the configured absolute tolerance.

Host scoring remains available after the countdown ends because live verbal answers may have been given just before the deadline. Phone answers are strictly rejected after the server deadline.

### 5. Run special rounds

- **Rapid fire:** the active team has 60 seconds; award +100 for correct, zero for wrong, then select **Next rapid question**. The seed bank has five rapid prompts. Add more in the Speed round category for a longer sequence. No streak multiplier is applied.
- **Draw it:** teams sketch a courtyard house with a wind tower in 60 seconds. Use manual score adjustments for each team.
- **Design challenge:** teams have two minutes to design a desert shelter. Judge creativity, function, sustainability, aesthetics, and presentation, each 0–100. Enter the total as a manual adjustment.
- These are in-person, host-judged creative rounds. The application does not collect or automatically evaluate sketches.

### 6. Finish with a wager

1. Select **Final challenge**.
2. Each team’s first phone participant is its captain and can lock its wager privately. Other participants cannot change that wager.
3. For an offline team, collect a written wager and use **Enter wager** on the host screen.
4. Wagers range from zero to the team’s available non-negative score and cannot be changed once locked.
5. Open the final question once all wagers are locked.
6. Teams write down or present their answers. Reveal the answer, then judge each team correct or incorrect.
7. End the game to save rankings and display the winner.

Wagers are never shown on the public display during collection. Each final wager can be applied only once.

### Keyboard shortcuts

On the host board, outside forms and dialogs:

- **Space:** pause/resume an open timer
- **R:** reveal answer
- **B:** return to the board / skip
- **Escape:** close dialog

## Question schema

Questions are stored as data, not in UI components. `seed.py` supplies new-event defaults; each event stores its own editable library in SQLite.

```json
{
  "id": "unique-id",
  "category": "uae",
  "difficulty": 3,
  "points": 300,
  "type": "choice",
  "question": "Who designed the Louvre Abu Dhabi?",
  "options": ["Jean Nouvel", "Norman Foster", "Frank Gehry", "Zaha Hadid"],
  "correctAnswer": "Jean Nouvel",
  "explanation": "Its dome creates a rain-of-light effect.",
  "image": "",
  "source": "Organizer-reviewed reference",
  "timeLimit": 30,
  "customTimer": true,
  "hint": "Think of a French Pritzker laureate.",
  "tolerance": 0
}
```

Seed questions use the event timer by default. Saving a question in the editor gives it its own timer override. Matching and timeline prompts use text rather than drag-and-drop interaction. Image questions may have choices or accept an open answer.

The visual question assets use opaque filenames to avoid leaking building names or drawing types through their URLs. Uploads are also renamed to random filenames and re-encoded.

## Persistence and recovery

- Live rooms and completed history: `data/game.sqlite`.
- SQLite WAL commits save every mutation before the server acknowledges it.
- Uploaded assets: `static/assets/upload-*.jpg`.
- Timers use absolute server deadlines. A host refresh does not reset a timer.
- A disconnected screen shows a reconnect banner; SSE reconnects and retrieves the current authoritative state.
- Keep the same browser profile to preserve a participant identity. Clearing cookies removes automatic identity recovery.
- Host access can be restored using the private recovery key in **Event settings → Restore host access**.
- Embedded previews may use a different partitioned-cookie context from a standalone tab. Use recovery if moving the host workspace between those contexts.
- An unpaused timer continues during a network interruption or server restart. Pause before planned maintenance.
- Reconnection does not resubmit uncertain or late answers. The server’s stored submission is authoritative.

### Backups

Back up the database with SQLite’s backup API, not by copying only the live main database file while WAL writes are active:

```bash
python - <<'PY'
import sqlite3
with sqlite3.connect('data/game.sqlite') as source:
    with sqlite3.connect('data/game-backup.sqlite') as destination:
        source.backup(destination)
PY
```

Back up uploaded images alongside the database. A database backup does not contain the image bytes.

## Deployment and security boundaries

This is a **single-server event application**, not a managed high-availability service.

- Use **one Uvicorn worker** with this SQLite implementation and in-process request limiting.
- Keep data and uploads on persistent storage. Container-local storage alone is not sufficient.
- Use HTTPS for an internet-facing event. See `nginx.conf.example` for SSE-friendly proxy settings.
- Trust forwarded headers only from your actual reverse proxy. Do not expose a proxy that passes arbitrary client-supplied forwarding headers unchanged.
- Do not put authentication or answer responses in a shared cache. API responses are marked `no-store`.
- Host access is protected by a high-entropy session/recovery secret, not institutional SSO or a password account system.
- Host secrets and participant tokens are stored as hashes in the database. Cookies are HTTP-only; HTTPS cookies are Secure and support partitioned embedded-preview sessions.
- Public clients do not receive the question bank, answer key, unrevealed explanation, raw submissions, or private wagers.
- The server checks ownership, identity, deadlines, pause/reveal state, single submissions, scoring state, and wager bounds.
- Basic request limiting and image size/type validation are included.
- Anonymous joining cannot guarantee one physical person per account across different browsers/devices. Verified student identity, admission approval, and institutional SSO are not included.
- Participant nicknames and submitted answers are event data. Apply your university’s privacy and retention policies.

## Scope and event-readiness notes

- **Not load-tested for a university-size crowd.** There is a 500-participant room cap, but that is a guardrail, not a demonstrated capacity. Rehearse on the intended hardware and network with the expected number of devices.
- The application and all bundled assets work without external APIs once installed. For an internet outage, run the server on the venue LAN in advance. A phone that cannot reach the server cannot submit answers; there is no fully disconnected service-worker mode.
- Image identification includes a starter set, not an exhaustive licensed photo archive. Review imagery and add campus/building photos you have permission to display.
- The question bank is editorial starter content, not a fact-checked academic publication. Review attribution, difficulty, and curriculum fit before publishing your event.
- AI question generation, automated sketch grading, institutional authentication, and distributed multi-server deployment are intentionally not included. No fake AI or simulated real-time functionality is used.
- Sponsors are text acknowledgements; there is an event logo slot, not a multi-logo advertising system.

## Validation

```bash
python tests/test_api.py
```

**44 passing API checks:** default board balance, zero scores, private answer filtering, unauthorized access, identity continuity, duplicate/late/paused submissions, team and audience scoring, steals, used questions, final wager bounds and single application, history, response-performance data, reset, recovery, cross-origin rejection, question CRUD, and editable final prompts.

Optional browser tests require Playwright and a running server:

```bash
pip install playwright
python -m playwright install --with-deps chromium
python tests/browser_smoke.py
python tests/realtime_browser.py
```

The real-time test uses a host, projector, and two independent phone browser contexts. It checks actual synchronization, hidden answers, preservation of unfinished answers during updates, refresh recovery, question creation, and a 1920×1080 projector board without vertical scrolling. These are functional checks, not a load test or independent security audit.

## Project map

```text
server.py                  FastAPI, persistence, sessions, scoring, SSE, uploads
seed.py                    Question/category data and final prompt
static/index.html          Application shell
static/app.js              Host, projector, admin, and mobile interfaces
static/style.css           Original responsive visual system
static/assets/             Local photos, diagrams, fonts, and uploads
data/game.sqlite           Persistent live rooms and game history
tests/                     API and browser checks
Dockerfile / compose.yaml  Persistent single-server deployment
nginx.conf.example         Reverse-proxy example
SOURCES.md                 Asset provenance and reference review notes
```
