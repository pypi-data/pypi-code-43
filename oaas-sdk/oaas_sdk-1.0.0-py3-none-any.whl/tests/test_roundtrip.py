"""
Simple roundtrip test. Expects to be set up as if running from a client, no mocking and needs a running webservice to point to.
"""
import pandas as pd

from oaas_sdk import LabelingTask


def test_default_args(): #Default args are "verified",  "search"
    # create a new labeling task
    df = pd.DataFrame(
        [
            {
                "document_id": "doc0",
                "from_email": "sales@shoefly.example.com",
                "product_description": "Nk AJ Size 11 Blk",
            },
            {
                "document_id": "doc1",
                "from_email": "sales@generic.example.com",
                "product_description": "Adidas Shoes"
            },
            {
                "from_email": "sales@generic.example.com",
                "product_description": "A generic cobbler's shoe"
            }
        ]
    )

    labeling_task = LabelingTask.create(df)

    assert labeling_task.status in ('submitted', 'processed')

    result = labeling_task.join()

    print(result)

    assert type(result) is pd.DataFrame



def test_roundtrip_unverified():
    # create a new labeling task
    df = pd.DataFrame(
        [
            {
                "document_id": "doc0",
                "from_email": "sales@shoefly.example.com",
                "product_description": "Nk AJ Size 11 Blk",
            },
            {
                "document_id": "doc1",
                "from_email": "sales@generic.example.com",
                "product_description": "Adidas Shoes"
            },
            {
                "from_email": "sales@generic.example.com",
                "product_description": "A generic cobbler's shoe"
            }
        ]
    )

    labeling_task = LabelingTask.create(df,
        'unverified',
        'search')

    assert labeling_task.status in ('submitted', 'processed')

    result = labeling_task.join()

    print(result)

    assert type(result) is pd.DataFrame