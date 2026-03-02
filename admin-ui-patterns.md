# AppStudio Admin UI/UX Patterns
*Extracted from RixAPI Platform Inspection*

## Design System Observations
- **Spacing Rhythm**: High-density data tables (approx 40-48px row height); Form pages use comfortable vertical rhythm (~24px between groups).
- **Typography**: System font stack. Bold section headers (text-lg). Heavy use of `text-muted-foreground` (gray) for helper text below inputs.
- **Table Density**: Information-dense. Uses stacked content within cells (e.g., Cost/Limit split by `/`) to save horizontal space.
- **Filter Layout**: Top-aligned 4-column grid. Inputs for specific identifiers (Keyword, Key, Model) + Select for Categories. Expandable "Advanced" toggle.
- **Action Buttons**: Icon-heavy. Tables use "Split Button" pattern (Primary Action + Dropdown Menu).
- **Status**: Direct interactive **Toggle Switches** in table rows (vs static badges).
- **Navigation**: Sidebar with collapsible distinct sections (General, Admin, Support). Tabs used within detailed config pages.

## UI/UX Pattern Checklist (Transplant Candidates)

### 1. Table & List View (`/admin/channels`)
- [ ] **Inline Status Toggles**: Replace static "Active" chips with direct `<Switch />` components in the "Status" column for immediate enablement/disablement.
- [ ] **Split-Action Rows**: Primary column action is a direct button (e.g., "Test"), secondary actions hidden in a `...` or "More" dropdown.
- [ ] **Stacked Metric Cells**: Combine related metrics in one cell (e.g., `¥0 / ¥0` for Usage/Limit) using a muted separator to reduce column clutter.
- [ ] **Visual Vendor Identity**: Prefix "Type" or "Model" text with the vendor's logo icon for scanning speed.
- [ ] **Expandable Filter Bar**: Primary filters (Keyword, Type) visible; secondary filters hidden behind an "Expand" button to keep the header clean.

### 2. Configuration Forms (`/admin/channel-settings`)
- [ ] **Tabbed Context Switching**: Use horizontal text+icon tabs (Behavior, Rules, Monitoring) to segment complex model configurations.
- [ ] **Descriptive Section Headers**: Start form groups with a `Heading` + `Paragraph` (muted) explaining the section's purpose (e.g., "System Behavior").
- [ ] **Rich Toggle Rows**: For boolean settings, use a "Label + Description" block on the left and the `<Switch />` on the far right (justify-between).
- [ ] **Explicit Helper Text**: Place persistent help text *below* inputs (not just tooltips), explaining formats like "e.g., custom_api_error".
- [ ] **Change Detection Footer**: A sticky or fixed bottom bar indicating state ("No changes" vs "Save Changes") to prevent data loss.

## Component Map

| Component | Pattern / Application |
| :--- | :--- |
| **Table** | Checkbox selection, Stacked data cells, Inline Switches, Sticky Header. |
| **Input** | Clean borders, clear focus states, persistent helper text below. |
| **Button** | Icon-led for actions (Test, View), Split-dropdowns for overflow. |
| **Modal** | Used for "Log" or quick view details; main editing happens in full pages. |
| **Chip/Tag** | Used minimally; prefer Icons or Text for types, Switches for status. |
| **Tabs** | Horizontal, high-contrast active state, includes icons. |
