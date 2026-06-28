Build a premium dark-mode SaaS web application called "Meridian" with the 
tagline "Decision intelligence for customer success teams". This is an AI 
Next Best Action platform for Customer Success Managers.

DESIGN SYSTEM
Background: #08090D
Card surface: #10131A
Card surface hover: #13172000
Border default: rgba(255,255,255,0.07)
Border hover: rgba(255,255,255,0.14)
Accent indigo: #6366F1
Success: #10B981
Danger: #EF4444
Warning: #F59E0B
Text primary: #F1F5F9
Text secondary: #94A3B8
Text muted: #4B5563
Font: Inter — weights 400, 500, 600 only
Card border-radius: 10px
Input border-radius: 8px
No drop shadows — use border colors and background contrast for depth
No emoji anywhere. Use Lucide icons throughout.

LAYOUT
Three-column layout filling the viewport:
- Left sidebar: 256px, fixed height, dark bg #0C0E14 with right border
- Main content: flex-1, padded, vertically scrollable
- Right panel: 288px, fixed height, scrollable, subtle left border

LEFT SIDEBAR
Top section:
  - A small indigo circle (8px) followed by "Meridian" in 17px 600 weight
  - Below: "Decision intelligence" in 11px muted
  - 1px divider

Account section:
  - "ACCOUNT" label in 10px uppercase muted tracking-wider
  - A dark styled <select> dropdown showing account options, each with a 
    small colored dot indicating risk level (red=critical, amber=high, 
    green=low). Default selected: "Acme Corp — Critical"

Transcript section:
  - "MEETING TRANSCRIPT" label in 10px uppercase muted
  - A <textarea> with bg #08090D, 1px border rgba(255,255,255,0.1), 
    border-radius 8px, placeholder "Paste meeting notes, call transcript, 
    or CRM update…", min-height 160px, text 12px, resizable vertically

Action:
  - Full-width button "Analyse account" in #6366F1 bg, white text, 
    13px 500, height 36px, radius 8px. On click: shows spinner, 
    button text changes to "Analysing…"

Bottom:
  - Row: green pulsing dot + "Backend connected" in 11px — left-aligned 
    at the very bottom of sidebar

MAIN CONTENT — TOP: ACCOUNT HEADER BAR
A compact horizontal flex row, no card wrapper:
  - Avatar circle (32px): "AC" initials in 13px 600, bg #1E1F3B, 
    indigo text
  - "Acme Corp" in 15px 600 white
  - Separator dot
  - "CSM: Sarah Chen" in 12px muted
  - Separator dot
  - "Renewal in 47 days" in 12px muted
  - Pushed right via flex: a pill badge "Critical · 84% churn risk" with 
    bg rgba(239,68,68,0.1), border 1px rgba(239,68,68,0.3), 
    text #EF4444, 11px 500

MAIN CONTENT — RISK AND SIGNALS CARD
A card (surface bg, border) with 2 columns side by side:

Left column — circular donut gauge SVG:
  - 120px diameter, stroke-width 10
  - Track: rgba(255,255,255,0.07)
  - Arc fill: gradient from #F59E0B to #EF4444, drawn to 84% of circle
  - Center text: "84%" in 28px 600 white, below it "Churn risk" in 11px muted
  - The arc animates in (draws from 0 to 84%) on load using CSS animation

Right column — signal list:
  - "4 signals detected" in 12px muted, margin-bottom
  - Four signal pills (stacked):
      "No login · 18 days" — bg rgba(239,68,68,0.12), border 
        rgba(239,68,68,0.25), text #EF4444, 6px left colored bar
      "Adoption 0%" — same red styling
      "Renewal threat mentioned" — bg rgba(245,158,11,0.12), 
        border rgba(245,158,11,0.25), text #F59E0B, 6px amber left bar
      "Stakeholder frustration" — amber styling
  - Each pill: 11px, border-radius 6px, padding 4px 10px

MAIN CONTENT — EVIDENCE CARDS
Section header row: "Evidence" in 13px 500 + pill badge "3 sources" 
in indigo (bg rgba(99,102,241,0.15), text #818CF8, 10px)

Three cards in a 3-column grid, equal width:
Each card: surface bg, border, radius 10px, padding 12px
  Top: source badge — "Meeting note" (#818CF8 indigo), 
       "Playbook §3.2" (#A78BFA purple), "CRM profile" (#FB923C amber)
       Each badge: 10px, bg rgba(color, 0.12), matching text, radius 4px
  Middle: 3 lines of evidence text in 12px secondary, line-height 1.5
  Bottom: thin 3px height relevance bar, 
          full width track bg rgba(255,255,255,0.07), 
          fill matching source badge color, border-radius 2px
          Small "92% match" label right-aligned in 10px muted

MAIN CONTENT — MEMORY CONTEXT CARD
Card with 3px left border solid #6366F1:
  Header row: brain/sparkles Lucide icon in indigo + 
    "Memory context" in 13px 500 + 
    "2 similar cases" badge in indigo
  
  Account chips row:
    "Globex Corp" chip (bg rgba(16,185,129,0.1), border rgba(16,185,129,0.2),
     text #10B981, check icon, 11px) and 
    "Initech" chip — same styling
  
  Confidence boost row:
    Labels: "Base 73%" (muted) — horizontal bar — "89% boosted" (green)
    Bar: height 6px, track bg rgba(255,255,255,0.07), 
         base segment gray to 73%, boost segment indigo from 73% to 89%
         Both segments animate in on load
    Below bar: "+16% confidence from memory" in 11px #10B981

MAIN CONTENT — PRIMARY RECOMMENDATION CARD
Card with 1px top border #6366F1 (accent top border only, 
other sides rgba(255,255,255,0.07)):
  
  "RECOMMENDED ACTION" label in 10px uppercase indigo tracking-wider
  
  Title: "Schedule Executive Business Review within 48 hours"
    in 17px 600 white, margin-bottom 8px
  
  Description: "Arrange a VP-level meeting to demonstrate ROI, address 
    reporting module adoption failure, and rebuild executive confidence 
    before the 47-day renewal window closes." 
    in 13px secondary, line-height 1.6
  
  Meta chips row (flex, gap 12px):
    Each chip format: Lucide icon (14px muted) + text (11px muted)
    "89% confidence" | "Est. +31% retention lift" | 
    "Precedents: Globex Corp, Initech"

MAIN CONTENT — ALTERNATIVE ACTIONS
"Alternative actions" in 12px 500 secondary, margin-bottom

Two cards side by side:
  Card 1: "Send personalised re-onboarding offer for reporting module" 
    title 13px 500, description 12px muted 2 lines, 
    bottom-right: "62%" in amber badge
  Card 2: "Send ROI summary with peer benchmarks"
    same format, "51%" badge

MAIN CONTENT — HITL DECISION
"Your decision" in 13px 500, margin-top 16px

Three buttons in a row, gap 8px:
  Accept: bg #10B981, white text "Accept recommendation", 
    Lucide check icon, 13px 500, height 38px, radius 8px, 
    hover: bg #059669, active: scale 0.98
  Modify: bg transparent, border rgba(255,255,255,0.12), 
    text secondary "Modify", Lucide edit icon, same height/radius
    On click → smooth slide-down (max-height transition) of:
      <textarea> placeholder "What would you like to change? 
        e.g. Change to 24-hour timeline, involve CTO instead of VP CS"
        bg #08090D, border rgba(255,255,255,0.1), radius 8px, 
        height 80px, 12px text
      Button "Submit and re-analyse" — indigo, 12px, right-aligned
      After submit: show success row "Updated: [feedback incorporated]" 
        in 12px green with check icon
  Reject: same as Modify styling, red border on hover, "Reject"

Accepted state (after clicking Accept):
  Replace HITL row with: 
  Green checkmark icon + "Recommendation accepted · logged to memory" 
  in 13px green, with a subtle green bg row

RIGHT PANEL — AGENT TRACE
"Agent trace" header with a static green dot (6px, #10B981)
"Completed in 4,438 ms" in 11px muted right-aligned

Vertical timeline — 5 steps with connecting line:
Each step:
  Left: colored pill badge (all-caps, 10px, 500):
    PLANNER — bg rgba(99,102,241,0.2) text #818CF8
    INTERACTION — bg rgba(99,102,241,0.2) text #818CF8  
    KNOWLEDGE — bg rgba(167,139,250,0.2) text #A78BFA
    RISK — bg rgba(245,158,11,0.2) text #F59E0B
    NBA — bg rgba(16,185,129,0.2) text #10B981
  Center: action text in 12px secondary
  Right: timing in 11px muted font-mono

Connecting vertical line between steps: 1px rgba(255,255,255,0.07)

Below trace: collapsible row "Evidence sources (50 chunks)" with a 
chevron toggle, 12px muted, expands to list source names in 11px

Use shadcn/ui for all base components. TypeScript. 
Tailwind CSS with the exact hex values above as custom colors.
The app calls a FastAPI backend at http://localhost:8000 — 
POST /analyze with {account_id, interaction_text} 
and POST /feedback with {request_id, decision, modification_notes}.
Show loading skeleton cards while waiting for API response.
Make it fully responsive down to 1280px wide minimum.