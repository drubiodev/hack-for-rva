# Quickstart

## Fastest path for teams
1. Read `00_core/00_pillar_overview.md`
2. Read `01_problem_space/02_targeted_problem_statements.md`
3. Read `02_data/00_index.md`
4. Pick one user and one problem
5. Read `04_build_guides/01_mvp_shapes.md`
6. Create your project brief using `99_templates/project_one_pager_template.md`

## Questions to answer before building
- Who is the user (resident trying to find a City service, City staff reviewing contracts, 311 agent routing requests)?
- What problem are they facing?
- What data or documents are you using?
- What can actually be built in a weekend?
- How will a judge understand the value in under 60–90 seconds?

## High-probability project types
- resident service navigator (plain-language routing to the right City department or 311 category)
- 311 category helper (decision tree or guided form that reduces misrouted requests)
- city website search enhancer (makes rva.gov content findable in plain language)
- procurement contract reviewer (surfaces expiring contracts and key terms from Socrata data)
- government transparency tool (visualizes spending or contract data for residents or staff)

## Critical constraints to know before starting
- RVA311 (AvePoint Citizen Services) has **no public API** — post-2018 data is not accessible programmatically
- Historical 311 data on Socrata (vgg4-hjn8) covers only January 2014–August 2015 (SeeClickFix era)
- rva.gov uses Drupal 8+ with a search API — content is crawlable but not officially structured for external apps
- City Contracts Socrata dataset (xqn7-jvv2) has a known column bug in the API; use CSV download for all 9 columns
- Any tool making routing or eligibility determinations must include clear disclaimers and escalation paths to staff
