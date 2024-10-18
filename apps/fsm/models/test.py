from django.db import models
from django.contrib.postgres.fields import JSONField
from .fsm import FSM,P
from .fsm import Paper , Player


class Test():
    GRADING_METHOD_CHOICES = [
        ('highest', 'Highest'),
        ('average', 'Average'),
        ('sum', 'Sum'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    cover_picture = models.ImageField(upload_to='test_covers/', blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    time_limit = models.DurationField(help_text="Time limit for the test in seconds")
    participation_limit = models.IntegerField(default=1, help_text="Number of times a participant can take the test")
    grading_method = models.CharField(max_length=10, choices=GRADING_METHOD_CHOICES)
    content = models.ForeignKey('FSM', on_delete=models.CASCADE)
    def correct_test(self):
        total_score = 0
        for widget in self.content.widgets.all():  # Assuming the content has widgets
            total_score += widget.correct()
        return total_score

    def __str__(self):
        return self.name



class Participation(Paper):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    answer_sheet = models.ForeignKey('AnswerSheet', on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Participation in {self.test.name}"


class Entrance(models.Model):
    participation = models.ForeignKey(Participation, on_delete=models.CASCADE)
    entry_time = models.DateTimeField(auto_now_add=True)
    device = models.CharField(max_length=255)

    def __str__(self):
        return f"Entrance at {self.entry_time}"


# Player model (for tracking player history)
class PlayerTest(Player):
    name = models.CharField(max_length=255)
    history = JSONField(default=dict)  # Store player's history as JSON

    def __str__(self):
        return self.name



class RandomWidget(models.Model):
    paper = models.ForeignKey('Paper', on_delete=models.CASCADE)  # Assuming Paper model is defined
    player = models.ForeignKey(Player, on_delete=models.CASCADE)

    def get_new_question(self):
        # Provide a new question based on player's history
        history = self.player.history
        # Logic to select a new question based on the player's history
        # For example, avoiding repeating questions they've already answered
        new_question = "Some question based on history"  # Placeholder
        return new_question

    def __str__(self):
        return f"Widget for player {self.player.name}"
