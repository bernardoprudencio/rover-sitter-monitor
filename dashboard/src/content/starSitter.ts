import type { StarSitterReport } from '../types';

// ---------------------------------------------------------------------------
// Star Sitter — Voice-of-Customer report content.
//
// This module is the committed narrative for the /star-sitter route. It is a
// .ts file (not JSON) on purpose: *.json is globally gitignored in this repo,
// and the dashboard's data/*.json is CI-regenerated. Charts on the route draw
// from the LIVE aggregates (problemsByDay / problemCounts for "Star Sitter");
// everything editorial — framing, quotes, research summaries, implications —
// lives here.
//
// Synthesized 2026-07-22 from the parallel agent waves:
//   - Reddit VoC: 276 core posts (Star Sitter) + 293 supporting posts, each
//     scored for sentiment/theme by a Claude subagent; every quote below was
//     machine-verified as a verbatim substring of its source post.
//   - Research: 10 Confluence studies (DSN + PSD), full findings harvested.
// See scripts/star_sitter/ for the corpus + merge tooling.
// ---------------------------------------------------------------------------

const R = 'https://reddit.com/r/RoverPetSitting/comments';

export const starSitterReport: StarSitterReport = {
  title: 'Star Sitter: Voice of the Customer',
  subtitle:
    'What sitters and owners actually say about the Star Sitter badge — read against Rover’s own research — to pressure-test moving from a single badge to a tiered loyalty program.',
  decisionQuestion:
    'Should Rover evolve Star Sitter from a single earned badge into a tiered loyalty program?',
  framing: [
    'Product is weighing whether to turn Star Sitter from a one-time earned badge into a tiered loyalty program. This artifact reads the Voice of the Customer from r/RoverPetSitting and reconciles it with Rover’s own prior research so the team can decide with evidence rather than intuition.',
    'The signal is not a clean yes or no. Sitters who earn the badge value it, and a few report real booking lifts the day it appears. But the current single-badge design already strains on three fronts — fairness, comprehension, and reward — and every one of those strains would multiply, not vanish, under tiers.',
    'Underneath Star Sitter sits a louder anxiety that explains why loyalty is even on the table: sitters overwhelmingly tie their standing in search to their income, and experience the ranking algorithm as opaque and punishing — "Algorithm dropped me from #5 to #139," "Anyone else suddenly hidden from Rover search results after years of 5-star reviews?" A loyalty program is one lever on that anxiety, but only if higher status buys something real and stays attainable.',
  ],
  corpusNote:
    'Core corpus: 276 r/RoverPetSitting posts mentioning Star Sitter (195 tagged + 81 free-text), Jan 2025 – Jul 2026. Supporting corpus: 293 posts on search rank, demand, and reviews, mined for the "why tiers" motivation. Sentiment and themes were assigned per-post by a Claude subagent; every quote is verified verbatim against its source. Prior research: 10 Confluence studies across DSN (User Experience) and PSD (Provider Space).',
  chartProblem: 'Star Sitter',
  headlineStats: [
    { label: 'Core posts analyzed', value: '276', hint: 'Jan 2025 – Jul 2026' },
    { label: 'Negative sentiment', value: '56%', hint: 'vs. just 5% positive' },
    { label: 'Prior studies synthesized', value: '10', hint: 'Confluence DSN + PSD' },
    {
      label: 'Asked for more tiers, unprompted',
      value: '2',
      hint: 'of 276 — progression isn’t top-of-mind',
    },
  ],
  overallSentiment: { positive: 14, negative: 155, mixed: 33, neutral: 74 },
  vocThemes: [
    {
      id: 'loss-anxiety',
      label: 'The badge churns — and losing it stings',
      count: 52,
      sentiment: { positive: 0, negative: 44, mixed: 4, neutral: 4 },
      summary:
        'The single biggest theme. Because status is re-evaluated continuously, sitters watch the badge come and go month to month — often over a single cancellation or client — and experience each loss as a personal and financial blow, even with a spotless rating.',
      quotes: [
        {
          text: 'Lost Star Sitter badge due one client',
          url: `${R}/1kbvu5o/lost_star_sitter_badge_due_one_client/`,
          author: 'Accomplished-List861',
          date: '2025-05-01',
        },
        {
          text: 'I’ve lost my star sitter status as a result, but I have a five star rating and all positive reviews.',
          url: `${R}/1k5q8wn/no_bookings_since_cross_country_move/`,
          author: 'LOLisauras',
          date: '2025-04-23',
        },
        {
          text: 'I had the Star Sitter badge since they launched the feature, however I’ve lost it since January because one client',
          url: `${R}/1kbvw4t/lost_my_star_sitter_badge_due_1_client/`,
          author: 'Ultimatecatlady1',
          date: '2025-05-01',
        },
      ],
      implication:
        'Tier demotion would amplify this. Rover’s own Round 2 usability study warns failing to reach status "wounds self-perception" — a ladder that can drop sitters a rung needs generous grace periods and stability, not more thresholds to fall below.',
    },
    {
      id: 'tied-to-search-and-bookings',
      label: 'Standing is money — the badge is tied to bookings',
      count: 56,
      sentiment: { positive: 1, negative: 36, mixed: 12, neutral: 7 },
      summary:
        'Sitters treat the badge as a lever on visibility and income, in both directions: some credit it for an immediate booking lift, while others blame its absence for a collapse in new-client requests. This coupling is the core reason a loyalty program is even attractive.',
      quotes: [
        {
          text: 'I got that STAR status today.',
          url: `${R}/1jzk5yn/i_got_that_star_status_today_then_i_get_2_doctors/`,
          author: 'Old_Asparagus3756',
          date: '2025-04-15',
        },
        {
          text: 'I got the STAR sitter status recently so I’m getting the top owner requests.',
          url: `${R}/1jzk9pe/just_booked_a_huge_house_with_3_dogs_in_maui_i/`,
          author: 'Old_Asparagus3756',
          date: '2025-04-15',
        },
        {
          text: 'I barely get any requests especially since the star sitter feature is in place.',
          url: `${R}/1icjq5p/deactivating_strategy/`,
          author: 'Good-Calendar-6594',
          date: '2025-01-29',
        },
      ],
      implication:
        'Because status maps to income, higher tiers have real pull — but also raise the stakes of getting the criteria wrong. Whether the badge causally drives bookings (vs. high-booking sitters simply earning it) is an open data-science question.',
    },
    {
      id: 'all-or-nothing-threshold',
      label: 'All-or-nothing thresholds feel unfair',
      count: 31,
      sentiment: { positive: 0, negative: 25, mixed: 5, neutral: 1 },
      summary:
        'Qualification is binary, so a single miss — one cancellation, a 5% dip, one client’s behavior — erases the badge. Sitters read this as punishing them for things outside their control, especially client-initiated cancellations.',
      quotes: [
        {
          text: 'I made one cancellation out of 16 completed bookings when I had to unexpectedly travel',
          url: `${R}/1iyzmkg/unfair_sitter_requirement/`,
          author: 'No_Leek_6965',
          date: '2025-02-26',
        },
        {
          text: 'I personally miss the critera by literally 5% in one category and I feel like not having the badge has affected my new client requests.',
          url: `${R}/1ju7pcw/what_are_everyone_thoughts_on_the_star_sitter/`,
          author: 'WhiskerzFurryFuckz',
          date: '2025-04-08',
        },
        {
          text: 'With Star Sitter now a thing, every time you book with a new sitter and cancel it, that counts against THE SITTER.',
          url: `${R}/1k1gtrk/owners_please_make_sure_your_plans_are_set_in/`,
          author: 'Jbrahms4',
          date: '2025-04-17',
        },
      ],
      implication:
        'The New Customer Booking Rate (NCBR) criterion is the recurring villain in both Reddit and every usability study. A tiered ladder gated on NCBR would reproduce this perceived unfairness at every threshold.',
    },
    {
      id: 'opaque-criteria',
      label: 'Criteria are confusing and opaque',
      count: 32,
      sentiment: { positive: 0, negative: 22, mixed: 0, neutral: 10 },
      summary:
        'Sitters can’t reliably tell how the badge is earned, when it is evaluated, or why their status flips. Mixed metric windows, disappearing quarterly dates, and stat errors leave even engaged sitters guessing.',
      quotes: [
        {
          text: 'Does anyone know why I would be on track for star sitter status and then as soon as I’m supposed to get it it says I’m not on track lol.',
          url: `${R}/1kc206n/star_sitter_status/`,
          author: 'Objective-Cookie4728',
          date: '2025-05-01',
        },
        {
          text: 'if for example my new client acceptance rate were to dip below 33% before the end of the period (April 10) will the Star Sitter status be revoked',
          url: `${R}/1jnfg46/star_sitter_status_question/`,
          author: 'undressedpoetess',
          date: '2025-03-30',
        },
      ],
      implication:
        'Comprehension is already the ceiling on a single badge. Every Confluence usability round flags the same thing — a multi-tier structure multiplies the surface area for confusion and CX contacts unless status and criteria are made radically clearer.',
    },
    {
      id: 'weak-reward',
      label: '"What else do I get?" — the reward feels thin',
      count: 19,
      sentiment: { positive: 0, negative: 13, mixed: 5, neutral: 1 },
      summary:
        'A vocal group questions what the badge actually buys them. When perks feel invisible or get removed, sitters conclude the effort-to-reward ratio is off — some reframe care itself, not the badge, as what matters.',
      quotes: [
        {
          text: 'We the sitters get absolutely no benefits from achieving this',
          url: `${R}/1j6qcyq/star_sitter_status_issue/`,
          author: 'InkedAngel85',
          date: '2025-03-08',
        },
        {
          text: 'I can see how to qualify. But do we get any perks.',
          url: `${R}/1jg3d1i/am_i_blind_what_are_the_benefits_of_reaching_star/`,
          author: 'LilChiwahhwahh',
          date: '2025-03-20',
        },
        {
          text: 'The care and compassion you provide to the animals is what makes you a superstar not a badge.',
          url: `${R}/1nx0935/star_sitter_status/`,
          author: 'radioflea',
          date: '2025-10-03',
        },
      ],
      implication:
        'This is the strongest pro-tiers signal in the corpus: it echoes the research "what else do I get?" theme and card-sort demand for tangible, chooseable rewards. Higher tiers could work — but only if they unlock benefits sitters actually value (earnings/take-rate, selectable perks), not just more status.',
    },
    {
      id: 'owner-perception',
      label: 'Owners: the badge barely moves the needle',
      count: 44,
      sentiment: { positive: 0, negative: 33, mixed: 6, neutral: 5 },
      summary:
        'From the demand side, the badge is weakly understood and rarely decisive. Owners lean on reviews, repeat history, and price; some wonder whether the badge is simply paid for, undercutting its trust value.',
      quotes: [
        {
          text: 'Should I always pick a Star Sitter?',
          url: `${R}/1m7go9s/should_i_always_pick_a_star_sitter/`,
          author: 'Zipper-is-awesome',
          date: '2025-07-23',
        },
        {
          text: 'I feel like I should be using a Star Sitter or one with repeat clients.',
          url: `${R}/1m7gu9k/should_i_always_use_a_star_sitter/`,
          author: 'Zipper-is-awesome',
          date: '2025-07-23',
        },
      ],
      implication:
        'Rover’s own owner-side study found 5 of 7 chose a non-Star-Sitter once the badge was removed. Elaborating status into tiers won’t shift owner behavior unless the tiers are made far more legible and trusted on search and profile.',
    },
    {
      id: 'new-sitter-disadvantage',
      label: 'New & part-time sitters feel locked out',
      count: 11,
      sentiment: { positive: 0, negative: 5, mixed: 1, neutral: 5 },
      summary:
        'Volume-based criteria make the badge feel unreachable for newer and small-market sitters, who can have perfect ratings yet still not qualify — a self-reinforcing disadvantage.',
      quotes: [
        {
          text: 'I meet all of the requirements to be a star sitter, except having a 4.9+ star rating. Except - I have a 5 star rating from 7 reviews.',
          url: `${R}/1lr1edo/why_am_i_not_qualified_for_star_sitter/`,
          author: 'environightmare',
          date: '2025-07-03',
        },
        {
          text: 'it isn’t possible for me to hold Star Sitter Status.',
          url: `${R}/1nxc34c/star_sitter_status/`,
          author: 'CatchingStarLight',
          date: '2025-10-03',
        },
      ],
      implication:
        'Tiers must feel attainable to mid/low-volume sitters or they widen this gap. Research echoes it: mid- and low-volume sitters worry they can’t earn status despite good care.',
    },
    {
      id: 'praise',
      label: 'When it works, sitters are proud of it',
      count: 9,
      sentiment: { positive: 8, negative: 0, mixed: 1, neutral: 0 },
      summary:
        'The counterpoint: earning the badge is a genuine moment of pride and recognition. The status itself clearly carries emotional weight — the asset a loyalty program would build on.',
      quotes: [
        {
          text: 'I finally got star sitter and I am so delighted!',
          url: `${R}/1mcuwro/it_finally_happened_for_me/`,
          author: 'Feminist-historian88',
          date: '2025-07-30',
        },
        {
          text: 'Just got my star Sitter status!',
          url: `${R}/1qhd1tz/just_got_my_star_sitter_status_when_did_you_get/`,
          author: 'LoneWanderer-87',
          date: '2026-01-19',
        },
      ],
      implication:
        'Recognition works. The card-sort ranked the status badge the #2 most-appealing reward. The design question is not whether status motivates, but whether more layers of it do — and for whom.',
    },
  ],
  research: [
    {
      id: '3253175284',
      title: 'Round 2 Findings: Star sitter tracking usability testing',
      space: 'DSN',
      url: 'https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/3253175284',
      method: 'Moderated usability testing (tracking-tab prototype, Round 2)',
      takeaway:
        'Bundling "does a good job" with "likely to book new customers" into one status risks harming Rover’s best established, repeat-heavy sitters — the study explicitly recommends separating the two.',
      quotes: [
        {
          text: 'By binding together the concept of “likely to book new customers” with “does a good job as a sitter” into a single status program, we’re risking harm to some of our best sitters: the well-established ones who are primarily booking repeats.',
          url: 'https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/3253175284',
          author: 'Study finding',
        },
        {
          text: 'as an established sitter who mostly books repeats, there isn’t a good way for her to improve that rate.',
          url: 'https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/3253175284',
          author: 'Participant',
        },
      ],
      relevanceToTiers:
        'The most strategically supportive study: decoupling quality recognition from new-demand metrics is exactly what a multi-track or tiered program could do — e.g. a track honoring long-tenured, repeat-heavy sitters separate from NCBR. Caution: failing to reach status wounds self-perception, so demotion must be handled gently.',
    },
    {
      id: '2921365713',
      title: 'Findings: sitter rewards interviews and card sort',
      space: 'DSN',
      url: 'https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/2921365713',
      method: 'Interviews + card sort + Q4 2022 satisfaction survey',
      takeaway:
        'Sitters rank flexible/monetary rewards (gift cards) #1 and the status badge #2, and strongly want choice over what they receive — but worry the badge loses value if too many earn it.',
      quotes: [
        {
          text: 'Sitters would like to pick/have some control over these rewards.',
          url: 'https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/2921365713',
          author: 'Study finding',
        },
        {
          text: 'Concerns about the value of badge being diluted if too many get it',
          url: 'https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/2921365713',
          author: 'Study finding',
        },
      ],
      relevanceToTiers:
        'Directly supports a loyalty structure where higher tiers unlock monetary or selectable perks. But the dilution concern warns that adding earners/tiers can weaken prestige, and mixed metric durations already confuse sitters — a multi-tier program risks compounding that.',
    },
    {
      id: '3510829441',
      title: 'Findings: Star sitter sentiment interviews',
      space: 'DSN',
      url: 'https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/3510829441',
      method: 'Interviews (holders, non-holders, never-earned, too-new)',
      takeaway:
        'Program awareness is very low and motivation to progress is split — part-timers treating Rover as supplemental income have little appetite, and a "what else do I get?" theme recurs.',
      quotes: [
        {
          text: 'There was a minor theme of “what else do I get?” when it comes to benefits.',
          url: 'https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/3510829441',
          author: 'Study finding',
        },
        {
          text: 'They might care more about it if they were a full time sitter, but because they are part-time (Rover is supplemental income), it’s not important.',
          url: 'https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/3510829441',
          author: 'Participant',
        },
      ],
      relevanceToTiers:
        'Cautions: the large part-time cohort has weak motivation to climb, and the badge alone isn’t driving more bookings for some holders — a ladder risks low engagement unless awareness and tangible perks improve. NCBR’s perceived unfairness would recur at every tier.',
    },
    {
      id: '4156228279',
      title: 'Findings: Star Sitter cadence revisions usability testing',
      space: 'DSN',
      url: 'https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4156228279',
      method: 'Moderated usability testing (rolling cadence: 7-day holding + 90-day grace)',
      takeaway:
        'A rolling qualification with a grace period tested as far easier and fairer than the rigid quarterly cadence — sitters appreciated the grace period, some said it could even be shorter.',
      quotes: [
        {
          text: 'The new qualification approach is much easier for sitters to understand than our current quarterly cadence.',
          url: 'https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4156228279',
          author: 'Study finding',
        },
        {
          text: 'Sitters appreciate the 90 grace period as a way to avoid losing the badge due to a temporary drop in stats.',
          url: 'https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4156228279',
          author: 'Study finding',
        },
      ],
      relevanceToTiers:
        'Supportive on mechanics: a tiered program should use rolling qualification and generous grace to feel fair and blunt loss anxiety. Caution: novel timing concepts are poorly understood upfront, so tier promotion/demotion rules must be communicated proactively.',
    },
    {
      id: '2664794089',
      title: 'Findings Report: Sitter Performance Score Interviews',
      space: 'DSN',
      url: 'https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/2664794089',
      method: 'Interviews (sitters recruited as metric "visitors")',
      takeaway:
        'Comprehension of performance metrics is basic and often wrong, the tracking surface is barely found, and sitters rarely act on the data — reviews, not Rover’s numbers, define whether they feel they do a good job.',
      quotes: [
        {
          text: 'When it comes to what makes them feel they’re a good sitter, it’s entirely about what clients think of them and not what Rover thinks.',
          url: 'https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/2664794089',
          author: 'Study finding',
        },
      ],
      relevanceToTiers:
        'Cautions: tiers lean harder on sitters understanding and tracking metrics, yet comprehension is poor and most sitters are part-timers not chasing progression. Tier thresholds tied to poorly-understood, low-control metrics may simply fail to motivate.',
    },
    {
      id: '3135636427',
      title: 'Findings: Star Sitter landing page testing',
      space: 'DSN',
      url: 'https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/3135636427',
      method: 'Moderated usability testing (landing-page prototype)',
      takeaway:
        'Sitters grasp the perks but struggle with how to earn the badge; when they don’t earn it, the app doesn’t clearly tell them they failed — and NCBR again drew the most concern as "out of their control."',
      quotes: [
        {
          text: 'There’s a big mental disconnect between the concept of “being a good sitter” and “taking lots of bookings on Rover”.',
          url: 'https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/3135636427',
          author: 'Study finding',
        },
      ],
      relevanceToTiers:
        'Cautions: even for one badge, earning mechanics are unclear and failure messaging is weak. Tiers need explicit "you are / aren’t at tier X, next evaluated on <date>" messaging, and the good-sitter-vs-bookings disconnect warns NCBR-gated tiers will feel unfair.',
    },
    {
      id: '3684204680',
      title: 'Findings: Star Sitter landing page and tab revisions',
      space: 'DSN',
      url: 'https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/3684204680',
      method: 'Moderated usability testing (landing page + tracking tab iteration)',
      takeaway:
        'Revised copy and an NCBR rename lifted comprehension, but grace-period understanding stayed low and sitters still think NCBR is about generating demand — and read a 5/6 period as not having the badge.',
      quotes: [
        {
          text: 'The visual cue of a green bar vs a red one is not strong enough to contend with seeing “5/6 criteria met”.',
          url: 'https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/3684204680',
          author: 'Study finding',
        },
      ],
      relevanceToTiers:
        'Cautions on complexity: even a single badge with a grace period is hard to parse. Any tiered design needs very explicit status indicators and progress bars ("accept N more requests") to avoid the misreads seen here.',
    },
    {
      id: '3203792897',
      title: 'Round 1 Findings: Star sitter tracking usability testing',
      space: 'DSN',
      url: 'https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/3203792897',
      method: 'Moderated usability testing (tracking-tab prototype, Round 1)',
      takeaway:
        'The quarterly qualification-period concept is hard to grasp and carries heavy cognitive load; sitters were confused why they didn’t get the badge immediately when all criteria showed "met."',
      quotes: [
        {
          text: 'Some wonder why they aren’t getting the badge immediately, if all criteria are “met”.',
          url: 'https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/3203792897',
          author: 'Study finding',
        },
      ],
      relevanceToTiers:
        'Cautions heavily: sitters already strain to understand one qualification period and the difference between one-time thresholds and fluctuating metrics — complexity a multi-tier program with promotion/demotion timing would amplify.',
    },
    {
      id: '3219587635',
      title: 'Write Up: Unmoderated New to Rover and Star Sitter',
      space: 'DSN',
      url: 'https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/3219587635',
      method: 'Unmoderated usability testing, 14 participants (pet-owner perspective)',
      takeaway:
        'From the owner side the badge is understood but weakly influential — reviews, ratings, repeats, and price dominate. When the badge was removed from a top sitter, 5 of 7 still chose a non-Star-Sitter.',
      quotes: [
        {
          text: 'From this test, 5 out of 7 participants chose a sitter that isn’t a Star Sitter.',
          url: 'https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/3219587635',
          author: 'Study finding',
        },
        {
          text: 'participants raised that having Star Sitters with less reviews than non-Star Sitters is confusing.',
          url: 'https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/3219587635',
          author: 'Study finding',
        },
      ],
      relevanceToTiers:
        'Important demand-side caution: a more elaborate tiered status may not shift owner behavior unless it is made far more legible and trusted on search/profile. Added tiers could deepen "is this paid?" skepticism rather than clarify quality.',
    },
    {
      id: '4255219826',
      title: 'Weekly interviews: top 20% of dog-walking & drop-in providers',
      space: 'PSD',
      url: 'https://roverdotcom.atlassian.net/wiki/spaces/PSD/pages/4255219826',
      method: 'Interviews across 3 segments (top 20% / recurring / top 3%)',
      takeaway:
        'Top providers are loyal and mostly content part-timers not seeking more bookings; they value practical help (scheduling, earnings guidance) over status. Only the small full-time top-3% shows growth appetite.',
      quotes: [
        {
          text: 'Most sitters in that segments are not actively looking to do more bookings and instead consider each request in light of their personal criteria (location, time of day, new vs repeat clients)',
          url: 'https://roverdotcom.atlassian.net/wiki/spaces/PSD/pages/4255219826',
          author: 'Study finding',
        },
      ],
      relevanceToTiers:
        'Mixed signal: top performers already treat Star Sitter as a client-attraction asset, so a top tier could reinforce loyalty — but most are content part-timers, and the levers they value are utility-based, not status. A growth-oriented top tier may resonate with only a narrow group.',
    },
  ],
  images: [],
  implications: {
    supports: [
      'Rover’s Round 2 study explicitly recommends separating recognition of care quality from likelihood-to-book-new-customers — a natural argument for multiple tracks or tiers.',
      'The rewards card-sort ranks the status badge #2 and flexible monetary rewards #1, and sitters want choice — higher tiers could unlock selectable, tangible perks.',
      'A rolling qualification + grace period tested as far clearer and fairer than the rigid quarterly model — the exact mechanic a tier ladder would need.',
      'The "what else do I get?" theme (Reddit + research) shows real appetite for benefits layered onto status, including lower take-rate / gig-style rewards.',
      'The badge demonstrably drives bookings for some ("I got that STAR status today" → immediate booking), and earning it is a genuine moment of pride — recognition has pull.',
    ],
    cautions: [
      'Comprehension of even one badge is poor across every usability round (qualification periods, grace period, mixed metric windows, NCBR); tiers would multiply this confusion and CX load.',
      'The all-or-nothing NCBR threshold is widely seen as unfair and outside sitters’ control, and would recur at every tier threshold — one cancellation, a 5% dip, or one client already erases the badge.',
      'Most sitters are content part-timers with low motivation to progress; only 2 of 276 posts spontaneously ask for more tiers or badges. A ladder may not engage the majority.',
      'Owners barely act on the badge (5 of 7 chose a non-Star-Sitter when it was removed); more status layers risk "is it paid?" skepticism and badge dilution rather than clearer quality signals.',
      'Loss anxiety is already the #1 theme (52 posts); tier demotion wounds self-perception and would amplify churn frustration unless stability is designed in.',
    ],
    openQuestions: [
      'Would higher tiers unlock benefits sitters actually value (earnings / take-rate, selectable rewards) rather than status alone?',
      'Can a tier that honors established, repeat-heavy sitters be decoupled from new-customer-booking metrics like NCBR?',
      'Does the badge causally drive bookings, or do high-booking sitters simply earn it? (Reddit shows both directions — a data-science question.)',
      'How do we make tier status and criteria legible enough on both sides to avoid compounding today’s comprehension gaps?',
      'What owner-facing explanation would make tiers shift owner choice instead of deepening "is this paid?" skepticism?',
    ],
  },
  generatedAt: '2026-07-22',
};
