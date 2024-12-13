from rest_polymorphic.serializers import PolymorphicSerializer

from apps.fsm.models.form import Form, RegistrationForm
from apps.fsm.serializers.form.form_serializer import FormSerializer
from apps.fsm.serializers.form.registration_form_serializer import RegistrationFormSerializer


class FormPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        Form: FormSerializer,
        RegistrationForm: RegistrationFormSerializer,
    }
