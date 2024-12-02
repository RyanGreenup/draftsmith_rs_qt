# Application Structure Documentation

This document provides an overview of the note-taking application's architecture and components.

## Overview

The application is a Qt-based note-taking system with a modern interface featuring multiple sidebars, markdown editing capabilities, and a command palette system.

## Core Components

### Main Window (`widgets/main_window.py`)
The `NoteApp` class serves as the application's main window and orchestrates the following key components:
- Menu Handler: Manages application menus
- Tab Handler: Controls tab-based navigation
- Main Content: Organizes the primary UI layout

### Content Organization

The main interface is divided into three main sections:

1. **Left Sidebar** (`widgets/left_sidebar.py`)
   - Contains a tree view for note navigation
   - Includes a tag management system
   - Features a tree selector for different view modes

2. **Main Content Area** (`widgets/main_content.py`)
   - Houses the markdown editor
   - Manages the layout of sidebars
   - Handles content splitting and resizing

3. **Right Sidebar** (`widgets/right_sidebar.py`)
   - Provides additional note navigation
   - Contains multiple text sections for metadata/properties
   - Vertically arranged with adjustable splits

### Key Features

#### Markdown Editor (`widgets/markdown_editor.py`)
- Split-view markdown editing
- Real-time preview capabilities
- Text editing with change tracking

#### Command Palette (`widgets/command_palette.py`)
- Quick access to application commands
- Popup interface for rapid navigation
- Inherits from base `PopupPalette` class

#### Tab Management (`widgets/tab_widget.py`)
- Supports multiple open notes
- Closeable and movable tabs
- Dynamic tab creation and management

#### Notes Tree (`widgets/notes_tree.py`)
- Hierarchical note organization
- Keyboard navigation support
- Customizable fold levels

## Data Model

### Note Model (`models/note.py`)
- Basic note structure with title and content
- Foundation for note management

## Utility Components

### Key Constants (`utils/key_constants.py`)
- Defines keyboard shortcuts and commands
- Uses IntEnum for key mappings

## Handler Classes

### Menu Handler (`ui/menu_handler.py`)
- Manages application menus and actions
- Organizes commands into categories
- Handles menu-related events

### Tab Handler (`ui/tab_handler.py`)
- Controls tab creation and management
- Coordinates with main window

## Development Guidelines

### Adding New Features
1. Extend existing handlers for new functionality
2. Follow Qt widget inheritance patterns
3. Maintain separation between UI and logic

### Best Practices
1. Use handler classes for coordinating components
2. Implement new widgets as independent classes
3. Follow existing naming and structure conventions

## Common Tasks

### Creating New Note Types
1. Extend the Note model
2. Add corresponding UI elements
3. Update handlers as needed

### Adding UI Components
1. Create new widget class
2. Integrate with existing handlers
3. Update menu system if needed

## Future Considerations

- Consider implementing a plugin system
- Plan for data persistence
- Design for extensibility
