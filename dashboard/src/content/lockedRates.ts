import type { VocReport } from '../types';

// ---------------------------------------------------------------------------
// Locked Rates — Voice-of-Customer report content.
//
// This module is the committed narrative for the /locked-rates route. It is a
// .ts file (not JSON) on purpose: *.json is globally gitignored in this repo,
// and the dashboard's data/*.json is CI-regenerated. Charts on the route draw
// from the LIVE aggregates (problemsByDay / problemCounts for "Locked rates");
// everything editorial — framing, quotes, research summaries, implications —
// lives here.
//
// Synthesized 2026-07-28 from the parallel agent waves:
//   - Reddit VoC: 238 core posts about setting / locking / changing rates for
//     repeat & recurring clients (tagged Locked rates / New-repeat clients /
//     Flag repeat clients + free-text mentions), each scored for sentiment and
//     theme by a Claude subagent; every quote below was machine-verified as a
//     verbatim substring of its source post.
//   - Research: 4 Confluence studies (DSN + PSD), findings harvested live.
// See scripts/locked_rates/ for the corpus + merge tooling.
// ---------------------------------------------------------------------------

const R = 'https://reddit.com/r/RoverPetSitting/comments';

export const lockedRatesReport: VocReport = {
  title: 'Locked Rates: Voice of the Customer',
  subtitle:
    'What sitters and owners actually say about locking, changing, and setting rates for repeat clients — read against Rover’s own research — to pressure-test moving from a binary lock/unlock to granular per-client rate management.',
  decisionQuestion:
    'Should Rover evolve Locked Rates from a binary lock/unlock into granular, per-client rate management — with better cross-client visibility and general edits?',
  framing: [
    'Product is scoping a next iteration of Locked Rates: more granularity in managing rates (beyond locking and unlocking), visibility into what each client sees, and more general edits. This artifact reads the Voice of the Customer from r/RoverPetSitting and reconciles it with Rover’s own prior research so the team can decide with evidence rather than intuition.',
    'The signal is unusually one-directional. Unlike a contested feature, almost every theme in the corpus points the same way: sitters want to hold, edit, and target their rates per client, and today’s all-or-nothing lock doesn’t let them. The dominant emotion is not outrage — most posts are questions — it is being stuck and being confused.',
    'The loudest, clearest pain is a sitter trapped at an old, low rate for a loyal or recurring client — "many of the clients who have been with me for years pay less than my current rate." Sitters improvise the missing feature by manually "grandfathering" regulars one at a time, and a large second cohort simply can’t tell how locking works or what the client sees. A granular, per-client model speaks directly to both — provided it stays legible and the underlying rate sync is made reliable.',
  ],
  corpusNote:
    'Core corpus: 238 r/RoverPetSitting posts about setting, locking, and changing rates for repeat/recurring clients, Jan 2025 – May 2026 (tagged under Locked rates / New-repeat clients / Flag repeat clients, plus free-text mentions, false-friends like "lockbox" pruned). Sentiment and themes were assigned per-post by a Claude subagent; every Reddit quote is verified verbatim against its source. Prior research: 4 Confluence studies across DSN (User Experience) and PSD (Provider Space), findings harvested live.',
  chartProblem: 'Locked rates',
  headlineStats: [
    { label: 'Core posts analyzed', value: '238', hint: 'Jan 2025 – May 2026' },
    {
      label: '#1 pain: stuck at an old rate',
      value: '60',
      hint: '25% of the corpus — repeat clients',
    },
    {
      label: 'Negative or mixed',
      value: '38%',
      hint: '90 of 238; 51% are how-to questions',
    },
    { label: 'Prior studies synthesized', value: '4', hint: 'Confluence DSN + PSD' },
  ],
  overallSentiment: { positive: 26, negative: 54, mixed: 36, neutral: 122 },
  vocThemes: [
    {
      id: 'stuck-old-rate-repeat-client',
      label: 'Trapped at the old rate for loyal clients',
      count: 60,
      sentiment: { positive: 1, negative: 13, mixed: 25, neutral: 21 },
      summary:
        'The single biggest theme. Sitters who started a client on a low intro rate — or deliberately locked one — find their rates have since risen or doubled, and there is no graceful way to move that one client up. Many "grandfather" regulars manually and feel stuck.',
      quotes: [
        {
          text: 'I locked in one of my first dog walking clients’ rates when I was very new and now my rates have nearly doubled.',
          url: `${R}/1m9hvcq/advice_on_letting_go_of_a_recurring_client/`,
          author: 'InitialRhubarb162',
          date: '2025-07-26',
        },
        {
          text: 'many of the clients who have been with me for years pay less than my current rate',
          url: `${R}/1ldp8mr/client_wants_to_pay_more_what_would_you_consider/`,
          author: 'realslhnv',
          date: '2025-06-17',
        },
        {
          text: 'Can I update my prices but lock in old prices for existing clients?',
          url: `${R}/1jkftrs/can_i_update_my_prices_but_lock_in_old_prices_for/`,
          author: 'Loud_Ad_6871',
          date: '2025-03-26',
        },
      ],
      implication:
        'The strongest pro-iteration signal: the exact job sitters are hiring a manual workaround for is "hold this specific client while I raise everyone else." Rover’s pricing survey measures it — ~1 in 3 keep charging repeat clients the old rate. A per-client model is the native fix.',
    },
    {
      id: 'wants-per-client-control',
      label: 'Sitters want per-client control, not a global switch',
      count: 23,
      sentiment: { positive: 1, negative: 4, mixed: 4, neutral: 14 },
      summary:
        'Explicit demand for the granular direction: raise prices for new clients while holding regulars, set a separate recurring-client rate, or lower a rate for one specific owner on rebook. Today’s lock is all-or-nothing, so sitters ask how to target one client at a time.',
      quotes: [
        {
          text: 'how do I set a rate for clients who book recurring bookings separate from my new client rate? or atleast lock a previous client at a specific rate',
          url: `${R}/1jmcyk7/i_might_be_blind_recurring_booking_help/`,
          author: 'Lesionia',
          date: '2025-03-29',
        },
        {
          text: 'Are we able to lower a rate for a specific owner when they are rebooking?',
          url: `${R}/1jj3a5n/adjusting_rover_rates/`,
          author: 'Effective-Unit-2078',
          date: '2025-03-24',
        },
        {
          text: 'I should only raise prices for new clients and keep my regulars what I have currently',
          url: `${R}/1ke4xbv/do_you_raise_prices_for_all_clients/`,
          author: 'orangelibster',
          date: '2025-05-03',
        },
      ],
      implication:
        'This is the feature request, stated in sitters’ own words. It maps directly to "granularity in managing rates" and "per-client" control — the core of the proposed iteration.',
    },
    {
      id: 'cant-edit-locked-rate',
      label: 'You can lock it, but you can’t edit it',
      count: 9,
      sentiment: { positive: 0, negative: 7, mixed: 0, neutral: 2 },
      summary:
        'Once a rate is locked or a recurring booking exists, sitters find the edit affordances gone — modify only exposes dates and times, not price. Changing a long-standing rate can require cancelling and rebooking the whole recurring booking.',
      quotes: [
        {
          text: 'when I go to modify, I can only adjust the dates/times basically.',
          url: `${R}/1mh19ga/recurring_puppy_is_now_an_adult_and_i_cant_modify/`,
          author: 'More_Ask_6745',
          date: '2025-08-04',
        },
        {
          text: 'I recently changed my rate for the first time in those 3 years, and had to cancel and rebook this recurring booking to do that.',
          url: `${R}/1ruejiy/recurrent_booking_canceled/`,
          author: 'quarantinefifty',
          date: '2026-03-15',
        },
        {
          text: 'I have a repeat client whose set price for walks I would like to change. How would I go about changing the price?',
          url: `${R}/1irqgz8/how_to_change_set_price/`,
          author: 'Ninjasrock00',
          date: '2025-02-17',
        },
      ],
      implication:
        'Directly supports the "more general edits" part of the iteration. The binary lock has no middle state — you cannot nudge a locked rate, only keep or destroy it. Editable per-client rates would remove a cancel-and-rebook workaround that itself risks lost bookings.',
    },
    {
      id: 'wants-bulk-or-granular-edit',
      label: 'All-or-nothing: no bulk, no fine grain',
      count: 6,
      sentiment: { positive: 0, negative: 3, mixed: 1, neutral: 2 },
      summary:
        'The lock operates one client at a time and one rate at a time. Sitters with many regulars find it impractical to lock each manually; others want to adjust a single night or a single service without the change cascading across all dates.',
      quotes: [
        {
          text: "I don't see a way to lock rates for multiple clients",
          url: `${R}/1ptdj52/easy_way_to_lock_rates_for_all_past_clients/`,
          author: 'JDMSubieFan',
          date: '2025-12-22',
        },
        {
          text: 'There’s too many of them to go manually lock in the existing price.',
          url: `${R}/1ouncc4/rates/`,
          author: 'Proof_Angle_5041',
          date: '2025-11-11',
        },
        {
          text: 'it changes the rate for *all* dates after that whereas I only want to adjust one night',
          url: `${R}/1l712zc/can_i_give_one_night_free_on_a_multiday_housesit/`,
          author: 'fuddy_dudley2233',
          date: '2025-06-09',
        },
      ],
      implication:
        'Argues for both ends of "granularity": bulk actions (lock all past clients at once) and finer grain (one night, one service). Rover’s Round 2 auto-rates study reaches the same conclusion — apply the feature "per rate, rather than an all or nothing."',
    },
    {
      id: 'unclear-how-to-lock-unlock',
      label: 'How does locking even work?',
      count: 16,
      sentiment: { positive: 0, negative: 4, mixed: 1, neutral: 11 },
      summary:
        'A large comprehension cohort: sitters aren’t sure whether they need to lock before raising rates, whether unbooked requests will reprice, or what locking a puppy rate does when the pup grows up. Several recent posts say the lock option "seems to have disappeared."',
      quotes: [
        {
          text: 'Can somebody let me know how I lock in my current clients with their price before I increase it?',
          url: `${R}/1sec46c/changing_prices/`,
          author: 'Individual-Amount147',
          date: '2026-04-06',
        },
        {
          text: "I know you can lock rates, but if you don't lock them will it change current bookings that haven't happened yet?",
          url: `${R}/1kp8p3x/does_changing_your_rates_effect_currentupcoming/`,
          author: 'AcidicSlimeTrail',
          date: '2025-05-18',
        },
        {
          text: 'Before that I saw there was a way to lock in rates for clients but now that seems to have disappeared.',
          url: `${R}/1szfhx3/lock_in_rates_after_change_to_tiered_rover_fee/`,
          author: 'Cee-Gee',
          date: '2026-04-29',
        },
      ],
      implication:
        'Comprehension is the ceiling. Before adding depth, the current model’s mental model and discoverability need fixing — and the "disappeared" reports suggest the entry point may have regressed with the tiered-fee change.',
    },
    {
      id: 'client-visibility-confusion',
      label: 'What does the client actually see?',
      count: 13,
      sentiment: { positive: 0, negative: 1, mixed: 3, neutral: 9 },
      summary:
        'Sitters repeatedly ask whether owners are notified — or can see — when a rate is locked, unlocked, or changed. The current behavior is invisible enough that sitters themselves can’t predict it, which makes them hesitant to use the feature at all.',
      quotes: [
        {
          text: 'If I lock a client’s current pricing, are they notified or do they see this in any way?',
          url: `${R}/1l0buyv/locked_pricing/`,
          author: 'daisiesdancing',
          date: '2025-06-01',
        },
        {
          text: 'do owners receive any kind of notification or indication that you have locked rates for them?',
          url: `${R}/1l95szo/locking_rateswhat_do_owners_see/`,
          author: 'OnionCharming7610',
          date: '2025-06-11',
        },
        {
          text: 'Does it notify clients when you lock rates?',
          url: `${R}/1n4kpu5/does_it_notify_clients_when_you_lock_rates/`,
          author: 'KaleidoscopeFuture50',
          date: '2025-08-31',
        },
      ],
      implication:
        'Maps to the "visibility across clients" goal — but the demand is two-sided. Any per-client control needs a deliberate answer to "what does the client see?", because that uncertainty is itself suppressing use today.',
    },
    {
      id: 'holiday-seasonal-rate-gap',
      label: 'Holiday & seasonal rates don’t fit real life',
      count: 8,
      sentiment: { positive: 0, negative: 3, mixed: 3, neutral: 2 },
      summary:
        'Rover’s holiday and seasonal rate logic is too rigid: sitters want to define their own holiday spans and local holidays, apply a rate to only part of a stay, or set a temporary seasonal rate — and fear a seasonal drop will be visible to existing clients who then demand it.',
      quotes: [
        {
          text: 'I’m wondering if there’s a way to add holidays rates to days that Rover doesn’t consider holidays?',
          url: `${R}/1i2sd9y/adding_holiday_rates/`,
          author: 'aureliabishh',
          date: '2025-01-16',
        },
        {
          text: 'we would be charged the holiday rate for the whole stay (this is a Rover policy apparently, but the sitter can change the rate on their end).',
          url: `${R}/1oiltoe/looking_for_perspective_on_rates/`,
          author: 'StorageExciting8567',
          date: '2025-10-28',
        },
        {
          text: 'my current clients will see the lowered rates and want to switch',
          url: `${R}/1q0hnzb/seasonal_rates/`,
          author: 'Flaky-Deer-5158',
          date: '2025-12-31',
        },
      ],
      implication:
        'Echoes the DSN satisfaction survey almost verbatim (self-defined holiday spans, temporary/seasonal rates). Granular time- and client-scoped rates would cover this; the "clients will see the drop" fear reconnects to the visibility question.',
    },
    {
      id: 'rate-sync-or-bug',
      label: 'Rates silently drift out of sync',
      count: 5,
      sentiment: { positive: 0, negative: 5, mixed: 0, neutral: 0 },
      summary:
        'A small but entirely negative reliability signal. Sitters report rebooking pulling the old price, new requests arriving at the old rate weeks after a change, and locked rates going "totally out of wack." The system’s rate state is not trusted.',
      quotes: [
        {
          text: 'Has anyone noticed their past client\'s locked in rates totally out of wack/being charged differently?',
          url: `${R}/1hxi3i5/rover_techinical_rates_issue/`,
          author: '_iSawRed',
          date: '2025-01-09',
        },
        {
          text: 'we realized Rover was rebooking at our original price.',
          url: `${R}/1lv69e2/software_bug_or_is_this_on_purpose/`,
          author: 'Competitive-Elk7007',
          date: '2025-07-09',
        },
        {
          text: 'I changed my rate over a month ago but keep getting new requests from new clients at my old rate.',
          url: `${R}/1obvswx/new_booking_requests_coming_in_with_old_rate/`,
          author: 'LotusBlooming90',
          date: '2025-10-20',
        },
      ],
      implication:
        'A caution, not a feature ask: adding granularity on top of a rate sync that already misfires will multiply bug reports and disputes. Reliability of the current rate model is a prerequisite for a richer one.',
    },
  ],
  research: [
    {
      id: '4792090636',
      title: 'Findings: Pricing / rates survey',
      space: 'DSN',
      url: 'https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4792090636/Findings+Pricing+rates+survey',
      method: 'Survey (n=1,430 providers), Jun 2025',
      takeaway:
        'Demand for per-client and per-context rate granularity is real but still a minority behavior today — and the sharpest ask is holiday rates auto-applying to recurring clients.',
      quotes: [
        {
          text: '~1 in 3 providers kept charging repeat clients their original, lower rate after raising their rates.',
          url: 'https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4792090636/Findings+Pricing+rates+survey',
          author: 'Survey finding (n=1,430)',
        },
        {
          text: '72% "Never" or "Rarely" adjust rates for specific clients.',
          url: 'https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4792090636/Findings+Pricing+rates+survey',
          author: 'Survey finding',
        },
        {
          text: '72% of providers who offer recurring services want holiday rates to auto-apply to recurring clients, not just one-time bookings.',
          url: 'https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4792090636/Findings+Pricing+rates+survey',
          author: 'Survey finding',
        },
      ],
      relevanceToTiers:
        'The quantitative backbone for the granular-management thesis: the pain (stuck old rates) and the desire (per-client, holiday-aware pricing) are both measured here at scale. Caution — per-client adjustment is a minority behavior today, so granular tools must be low-effort to move the majority, not just power users.',
    },
    {
      id: '4995940702',
      title: 'Round 2 findings: Weekend / short-notice rates and automatic rates feature',
      space: 'PSD',
      url: 'https://roverdotcom.atlassian.net/wiki/spaces/PSD/pages/4995940702/Round+2+findings+Weekend+short+notice+rates+and+automatic+rates+feature',
      method: 'Moderated usability testing, Aug 2025',
      takeaway:
        'A sibling all-or-nothing rate toggle (automatic rates) already tests poorly for the same reasons: sitters want per-rate granularity and cannot see the system’s status.',
      quotes: [
        {
          text: 'Allow for more granularity by applying the feature per rate, rather than an all or nothing.',
          url: 'https://roverdotcom.atlassian.net/wiki/spaces/PSD/pages/4995940702/Round+2+findings+Weekend+short+notice+rates+and+automatic+rates+feature',
          author: 'Study recommendation',
        },
        {
          text: 'They want more granular control than the feature affords them.',
          url: 'https://roverdotcom.atlassian.net/wiki/spaces/PSD/pages/4995940702/Round+2+findings+Weekend+short+notice+rates+and+automatic+rates+feature',
          author: 'Study finding',
        },
        {
          text: 'Automatic rates feature poorly understood; some sitters are unaware it is active on their account.',
          url: 'https://roverdotcom.atlassian.net/wiki/spaces/PSD/pages/4995940702/Round+2+findings+Weekend+short+notice+rates+and+automatic+rates+feature',
          author: 'Study finding',
        },
      ],
      relevanceToTiers:
        'The most direct precedent. A sibling all-or-nothing rate toggle failed usability for exactly the reasons Locked Rates does — no granularity, hidden system status. The explicit "per rate, not all-or-nothing" recommendation is precisely the direction under consideration.',
    },
    {
      id: '4198401220',
      title: 'Rates and calendar questions in sitter satisfaction survey — findings',
      space: 'DSN',
      url: 'https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4198401220/Rates+and+calendar+questions+in+sitter+satisfaction+survey+-+findings',
      method: 'Satisfaction survey + free-text analysis, Nov 2024',
      takeaway:
        'Baseline satisfaction with rate structure is high (avg 4.1/5), so this is an enhancement play — but free-text demand for self-defined holiday spans, scheduled increases, and temporary/seasonal rates is loud.',
      quotes: [
        {
          text: 'We should be able to select our own holiday rate spans.',
          url: 'https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4198401220/Rates+and+calendar+questions+in+sitter+satisfaction+survey+-+findings',
          author: 'Survey respondent',
        },
        {
          text: 'Automatically increase the rate for clients on a yearly basis. I currently do this manually',
          url: 'https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4198401220/Rates+and+calendar+questions+in+sitter+satisfaction+survey+-+findings',
          author: 'Survey respondent',
        },
        {
          text: 'Temporary rate increase or decrease … set temp October rates without having to change my whole rates menu.',
          url: 'https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4198401220/Rates+and+calendar+questions+in+sitter+satisfaction+survey+-+findings',
          author: 'Survey respondent',
        },
      ],
      relevanceToTiers:
        'Tempers the urgency (satisfaction is already high) while naming the specific granular features sitters ask for unprompted — holiday spans, scheduled auto-increases, temporary/seasonal rates. Scope these as additions, not a rescue.',
    },
    {
      id: '4347430531',
      title: 'Provider pricing preferences survey — study plan',
      space: 'DSN',
      url: 'https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4347430531/Provider+pricing+preferences+survey+-+study+plan',
      method: 'Study plan citing Blackstone provider survey, Mar 2025',
      takeaway:
        'The strategic "why now": the inability to set different prices per client is a top-10 retention driver and a named contributor to off-platform leakage.',
      quotes: [
        {
          text: '"Ability to set prices" is a top-10 reason sitters keep bookings on Rover (ranked #7) — and a top reason they don’t.',
          url: 'https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4347430531/Provider+pricing+preferences+survey+-+study+plan',
          author: 'Blackstone survey (via study plan)',
        },
        {
          text: '40% of providers admitted to dis-intermediation due at least in part to the inability to set different prices and cancellation policies for different clients.',
          url: 'https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4347430531/Provider+pricing+preferences+survey+-+study+plan',
          author: 'Blackstone survey (via study plan)',
        },
      ],
      relevanceToTiers:
        'The business case. Per-client price control isn’t just a satisfaction nicety — it is tied to retention and to 40% of off-platform leakage. Caveat: this is a study plan (learning objectives), so cite it as strategic framing, not validated findings.',
    },
  ],
  images: [],
  implications: {
    supports: [
      'The corpus is unusually one-directional: the top themes — stuck at an old rate (60), wanting per-client control (23), can’t edit a locked rate (9), wanting bulk/granular edits (6) — all point at the same fix: rate management that is per-client and editable, not a global on/off.',
      'Rover’s own Round 2 usability study on a sibling all-or-nothing rate toggle explicitly recommends "granularity … per rate, rather than an all or nothing" — the exact direction under consideration.',
      'The pricing survey (n=1,430) quantifies both the pain (~1/3 keep charging repeat clients the old rate) and the desire (72% want holiday rates to auto-apply to recurring clients) at scale.',
      'Sitters already improvise the missing feature — manually "grandfathering" loyal clients one at a time — and complain there are "too many of them to go manually lock." Bulk + per-client tooling removes real, repeated friction.',
      'The business case is on record: inability to set different prices per client is a top-10 retention driver and a named contributor to 40% off-platform leakage.',
    ],
    cautions: [
      'Comprehension is the ceiling. A large share of the corpus is simply "how does locking work / do I need to lock before raising rates / what will the client see?" — new granular controls must teach themselves or they add surface area for confusion.',
      'Visibility is a genuine open question for sitters, not just for us: 13 posts ask whether owners are notified or can see a locked or changed rate. Any per-client control needs a clear, deliberate answer to "what does the client see?"',
      'Reliability is fragile today: sitters report rates silently drifting — rebooking at the old price, new requests arriving at the old rate, locked rates "totally out of wack." Adding granularity on top of a flaky sync will multiply bug reports.',
      'The feature may have regressed: multiple recent posts say the lock-rates option "seems to have disappeared" after the tiered-fee change. Fix discoverability before adding depth.',
      'Satisfaction with today’s rate structure is already high (4.1/5 in the DSN survey); this is an enhancement play. Scope granular management as additive, and don’t overstate a crisis the data doesn’t show.',
    ],
    openQuestions: [
      'What should the client see when a sitter locks, unlocks, or edits their rate — and should Rover notify them? Sitters are asking us because the behavior is invisible to them too.',
      'Is the demand broad or concentrated? Per-client adjustment is a minority behavior today (72% "never/rarely") — would low-effort granular tools convert the majority, or only serve power sitters?',
      'Should raising a base rate auto-hold existing clients (opt-out) instead of requiring a manual per-client lock (opt-in)? Much of the pain is simply forgetting to lock.',
      'How much of the "stuck at old rate" pain is a tooling gap vs. a hard conversation sitters avoid? Granular edits help the former; they don’t make the "I need to charge you more" message any easier.',
      'Did the lock-rates entry point regress with the tiered-fee change, and how many sitters currently cannot find it at all?',
    ],
  },
  generatedAt: '2026-07-28',
};
