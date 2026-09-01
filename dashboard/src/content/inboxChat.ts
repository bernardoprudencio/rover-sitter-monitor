import type { VocReport } from '../types';

// ---------------------------------------------------------------------------
// Inbox & Chat — Voice-of-Customer report content.
//
// This module is the committed narrative for the /inbox-chat route. It is a
// .ts file (not JSON) on purpose: *.json is globally gitignored in this repo,
// and the dashboard's data/*.json is CI-regenerated. The chart on the route
// draws from the LIVE aggregates — uniquely for this report, from the
// `Communication` THEME (themesByDay/themeCounts) rather than a single
// problem, because no taxonomy problem is named "Inbox" or "Messaging" and the
// largest one that comes close (Media uploads, 94 posts) draws as an empty
// chart. Everything editorial lives here.
//
// Synthesized 2026-09-01 from the parallel agent waves:
//   - Reddit VoC: 610 core posts + 354 adjacent-surface posts, each scored for
//     sentiment / theme / relevance by a Claude subagent. Every quote below was
//     machine-verified as a verbatim substring of its source post — and unlike
//     the two prior reports, that check is actually implemented, in
//     scripts/inbox_chat/merge_results.py::verify_quote. 931 of 931 passed.
//   - Research: 11 Confluence studies (DSN + PSD), read in full via MCP rather
//     than through the dashboard's research export, which surfaces only 78 of
//     ~1,554 rows and filters out most of this topic's studies. Only 5 of the
//     11 are validated findings; each entry states its document type.
//
// Cross-check added 2026-09-01: the report is checked item-by-item against the
// BKS plan "Improve the Rover Messaging Experience" (6284542665). BKS is
// outside the DSN + PSD ingest scope, so that plan and the two other BKS pages
// surfaced alongside it (6142593222, 6005620935) are not in `research` above —
// they are product plans and a spec, not research, and are labelled as such.
// Feature-presence claims in that section were tested against the full 26,597
// post dashboard export rather than the 964-post corpus, because several terms
// (notably "reply to") were dropped during collection as false friends and an
// absence in the corpus alone would not have been conclusive.
//
// Theme counts and the sentiment donut use the 506 rows scored high or medium
// relevance, not all 932 — the low-relevance tail is keyword-sweep noise and is
// disclosed in corpusNote rather than quietly included.
// See scripts/inbox_chat/ for the corpus + merge tooling.
// ---------------------------------------------------------------------------

const R = 'https://reddit.com/r/RoverPetSitting/comments';

export const inboxChatReport: VocReport = {
    "title": "Inbox & Chat: Voice of the Customer",
    "subtitle": "What sitters and owners actually say about the Rover inbox, message threads, photos in messages, and message notifications — read against Rover’s own research — to work out where messaging hurts most and what to fix first.",
    "decisionQuestion": "Where does messaging hurt most for sitters and owners, and what should we fix first?",
    "framing": [
      "Messaging is the surface sitters touch more than any other, and it has never had a Voice-of-Customer read of its own. This artifact assembles one from r/RoverPetSitting and reconciles it with eleven of Rover’s own studies, so the team can sequence work on evidence rather than on whoever complained most recently.",
      "The headline is that the loudest problems are not the ones a redesign fixes. Two of the three largest clusters — reply-speed pressure and archiving — are incentive mechanics wearing an inbox costume: sitters archive conversations to protect their search visibility, and answer within minutes because they believe standing depends on it. Rover’s own filter and layout studies, by contrast, tested as successes.",
      "Underneath sits a self-inflicted loop that connects most of the rest. Photo and video upload fails often enough that sitters text photos instead; threads cannot carry a PDF or outlive their booking; messages sometimes never arrive at all. Each gap pushes conversation to SMS — and the contact-info filter then penalizes people for going there. Rover’s media-upload charter said as much in 2024, and also admitted it could not measure the failure rate at all."
    ],
    "corpusNote": "Core corpus: 610 r/RoverPetSitting posts tagged under the Communication theme (excluding Flag repeat clients, a clients/rates problem already counted in the Locked Rates report) or matching a word-boundary free-text sweep for inbox, thread, media and notification language, Jan 2025 – Sep 2026. Supporting corpus: 354 posts from eight adjacent problems (off-platform, Support quality, Rover Cards, booking requests and app bugs), keyword-gated and capped at 60 per problem so no single large problem could dominate — 1,072 lower-signal rows were dropped by that cap. 964 unique posts were scored one-by-one by Claude subagents and 32 same-author re-posts collapsed, leaving 932; theme counts and the sentiment mix below use only the 506 rows scored high or medium relevance, and the 426 low-relevance rows are reported rather than hidden. All 931 quotes offered by the scoring agents were machine-verified as verbatim substrings of their source post; none failed. Prior research: 11 Confluence studies across DSN and PSD, read in full — note that only 5 are validated findings; the rest are study plans, 1-pagers, survey instruments or analyses, and are labelled as such.",
    "chartProblem": "Media uploads",
    "chartTheme": "Communication",
    "headlineStats": [
      {
        "label": "Posts scored individually",
        "value": "964",
        "hint": "Jan 2025 – Sep 2026"
      },
      {
        "label": "On-topic after scoring",
        "value": "506",
        "hint": "high or medium relevance"
      },
      {
        "label": "Negative sentiment",
        "value": "64%",
        "hint": "326 of 506 — vs. 2% positive"
      },
      {
        "label": "Quotes verified verbatim",
        "value": "931",
        "hint": "of 931 offered — zero failures"
      }
    ],
    "overallSentiment": {
      "positive": 10,
      "negative": 326,
      "mixed": 36,
      "neutral": 134
    },
    "vocThemes": [
      {
        "id": "reply-speed-pressure",
        "label": "Answering fast is the job — and the clock never stops",
        "count": 134,
        "sentiment": {
          "positive": 0,
          "negative": 101,
          "mixed": 6,
          "neutral": 27
        },
        "summary": "The largest cluster in the corpus. Requests fan out to several sitters at once, so an inquiry reads as a race that a sitter loses by sleeping. Because reply speed is understood to feed search standing, the inbox stops being a place to talk to clients and becomes a monitored performance metric.",
        "quotes": [
          {
            "text": "I didn’t respond for two hours because I was asleep. They never responded back to me when I accepted and I assume they found someone else.",
            "url": R + "/1iid1ob/does_it_have_to_be_immediate/",
            "author": "Affectionate-Toe4",
            "date": "2025-02-05"
          },
          {
            "text": "I feel like if I don’t use my phone enough I miss out on potential bookings when they message me.",
            "url": R + "/1keqm6v/does_anyone_else_just_feel_phone_fatigue_on_rover/",
            "author": "Hot-Honeydew-9713",
            "date": "2025-05-04"
          },
          {
            "text": "My inbox was pretty overwhelmed and my quick reply time was hurt in the process, even got set to away when I just stepped away during the weekend.",
            "url": R + "/1mjhg54/i_think_ive_messed_up_my_rover_account/",
            "author": "claytwann",
            "date": "2025-08-06"
          }
        ],
        "implication": "Rover already tracks 24-hour non-response as a business metric, and its own SMS testing found providers want enough detail in the notification to answer straight from their texts. The lever is notification quality and content — not more nudging, which sitters describe as harassment."
      },
      {
        "id": "archive-as-ranking-chore",
        "label": "Archiving is a ranking chore, not an inbox action",
        "count": 125,
        "sentiment": {
          "positive": 0,
          "negative": 71,
          "mixed": 6,
          "neutral": 48
        },
        "summary": "Sitters do not read “archive” as tidying up. They read it as compliance: an unbooked conversation left past roughly 72 hours reportedly suppresses their search visibility, so they archive constantly — while fearing the archive is itself recorded as a decline against their standing. The flow never tells them what the owner sees, or whether it can be undone.",
        "quotes": [
          {
            "text": "When unbooked requests sit in your inbox for 72 hours or longer, that indicates to Rover that you're too busy or unavailable.",
            "url": R + "/1ina8nn/archiving_notification/",
            "author": "marfatapes",
            "date": "2025-02-11"
          },
          {
            "text": "I am ALWAYS having to archive chats.",
            "url": R + "/1l4d4tg/how_long_do_you_give_new_clients_to_respond/",
            "author": "No-Principle7562",
            "date": "2025-06-05"
          },
          {
            "text": "will archiving for “i wasn’t available” affect my sitter status at all?",
            "url": R + "/1il1wvn/does_archiving_affect_my_rates/",
            "author": "anger_leaf",
            "date": "2025-02-09"
          }
        ],
        "implication": "The single highest-volume inbox complaint is not layout — it is an incentive mechanic surfacing as an inbox action. The unusually high neutral share (48 of 125) is sitters asking each other how the rule works, which makes this an in-product explanation gap as much as a design one."
      },
      {
        "id": "notifications-both-ways",
        "label": "Notifications are simultaneously too many and too few",
        "count": 82,
        "sentiment": {
          "positive": 0,
          "negative": 64,
          "mixed": 7,
          "neutral": 11
        },
        "summary": "The same sitter is nagged about an unanswered 2am inquiry and gets no alert at all when a recurring client adds a date. Push arrives late or never, SMS mirrors messages in duplicate, and the quiet-hours control some sitters relied on vanished in an update.",
        "quotes": [
          {
            "text": "If a prospective sit messages me at 2am I have a text notification by 3am chastising me for keeping them waiting, but nothing the morning of with your daily schedule?",
            "url": R + "/1ipsped/no_calendar_export_feature/",
            "author": "brightlove",
            "date": "2025-02-15"
          },
          {
            "text": "I used to be able to set quiet hours so that people can’t message me past midnight and then the app updated and I swear I can’t find this setting anywhere.",
            "url": R + "/1kteyne/where_is_the_quiet_hours_setting_in_the_app/",
            "author": "nobodyshome122",
            "date": "2025-05-23"
          },
          {
            "text": "I did not get a notification that she added Saturday for this week.",
            "url": R + "/1kvtcxe/recurring_weekly_client_no_notification_when/",
            "author": "Big-Business2574",
            "date": "2025-05-26"
          }
        ],
        "implication": "Rover's own Notification Center concept names the over-notification half — users feel “spammed”, driven by over-reliance on email. The VoC supplies the other half: the misses cluster on booking changes and recurring bookings. Cutting volume alone would make the misses worse; this needs routing by event type."
      },
      {
        "id": "media-upload-failure",
        "label": "Photo and video upload is the most concrete failure",
        "count": 53,
        "sentiment": {
          "positive": 2,
          "negative": 38,
          "mixed": 3,
          "neutral": 10
        },
        "summary": "Uploads stall, fail, or require the app to stay in the foreground; a 17-second video can take minutes. When it fails sitters do not retry — they text the photo instead. This is the clearest case where the surface's own unreliability manufactures the off-platform behavior Rover polices elsewhere.",
        "quotes": [
          {
            "text": "god forbid I try to send a 17 second video, that shit takes over 5 minutes to send and I have to stay on the Rover app or it won’t send",
            "url": R + "/1j39dob/rover_app_sucks/",
            "author": "NootokTheGecko",
            "date": "2025-03-04"
          },
          {
            "text": "even if I decline and archive a booking, it stays, and doesn't give me the option to delete directly from the calendar",
            "url": R + "/1hsvou9/appgoogle_calendar_question/",
            "author": "StoryAlternative6476",
            "date": "2025-01-03"
          },
          {
            "text": "Since yesterday I have not been able to upload any photos from my gallery to Rover.",
            "url": R + "/1j9jjdq/photos_not_uploading/",
            "author": "randomcactuspup",
            "date": "2025-03-12"
          }
        ],
        "implication": "Rover chartered a survey on exactly this in 2024 and recorded that it could not measure success or failure rates at all. Two years on, the VoC is unchanged. Closing the measurement gap is a prerequisite to fixing the failure — and because Cards usability tested clean, the fault is upload reliability on the conversation page, not the flow."
      },
      {
        "id": "messages-vanish",
        "label": "Messages that never arrive, and threads that disappear",
        "count": 50,
        "sentiment": {
          "positive": 0,
          "negative": 46,
          "mixed": 2,
          "neutral": 2
        },
        "summary": "The most uniformly negative theme in the set: 46 of 50 rows are negative. Requests announced by SMS that are absent from the app, clients receiving neither messages nor Cards, auto-replies the sitter never wrote. Sitters' recurring fear is that they have been silently ignoring clients for days.",
        "quotes": [
          {
            "text": "I got a text notification for a new request on Rover, but when I went to the app to view the request, it wasn’t there?",
            "url": R + "/1kkfp95/bug_in_app_when_viewing_new_requests/",
            "author": "violetslush",
            "date": "2025-05-12"
          },
          {
            "text": "Every time I get a message from a client on Rover an automatic response happens and I don’t know what is going on.",
            "url": R + "/1k9adjq/please_help/",
            "author": "Plaintalk97",
            "date": "2025-04-27"
          },
          {
            "text": "she isn’t getting any rover cards nor any messages I send through rover",
            "url": R + "/1ldm0zd/rover_cards/",
            "author": "jellsmi",
            "date": "2025-06-17"
          }
        ],
        "implication": "Rover's own post-launch interviews recorded sitters using SMS “because they find messages don't always send properly on the app.” This theme is the mechanism behind the platform's SMS dependence, and the 100-conversations analysis shows what leaves with it: logistics and booking changes."
      },
      {
        "id": "contact-filter-friction",
        "label": "The contact-info filter punishes people for its own gaps",
        "count": 43,
        "sentiment": {
          "positive": 0,
          "negative": 30,
          "mixed": 2,
          "neutral": 11
        },
        "summary": "The filter reads booking date ranges as phone numbers, stops clients sending their own address before a home visit, and fires while sitters are actively refusing off-app requests. Sitters self-censor in the thread; clients route around it by photographing their number. Some report warnings and lost status.",
        "quotes": [
          {
            "text": "And I kept getting this stupid pop up and it wouldn’t allow me to send the message?!",
            "url": R + "/1kozn65/phone_number_detection_getting_ridiculous/",
            "author": "uberdyke420",
            "date": "2025-05-17"
          },
          {
            "text": "they are not being allowed to send me their address via messaging. It keeps saying it’s like a phone number.",
            "url": R + "/1s8yyde/asking_for_client_address/",
            "author": "Corkster-JC",
            "date": "2026-03-31"
          },
          {
            "text": "the client sent me a photo of her phone number",
            "url": R + "/1tope0a/client_sent_me_her_phone_number_after_i_archived/",
            "author": "strawb3rry_fr0g",
            "date": "2026-05-27"
          }
        ],
        "implication": "Enforcement lands on the wrong end of the causal chain. Rover's media survey itself named upload failure as an avenue to diversion, and the sharpest case in this corpus is a sitter warned for sharing a number only because the thread would not carry a PDF of care instructions. Close the capability gaps and the filter has less to police."
      },
      {
        "id": "cards-vs-messages",
        "label": "Rover Cards and chat photos blur — sometimes publicly",
        "count": 34,
        "sentiment": {
          "positive": 2,
          "negative": 19,
          "mixed": 5,
          "neutral": 8
        },
        "summary": "Sitters cannot reliably tell which surface a photo will land on. Several independent reports describe images sent privately in a conversation — a chewed couch, litter-box shots, a hidden-key photo — auto-publishing to the pet's profile after a per-photo toggle was removed, with no way to take them back.",
        "quotes": [
          {
            "text": "I sent the owner a picture of a couch her dog chewed up and it posted to the dogs profile",
            "url": R + "/1htn1q5/help/",
            "author": "Lonely_Cranberry5829",
            "date": "2025-01-04"
          },
          {
            "text": "they will upload photos from their stay of my baby and it automatically goes into ur pet’s profile",
            "url": R + "/1mcygff/photos_taken_by_sitter_now_on_pet_photo_feed/",
            "author": "Freck2392",
            "date": "2025-07-30"
          },
          {
            "text": "all could do was take a picture via the Rover app, I couldn't upload anything from my device or photo storage",
            "url": R + "/1jhpl81/is_uploading_photos_to_rover_no_longer_allowed/",
            "author": "Mysterious-Sound-893",
            "date": "2025-03-23"
          }
        ],
        "implication": "The highest-severity item in the set relative to its volume: a sharing default that publishes what the sender believed was a private message. Rover Card usability tested clean at 10 of 10 users, so this is a surface-boundary and default-sharing problem, not a usability one."
      },
      {
        "id": "inbox-navigation",
        "label": "The inbox itself: loading, state, and finding things again",
        "count": 23,
        "sentiment": {
          "positive": 0,
          "negative": 19,
          "mixed": 4,
          "neutral": 0
        },
        "summary": "Threads fail to load exactly when a sitter is busiest, requests hold contradictory Pending and Booked states, archived items stay stuck until a reinstall. The redesign drew both praise for killing unread-hunting and an “ugly and confusing”. Strikingly, almost nobody asks for search — one post in the entire corpus.",
        "quotes": [
          {
            "text": "my inbox is so ugly and confusing",
            "url": R + "/1ld1pi0/new_update/",
            "author": "Odd_Sun_6861",
            "date": "2025-06-16"
          },
          {
            "text": "The one booking request sat in my inbox forever showing as Pending, the second was showing as Booked.",
            "url": R + "/1jm080n/booked_sit_showing_as_pending/",
            "author": "angelsowlsbellsboots",
            "date": "2025-03-28"
          },
          {
            "text": "Bookings weren't showing up in my inbox and pending requests in my inbox that I've either finished or archived wouldnt move.",
            "url": R + "/1kucni6/the_app_issues_lately/",
            "author": "throwawaylovesdogs",
            "date": "2025-05-24"
          }
        ],
        "implication": "The sharpest divergence between VoC and research on this page. Three Rover studies name retrieval from old threads — door codes, revised care instructions — as a top need, but Reddit says the inbox is slow and its states are wrong, not that search is missing. The funded search MVP indexes conversation names rather than message content, so it will not close the need research identified."
      },
      {
        "id": "thread-bound-to-booking",
        "label": "Conversations are hostages of their booking",
        "count": 17,
        "sentiment": {
          "positive": 0,
          "negative": 12,
          "mixed": 0,
          "neutral": 5
        },
        "summary": "A thread's existence is tied to a booking's state. Inquiries stay invisible until something is confirmed, an expired request makes the conversation unreachable, and owners cannot simply message a sitter without filing a request first.",
        "quotes": [
          {
            "text": "I can't find the conversation anymore in order to book it, does this mean i was blocked? or since the request expired, can I just not access it?",
            "url": R + "/1uzbrln/cant_see_a_request_anymore/",
            "author": "TrishTrashWannaSmash",
            "date": "2026-07-17"
          },
          {
            "text": "It’s annoying that pet parents can’t send a message/ contact a sitter in any way without sending a booking request.",
            "url": R + "/1v9v1s1/cant_contact_sitters_without_sending_booking/",
            "author": "ashbash325",
            "date": "2026-07-29"
          },
          {
            "text": "And until I confirm some part of the sit/drop in/walk, the convo doesn't show up in Rover.",
            "url": R + "/1krn30m/ongoing_convos_are_missing/",
            "author": "Guttermouthphd",
            "date": "2025-05-21"
          }
        ],
        "implication": "Owners and sitters both hit this from opposite sides. It is also the structural reason the off-platform pull is strongest around changes: when a thread cannot outlive or precede its booking, SMS becomes the only continuous record of the relationship."
      },
      {
        "id": "support-in-thread",
        "label": "Support inside the thread adds a third, unclear voice",
        "count": 7,
        "sentiment": {
          "positive": 0,
          "negative": 6,
          "mixed": 1,
          "neutral": 0
        },
        "summary": "Small in volume but corrosive in effect. Support's advice on the archive rule contradicts itself between agents, Support messaging from inside a client's account reads as phishing, and sitters escalate past an AI assistant to get an answer about their own inbox.",
        "quotes": [
          {
            "text": "Rover Support's answer was to archive the request until I book it.",
            "url": R + "/1jlwdw7/anyone_else_have_to_archive_requests_past_5_days/",
            "author": "MrCatWrangler",
            "date": "2025-03-28"
          },
          {
            "text": "I got a message from a potential boarder, but they claim to be from Rover Support on behalf of the boarder.",
            "url": R + "/1mfi8lq/rover_support_using_boarders_account/",
            "author": "Pristine-Elk-7723",
            "date": "2025-08-02"
          },
          {
            "text": "I cannot modify, cancel, or archive the booking because I literally do not have any options to do that anywhere in the app or the desktop version.",
            "url": R + "/1nor0ur/so_has_anyone_been_unable_to_archive_or_cancel_a/",
            "author": "literal-e-0",
            "date": "2025-09-23"
          }
        ],
        "implication": "Because the archive rule is unclear, Support becomes its documentation — and gives inconsistent answers. Explaining the mechanic in-product would remove most of this contact, and the phishing-shaped Support message is worth fixing on trust grounds alone."
      },
      {
        "id": "what-works",
        "label": "What already works",
        "count": 7,
        "sentiment": {
          "positive": 6,
          "negative": 0,
          "mixed": 1,
          "neutral": 0
        },
        "summary": "Positive sentiment is thin — 10 of 506 on-topic rows — and almost all of it is about the same two things: the redesigned inbox's unread and status tabs, and the simple act of sending pet photos, which sitters and owners both describe with real warmth.",
        "quotes": [
          {
            "text": "Unread: This fixes the issue where you used to have to scroll and scroll to find the one unread message.",
            "url": R + "/1lei788/several_things_i_like_about_this_app_update_and/",
            "author": "Repulsive-Berry-82",
            "date": "2025-06-18"
          },
          {
            "text": "One of my absolute favorite things is sending photos to owners during their pets’ boarding or daycare.",
            "url": R + "/1jcv3ev/love_taking_pictures_for_clients/",
            "author": "ResidentScience8059",
            "date": "2025-03-16"
          },
          {
            "text": "They send 2-3 random pics throughout the day, sometimes with a funny caption, and I am happy as a clam.",
            "url": R + "/1r9p0xu/updates_from_my_sitter/",
            "author": "NOjax05",
            "date": "2026-02-20"
          }
        ],
        "implication": "Worth protecting. The photo-sharing moment is the emotional core of the product for both sides, which is exactly why upload failure and the profile-publishing default are more damaging than their volume suggests."
      }
    ],
    "research": [
      {
        "id": "4334848179",
        "title": "Findings: Inbox usability testing",
        "space": "DSN",
        "url": "https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4334848179/Findings+Inbox+usability+testing",
        "method": "Moderated usability testing with US and CAN providers · segments stated verbatim as 'High volume / Variant / 5.5', 'High volume / Holdout / 5', 'Infrequent / Variant / 1', 'Infrequent / Holdout / 2' · Dec 2024",
        "takeaway": "The redesigned Inbox with status filters tested well and was seen as superior to both the current prod variant and the holdout, but the message-card layout reads as chaotic and the single loudest unprompted complaint from high-volume sitters was app slowness and bugginess in Inbox and the conversation page.",
        "quotes": [
          {
            "text": "Top issue almost all HVS mentioned: Lags, slowness, and bugginess.",
            "url": "https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4334848179/Findings+Inbox+usability+testing",
            "author": "Other findings/observations — What do they find frustrating or challenging?"
          },
          {
            "text": "The app can be slow to show the new message after notification comes through.",
            "url": "https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4334848179/Findings+Inbox+usability+testing",
            "author": "Other findings/observations — What do they find frustrating or challenging?"
          },
          {
            "text": "Bugginess – having to restart the app entirely to see messages appear.",
            "url": "https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4334848179/Findings+Inbox+usability+testing",
            "author": "Other findings/observations — What do they find frustrating or challenging?"
          }
        ],
        "relevanceToTiers": "The strongest single piece of validated evidence that messaging's biggest pain for high-volume sitters is reliability and latency in the thread, not organization — filters already tested as a success."
      },
      {
        "id": "4484235551",
        "title": "Findings: Inbox filter revision usability testing",
        "space": "DSN",
        "url": "https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4484235551/Findings+Inbox+filter+revision+usability+testing",
        "method": "Moderated usability testing on a revised Inbox filter prototype · '5 HVS in the holdout group / 4 HVS in the variant group' · Feb 2025",
        "takeaway": "Sitters strongly understand and value the booking-status and unread filters, but the default \"Inbox\" filter itself is not noticeable or comprehensible on landing; separately, sitters cannot retrieve information (door codes, revised care instructions) buried in past message threads.",
        "quotes": [
          {
            "text": "The “Inbox” filter is not noticeable as being applied by default.",
            "url": "https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4484235551/Findings+Inbox+filter+revision+usability+testing",
            "author": "Findings by learning objective — Do highly active sitters understand the inbox on landing? (low comprehension)"
          },
          {
            "text": "Highest priority to see when arriving at Inbox is Unread messages, to ensure they’re not missing anything or failing to respond.",
            "url": "https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4484235551/Findings+Inbox+filter+revision+usability+testing",
            "author": "Findings by learning objective — What is the sentiment around the default Inbox view?"
          },
          {
            "text": "Difficulty finding details the owner provided in past messages, like door codes or revised care instructions.",
            "url": "https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4484235551/Findings+Inbox+filter+revision+usability+testing",
            "author": "Other inbox feedback"
          }
        ],
        "relevanceToTiers": "Establishes the retrieval problem (information trapped in old threads) and the SMS/app message-ordering defect as live, validated complaints on top of an otherwise well-received filter design."
      },
      {
        "id": "4198694976",
        "title": "App Inbox: post-launch write-up",
        "space": "DSN",
        "url": "https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4198694976/App+Inbox+post-launch+write-up",
        "method": "Post-launch qualitative interviews about the migrated app Inbox · page states no sample size, referring only to 'participants' and 'high booking volume participants' · Oct 2024",
        "takeaway": "After the Inbox migration, only high-volume sitters struggled — past bookings mixed in with pending/upcoming/current felt disorganized and required more scrolling — and the absence of search made retrieving information from a past conversation so cumbersome that sitters preferred to re-ask the owner or keep personal notes.",
        "quotes": [
          {
            "text": "Several participants mentionned having difficulty finding specific information that lived in a past booking conversation because the lack of search feature required them to scroll through a long list of conversation",
            "url": "https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4198694976/App+Inbox+post-launch+write-up",
            "author": "Interview insights — General"
          },
          {
            "text": "Even then, the lack of search feature makes this task cumbersome and most participant prefer to ask for the information again or make use of personal notes",
            "url": "https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4198694976/App+Inbox+post-launch+write-up",
            "author": "Interview insights — Folder structure"
          },
          {
            "text": "Some used primarily text or a mix of both because they find messages don’t always send properly on the app",
            "url": "https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4198694976/App+Inbox+post-launch+write-up",
            "author": "Interview insights — General"
          }
        ],
        "relevanceToTiers": "Ties the search gap directly to a behavioral cost (sitters re-ask owners or leave the platform for notes) and names message send-failure as a stated reason sitters switch to SMS."
      },
      {
        "id": "6111789075",
        "title": "1P: Search in the Inbox",
        "space": "PSD",
        "url": "https://roverdotcom.atlassian.net/wiki/spaces/PSD/pages/6111789075/1P+Search+in+the+Inbox",
        "method": "Product one-pager · no study or sample; the 'Customer feedback' and 'Usage data' sections are empty · Aug 2026",
        "takeaway": "Rover states as its own problem definition that scrolling to find information in the Inbox is a top usability pain point, and the MVP answer is a name-only search that indexes conversations rather than message content.",
        "quotes": [
          {
            "text": "Currently, Sitters have scroll and scroll and scroll to find relevant information in their Inbox making it a top usability pain point",
            "url": "https://roverdotcom.atlassian.net/wiki/spaces/PSD/pages/6111789075/1P+Search+in+the+Inbox",
            "author": "Problem statement"
          },
          {
            "text": "Only allow user to search by pets' and people’s name so we only index conversations and not messages",
            "url": "https://roverdotcom.atlassian.net/wiki/spaces/PSD/pages/6111789075/1P+Search+in+the+Inbox",
            "author": "Solution Space — MVP"
          },
          {
            "text": "For the initial ramp up we will index conversation from users that have had a new conversation created in the last 6 months",
            "url": "https://roverdotcom.atlassian.net/wiki/spaces/PSD/pages/6111789075/1P+Search+in+the+Inbox",
            "author": "Solution Space — MVP"
          }
        ],
        "relevanceToTiers": "Product 1-pager in 'Roll-out plan: TBD / Results: TBD' state with empty customer-feedback and usage-data sections — cite as Rover's own problem framing and current scope, not as evidence. Shows search is now funded but scoped to conversation names only — which does not solve the repeatedly validated need to find a door code or care instruction inside an old message."
      },
      {
        "id": "3631644973",
        "title": "Media Upload Feedback Survey",
        "space": "DSN",
        "url": "https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/3631644973/Media+Upload+Feedback+Survey",
        "method": "Survey plan (page 3631644973, May 2024) plus its finalized instrument (page 3735322658 'Media upload feedback survey draft', May 2024) · 'Qualaroo survey on iOS, triggered on next page view after a photo or video upload on the conversation page' · targeted to Sitters in US/CAN/UK on the iOS native app · Apr–May 2024",
        "takeaway": "Rover chartered this survey because it could not quantify media-upload failures at all — logging gaps meant no read on success rates, upload time, failure reasons or retries — while sitters were already routing photo and video updates to SMS and Facebook Messenger instead.",
        "quotes": [
          {
            "text": "We have consistently received feedback from Sitters about how it is difficult for them to send photo and video updates to their clients in the App. And because of this, they have had to rely on other communication methods like text and FB messenger to send these updates. Off platform communication is an easy avenue to diversion which we want to prevent.",
            "url": "https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/3631644973/Media+Upload+Feedback+Survey",
            "author": "Background"
          },
          {
            "text": "This app has become less usable over my several years as a high volume sitter. App is very slow to respond lately. I have to send videos thru fb msgr because maybe 20% off the videos actually are sent to my clients...",
            "url": "https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/3631644973/Media+Upload+Feedback+Survey",
            "author": "Verbatim sitter feedback quoted in Background"
          },
          {
            "text": "we have come across measurability gaps in our data that is making it difficult for us get a pulse on success/ failure rates, time it takes to upload, failure reasons, number of retries, etc.",
            "url": "https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/3631644973/Media+Upload+Feedback+Survey",
            "author": "Background"
          }
        ],
        "relevanceToTiers": "Survey plan plus its finalized question wording — no results are recorded on either page. The six failure-mode answer options are evidence of the failure modes Rover already knew about, not of their prevalence. The clearest internal statement that media upload in the conversation page is both a known failure mode and unmeasured, and that its failure directly drives off-platform communication and diversion risk."
      },
      {
        "id": "4747695919",
        "title": "Q1 2025 Report: Ad-hoc questions - Messaging",
        "space": "DSN",
        "url": "https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4747695919/Q1+2025+Report+Ad-hoc+questions+-+Messaging",
        "method": "Ad-hoc messaging questions on a multi-country sitter survey (CA, ES, FR, UK, US), reported as percentages by country and by 'all sitters' vs 'HVS + consistent' segments · page states no respondent counts, only percentages · Q1 2025, published Jun 2025",
        "takeaway": "SMS, not the app, is how a large share of sitters actually prefer to be notified and (in the US) to communicate — 77% of US sitters call SMS essential and 56% of US sitters prefer SMS over the app for client communication — while net-new messaging features (audio, video calling) draw little appetite.",
        "quotes": [
          {
            "text": "For most sitters in the US and CA, SMS is essential and its removal would negatively impact them. This feeling is even more prevalent among US and CA HVS and consistent sitters.",
            "url": "https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4747695919/Q1+2025+Report+Ad-hoc+questions+-+Messaging",
            "author": "SMS: CA, UK, and US — Summary"
          },
          {
            "text": "SMS is the most preferred notification method, over email and push, in all countries, but to a lesser extent in the UK.",
            "url": "https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4747695919/Q1+2025+Report+Ad-hoc+questions+-+Messaging",
            "author": "SMS: CA, UK, and US — Summary"
          },
          {
            "text": "The Rover app is the preferred communication method for a majority of CA and UK sitters, while more US sitters prefer SMS over the app.",
            "url": "https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4747695919/Q1+2025+Report+Ad-hoc+questions+-+Messaging",
            "author": "SMS: CA, UK, and US — Summary"
          }
        ],
        "relevanceToTiers": "Percentages are reported without base sizes anywhere on the page, so segment cuts (especially 'HVS + consistent') cannot be weighted for precision. Quantifies how much messaging traffic is already leaving the product surface, and argues against spending on new modalities (audio, video) before fixing notification and thread reliability."
      },
      {
        "id": "4085973319",
        "title": "Findings: SMS comparative testing",
        "space": "DSN",
        "url": "https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4085973319/Findings+SMS+comparative+testing",
        "method": "Comparative concept testing of three SMS booking-request notification treatments (A = current 3 texts + profile screenshot, B = 2 texts + screenshot, C = single minimal notification) with providers · page states no participant count, referring only to 'participants' and 'the majority' · Aug 2024",
        "takeaway": "Providers reject a stripped-down SMS notification: they want enough booking detail (dates, times, pet names, pet profile screenshot) to answer immediately from their texts, and removing detail predictably pushes them into asking the owner questions the owner already answered.",
        "quotes": [
          {
            "text": "C was universally seen as too minimal and because of the lack of information, removes the possibility that they could respond immediately via text.",
            "url": "https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4085973319/Findings+SMS+comparative+testing",
            "author": "Reaction to the notification options"
          },
          {
            "text": "We shouldn’t underestimate the annoyance factor that comes with switching contexts from SMS to our app.",
            "url": "https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4085973319/Findings+SMS+comparative+testing",
            "author": "Reaction to the notification options"
          },
          {
            "text": "Push can be easy to miss among other notifications, while SMS is higher visibility and persistance.",
            "url": "https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4085973319/Findings+SMS+comparative+testing",
            "author": "Notifications — The value of SMS notifications"
          }
        ],
        "relevanceToTiers": "Findings are validated qualitative, but the page never states a participant count or recruitment criteria — treat magnitudes ('the majority', 'a few') as directional. Explains why booking-request notification content is load-bearing for response speed, and why push alone is not a substitute for SMS in sitters' actual workflow."
      },
      {
        "id": "4644766640",
        "title": "Notification center",
        "space": "DSN",
        "url": "https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4644766640/Notification+center",
        "method": "Concept 1-pager, status stated verbatim as 'Status: Concepting' · no study; sole supporting evidence cited is 'Feedback from the VoC' · Feb 2026",
        "takeaway": "Rover's own framing is that notification volume across email, push and SMS makes users feel spammed, and that the existing notification center occupies prominent UI in both apps and on web while delivering no meaningful value.",
        "quotes": [
          {
            "text": "Rover users are experiencing multiple and fragmented communications, leading to a feeling of being “spammed.” This is primarily due to an over-reliance on email.",
            "url": "https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4644766640/Notification+center",
            "author": "Opening problem statement"
          },
          {
            "text": "The current notification center is underutilized and lacks meaningful value despite occupying a prominent place in the UI in both the native mobile apps and the web.",
            "url": "https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4644766640/Notification+center",
            "author": "Opening problem statement"
          },
          {
            "text": "SMS does not stay within native notification centers. This would provide a permanent place for redundant messages",
            "url": "https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4644766640/Notification+center",
            "author": "Additional benefit"
          }
        ],
        "relevanceToTiers": "Concepting 1-pager (hypothesis and proposed solution), not findings — its only cited evidence is unspecified 'Feedback from the VoC'. Cite as framing. Names the counterweight to the SMS findings: notification volume is itself a complaint, so the fix for missed messages cannot simply be more channels."
      },
      {
        "id": "5822383408",
        "title": "100 conversations in smoke test",
        "space": "PSD",
        "url": "https://roverdotcom.atlassian.net/wiki/spaces/PSD/pages/5822383408/100+conversations+in+smoke+test",
        "method": "Qualitative content analysis of message threads · 'a sample of 100 conversations pulled from Rover’s admin tools', each thread reviewed end-to-end and tagged against logistics, payment/booking mechanics, and off-platform coordination themes · Mar 2026",
        "takeaway": "Read end-to-end, real sitter-owner threads are dominated by logistics and care coordination, and the off-platform pull shows up not as an explicit decision but as micro-changes (moving a day, adding a walk, paying for one extra visit) handled in SMS because the booking product is more friction than the text thread.",
        "quotes": [
          {
            "text": "Owners and sitters adjust days, times, and sometimes full trips purely in SMS",
            "url": "https://roverdotcom.atlassian.net/wiki/spaces/PSD/pages/5822383408/100+conversations+in+smoke+test",
            "author": "Diversion & Off‑Platform Gravity — Granular changes handled via text, not bookings"
          },
          {
            "text": "Those micro‑interactions are where diversion risk spikes:",
            "url": "https://roverdotcom.atlassian.net/wiki/spaces/PSD/pages/5822383408/100+conversations+in+smoke+test",
            "author": "Diversion & Off‑Platform Gravity — Granular changes handled via text, not bookings"
          },
          {
            "text": "When there are lots of small changes, Rover’s booking UX can feel like friction, so people start negotiating outside",
            "url": "https://roverdotcom.atlassian.net/wiki/spaces/PSD/pages/5822383408/100+conversations+in+smoke+test",
            "author": "Diversion & Off‑Platform Gravity — Busy or complicated bookings"
          }
        ],
        "relevanceToTiers": "Live page written as an AI-assisted thematic review of admin conversation logs; the tagging was not independently coded and the sample was drawn for a tiered-incentives question, so messaging themes are a secondary read of the same corpus. The only source here that reads what is actually said inside threads, and it locates the highest-value in-thread gap: inline booking changes and a plain-language explanation of payment mechanics that sitters currently improvise themselves."
      },
      {
        "id": "4500457050",
        "title": "Prevent Third Party Interruptions in Conversations",
        "space": "DSN",
        "url": "https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4500457050/Prevent+Third+Party+Interruptions+in+Conversations",
        "method": "Problem 1-pager built from a single documented incident (12/1/24, traced in admin) plus four verbatim sitter comments collected from a Rover sitters Facebook group · no study or sample · Feb 2025",
        "takeaway": "Strangers still land inside Rover conversations via the Twilio relay number, and the author's read of the evidence is that the relay number rather than the user-supplied number is the likely cause — which sitters experience as lost clients and abusive messages in front of their customers.",
        "quotes": [
          {
            "text": "We have some reports of third parties being looped into Rover conversations. Often this leads to the third party responding in a negative way which is a major trust breaker.",
            "url": "https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4500457050/Prevent+Third+Party+Interruptions+in+Conversations",
            "author": "Problem"
          },
          {
            "text": "I’ve lost many potential clients because of this reason - rover uses phone numbers that can be registered to other people..I’ve had people cuss in the chat, I’ve had people call and it go to my client and they get their face chewed off, some have blocked it so I have to wait until they go on the app to chat.",
            "url": "https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4500457050/Prevent+Third+Party+Interruptions+in+Conversations",
            "author": "Sitter comment quoted from the Rover sitters Facebook group"
          },
          {
            "text": "It happened to me a couple times. It’s when a spoofed Rover number is also someone’s actual number. Report to Rover and they’ll pull the spoofed number out of the system.",
            "url": "https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4500457050/Prevent+Third+Party+Interruptions+in+Conversations",
            "author": "Sitter comment quoted from the Rover sitters Facebook group"
          }
        ],
        "relevanceToTiers": "Problem 1-pager with 'TBD solution' — root cause is stated as a hypothesis awaiting a spike, and the corroborating quotes are unverified Facebook-group comments, not recruited research. A low-frequency but maximum-severity messaging failure: a third party speaking inside a live client conversation, with the solution still at 'conduct a spike' and 'TBD solution'."
      },
      {
        "id": "4027580577",
        "title": "Write-up: Rover Card migration validation",
        "space": "DSN",
        "url": "https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4027580577/Write-up+Rover+Card+migration+validation",
        "method": "'unmoderated user testing with 10 users. Half has done Rover Cards in the past, half haven’t' · task flow from starting a Rover Card in the Daily Dash to sending the card to the pet parent · Jul 2024",
        "takeaway": "The migrated Rover Card flow validated cleanly — all 10 users rated it Very Easy and everyone found photo adding, care info, activities and calling the owner — with the residual gaps being video support, an option to message the pet parent, and unclear finality of the Finish CTA.",
        "quotes": [
          {
            "text": "All users rated the test as Very Easy.",
            "url": "https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4027580577/Write-up+Rover+Card+migration+validation",
            "author": "Opening summary"
          },
          {
            "text": "Yes, all users were able to discover and add photos easily.",
            "url": "https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4027580577/Write-up+Rover+Card+migration+validation",
            "author": "Learning Objectives — Can users discover how to and add photos?"
          },
          {
            "text": "1 user mentioned it is missing the ability to add videos.",
            "url": "https://roverdotcom.atlassian.net/wiki/spaces/DSN/pages/4027580577/Write-up+Rover+Card+migration+validation",
            "author": "Learning Objectives — Is there anything missing or confusing with the new experience?"
          }
        ],
        "relevanceToTiers": "Sets the baseline that photo sending inside Rover Cards is not a usability problem — which isolates the media pain to upload reliability in the conversation page rather than to the flow itself."
      }
    ],
    "images": [],
    "crossCheck": {
      "title": "Cross-check: the BKS plan to improve Rover messaging",
      "source": {
        "title": "Improve the Rover Messaging Experience",
        "url": "https://roverdotcom.atlassian.net/wiki/spaces/BKS/pages/6284542665/Improve+the+Rover+Messaging+Experience",
        "space": "BKS · Booking Product Group",
        "author": "Aaron Mitchell",
        "date": "Aug 2026",
        "docType": "Evidence tier: this is a product plan, not research — its benchmark table is a competitive scan of iOS Messages, WhatsApp, Airbnb, Reddit, Slack and Instagram, and it states no study behind any prioritization."
      },
      "framing": [
        "BKS sits outside the DSN + PSD scope this dashboard ingests, so this plan was not in the evidence base above, and the plan in turn does not cite this corpus. Read together they agree on the diagnosis — messaging is heavily used and heavily complained about — and disagree almost completely on the remedy. The plan is feature-parity work: emoji reactions, reply-to-message and send animations are its three P0s. The corpus’s loudest clusters are reliability defects and marketplace incentive mechanics, and none of the three P0s appears in it at all.",
        "The sharpest challenge to the plan is not this corpus, though — it is another BKS page. “Rover Messaging: The Case for Investment” (Josh Harris and Guillem Pons, Jun 2026) argues the problem is that the product “fails at the basics”: in-app calling broken for over two years, every message firing three simultaneous notifications, video uploads too slow to be practical, no group chat, and every booking starting a new thread. That page and this corpus agree closely. The Aug 2026 plan shares almost none of its content, and its cut line rejects items on polish grounds without engaging the reliability argument. Two BKS documents two months apart propose different products; the VoC backs the earlier one.",
        "Even-handedly: several of the plan’s rejections are exactly right, its emoji copy spec is well-specified, and its read-receipts rationale correctly anticipates this corpus’s single largest cluster. Where the plan is under-evidenced, that is often because Reddit does not complain about missing conveniences — an absence here is weak evidence of absence, and Jakob’s-Law parity does not need VoC support to be a reasonable argument. Each verdict below says which kind of gap it is."
      ],
      "alsoFound": [
        {
          "title": "Rover Messaging: The Case for Investment",
          "url": "https://roverdotcom.atlassian.net/wiki/spaces/BKS/pages/6142593222/Rover+Messaging+The+Case+for+Investment",
          "note": "Josh Harris and Guillem Pons, Jun 2026. A joint Owner/Provider proposal whose problem statement — broken in-app calling, triple notifications, slow video upload, no group chat, thread-per-booking, no relationship history — matches this corpus more closely than any of the eleven DSN/PSD studies above. Also a proposal rather than research, and candid that “you can’t build a clean feature-level ROI model for messaging infrastructure.”"
        },
        {
          "title": "🚧 Spec: UK Provider U2U SMS Sunset",
          "url": "https://roverdotcom.atlassian.net/wiki/spaces/BKS/pages/6005620935/Spec+UK+Provider+U2U+SMS+Sunset",
          "note": "Emma Sahn, Jul 2026. A live 50:50 A/B suppressing user-to-user SMS for UK providers against ~£280K a year, with response rate within one hour as the primary metric. This is the SMS cost thesis already under test, and it is the instrument that would settle the survey question below — the messaging plan cites the savings without citing the experiment."
        }
      ],
      "items": [
        {
          "id": "read-receipts",
          "claim": "“Add Read receipts — No - This puts pressure on the sitter to respond and may increase owner anxiety.” Also cut: “Add ‘typing’, ‘sent’, ‘seen’ to inbox preview — No - Not worth building inbox preview if we are not going to build read receipts.”",
          "planPosition": "Cut line · No",
          "verdict": "mixed",
          "headline": "The rejection is well-reasoned and the corpus backs its stated reason — but users are already reverse-engineering an indicator Rover ships today",
          "evidence": "The plan’s reason is this report’s largest cluster, so it deserves the credit: 134 on-topic posts describe reply speed as a monitored performance metric, 101 of them negative. Adding a read state to that would land on people who already believe standing depends on answering within minutes. The demand side is real too, and much smaller: “read receipt” appears in zero of the 26,597 posts in the export, but four rows across three distinct complaints try to work out what the green check mark already means — and two of the three are asking about delivery, not reading. That is the gap the plan strands. Its send-animation milestone proposes to “Define ‘optimistic’ message status … and ‘delivered’ message status”, then defers that to “the read receipts project” it has just rejected. Delivery confirmation is not a read receipt, carries none of the response pressure, and matters more here than in a normal chat app because 50 posts describe messages that genuinely never arrived. Disambiguating the existing check mark is the version of this the evidence asks for.",
          "quotes": [
            {
              "text": "When you're messaging your sitter does the green check mean they read it?",
              "url": R + "/1rwnbjg/when_youre_messaging_your_sitter_does_the_green/",
              "author": "Popular-Pirate610",
              "date": "2026-03-17"
            },
            {
              "text": "I noticed the message sent without a green check on the bottom right, did she receive my message",
              "url": R + "/1uetcwi/message_delivery/",
              "author": "Due-Team-6129",
              "date": "2026-06-24"
            },
            {
              "text": "she never responded and the green check isn’t there",
              "url": R + "/1tssz29/client_not_responding/",
              "author": "Negative-Pie5361",
              "date": "2026-05-31"
            }
          ]
        },
        {
          "id": "unsend-edit-delete",
          "claim": "“Edit message (temporary window)” and “Delete or Unsend Message (temporary window)” — “Decision to make - Do we want to allow users to edit or delete messages after sending.”",
          "planPosition": "Cut line · Decision to make",
          "verdict": "silent",
          "headline": "Almost no demand as a message feature — but the retraction problem that is documented sits on a surface the plan never touches",
          "evidence": "Exactly one post in the 26,597-post export asks to remove a sent message, and it is a bare question with no body. As a message-level feature this is unevidenced in either direction, and the decision can be made on product grounds. The retraction need that this corpus does document is a different thing on a different surface: 34 posts describe Rover Cards and conversation photos blurring together, including several independent reports of images sent privately in a thread — a chewed couch, litter-box shots, a photo of a hidden key — auto-publishing to the pet’s public profile with no way to take them back. A temporary edit window on messages would not reach any of that. If the plan wants to solve retraction, the photo-publishing default is where the harm actually is, and it is the highest-severity item in this report relative to its volume.",
          "quotes": [
            {
              "text": "Can I delete a message from a convo",
              "url": R + "/1m3ghp1/can_i_delete_a_message_from_a_convo/",
              "author": "Actual-Station7300",
              "date": "2025-07-18"
            }
          ]
        },
        {
          "id": "emoji-reactions",
          "claim": "Emoji reactions, “Feature Parity - Baseline”, P0 — giving “users a way to respond to messages without needing to write a new mwessage, which is a persistent complaint today.” Notification copy is specified as “❤️ to \"{message}\"” or “❤️ to photo”.",
          "planPosition": "P0 · Milestone",
          "verdict": "silent",
          "headline": "No corpus evidence for or against, and the specific defect this cross-check went looking for is not there — but the copy spec already forecloses it",
          "evidence": "This report went looking for a reported defect in which a reaction notification never says which photo was reacted to. It is not in the data: zero posts across the full export match any phrasing of liking, hearting or reacting to a photo or message, and the only adjacent post is a sitter describing an owner who sent no thumbs up or reaction of any kind — a complaint about owner silence, not about the feature. So the hypothesis is not corroborated and should not be repeated. Separately, the plan’s own requirement — “❤️ to \"{message}\"” or “❤️ to photo” — already names the referent, so the ambiguity would not arise as specified. The “persistent complaint today” claim is worth attributing correctly: the plan makes it about having to write a new message to respond, and this corpus contains no instance of that complaint. That is a Reddit-shaped absence rather than a refutation — people rarely post to say a convenience is missing — but the plan should not present it as an established complaint without a source.",
          "quotes": []
        },
        {
          "id": "reply-to-message",
          "claim": "Reply to messages, “Feature Parity - Baseline”, P0 — so users “can clearly communicate what they are referring to when responding to the other party.”",
          "planPosition": "P0 · Milestone",
          "verdict": "silent",
          "headline": "Zero posts, and the collection-artifact explanation was tested and ruled out",
          "evidence": "Nobody in this evidence base asks for threaded replies. Because the term “reply to” had been dropped from the corpus term list early on as a false friend — it matched “reply to a review” — the absence was re-tested against the full 26,597-post export rather than the 964-post corpus, using phrasings that survive that removal: replying to a specific or individual message, quoting a message, threaded replies, and confusion about which message someone is answering. All return zero. The absence is real, not a collection artifact. It is still weak evidence: a subreddit is a complaint channel, and missing conveniences generate far fewer posts than broken features do, so this does not argue against building it. It does argue that “P0” cannot be justified by customer voice, and that the plan’s honest ground here is the parity argument it already makes.",
          "quotes": []
        },
        {
          "id": "audio-messages",
          "claim": "Audio messages — “This feels like it adds a lot of value - but we should be mindful of diversion, so we’d need to speech to text to analyze pipeline.”",
          "planPosition": "Benchmark · above the cut line",
          "verdict": "contradicted",
          "headline": "Rover’s own survey measured this and found the opposite everywhere except Spain",
          "evidence": "The Q1 2025 messaging survey asked sitters in five countries directly. Rated useful (4 or 5 of 5): US 23%, CA 24%, UK 25%, FR 39%, ES 63%. Would use them regularly in daily conversations: US 15%, UK 15%, CA 20%, FR 29%, ES 56%. Combining both, the share that finds audio useful and expects daily use is US 13%, UK 14%, CA 17%, FR 27% — and ES 50%. Among high-volume and consistent sitters it drops further, to 19% useful and 14% daily in the US. The survey’s own first-page insight is that audio messages “are appealing for daily use for about half of ES sitters, but are not as desired in other countries.” The corpus adds one post, a title-only question about whether voice notes would beat typing visit updates — curiosity, not demand. Caveat on tier: the survey is an analysis page and reports percentages with no base sizes anywhere, so treat the magnitudes as directional. Directionally it is unambiguous, it is Rover’s own, and it is aimed squarely at this question. Video calling scores no better: 16–24% on the same combined measure in every country. If audio is built, the survey points at ES and at a WhatsApp-shaped need there, not at a general rollout.",
          "quotes": [
            {
              "text": "Pet sitters — would voice notes be easier than writing visit updates?",
              "url": R + "/1srtxnn/pet_sitters_would_voice_notes_be_easier_than/",
              "author": "VisibleAd7084",
              "date": "2026-04-21"
            }
          ]
        },
        {
          "id": "sms-savings",
          "claim": "“Significant SMS costs savings if we can make it good enough” — listed as a motivation for the investment.",
          "planPosition": "Problem · motivation",
          "verdict": "mixed",
          "headline": "The saving is real and already under test, but the plan states it as settled while the experiment that would justify it has not read out",
          "evidence": "SMS is not a fallback for US sitters, it is the primary channel: Rover’s Q1 2025 survey has 77% calling SMS essential (80% among high-volume and consistent sitters), 66% naming SMS their preferred way to receive updates, and 56% preferring SMS over the app for talking to clients at all. So “make the app good enough and the SMS spend goes away” is a bigger behavioural change than the phrasing implies. On why traffic sits there, this corpus cannot cleanly separate failure from preference and should not pretend to: 74 on-topic posts mention SMS or texting, and 31 of those sit in a delivery-failure theme — photos that only send over text, requests announced by SMS and absent from the app, messages surfacing days late. Failure is clearly part of it. The sharpest wrinkle is that the SMS relay is itself unreliable: one sitter reports roughly half her SMS replies and photos never reaching the Rover thread, so cost is being spent on a channel that is also dropping messages. Credit where due — BKS is already running the right instrument. The UK Provider U2U SMS Sunset spec is a live 50:50 A/B against ~£280K a year, and an experiment is exactly how you resolve stated preference against revealed behaviour. Two cautions on reading it: the survey puts the UK at the low end of SMS attachment (60% essential, versus 77% in the US), so a UK win is the weakest possible read-across to the US; and its primary metric, response rate within one hour, is measured on a population that already experiences the reply clock as punishing. “Response rate held” and “sitters are fine” are not the same finding.",
          "quotes": []
        },
        {
          "id": "star-pin-save",
          "claim": "“Star / Pin / Save Message — This is helpful for things like care instructions, saved items would appear in relationship view.” Listed above the cut line with no priority assigned.",
          "planPosition": "Benchmark · unprioritized",
          "verdict": "supported",
          "headline": "The best-evidenced item on the plan’s list, and it is the one left without a priority",
          "evidence": "Rover’s Feb 2025 inbox filter usability testing — a validated findings page, one of only five in this report’s research set — records that sitters cannot retrieve information buried in past threads, naming door codes and revised care instructions specifically. Three of the studies above converge on the same need. The plan identifies exactly this use case, unprompted, and pairs it with the relationship view, which is the structural fix the Case for Investment argues for. Reddit is nearly silent: only four posts in the whole export use retrieval-from-thread phrasing, consistent with this report’s existing finding that sitters describe the inbox as slow and wrongly stated rather than unsearchable. So the support is research-side, not VoC-side. That is still a stronger evidentiary base than either P0 has, and it is worth noting that the funded search MVP indexes conversation names rather than message content, so pinning may close this need where search will not.",
          "quotes": []
        },
        {
          "id": "plan-evidence-claims",
          "claim": "“It’s the most used part of the app (40% page views) and one of the most complained about”; “Direct evidence it drives diversion on rebooking reach-outs (110k unbooked conversations in 2025)”.",
          "planPosition": "Problem · evidence",
          "verdict": "mixed",
          "headline": "The complaint claim is corroborated in kind; the two analytics figures are outside what this evidence base can check",
          "evidence": "On complaint volume the plan is right, and independently so: 506 on-topic posts across Jan 2025 – Sep 2026, 64% negative against 2% positive, sustained across the whole window rather than spiking around a release. One qualification matters in both directions. This report had to build a bespoke corpus because the dashboard’s taxonomy has no keyword for message, inbox, chat, notification or photo — 249 of the 610 core posts were reachable only by free-text sweep. That means messaging complaints are badly under-counted by Rover’s standing tagger, which strengthens the plan’s claim; it also means this corpus cannot rank messaging against other Rover topics, so “one of the most complained about” is corroborated as large and sustained volume, not as a rank. The 40% page-views and 110k-unbooked-conversations figures are product analytics. Nothing in this evidence base can confirm or refute them, and this report does not attempt to — they should carry a link to the query that produced them so a reader can check them the way the Reddit counts here can be checked.",
          "quotes": []
        }
      ],
      "blindSpots": [
        {
          "label": "The archive mechanic",
          "count": 125,
          "note": "the second-largest cluster in the report and absent from the plan entirely. Sitters archive constantly because an unbooked conversation left past roughly 72 hours is believed to suppress search visibility, while fearing the archive is itself recorded as a decline. Fairly: this is a search-ranking and marketplace decision, not a messaging one — but it is the inbox action sitters take most, and the plan’s cut line rejects “Mark unread” as “unnecessary” without noticing the adjacent state mechanic people are genuinely confused by."
        },
        {
          "label": "Notification delivery and routing",
          "count": 82,
          "note": "the plan has an “Improved in-app notifications” milestone, but it is scoped to appearance — “It should look better / follow kibble”. The corpus problem is not appearance. The same sitter is chased about an unanswered 2am inquiry and gets no alert when a recurring client adds a date; misses cluster on booking changes. Routing by event type is untouched, and the Case for Investment’s triple-notification complaint appears nowhere in this plan."
        },
        {
          "label": "Photo and video upload reliability",
          "count": 53,
          "note": "the most concrete reproducible failure in the report — a 17-second video taking over five minutes with the app held in the foreground, uploads that block every text queued behind them — and the plan’s media content is stickers, custom emoji and branded wallpaper. The Case for Investment names slow video upload explicitly; this plan does not. Rover’s 2024 media survey charter admitted it could not measure the failure rate at all, and that is still true."
        },
        {
          "label": "Messages and threads that never arrive",
          "count": 50,
          "note": "the most uniformly negative theme in the report, 46 of 50 rows negative: requests announced by SMS and missing from the app, clients receiving neither messages nor Cards, one thread showing different photos to each side. This is the mechanism behind the SMS dependence the plan wants to cost-reduce, and no item on the plan — above or below the cut line — addresses delivery."
        },
        {
          "label": "The contact-info filter’s false positives",
          "count": 43,
          "note": "booking date ranges read as phone numbers, clients blocked from sending their own address before a home visit, warnings issued while sitters are actively refusing off-app requests. Partly a Trust and Safety surface rather than a messaging one, but it fires inside the message composer the plan is redesigning, and the plan’s “Report Message” entry point is the only enforcement-adjacent item it carries."
        },
        {
          "label": "Conversation photos publishing publicly",
          "count": 34,
          "note": "a sharing default that publishes what the sender believed was private, with no way to retract it. Directly adjacent to the plan’s open “Decision to make” on unsend, and higher severity than anything above its cut line."
        }
      ]
    },
    "implications": {
      "supports": [
        "Ship delivery confirmation, not read receipts. The BKS plan rejects read receipts for a reason this corpus backs — 134 posts describe reply speed as a monitored metric — but it then defers “define ‘optimistic’ and ‘delivered’ message status” into that rejected project. Owners and sitters are already reverse-engineering the green check mark, two of the three cases are asking about delivery rather than reading, and 50 posts describe messages that never arrived. Delivery state carries none of the response pressure and answers the question people are actually asking.",
        "Give Star / Pin / Save a priority. It is the best-evidenced item on the BKS plan and the only one of its well-aimed items left unprioritized: a validated Rover usability finding names retrieval of door codes and revised care instructions from old threads as an unmet need, and the funded search MVP indexes conversation names rather than message content, so pinning closes a gap search will not.",
        "Fix upload reliability on the conversation page before adding any new media capability. It is the most concrete, most reproducible failure in the corpus, Rover already identified it in 2024, and Cards testing proves the flow is fine — so this is an engineering reliability problem with a known owner.",
        "Instrument media upload success, failure reason and duration. Rover’s own survey charter said the logging gaps made it impossible to get a pulse on failure rates; that is still the blocking constraint on prioritizing this work honestly.",
        "Explain the archive mechanic in-product. 125 rows argue about what archiving does to standing, and a large neutral share is sitters asking each other rather than complaining — a comprehension gap that documentation and one honest in-flow explanation could close cheaply.",
        "Change the default that publishes conversation photos to a pet’s public profile. Multiple independent reports describe private images — a chewed couch, litter-box shots, a hidden key — becoming public with no way to retract them. Low volume, high severity, and a trust problem rather than a feature gap.",
        "Route notifications by event type rather than tuning total volume. The corpus shows misses concentrated on booking changes and recurring-booking edits while nagging is concentrated on unanswered inquiries; a blunt volume cut would worsen the first to fix the second."
      ],
      "cautions": [
        "Do not read this as a mandate to redesign the inbox. Rover’s filter and layout studies tested well, the redesign’s unread tabs drew the corpus’s clearest praise, and the volume here points at mechanics and reliability instead.",
        "Search as currently scoped will not land as a win. Three studies name retrieval of door codes and care instructions from old threads, but the MVP indexes conversation names, not message content — and Reddit barely articulates search at all, so expect little credit and an unmet need.",
        "Resist new modalities, and audio specifically. Rover’s own Q1 2025 survey put the share of sitters who find audio useful and expect daily use at 13% in the US, 14% in the UK and 17% in Canada — against 50% in Spain. Video calling scores 16–24% everywhere. The BKS plan’s read that audio “feels like it adds a lot of value” is contradicted by Rover’s own measurement in every market except ES, where the real signal is WhatsApp.",
        "Do not treat the SMS saving as banked. 77% of US sitters call SMS essential and 56% prefer it over the app for client communication, so this is a behaviour change, not a channel swap — and 31 of the 74 SMS-mentioning posts here sit in a delivery-failure theme, including a sitter reporting roughly half her SMS replies never reach the thread. The UK U2U SMS Sunset A/B is the right instrument and has not read out; its primary metric, response rate within one hour, is also measured on people who already experience that clock as punishing.",
        "Feature parity is not the corpus’s complaint. All three of the BKS plan’s P0s — emoji reactions, reply-to-message, send animations — return zero posts in a 26,597-post export, tested against phrasings chosen to survive the corpus’s own term-list gaps. That is weak evidence rather than a refutation, because Reddit under-reports missing conveniences. But it means P0 here rests on Jakob’s-Law parity, not on customer voice, and the plan should say so rather than calling it “a persistent complaint today”.",
        "Tightening the contact-info filter would make things worse. Its false positives — booking dates read as phone numbers, clients blocked from sending an address — already cost legitimate conversations, and sitters report warnings and status loss over words a client typed.",
        "Two of the top three themes are not owned by messaging. Reply-speed pressure and the archive rule are search-ranking and marketplace-incentive decisions; a messaging team cannot fix them alone, and framing them as inbox work would stall."
      ],
      "openQuestions": [
        "What is the actual media-upload failure rate, by platform and file type? Nobody in this evidence base knows, which is the single largest hole in the story.",
        "Is the 72-hour archive rule real as sitters describe it, and does archiving in fact affect standing? Support has given contradictory answers, and the VoC is built on sitters’ belief rather than on documented behavior.",
        "How much messaging volume actually leaves for SMS, and how much of that is explained by failure rather than preference? 56% of US sitters say they prefer SMS — preference and breakage are currently indistinguishable in the data.",
        "The taxonomy behind this dashboard has no keyword for message, inbox, chat, notification or photo, so the tagger under-collects this topic badly: 249 of the 610 core posts were found only by free-text sweep. Worth a taxonomy round before the next read.",
        "Which BKS plan is the company funding? “Rover Messaging: The Case for Investment” (Jun 2026) and “Improve the Rover Messaging Experience” (Aug 2026) describe different products two months apart — the first is reliability and relationship continuity, the second is feature parity — and this corpus backs the first. The two pages do not reference each other.",
        "What produced the 40% page-views and 110k-unbooked-conversations figures? Both are load-bearing in the BKS plan’s problem statement and neither is checkable from this evidence base; they need a link to the query behind them.",
        "How often does the relay number put a stranger inside a live client conversation? Rover’s 1-pager still lists a spike and a TBD solution, and the severity ceiling is high."
      ]
    },
    "generatedAt": "2026-09-01"
  };
