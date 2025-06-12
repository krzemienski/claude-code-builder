# File Organization CLI Tool

Create a command-line tool that organizes files in a directory based on their types.

## Features

### Core Functionality
- Scan a directory for files
- Organize files by extension into subdirectories
- Support for custom organization rules
- Dry-run mode to preview changes
- Undo functionality

### Commands
```bash
# Basic usage
file-organizer organize /path/to/directory

# With options
file-organizer organize /path/to/directory --dry-run
file-organizer organize /path/to/directory --config rules.yaml
file-organizer undo /path/to/directory
```

### Default Organization
- Images: jpg, jpeg, png, gif, bmp → Images/
- Documents: pdf, doc, docx, txt → Documents/
- Videos: mp4, avi, mkv, mov → Videos/
- Audio: mp3, wav, flac → Audio/
- Archives: zip, tar, gz, rar → Archives/
- Code: py, js, java, cpp → Code/

### Configuration File Format
```yaml
rules:
  - name: "Project Files"
    extensions: [".proj", ".config"]
    destination: "Projects"
  - name: "Data Files"
    extensions: [".csv", ".json", ".xml"]
    destination: "Data"
```

### Technical Requirements
- Use Click for CLI framework
- Add colorful output with Rich
- Implement logging
- Handle errors gracefully
- Support Windows, macOS, and Linux

### Acceptance Criteria
- Files are moved to correct directories
- Original file timestamps preserved
- Duplicate files handled appropriately
- Undo restores original structure
- Progress shown during operation