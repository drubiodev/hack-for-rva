# Developer Implementation Guide: Modern Analyst Dashboard

To get the best results when asking an LLM (like Claude) to code these designs, follow this modular strategy. **Do not paste all screens at once.**

## 1. The "Base Foundation" Prompt
Start by establishing the global styles and the shared sidebar layout. This ensures consistency across all pages.

**Prompt to Claude:**
> "I am building a civic tech dashboard for the City of Richmond. I need you to create a base layout using Tailwind CSS. 
> 
> **Global Styles:**
> - **Font:** 'Bricolage Grotesque' for headings, 'DM Sans' for body, 'DM Mono' for small data/tags.
> - **Colors:** Primary: #0F2537, Background: #F7F5F2, Surface: #FFFFFF.
> - **Sidebar:** 250px width, fixed left, containing navigation links (Dashboard, Portfolio, Matrix, Evaluation).
> 
> Please provide the HTML and Tailwind config/CDN link for this shell."

## 2. Screen-by-Screen Implementation
Once the shell is ready, ask for one screen at a time. For each screen, provide the specific screenshot from this session and the following context:

### For the Dashboard Overview ({{DATA:SCREEN:SCREEN_5}})
> "Now, implement the main content for the 'Dashboard Overview' inside the shell. 
> - **Top Row:** 3 Metric cards (Total Active Value, Expiring, Identified Savings) with large Bricolage Grotesque numbers.
> - **Main Grid:** A 2-column layout (60/40).
> - **Left Column:** 'Urgent Expirations' card with a list of contracts, including source tags (VITA/GSA/City) and days remaining.
> - **Right Column:** 'AI Opportunity Feed' showing a vertical timeline of insights."

### For the Unified Portfolio ({{DATA:SCREEN:SCREEN_4}})
> "Implement the 'Unified Portfolio' view.
> - **Filter Bar:** Global search input (400px wide) and dropdown filters for Source, Department, Value, and Status.
> - **Data Table:** A dense, high-contrast table with columns for Vendor, Source (using colored tags), Department, Value, and Dates. 
> - **Style:** Use a hover effect on rows (#F5F5F4) and a clean header background (#F5F5F4)."

### For the Contract Detail ({{DATA:SCREEN:SCREEN_7}})
> "Implement the 'Contract Detail' split-view.
> - **Left Pane (50%):** AI Summary section with bullet points, 'Key Extracted Terms' grid, and an 'Export Brief' primary button.
> - **Right Pane (50%):** A mock PDF viewer with a toolbar and a scrollable document area. Highlight specific text in the document as if it was found by AI."

## 3. Handling Complex Components (The "Evaluation Hub")
For the charts in the Evaluation Hub ({{DATA:SCREEN:SCREEN_2}}), ask Claude to use a library like **Chart.js**.

**Prompt Snippet:**
> "For the Evaluation Hub, use Chart.js to render a Radar Chart for the 'Dimension Balance' and a Radial Progress Bar for the 'Overall Score'. Use the color #818CF8 for the chart elements."

## Pro-Tips for Success:
1. **Componentize:** Ask Claude to "write this as a clean, single-file HTML/Tailwind prototype" so you can easily copy-paste it into your project.
2. **Be Specific about Tags:** Mention the specific hex codes for tags (e.g., VITA: #BAE6FD) so the AI doesn't guess.
3. **Double-Click to Copy:** Remember you can double-click any screen here in Stitch to see and copy the actual HTML code I've generated—this is the most "error-free" way to get started!