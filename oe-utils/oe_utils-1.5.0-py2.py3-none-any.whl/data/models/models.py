"""
Dit bestand bevat een OE Base Model dat in alle OE toepassingen kan worden gebruikt.

Het voordeel van een generieke Base is dat we op deze werkwijze per toepassing 1 zelfde
Base kunnen gebruiken voor al de aanwezige Models.
Dit omvat zowel Models van de applicatie zelf,
als de Models uit libraries zoals oe_utils en oe_geoutils.

Hier kan eveneens de nodige generieke metadata aan ons Base Model worden meegegeven.
Hiervoor kan sqlalchemy.schema.MetaData worden gebruikt
"""
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.sql import func

Base = declarative_base()


class Wijziging(Base):
    """
    A database table configuration object.

    This table contains information about the audit of a resource object.

    This object will not create the db table object.
    To create the table insert following code in the alembic migration file

    `alembic revision -m "wijzigingshistoriek"`


    from alembic import op
    import sqlalchemy as sa
    from sqlalchemy.dialects.postgresql import JSON
    from sqlalchemy.sql import func


    def upgrade():
        op.create_table(
            "wijzigingshistoriek",
            sa.Column("versie", sa.String(), nullable=False),
            sa.Column("resource_object_id", sa.Integer(), nullable=False),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                default=func.now(),
                nullable=False,
            ),
            sa.Column("updated_by", sa.String(length=255), nullable=False),
            sa.Column("updated_by_omschrijving", sa.String(length=255), nullable=False),
            sa.Column("resource_object_json", JSON, nullable=True),
            sa.Column("actie", sa.String(length=50), nullable=False),
            sa.PrimaryKeyConstraint("versie", name="wijzigingshistoriek_pk"),
        )

        op.execute("GRANT ALL ON wijzigingshistoriek to <user>_dml")


    def downgrade():
        op.drop_table("wijzigingshistoriek")
    """

    __tablename__ = "wijzigingshistoriek"
    versie = Column(String(64), primary_key=True)
    resource_object_id = Column(Integer, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_by = Column(
        String(255), default="https://id.erfgoed.net/actoren/501", nullable=False
    )
    updated_by_omschrijving = Column(
        String(255), default="Onroerend Erfgoed", nullable=False
    )
    resource_object_json = Column(MutableDict.as_mutable(JSON()), nullable=True)
    actie = Column(String(50), nullable=False)
