from rest_polymorphic.serializers import PolymorphicSerializer
from apps.fsm.models import SmallAnswer, BigAnswer, MultiChoiceAnswer, UploadFileAnswer, Choice, SmallAnswerProblem, Answer
from apps.responses.serializers.answers.answer_serializers import SmallAnswerSerializer, BigAnswerSerializer, MultiChoiceAnswerSerializer, UploadFileAnswerSerializer


class AnswerPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        SmallAnswer: SmallAnswerSerializer,
        BigAnswer: BigAnswerSerializer,
        MultiChoiceAnswer: MultiChoiceAnswerSerializer,
        UploadFileAnswer: UploadFileAnswerSerializer,
    }

    resource_type_field_name = 'answer_type'
