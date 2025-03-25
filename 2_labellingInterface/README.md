# Temporal Action Segmentation Labeling Interface

This is a simple Svelte-based labeling tool designed for creating ground truth datasets for **temporal action segmentation** tasks. It provides an interactive timeline where you can label and adjust action segments easily.

---

## 📂 Project Structure

| File            | Purpose                                                                 |
|-----------------|-------------------------------------------------------------------------|
| `+page.svelte`  | **Main UI** — The interactive labeling interface with timeline controls. |
| `index.ts`      | **App Entry** — Mounts the Svelte app in the browser.                    |
| `app.d.ts`      | **TypeScript Types** — Provides types for better developer experience.  |
| `app.html`      | **HTML Template** — Base HTML structure to load the app.                 |
| `README.md`     | **Project Guide** — You're reading it.                                   |

---

## ✨ Features

✅ Visualize and label temporal segments  
✅ Click and drag to create segments  
✅ Adjust or delete existing labels  
✅ (Planned) Export labeled data for model training  
✅ Clean and simple interface for rapid annotation  

---

## 🚀 Getting Started

### 1. Install Dependencies
\`\`\`bash
npm install
\`\`\`

### 2. Run the Development Server
\`\`\`bash
npm run dev
\`\`\`
Access the app at:  
\`\`\`
http://localhost:5173/
\`\`\`
Or open it automatically:
\`\`\`bash
npm run dev -- --open
\`\`\`

---

## 🏗 Building for Production
\`\`\`bash
npm run build
npm run preview
\`\`\`

---

## 🖥 Usage Overview

1. Open the app in your browser.
2. **Create segments** by clicking and dragging on the timeline.
3. **Assign labels** to each segment (e.g., "Jump", "Run", "Sit").
4. **Modify or delete** segments as needed.
5. (Optional) **Export** the segments for use in model training.

---

## 📸 Screenshots

### 📍 Timeline Interface - Create and Adjust Segments
![Timeline Interface](screenshots/timeline.png)

### 🏷 Label Assignment Example
![Label Assignment](screenshots/label-assignment.png)

### 📤 Export Example (if implemented)
![Export Example](screenshots/export.png)

> 👉 Place your screenshots in a `/screenshots` folder. The images should illustrate the tool's key features.

---

## 📄 Example Export Format (Optional)
\`\`\`json
[
  { "start": 0.0, "end": 2.5, "label": "Walking" },
  { "start": 2.5, "end": 5.0, "label": "Running" }
]
\`\`\`

---

## 🤖 Ideal Use Cases
- Preparing training datasets for temporal models like **TCN**, **MS-TCN**, etc.
- Annotating long videos or sensor recordings for action recognition tasks.

---

## 🔧 Future Improvements
✅ Export/Import JSON functionality  
✅ Video/audio synchronization (optional)  
✅ Multi-label support

---

## 🙏 Acknowledgments
Built with [SvelteKit](https://kit.svelte.dev/) ❤️