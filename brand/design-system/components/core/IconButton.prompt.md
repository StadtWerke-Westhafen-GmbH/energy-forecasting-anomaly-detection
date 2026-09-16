One-line: square icon-only control for toolbars, table rows and the navy app shell; `label` is mandatory.

```jsx
<IconButton icon="filter" label="Filter" bordered />
<IconButton icon="more-vertical" label="Weitere Aktionen" size="sm" />
<IconButton icon="bell" label="Benachrichtigungen" onNavy />
```

- Never use for a view's main action — that is a `Button` with a word.
- `pressed` drives the teal selected state for toggles (e.g. compact table density).
