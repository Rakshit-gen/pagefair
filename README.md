# pagefair

Scores how fairly an on-call rotation's pain is actually distributed,
instead of just counting pages per engineer.

## The problem

"How many pages did each person get" is the metric everyone tracks and the
metric that's wrong. A quiet week of five sev-4 Slack pings during business
hours and a week with one 3am sev-1 that took two hours to resolve look
identical on a raw page count, and are not remotely the same experience for
the engineer holding the pager. Teams keep discovering an engineer is burnt
out only after they've already said something, because nothing was
measuring the thing that actually predicts it.

PagerDuty and Opsgenie can show this, but only behind their paid analytics
tiers, and only for teams already paying for their full incident platform.
`pagefair` is vendor-agnostic: point it at a CSV export of your incidents
(from PagerDuty, Opsgenie, or a Slack-based process) and it computes the
same kind of severity- and time-weighted burden score without requiring
you to buy or switch platforms just to see it.

## How it works

1. Import incidents: who was paged, severity, when it was paged, when it
   was acknowledged, when it was resolved.
2. Each incident gets a burden score: its severity weight, doubled if it
   paged someone between 22:00 and 07:00, plus a smaller factor for how
   long it took to resolve (a sev-1 that drags on for hours is worse than
   one closed in five minutes).
3. Per engineer, burden scores sum into a rolling total, compared against
   the team average for the same window.
4. Anyone carrying more than 150% of the team's average burden is flagged
   overloaded; under 50% is flagged underloaded. That's the imbalance a
   raw page count hides.

## Stack

- **Backend**: Django + Django REST Framework, SQLite for local/demo use.
- **Frontend**: React + Vite, calling the DRF API directly.

## Running locally

```bash
# backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver

# frontend
cd frontend
npm install
npm run dev
```

## What's not built

No live PagerDuty/Opsgenie webhook ingestion — this reads CSV exports, not
a push integration. No auto-rebalancing of the actual rotation schedule;
it tells you who's overloaded, not how to fix the calendar.
