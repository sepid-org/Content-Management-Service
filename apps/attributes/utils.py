def perform_posterior_actions(attributes, *args, **kwargs):
    from apps.attributes.models import PerformableAction
    performable_attributes = attributes.instance_of(
        PerformableAction)
    for performable_attribute in performable_attributes:
        performable_attribute.perform(*args, **kwargs)
