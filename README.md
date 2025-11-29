# MedHub
Software Engineering Project

# Link to Report: 
https://docs.google.com/document/d/1kf8rqALewgdmWvzl2XpwXXJE7NK8Jn7AI0NEWxbvZGY/edit?usp=sharing


# Project Report (Requirements): 
https://docs.google.com/document/d/11FL64EoB6v9foHtBBdztM4g4KK9vRDJA5s0-uT1yMXA/edit?usp=sharing

# Link to Project Presentation 10/22
https://docs.google.com/presentation/d/1pd3wO-VcSjIu5IyBfEUgRBJblETb9KPS_r91ngJ8zUo/edit?slide=id.g37a9bdaa5b1_0_610#slide=id.g37a9bdaa5b1_0_610

# MedHub prototype

A static prototype for **MedHub**, a class project website that simplifies dental insurance selection. The page showcases:

- A hero section describing the product value.
- Feature highlights for insurance search, sorting/filtering, and ER wait awareness.
- An interactive plan finder with search, network filter, premium slider, and sorting controls.
- Sample ER wait time cards with a refresh action to shuffle data.

## Running locally

Follow these steps to view the static prototype in your browser:

1. **Install Python (if needed).** Python 3 comes preinstalled on macOS and most Linux distributions. On Windows, install it from the [official download page](https://www.python.org/downloads/). Any Python 3.8+ version works.
2. **Open a terminal in the project folder.**
   - On **Windows**: press `Win + R`, type `cmd`, and press Enter to open Command Prompt. If you downloaded a ZIP from GitHub, unzip it first, then run `cd` to the folder that contains `index.html` (example: `cd %HOMEPATH%\Downloads\delete-me`).
   - On **macOS**: press `Cmd + Space`, type `Terminal`, and hit Enter. If you cloned the repo, navigate to it with `cd ~/path/to/delete-me`.
   - On **Linux**: open your terminal app from the application launcher or with `Ctrl + Alt + T`, then `cd` into the folder with `index.html`.
   - Tip: if `cd` fails with “No such file or directory,” copy the folder path from your file explorer and paste it after `cd`.
3. **Start a simple web server.** This serves the files so relative links and scripts load correctly:
   ```bash
   python -m http.server 8000
   ```
   If port `8000` is busy, pick another open port (e.g., `python -m http.server 8080`).
4. **Visit the site in your browser.** Go to `http://localhost:8000` (or the port you chose). You should see the MedHub landing page with the interactive plan finder and ER wait-time cards.
5. **Stop the server when finished.** Return to the terminal and press `Ctrl+C` to exit.

### Troubleshooting

- If the page doesn’t load, confirm you ran the server from the correct folder (the one containing `index.html`).
- Some enterprise environments block `localhost`—try `http://127.0.0.1:8000` instead.
- If you still see a directory listing instead of the page, ensure `index.html` exists in the directory where you started `python -m http.server`.

## What to do next

- Swap the sample plan and ER JSON in `script.js` with real data sources and document the API contract.
- Add authentication and saved-plan flows so users can keep picks between sessions.
- Polish accessibility: keyboardable filters, stronger color contrast, and aria labels on interactive elements.
- Write lightweight Cypress or Playwright checks to keep the interactive filters and ER refresh from regressing.
