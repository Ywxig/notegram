# 📝 Notegram

A feature-rich Telegram bot for organizing and managing your study notes with hierarchical folder structure and GitHub integration.

## 🎯 Overview

**Notegram** is a personal note management system built directly into Telegram. Upload, organize, and manage your lecture notes, study materials, and documents with an intuitive folder structure. Optionally sync everything to your GitHub repository for backup and version control.

## ✨ Key Features

### 📂 Hierarchical Note Organization
- Create unlimited nested folders inside your personal `_notes_` directory
- Organize notes by subject, week, or any custom structure
- Interactive tree-view interface with expandable/collapsible folders

### 📤 Smart File Upload
- Upload documents directly to Telegram
- Save files to root or any nested folder using `/add <folder>` syntax
- Auto-create folders on first file upload to that directory

### 📥 File Management
- Download files back from the bot anytime
- Delete files individually using inline buttons or `/delete` command
- Browse all files and folders in a clean tree interface with `/myfiles`

### 🔗 GitHub Integration
- Link your GitHub repository with `/repo <url>`
- Store repository info for future automated sync features
- Prepare infrastructure for pushing notes to GitHub

### 🛡️ Security & Validation
- Per-user isolation: each user has their own notes folder
- Path-traversal protection against directory escape attempts
- Secure file handling with proper path normalization

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- aiogram 3.x (Telegram Bot API framework)
- A Telegram Bot Token (from [@BotFather](https://t.me/BotFather))

### Installation

1. Clone the repository:
```bash
git clone <your-repo>
cd notegram
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `config.json` file:
```json
{
  "token": "YOUR_BOT_TOKEN_HERE"
}
```

4. Create a logger module at `src/log.py`:
```python
import logging

logger = logging.getLogger(__name__)
handler = logging.FileHandler("bot.log")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

5. Run the bot:
```bash
python main.py
```

## 📖 Usage Guide

### Commands

| Command | Usage | Description |
|---------|-------|-------------|
| `/start` | `/start` | Initialize your account and create personal folders |
| `/help` | `/help` | Show available commands and usage tips |
| `/myfiles` | `/myfiles` | Display interactive tree of all files and folders |
| `/mkdir` | `/mkdir <path>` | Create a new folder (e.g., `/mkdir math/calculus`) |
| `/delete` | `/delete <path>` | Delete a file by path (e.g., `/delete math/notes.pdf`) |
| `/repo` | `/repo <url>` | Link GitHub repository (e.g., `/repo https://github.com/user/notes`) |

### File Upload

#### To Root Folder:
Simply send a document to the bot without any caption.

#### To Specific Folder:
Send a document with caption `/add <folder_path>`:
```
Send file with caption: /add math
Send file with caption: /add math/week1
Send file with caption: /add semester2/physics/chapter3
```

If the folder doesn't exist, it will be created automatically.

### Interactive Tree View

When you use `/myfiles`, you get an interactive tree:
- **▶ Folder** — Closed folder (tap to expand)
- **▼ Folder** — Open folder (tap to collapse)
- **📄 File** — Shows file with download (⬇️) and delete (🗑) buttons
- **🔄 Refresh** — Update the tree without re-running the command

## 📁 Project Structure

```
notegram/
├── main.py              # Main bot logic and command handlers
├── users.py             # User and UserFiles classes
├── config.json          # Bot token configuration
├── requirements.txt     # Dependencies
├── log.py               # Logging module
├── src/                 # Source files
├── README.md            # This file
└── users/               # User data directory (auto-created)
    ├── {user_id}/
    │   ├── config.json  # User metadata and repo link
    │   └── _notes_/     # All user files and folders
    │       ├── math/
    │       ├── physics/
    │       └── lecture.pdf
```

## 🔑 Key Classes

### `User`
Handles user creation and repository linking.

**Methods:**
- `create()` — Create user directory structure
- `set_repository(url)` — Save GitHub repo URL
- `get_repository()` — Retrieve saved repo URL
- `load(id)` — Load user config from JSON
- `save(data)` — Write user config to JSON

### `UserFiles`
Manages file and folder operations within a user's `_notes_` directory.

**Directory Operations:**
- `mkdir(rel_path)` — Create folder(s)
- `rmdir(rel_path)` — Remove empty folder
- `list_dir(rel_path)` — List immediate contents
- `tree(rel_path)` — Build full directory tree

**File Operations:**
- `save_file(rel_dir, filename)` — Get destination path for upload
- `get_file_path(rel_path)` — Get absolute path
- `file_exists(rel_path)` — Check if file exists
- `delete(rel_path)` — Delete file

## 🎨 UI/UX Features

### Expandable Tree Navigation
- Folder state persists during the bot session
- Each user's open/closed folders remembered separately
- Click folder icon to toggle expand/collapse
- Refresh button to sync with file system

### Inline Buttons
- **⬇️** — Download file
- **🗑** — Delete file immediately (with tree refresh)
- **📁** — Toggle folder visibility

## 🔒 Security Considerations

1. **Path Traversal Protection**: All relative paths validated with `_safe_rel()`
2. **Per-User Isolation**: Users only access their own `users/{id}/_notes_/` directory
3. **No Arbitrary Execution**: File operations are read/write only
4. **Token Security**: Keep `config.json` in `.gitignore`

## 🚧 Future Enhancements

- [ ] Auto-push to GitHub on file upload
- [ ] Pull from GitHub to sync notes
- [ ] Search functionality across files
- [ ] File preview (for PDFs, images)
- [ ] Share folders with other users
- [ ] Tags and categorization system
- [ ] Markdown note editing in Telegram
- [ ] Integration with cloud storage (Google Drive, OneDrive)

## 📝 Example Workflow

1. **Start the bot:**
   ```
   /start
   ```
   ✅ Account created

2. **Create folders:**
   ```
   /mkdir semester1/math
   /mkdir semester1/physics
   ```

3. **Upload files:**
   - Send `lecture1.pdf` with caption `/add semester1/math`
   - Send `lab_notes.pdf` with caption `/add semester1/physics`

4. **View all files:**
   ```
   /myfiles
   ```
   See tree: `semester1 ▼ → math ▼ → lecture1.pdf [⬇️ 🗑]`

5. **Link repository:**
   ```
   /repo https://github.com/yourname/my-notes
   ```
   ✅ Repository linked for future sync

6. **Manage files:**
   - Click ⬇️ to download any file
   - Click 🗑 to delete
   - Use `/delete semester1/math/old_notes.pdf` for command-based deletion

## 📦 Dependencies

- **aiogram 3.x** — Async Telegram Bot API wrapper
- **Python 3.10+** — For type hints and modern async/await

## 🤝 Contributing

Feel free to fork, modify, and improve! This is a personal project template.

## 📄 License

MIT License — Use freely for personal and educational purposes.

## 🐛 Troubleshooting

### "File not found" error
- Check that the file path is correct relative to `_notes_/`
- Use `/myfiles` to see exact paths

### Folder not created on upload
- Ensure the `/add` syntax is correct: `/add folder/subfolder`
- Bot will auto-create missing directories

### Inline buttons not responding
- Refresh the message with the 🔄 button
- Use `/myfiles` again to regenerate the tree

## 📞 Support

For issues or questions:
1. Check `/help` for command syntax
2. Verify file paths using `/myfiles`
3. Review logs in `bot.log` for detailed errors

---

**Happy note-taking! 📚**