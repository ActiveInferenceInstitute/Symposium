# Symposium public explorer design contract

## 1. Atmosphere & identity
This is an Institute research program and reading room. Editorial serif titles and quiet monochrome surfaces give full abstracts room to breathe; red identifies actions. Port the existing Institute component system, not a marketing template.
Sources inspected: InstituteOS `library/design-system/tokens/tokens.json` and the public `institute_website/assets/css/instituteos-ds.css` and `styles.css`. These are reference sources only; no private operational content is exported.

## 2. Color
Canonical light palette: background #f9fafb, surface #ffffff, secondary #f3f4f6, text #111827, muted #4b5563; dark: #0a0a0a, #151515, #2a2a2a, #e5e5e5, #999999. Brand fill #dc2626, hover #b91c1c, on-accent #ffffff. Readable link ink #b91c1c light / #f87171 dark follows public website text roles. Neutral dividers use current text at 15% opacity. Dark preference follows the operating system.

## 3. Typography
Institute display stack: Fraunces, Iowan Old Style, Palatino Linotype, Georgia, serif. Body: Inter Tight, Inter, system-ui, sans-serif. Locally available fallbacks preserve offline behavior; no external font requests. Scale 0.875, 1, 1.125, 1.375, 1.75, 2.25, 3rem. Display line-height 1.15; body 1.6. Titles wrap, all unbroken content can wrap. Full abstracts preserve paragraphs.

## 4. Spacing & layout
Institute spacing: .25, .5, .75, 1, 1.5, 2, 3, 4rem. Reader width 960px; page width 1200px is a project extension for controls and participant grid. Document owns scrolling; no nested scrollers. Cluster navigation and controls wrap. Disclosure list preserves document order, intrinsic cards collapse safely to one column. Reference: [StyleGallery cluster](https://github.com/changeroa/StyleGallery/blob/main/patterns/in-line-grouping/cluster.md). Desktop section introductions and controls precede readable full-width lists; compact view stacks all controls.

Layout: public program and provenance - readable sections with related actions -> cluster (https://github.com/changeroa/StyleGallery/blob/main/patterns/in-line-grouping/cluster.md); scroll owner: document; anti-patterns: nested scrolling and visual reordering of links.

## 5. Components
Primary action: register to participate when the approved event provides a registration URL.
Information priorities: event identity and source dates; abstracts and participants; schedule, downloads, and source limits.
Required content: approved records, pending abstract/session labels and counts, source links, registration links, JSON, available books/calendar/dossiers/briefs, working-book guidance, consent and revision authority.
Left out on purpose: inferred attendance cost or venue, invented publication timestamps, automatic-sync claims, inferred research validation, new branding or people.

- Masthead and anchor navigation: wrapping cluster; visible keyboard focus; real anchor destinations.
- Event introduction: editorial title, explicit event dates, dates derived exclusively from the event fields and action links; missing URLs omit the corresponding action.
- Filter bar: labelled search and select, reset action and polite result count; initially hidden until enhancement is active. Empty results explain how to reset.
- Presentation disclosure: native details/summary, type and presenter visible before opening, complete abstract and approved images within; opens without JavaScript. Source and available dossier downloads follow the abstract.
- Participant disclosure: self-reported background/application and learning needs; empty fields omitted; no inferred matching or ranking.
- Schedule row: title, presenter, semantic time; UTC default; local toggle only for explicit sessions.
- Resource card: category, linked name and description; responsive intrinsic grid.

## 6. Motion & interaction
Native disclosure is the accessibility baseline. The beui bouncy-accordion source was consulted for explicit expanded state and retained content; no springs or runtime library are needed for document reading. Hover uses tonal surface feedback; active controls use the secondary surface. Focus ring 2px with 3px offset. Reduced motion is respected; no automatic motion, smooth scrolling, or animated layout. Search matches every whitespace-separated word, in any order across a record. Deep links reveal filtered records and focus their summaries without hiding other data. Filtering updates `hidden` and a polite count; user prose never enters innerHTML.

## 7. Depth & surface
Tonal surfaces plus neutral 1px rules, no decorative colored stripes. Institute radii 10px controls, 16px panels. No ornamental shadows. Photos keep their natural aspect ratio with bounded width; all approved pictures are retained.

## 8. Accessibility constraints & accepted debt
Target WCAG 2.2 AA: semantic landmarks, skip link, labelled controls, visible focus, 44px minimum control height, source order matching visual order, no forced motion, text contrast 4.5:1. No JS retains every full abstract and every participant record. Browser visual/keyboard/mobile/dark-mode and Lighthouse checks are integration gates owned by the coordinating agent; this document does not claim they have passed. No accepted accessibility debt. Local system font fallback is intentional to avoid network dependencies; licensed brand font assets may be added separately after custody review.

Pending labels remain visible in closed disclosure summaries. Downloads link to working-book guidance and to record sections for available individual files. The methods section distinguishes consented self-report and source-grounded reading aids from independent research verification; it explicitly states no automatic live synchronization. These additions reuse the existing text, surface, spacing, and focus tokens. Fresh browser verification remains the coordinator's integration gate.

## 9. Methods discovery
Primary action: choose a workflow. Reading order: tasks and local commands, public repository handoffs, provenance and credential limits. Reuse existing typography, panels, clusters and focus tokens.
Layout: workflow sections and repository evidence -> document stack with wrapping link clusters (https://github.com/changeroa/StyleGallery/blob/main/patterns/in-line-grouping/cluster.md); scroll owner: document; anti-patterns: nested scrolling and reordered links.
Required: methods navigation, commands, credentials, pinned repository evidence, manual handoff limits, catalog, search index, canonical sitemap, official sources and privacy guidance. Exclude participant self-reports from discovery metadata. No inferred integrations, rankings, live synchronization, indexing guarantees or Person entities. All methods content works without JavaScript. Browser verification belongs to the coordinator.
