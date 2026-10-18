# Avatars

Avatars for personal use.

Every avatar is a **512 × 512 PNG** with a transparent background: a coloured circle with the character inside. There's a little empty space around the circle so that extras like the Owner's crown fit.

## Folders

```
office/
  male/
    owner.png
    manager.png
    employee.png
    guest.png
    custom.png
  female/        (planned)
sources/         original sheets the avatars were cut from
tools/           script that cuts a sheet into single avatars
```

Use them like this:

```
https://raw.githubusercontent.com/darshitshah8/Avatars/main/office/male/owner.png
```

## Planned

- `office/female/` – the same five roles in a female version
- More roles for both sets, such as `hr.png`, `sales.png`, `accounts.png`, `support.png` and `admin.png`

## Adding a new sheet

1. Save the sheet image in `sources/` (for example `sources/office-female.webp`).
2. In `tools/extract_avatars.py`, set the search box and the banner top for each avatar in `AVATARS`.
3. Run:

   ```
   python tools/extract_avatars.py sources/office-female.webp office/female
   ```

The script fits each circle, removes the name banner by extending the clothes downward, keeps anything that sticks out above the circle (like the crown), and saves the result as a PNG.
