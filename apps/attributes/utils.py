from apps.fsm.models.base import Object


def perform_posterior_actions(attributes, user, player, website):
    from apps.attributes.models import PerformableAction
    performable_attributes: list[PerformableAction] = attributes.instance_of(
        PerformableAction)
    for performable_attribute in performable_attributes:
        performable_attribute.perform(user, player, website)


def is_object_free_to_buy(object: Object):
    result = True
    from apps.attributes.models import Buy
    buy_attributes = object.attributes.instance_of(Buy)
    for buy_attribute in buy_attributes:
        from apps.attributes.models import Cost
        if buy_attribute.attributes.instance_of(Cost).exists():
            result = False

    return result


def does_object_have_any_reward(object: Object):
    from apps.attributes.models import Reward
    return object.attributes.instance_of(Reward).exists()


def get_object_default_rewards(object: Object):
    from apps.attributes.models import Default, Reward
    default_attribute = object.attributes.instance_of(Default).first()
    if default_attribute:
        reward_attributes = default_attribute.attributes.instance_of(
            Reward)
        return reward_attributes
    return []
