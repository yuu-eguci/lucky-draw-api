from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from attendee.models import Attendee

MAX_COUNT = 9999


class Command(BaseCommand):
    help = "動作確認用のダミー参加者を登録します。登録済みのダミーは追加しません。"

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=10)

    def handle(self, *args, count, **options):
        if not 1 <= count <= MAX_COUNT:
            raise CommandError(f"--count は 1 から {MAX_COUNT} で指定してください")

        created = existing = skipped = 0
        for number in range(1, count + 1):
            email = f"seed{number:04d}@example.com"
            if Attendee.objects.filter(email=email).exists():
                existing += 1
                continue
            attendee = Attendee(
                name=f"Seed {number:04d}", email=email, phone=f"0900{number:06d}"
            )
            try:
                attendee.full_clean()
            except ValidationError:
                # 本物の参加者と phone が重なる場合などは登録しません
                skipped += 1
                continue
            attendee.save()
            created += 1

        self.stdout.write(
            f"created: {created}, existing: {existing}, skipped: {skipped}"
        )
