from apps.fsm.models.base import Widget, clone_widget


class CustomWidget(Widget):
    pass

    def clone(self, paper):
        return clone_widget(self, paper)

    def __str__(self):
        return f'<{self.id}-{self.widget_type}>:{self.name}'
