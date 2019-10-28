import factory

from faker import Faker

from referral.models import Campaign

faker = Faker()


class FakeCampaignFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Campaign

    campaign_id = factory.LazyAttribute(lambda x: faker.sha1())
    name = factory.LazyAttribute(lambda x: faker.word())
