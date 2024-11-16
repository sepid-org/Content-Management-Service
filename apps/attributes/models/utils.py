class SumDict(dict):
    def __add__(self, other):
        result = self.copy()
        for key, value in other.items():
            if key in result:
                result[key] += value
            else:
                result[key] = value
        return SumDict(result)

    def __radd__(self, other):
        if other == 0:  # Handle sum() function case
            return self
        return self.__add__(other)

    def __bool__(self):
        """Returns False if the dictionary is empty or all values are zero/empty"""
        return any(bool(value) for value in self.values())

    def is_zero(self):
        """Check if all values are numeric zero or empty collections"""
        for value in self.values():
            if isinstance(value, (int, float)):
                if value != 0:
                    return False
            elif isinstance(value, (dict, list, set, str)):
                if value:
                    return False
            else:
                if bool(value):
                    return False
        return True


def get_net_rewards(self):
    total_reward = SumDict({})

    from .intrinsic_attributes import Reward
    reward_attributes = self.attributes.instance_of(Reward)
    for reward in reward_attributes:
        total_reward += SumDict(reward.value)

    return total_reward


def get_allocated_rewards(net_rewards, allocation_percentage):
    allocated_rewards = {}
    for currency, amount in net_rewards.items():
        allocated_rewards[currency] = round(
            amount * allocation_percentage / 100)
    return allocated_rewards
