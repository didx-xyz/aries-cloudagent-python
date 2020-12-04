"""An object for containing information on an individual route."""

from typing import Any
from marshmallow import EXCLUDE, fields, validates_schema, ValidationError

from .....config.injection_context import InjectionContext

from .....messaging.models.base_record import BaseRecord, BaseRecordSchema


class RouteRecord(BaseRecord):
    """Class representing stored route information."""

    class Meta:
        """RouteRecord metadata."""

        schema_class = "RouteRecordSchema"

    RECORD_TYPE = "forward_route"
    RECORD_ID_NAME = "record_id"
    TAG_NAMES = {"connection_id", "recipient_key"}

    def __init__(
        self,
        *,
        record_id: str = None,
        connection_id: str = None,
        wallet_id: str = None,
        recipient_key: str = None,
        **kwargs
    ):
        """
        Initialize a RouteRecord instance.

        Args:

            connection_id: The id of the connection for the route
            wallet_id: The id of the wallet for the route. Used for multitenant relay
            recipient_key: The recipient verkey of the route
        """
        super().__init__(record_id, None, **kwargs)
        self._id = record_id
        self.connection_id = connection_id
        self.wallet_id = wallet_id
        self.recipient_key = recipient_key

    @property
    def record_id(self) -> str:
        """Get record ID."""
        return self._id

    @classmethod
    async def retrieve_by_recipient_key(
        cls, context: InjectionContext, recipient_key: str
    ):
        """Retrieve a route record by recipient key."""
        tag_filter = {"recipient_key": recipient_key}
        # TODO post filter out our mediation requests?
        return await cls.retrieve_by_tag_filter(context, tag_filter)

    @property
    def record_value(self) -> dict:
        """Accessor for JSON record value."""
        return {
            prop: getattr(self, prop)
            for prop in (
                "connection_id",
                "wallet_id",
                "recipient_key",
            )
        }

    @classmethod
    async def retrieve_by_connection_id(
        cls, context: InjectionContext, connection_id: str
    ):
        """Retrieve a route record by connection id."""
        tag_filter = {"connection_id": connection_id}
        # TODO post filter out our mediation requests?
        return await cls.retrieve_by_tag_filter(context, tag_filter)

    def __eq__(self, other: Any) -> bool:
        """Comparison between records."""
        return super().__eq__(other)


class RouteRecordSchema(BaseRecordSchema):
    """RouteRecord schema."""

    class Meta:
        """RouteRecordSchema metadata."""

        model_class = RouteRecord
        unknown = EXCLUDE

    record_id = fields.Str()
    connection_id = fields.Str()
    wallet_id = fields.Str()
    recipient_key = fields.Str(required=True)

    @validates_schema
    def validate_fields(self, data, **kwargs):
        """
        Validate schema fields.

        Args:
            data: The data to validate

        Raises:
            ValidationError: If any of the fields do not validate

        """

        if not data.get("connection_id") and data.get("wallet_id"):
            raise ValidationError(
                "Either connection_id or wallet_id must be set for route"
            )
