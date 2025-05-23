from django.core.management.base import BaseCommand
from django.db import transaction

from apps.attributes.models.performable_actions import Transition
from apps.widgets.models.other_widgets.button import ButtonWidget


class Command(BaseCommand):
    help = (
        "For each existing ButtonWidget, create a Transition for each "
        "destination_state in its JSONField and attach it to button.attributes."
    )

    def handle(self, *args, **options):
        """
        - We assume that `ButtonWidget.destination_states` is a JSONField containing
          a list of integer IDs corresponding to `State.id`.
        - We also assume that `ButtonWidget` has a ManyToManyField named `attributes`
          (pointing at `Attribute`, thereby accepting our `Transition` instances).
        """

        buttons = ButtonWidget.objects.all()
        total_buttons = buttons.count()
        created_count = 0

        for button in buttons:
            dest_list = button.destination_states or []
            if not isinstance(dest_list, (list, tuple)):
                self.stderr.write(
                    f" • [Button {button.id}] “destination_states” is not a list; skipping."
                )
                continue

            if not dest_list:
                self.stdout.write(
                    f" • [Button {button.id}] no destination_states; skipping.")
                continue

            # We wrap each widget's work in an atomic block so that
            # if something fails mid‐way, it won't half‐apply.
            with transaction.atomic():
                for state_id in dest_list:
                    # Create one Transition per destination_state
                    transition = Transition.objects.create(
                        title=f"Auto‐transition for Button {button.id} → State {state_id}",
                        description="(created via management command)",
                        order=-1,
                        destination_state_id=state_id
                    )
                    # Attach the newly created Transition to this button's attributes M2M
                    button.object.attributes.add(transition)
                    created_count += 1
                    self.stdout.write(
                        f"   • Created Transition(id={transition.id}) "
                        f"for Button(id={button.id}) → State(id={state_id})"
                    )

        self.stdout.write(
            f"\nDone. Scanned {total_buttons} ButtonWidget(s), "
            f"created {created_count} Transition(s) in total."
        )
