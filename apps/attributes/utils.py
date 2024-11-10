from apps.fsm.models.base import Object


def perform_posterior_actions(attributes, *args, **kwargs):
    from apps.attributes.models import PerformableAction
    performable_attributes = attributes.instance_of(
        PerformableAction)
    for performable_attribute in performable_attributes:
        performable_attribute.perform(*args, **kwargs)


def is_object_free_to_buy(object: Object):
    result = True
    from apps.attributes.models import Buy
    buy_attributes = object.attributes.instance_of(Buy)
    for buy_attribute in buy_attributes:
        from apps.attributes.models import Cost
        if buy_attribute.attributes.instance_of(Cost).exists():
            result = False

    return result
