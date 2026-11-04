# editor/ — Vibe Studio (proposal)

A Rust desktop NLE for vibe-editing: Premiere-grade timeline, CapCut-simple surface, Resolve-style pages,
and every pipeline job opens as a fully editable timeline. Built downstream of
[FilmCraft](https://github.com/storytold/filmcraft)'s engine (MIT/Apache-2.0).

Nothing is built yet. This branch holds the research and the plan for approval:

- [`docs/RESEARCH.md`](docs/RESEARCH.md): Premiere 26, Resolve 21.1, CapCut, the FilmCraft deep dive, the Rust stack
- [`docs/PLAN.md`](docs/PLAN.md): the decision, architecture, pipeline → timeline mapping, milestones M0–M6 with gates, risks, open decisions
- [`docs/DESIGN.md`](docs/DESIGN.md): the clean dark design system (tokens, pages, components, the "do not" list)
- [`design/mockup.html`](design/mockup.html) / [`design/mockup.png`](design/mockup.png): the Edit page with the 9278 baseline loaded
