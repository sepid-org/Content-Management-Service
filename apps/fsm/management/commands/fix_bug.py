from django.core.management.base import BaseCommand
from django.db import transaction

from apps.fsm.models import Program, Widget
from apps.fsm.models.base import Paper

id_mapper = {
    1: 2770,
    293: 2772,
    306: 2793,
    307: 2752,
    308: 2754,
    520: 2755,
    521: 2753,
    530: 2756,
    629: 2758,
    630: 2757,
    788: 2771,
    1117: 2759,
    1118: 2760,
    1130: 2761,
    1286: 2768,
    1375: 2769,
    1437: 2767,
    2193: 2783,
    2276: 2762,
    2277: 2763,
    2298: 2775,
    2303: 2777,
    2489: 2789,
    2497: 2792,
    2610: 2790,
}


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write(
            'Starting migration of RegistrationForm to RegistrationForm2...')

        widgets = Widget.objects.all()
        for widget in widgets:
            try:
                with transaction.atomic():
                    paper_id = widget.paper.id
                    if paper_id in id_mapper:
                        new_paper_id = id_mapper[paper_id]
                        new_paper = Paper.objects.get(id=new_paper_id)
                        widget.paper = new_paper
                        widget.save()

            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'Failed {widget.id}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(
            f'job completed'))
