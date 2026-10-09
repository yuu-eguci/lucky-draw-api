from django.db import IntegrityError, transaction
from rest_framework import viewsets

from .models import Attendee
from .serializers import AttendeeSerializer


class AttendeeViewSet(viewsets.ModelViewSet):
    queryset = Attendee.objects.all()
    serializer_class = AttendeeSerializer

    def perform_create(self, serializer):
        self._save(serializer)

    def perform_update(self, serializer):
        self._save(serializer)

    def _save(self, serializer):
        try:
            with transaction.atomic():
                serializer.save()
        except IntegrityError:
            # 検証のあとに別リクエストが同じ email や phone を登録した場合は、
            # 再検証して通常の重複エラー (400) を返します
            retry = self.get_serializer(
                serializer.instance, data=self.request.data, partial=serializer.partial
            )
            retry.is_valid(raise_exception=True)
            raise
