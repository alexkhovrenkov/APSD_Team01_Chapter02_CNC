# Prompts and logs – run protocol (applies to Mode I here and to Mode II in 06)

Each AI attempt is one folder `runs/<UTC>_mode<I|II>_<part>/`:

| File | Written by | Contents |
|---|---|---|
| `prompt.md` | `build-prompt` | the exact text pasted into the chat |
| `input_manifest.json` | `build-prompt` | SHA-256 of the template, config, dialect file, manifest (Mode II) and attachment (Mode I); preflight problems; accepted deviations |
| `isolation_check.json` | `build-prompt` | results of the automatic isolation checks |
| `reply.txt` | operator | the complete reply, copied from the chat |
| `response_raw.txt` | `import-response` | byte copy of the reply (write-once) |
| `run_meta.json` | `import-response` | provider, model name as shown in the selector, interface, date, operator, modalities, settings, hashes, extracted files |

## Isolation protocol (what can and cannot be shown)

1. **Automatic, provable** (`isolation_check.json`). The prompt contains no evaluation-reference content and no line of a
   human baseline program. Mode I contains no manifest content. Mode II contains no drawing file and no process hints.
   The shared config and template contain no reference dimension of the part.
2. **Procedural, documented by the operator.** Use a **new** claude.ai conversation for every attempt, outside any
   Project, with memory/chat-history features off, and attach only the file listed in `input_manifest.json`. Record
   this in `run_meta.json` (`conversation_ref`, `interface`). The team account holds earlier chats about this project
   (Chapter 1 noted the same), so the separation of the chat context **cannot be proven technically**. Report it as a
   controlled procedure, not as proven isolation.
3. Never paste the baseline, the manifest (in Mode I), the drawing (in Mode II), the reference files or the other mode's
   output into an attempt's conversation. Corrections go in a follow-up message in the same conversation and are
   archived as a revision with `author-type AI`.

Status 2026-11-26: `runs/` is empty. `build-prompt` currently stops at preflight (Part B inputs and baselines are missing).
