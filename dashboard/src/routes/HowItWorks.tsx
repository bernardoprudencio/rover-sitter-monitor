import { useData } from '../context/DataContext';

const REPO_URL = 'https://github.com/bernardoprudencio/rover-sitter-monitor';

export default function HowItWorks() {
  const { meta } = useData();
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-h1 text-neutral-900">How it works</h1>
        <p className="mt-2 text-body text-neutral-500">
          The data behind this dashboard flows through three stages — ingestion, tagging, and
          publishing. Here's the end-to-end pipeline.
        </p>
      </div>

      <section className="space-y-2 rounded-xl bg-white p-6 shadow-card">
        <div className="flex items-baseline gap-3">
          <span className="font-mono text-h2 text-primary-600">1</span>
          <h2 className="text-h2 text-neutral-900">Ingestion — two sources, two cadences</h2>
        </div>
        <p className="text-body text-neutral-700">
          Two scheduled jobs in GitHub Actions feed a single Google Sheet that backs the dashboard.
        </p>
        <ul className="ml-2 list-disc space-y-2 pl-4 text-body text-neutral-700">
          <li>
            <strong>Reddit, daily at 08:00 UTC.</strong> <code className="font-mono text-caption">rover_monitor.py</code>{' '}
            sends an email digest of new <code className="font-mono text-caption">r/RoverPetSitting</code> posts to
            stakeholders, then <code className="font-mono text-caption">rover_sheet_dump.py</code> appends those
            posts to the <em>Reddit Posts</em> tab of the sheet.
          </li>
          <li>
            <strong>Confluence, weekly on Mondays at 08:00 UTC.</strong>{' '}
            <code className="font-mono text-caption">rover_confluence_dump.py</code> fetches new pages from the{' '}
            <code className="font-mono text-caption">DSN</code> (User Experience) and{' '}
            <code className="font-mono text-caption">PSD</code> (Provider Space) Confluence spaces, applies an
            eligibility filter (doc-type whitelist + provider-audience check), and appends them to the{' '}
            <em>Confluence Research</em> tab.
          </li>
        </ul>
      </section>

      <section className="space-y-2 rounded-xl bg-white p-6 shadow-card">
        <div className="flex items-baseline gap-3">
          <span className="font-mono text-h2 text-primary-600">2</span>
          <h2 className="text-h2 text-neutral-900">Tagging — two stages</h2>
        </div>
        <p className="text-body text-neutral-700">
          Each row gets one or more theme/problem tags from a fixed taxonomy of 13 themes and 107 problems.
          A regex fallback runs at ingest time; a Claude subagent runs periodically to upgrade quality.
        </p>
        <ul className="ml-2 list-disc space-y-2 pl-4 text-body text-neutral-700">
          <li>
            <strong>Stage 1 — keyword fallback (~32% precision).</strong> The ingest scripts call a regex tagger
            (<code className="font-mono text-caption">tag_post</code>) that matches taxonomy keywords against post
            text. Fast and deterministic, but low precision — used so newly ingested rows always land tagged.
          </li>
          <li>
            <strong>Stage 2 — Claude subagent retag (~92% precision).</strong> The{' '}
            <code className="font-mono text-caption">/retag-new</code> and{' '}
            <code className="font-mono text-caption">/retag-all</code> slash commands spawn Claude subagents that
            re-tag rows against the same taxonomy. Re-tagged rows are stamped with{' '}
            <code className="font-mono text-caption">LLMTaggedAt</code> in the sheet and show an{' '}
            <span className="rounded-full bg-primary-50 px-1.5 py-0.5 font-mono text-[10px] text-primary-700">
              LLM
            </span>{' '}
            pill in the post lists.
          </li>
        </ul>
      </section>

      <section className="space-y-2 rounded-xl bg-white p-6 shadow-card">
        <div className="flex items-baseline gap-3">
          <span className="font-mono text-h2 text-primary-600">3</span>
          <h2 className="text-h2 text-neutral-900">Publishing — sheet to dashboard</h2>
        </div>
        <p className="text-body text-neutral-700">
          On every push to <code className="font-mono text-caption">main</code> (and after every cron run),
          GitHub Actions exports the sheet to hashed JSON, builds the Vite frontend, and deploys to GitHub Pages.
        </p>
        <ul className="ml-2 list-disc space-y-2 pl-4 text-body text-neutral-700">
          <li>
            <code className="font-mono text-caption">rover_export_json.py</code> reads both sheet tabs, drops
            Confluence rows the eligibility filter rejected, and writes{' '}
            <code className="font-mono text-caption">posts.&lt;hash&gt;.json</code>,{' '}
            <code className="font-mono text-caption">research.&lt;hash&gt;.json</code>, and{' '}
            <code className="font-mono text-caption">meta.json</code>.
          </li>
          <li>
            The dashboard you're reading now is a static React app. It loads those JSON files at startup, then
            renders Overview, Trends, Research, Untagged, and per-theme drill-downs entirely client-side.
          </li>
        </ul>
      </section>

      <div className="flex flex-wrap gap-4 text-body text-neutral-500">
        <a
          href={REPO_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="text-primary-700 hover:underline"
        >
          View source on GitHub ↗
        </a>
        {meta.sheet_url && (
          <a
            href={meta.sheet_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary-700 hover:underline"
          >
            Open the Google Sheet ↗
          </a>
        )}
      </div>
    </div>
  );
}
