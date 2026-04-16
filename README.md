# 7TV Paint Applier for DaVinci Resolve

A sleek, modern Fusion script for DaVinci Resolve that fetches **7TV Paints** via GraphQL and automatically generates a complete 'User: Message' node setup with perfect color gradients, repeating patterns, and drop shadows.

Created by **Arsynator**
[GitHub](https://github.com/Arsynator) | [Twitch](https://twitch.tv/arsynatorlive)

---

## ✨ Features

- **GraphQL Integration:** Directly fetches live cosmetic data from the 7TV API.
- **Advanced Gradient Engine:** Supports standard, linear, and radial gradients.
- **Singularity-Ready Tiling:** Full support for `repeating-linear-gradient` logic, ensuring patterns loop seamlessly across text.
- **Smart Shadow Engine:** Automatically detects and applies 7TV `drop_shadow` properties using native Fusion Shadow nodes.
- **Dynamic Centering:** Automatically calculates offsets so that the "Name: Message" block remains centered in your frame.
- **Modern UI:** Zinc-dark theme with a smooth purple-to-black background gradient.
- **Customization Modal:** Edit your placeholder message and toggle shadows before generating nodes.
- **Auto-Routing:** Automatically connects the final Merge node to your `MediaOut` and snaps nodes to a clean grid.

## 🚀 Installation

### 1. Locate your Fusion Scripts folder
Copy the script (`7TV_Paint_Applier.py`) into the appropriate directory for your OS:

* **Windows:** `%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Comp\`
* **macOS:** `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Comp/`
* **Linux:** `~/.local/share/DaVinciResolve/Fusion/Scripts/Comp/`

### 2. Run the Script
1. Open **DaVinci Resolve** and go to the **Fusion Page**.
2. Go to the top menu: **Workspace > Scripts > Comp > 7TV_Paint_Applier**.
3. Search for a 7TV username, select a paint, and click **Customize & Apply**.

## 🛠 Usage

1. **Search:** Enter a username to see all paints owned by that user.
2. **Preview:** Select a paint to see its color code or animated URL in the inspector.
3. **Customize:** Click "Customize & Apply" to change the placeholder chat text or toggle the shadow/glow effect.
4. **Animated Paints:** For animated GIF/WebP paints, the button will change to "Open Image," allowing you to download the asset to use as a MediaIn.

## 📝 Requirements

- DaVinci Resolve 17/18/19 (Studio or Free)
- Python 3.x installed and configured in Resolve Preferences.

## 🤝 Credits
Developed by **Arsynator**. If you find this tool helpful, feel free to follow on [Twitch](https://twitch.tv/arsynatorlive)!

---
*Disclaimer: This tool is not officially affiliated with 7TV or Blackmagic Design.*
