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

## 🚀 Installation (Windows)
*For macOS or Linux, please use the **Manual Installation** steps below.*

1. Go to the [Releases](https://github.com/Arsynator/7TV-Chat-Builder/releases) page.
2. Download the latest `setup.exe`.
3. Run the installer. It will automatically locate your Resolve directories and verify your Python environment.
4. Restart DaVinci Resolve.

> [!TIP]
> **Windows SmartScreen Warning:** > Because this is a new open-source tool, Windows may show a "Protected your PC" popup. Click **"More info"** and then **"Run anyway"** to proceed. As the project gains more users and stars on GitHub, this warning will eventually disappear!

### 🛠️ Manual Installation (No .exe)
If you prefer not to use the automated installer, you can install the script manually:

1. **Download the script:** Download the `7TV_Paint_Applier.py` file from the source code.
2. **Locate the Folder:** Navigate to your Resolve Fusion scripts directory:
   * **Windows:** `%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Comp\`
   * **macOS:** `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Comp/`
   * **Linux:** `~/.local/share/DaVinciResolve/Fusion/Scripts/Comp/`
3. **Move the File:** Drop the `.py` file into that `Comp` folder.
4. **Dependencies:** Ensure you have [Python 3](https://www.python.org/downloads/) installed on your system and added to your **System PATH**.
5. **Enable in Resolve:** * Open Resolve Preferences > System > General.
   * Set **External scripting using** to **Python 3**.
   * Restart DaVinci Resolve.

### 2. Run the Script
The script requires an active Fusion composition to generate nodes. Follow these steps:

1.  **Create a Composition:** * In the **Edit Page**, go to the **Effects Library > Toolbox > Generators**.
    * Drag a **Fusion Composition** onto your timeline.
    * Right-click the clip on the timeline and select **Open in Fusion Page**.
2.  **Launch the Tool:**
    * Once you are on the Fusion page (you should see a `MediaOut1` node), go to the top menu bar.
    * Select **Workspace > Scripts > Comp > 7TV_Paint_Applier**.
3.  **Generate Your Overlay:**
    * Enter a **7TV Username** in the search bar and hit Enter.
    * Select your desired paint from the list.
    * Click **Customize & Apply** to open the layout menu.
    * **Note:** The script automatically detects your `MediaOut1` node and wires the final Merge node into it for an instant preview.

## 🛠 Usage

1. **Search:** Enter a username to see all users that start with that name.
2. **Preview:** Select a paint to see its color code or animated URL in the inspector.
3. **Customize:** Click "Customize & Apply" to change the placeholder chat text or toggle the shadow/glow effect.
4. **Animated Paints:** For animated GIF/WebP paints, the button will change to "Open Image," allowing you to download the asset to use as a MediaIn. (this will be changed in the future when the animated paint support is added, check roadmap below)

<img width="754" height="714" alt="Screenshot 2026-04-16 140732" src="https://github.com/user-attachments/assets/f3be1820-5344-471a-96dc-61eaf206765d" />


## 🛠 Troubleshooting

**Script not appearing in the menu?**
* Ensure you have **Python 3.x** installed on your system.
* In DaVinci Resolve, go to **Preferences > System > General**.
* Check that **External scripting using** is set to **Python 3**.
* Restart Resolve after changing these settings.

**Nodes spawning in weird places?**
* The script is designed to spawn nodes in the center of your current view. If you can't see them, check your **Flow View** (Node Graph) and zoom out; they are snapped to a clean 2x2 grid.

## 📝 Requirements

- DaVinci Resolve 17/18/19 (Studio or Free)
- Python 3.x installed and configured in Resolve Preferences.

## 🗺️ Roadmap
- [ ] **Native Animated Paint Support:** Automated downloading and looping of WebP/GIF assets directly into the Fusion timeline.
- [ ] **Font Customization:** Select local system fonts from within the UI.
- [ ] **Multi-Line Support:** Support for longer chat messages that wrap automatically.

## 🤝 Credits
Developed by **Arsynator**. If you find this tool helpful, feel free to follow on [Twitch](https://twitch.tv/arsynatorlive)!

---
*Disclaimer: This tool is not officially affiliated with 7TV or Blackmagic Design.*
