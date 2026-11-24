# Live Scoring Page Overrides

> **PROJECT:** FinAudit AI
> **Generated:** 2026-11-25 02:16:49
> **Page Type:** General

> ⚠️ **IMPORTANT:** Rules in this file **override** the Master file (`design-system/MASTER.md`).
> Only deviations from the Master are documented here. For all other rules, refer to the Master.

---

## Page-Specific Rules

### Layout Overrides

- **Max Width:** 1200px
- **Layout:** Responsive grid

### Spacing Overrides

- No overrides — use Master spacing

### Typography Overrides

- No overrides — use Master typography

### Color Overrides

- No overrides — use Master colors

### Component Overrides

- Avoid: Call form.reset(), clear the failing fields, or reload an empty form after a validation or server error
- Avoid: No feedback after submit
- Avoid: Placeholder-only inputs

---

## Page-Specific Components

- No unique components for this page

---

## Recommendations

- Forms: Show the form again with every value as the user entered it, both passing and failing (secret fields such as passwords may be left empty); mark only the fields that need changes
- Forms: Show loading then success/error state
- Accessibility: Use label with for attribute or wrap input
