One-line: monochrome Lucide glyph that inherits `currentColor`; the only sanctioned way to render an icon in SWW UI.

```jsx
<Icon name="triangle-alert" size={16} />
<Icon name={DOMAIN_ICONS.prognose} size={20} title="Prognose" />
```

- Sizes limited to 14 / 16 / 20 / 24. 16 is the UI default, 20 in the sidebar, 24 in empty states.
- Colour comes from the parent's text colour — set `color` only for status glyphs on neutral text.
- Use `DOMAIN_ICONS` for domain concepts so the same idea always gets the same glyph.
- Never pair an icon with no label for status; status = icon + colour + word.
