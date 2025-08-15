
class AppState:
    def __init__(self):
        self.user_selected_image_path: str | None = None
        self.story_title: str = ""
        self.pages = {}