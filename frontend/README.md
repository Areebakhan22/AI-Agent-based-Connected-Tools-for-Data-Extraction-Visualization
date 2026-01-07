# SysML Relationship Image Viewer - React App

A React application to view and filter Gemini-generated SysML relationship images.

## Features

- 🎨 **Visual Image Display**: View high-quality generated images for each relationship
- 🔍 **Category Filtering**: Filter relationships by type (part_to_actor, actor_to_use_case, etc.)
- 📊 **Statistics Dashboard**: See total relationships, filtered count, and generated images
- ✨ **Modern UI**: Beautiful, responsive interface with smooth transitions
- 🖼️ **Unique Images**: Each relationship has a distinct, visually appealing diagram

## Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Ensure Files Are in Place

Make sure these files exist:
- `public/relationship_images_metadata.json` - Relationship metadata
- `public/generated_images/*.png` - Generated images

If not, copy them from the project root:
```bash
# From project root
cp relationship_images_metadata.json frontend/public/
cp -r generated_images frontend/public/
```

### 3. Start Development Server

```bash
npm run dev
```

The app will open at `http://localhost:3000`

## Usage

1. **Select Category**: Use the dropdown to filter relationships by category
2. **Click Relationship**: Click any relationship in the list to view its image
3. **View Details**: See relationship details, connection type, and element types below the image

## Project Structure

```
frontend/
├── public/
│   ├── relationship_images_metadata.json
│   └── generated_images/
│       └── *.png
├── src/
│   ├── components/
│   │   ├── RelationshipViewer.jsx
│   │   └── RelationshipViewer.css
│   ├── App.jsx
│   ├── App.css
│   ├── main.jsx
│   └── index.css
├── index.html
├── vite.config.js
└── package.json
```

## Build for Production

```bash
npm run build
```

Output will be in `dist/` directory.

## Troubleshooting

### Images Not Loading

- Ensure images are in `public/generated_images/` directory
- Check that `relationship_images_metadata.json` is in `public/` directory
- Open browser console (F12) to see error messages

### Metadata Not Found

- Copy `relationship_images_metadata.json` from project root to `frontend/public/`
- Refresh the page

### Port Already in Use

- Change port in `vite.config.js` or use `npm run dev -- --port 3001`




