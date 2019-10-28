from django.dispatch import Signal

referral_reward_acquired = Signal(providing_args=['user', 'reward_data'])
