One-line: modal for confirmations and short focused forms (Anomalie-Ticket, Schwellwert-Politik).

```jsx
<Dialog open={open} onClose={close} title="Anomalie-Ticket anlegen" subtitle="Zähler ZW-04412 · 03/2025"
  footer={<><Button variant="secondary" onClick={close}>Abbrechen</Button>
            <Button variant="primary" icon="check">Ticket anlegen</Button></>}>
  <p>Abweichung +38,2 % über dem Schwellwert. Das Ticket geht an Netzmanagement.</p>
</Dialog>
```

- Confirm button repeats the verb from the title; never "OK".
- Scrim is navy 48 % with 2px blur — do not restyle.
- Nothing bounces: fade + 4px rise, 180ms.
