# Save Logic

I wrote this out because the UI was not refreshing after saving a note. To debug these sort of issues, follow the logic from the `actions_manager` until you get to the logic connecting the signal to the slot.

Ultimately, I had to add, `self.notes_model.refresh_notes()` to `TabContent._handle_save_request` (in `widgets/tab_content.py`) to refresh the notes model after saving a note.

When a user selects save from the menu, the logic is as follows:


1. `ui/actions_manager.py`

    ```python

    actions["save"].setShortcut("Ctrl+S")
    actions["save"].setStatusTip("Save the current note")
    actions["save"].setToolTip("Save the current note")
    ```

2. ~~`widgets/main_window.py`~~ `ui/menu_handler.py`

    To find this grep for `actions["save"]`

    ```python
        # Connect save action to current tab
        self.actions["save"].triggered.connect(
            self.main_window._trigger_save_current_tab
        )

    ```

3. `widgets/main_window.py`

    To find this use `gd` or `:lua vim.lsp.buf.definition()` on the `trigger_save_current_tab` function fn. [^1733562215]



    ```python
    def _trigger_save_current_tab(self):
        """Trigger save on the currently active tab"""
        current_tab = self.tab_handler.tab_widget.currentWidget()
        if isinstance(current_tab, TabContent):
            note_id = current_tab.get_current_note_id()
            if note_id is not None:
                current_tab._handle_save_request(note_id)
    ```

5. `widgets/tab_content.py`

    To find this use `<SPC>sr` or `:lua vim.lsp.buf.references()` on the `save_requested` signal. [^1733562166]
    Here the note is saved and the notes model is refreshed.

    ```python
       def _handle_save_request(self, note_id: int):
        """Internal handler for save requests"""
        content = self.editor.get_content()
        if self.notes_model:
            if self.notes_model.update_note(note_id, content=content):
                self.note_saved.emit(note_id)
     ```

6. `models/notes_model.py`
   Here the note is updated using the client bindings and a the notes are refreshed for the UI.

    ```python
    def update_note(
        self, note_id: int, title: Optional[str] = None, content: Optional[str] = None
    ) -> bool:
        """Update an existing note"""
        try:
            note = self.notes.get(note_id)
            if not note:
                return False

            # Create update request using the imported type
            update_data = UpdateNoteRequest(title=title, content=content)

            api_response = self.note_api.update_note(note_id, update_data)
            note.update_from_api_note(api_response)

            # Update the notes to reflect the new state
            self.refresh_notes()
            return True
    ```

7. `api/client.py`
    This is a thin wrapper around the Rust API.

    ```python
    class UpdateNoteRequest(BaseModel):
        title: Optional[str] = None
        content: Optional[str] = None

   def update_note(self, note_id: int, request: UpdateNoteRequest) -> Note:
       """
       Update an existing note

       Args:
           note_id: The ID of the note to update
           request: The update request containing new note data

       Returns:
           Note: The updated note data

       Raises:
           requests.exceptions.RequestException: If the request fails
           requests.exceptions.HTTPError: If the note is not found (404)
       """
       response = requests.put(
           f"{self.base_url}/notes/flat/{note_id}",
           headers={"Content-Type": "application/json"},
           data=request.model_dump_json(),
       )

       response.raise_for_status()
       return Note.model_validate(response.json())
    ```



## Footnotes

[^1733562166]: Or just `grep -r "save_requested" .` in the project root
[^1733562215]: Or just `grep -r "_trigger_save_current_tab" .` in the project root
