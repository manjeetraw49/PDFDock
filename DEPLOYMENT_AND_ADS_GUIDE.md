# PDFDock: Free Netlify Deployment & Ad Setup Guide

This guide explains how to deploy **PDFDock** and its full suite of **18 free document tools** live to the web using Netlify for free, and how to monetize traffic using **Adsterra** and **Monetag**.

---

## 1. How to Upload PDFDock for Free Using Netlify

Netlify hosts static multi-page websites completely free with automatic SSL (HTTPS), high-speed global CDN, and unlimited page views within fair use.

### Step-by-Step (Takes 30 Seconds via Netlify Drop):

1. In your browser, open **[https://app.netlify.com/drop](https://app.netlify.com/drop)**.
2. Sign up or log in to your free Netlify account.
3. You will see a large drag-and-drop zone that says:  
   **"Drag and drop your site output folder here"**.
4. In your Windows file explorer, go to:  
   `C:\Users\HP\Downloads\PDF Website`
5. **Drag and drop the entire `PDF Website` folder** into the Netlify upload zone.
6. **Done!** Netlify will automatically upload and host all 19 pages:
   - `index.html` (Main Portal)
   - `merge-pdf.html`
   - `split-pdf.html`
   - `compress-pdf.html`
   - `jpg-to-pdf.html`
   - `pdf-to-jpg.html`
   - `delete-pdf-pages.html`
   - `reorder-pdf-pages.html`
   - `pdf-to-png.html`
   - `png-to-pdf.html`
   - `pdf-to-text.html`
   - `add-text.html`
   - `protect-pdf.html`
   - `word-to-pdf.html`
   - `excel-to-pdf.html`
   - `powerpoint-to-pdf.html`
   - `pdf-to-word.html`
   - `pdf-to-excel.html`
7. Your site is immediately live with a free URL like `https://pdfdock-12345.netlify.app`.

#### (Optional) Custom Site Name:
In the Netlify dashboard for your new site:
- Go to **Site configuration** &rarr; **Change site name**.
- Enter something memorable, like `my-pdfdock` or `pdfdock-tools`.
- Your public website address becomes `https://my-pdfdock.netlify.app`.

---

## 2. How to Set Up Ads Using Adsterra

Adsterra has zero traffic requirements and approves utility sites quickly (even `.netlify.app` subdomains).

### Steps:
1. Register at **[https://publishers.adsterra.com](https://publishers.adsterra.com)** as a **Publisher**.
2. Go to **Websites** &rarr; click **Add Website**.
3. Enter your Netlify domain (e.g., `my-pdfdock.netlify.app`), choose category **Tools / Utilities**, and select your desired ad format:
   - **728x90 Leaderboard Banner** (or 320x50 on mobile)
   - **300x250 Medium Rectangle**
   - **Social Bar** (interactive mobile bubble with high CTR)
   - **Popunder**
4. When your domain is approved (usually 5–10 minutes), click **Get Code**.
5. Paste your code into the placeholder slots in your HTML files:
   - **Top Banner**: Replace the contents of `<aside class="ad-container ad-banner-top" id="ad-top">`.
   - **Mid Rectangle**: Replace the contents of `<aside class="ad-container ad-banner-mid" id="ad-mid">`.
   - **Bottom Banner**: Replace the contents of `<aside class="ad-container ad-banner-bottom" id="ad-bottom">`.
   - **Social Bar / Popunder**: Paste inside the `<!-- START HEADER AD CODE -->` or right before `</body>`.

---

## 3. How to Set Up Ads Using Monetag

Monetag specializes in high-paying mobile web and utility monetization.

### Steps:
1. Register at **[https://monetag.com](https://monetag.com)** as a **Publisher**.
2. Click **Sites** &rarr; **Add Site**, and enter your Netlify domain.
3. Verify your site using Monetag's `<meta name="monetag" ...>` tag placed inside `<head>`.
4. Create your ad zones:
   - **In-Page Push (IPP)**: Highly recommended for mobile users. Clean, non-intrusive alert style with excellent payouts.
   - **Vignette Banner**: Shows cleanly between screen interactions.
   - **OnClick (Popunder)**: Maximum eCPM.
5. Copy your generated script and paste it into the designated header or footer placeholders:
   - `<!-- START HEADER AD CODE -->`
   - `<!-- START FOOTER AD CODE -->`

---

## 4. Redeploying Your Site After Adding Ads

1. Save your edited HTML files.
2. Open your Netlify site dashboard &rarr; **Deploys**.
3. Drag and drop the `PDF Website` folder into the deploy box again.
4. Netlify will instantly refresh your live site with ads active!
