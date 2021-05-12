from collections.abc import Mapping
import inspect

from marshmallow import Schema, ValidationError, RAISE


# these helpers copied from marshmallow.utils #


def is_generator(obj) -> bool:
    """Return True if ``obj`` is a generator"""
    return inspect.isgeneratorfunction(obj) or inspect.isgenerator(obj)


def is_iterable_but_not_string(obj) -> bool:
    """Return True if ``obj`` is an iterable object that isn't a string."""
    return (hasattr(obj, "__iter__") and not hasattr(obj, "strip")) or is_generator(obj)


def is_collection(obj) -> bool:
    """Return True if ``obj`` is a collection type, e.g list, tuple, queryset."""
    return is_iterable_but_not_string(obj) and not isinstance(obj, Mapping)


# end of helpers copied from marshmallow.utils #


class OneOfSchema(Schema):
    """
    This is a special kind of schema that actually multiplexes other schemas
    based on object type. When serializing values, it uses get_obj_type() method
    to get object type name. Then it uses `type_schemas` name-to-Schema mapping
    to get schema for that particular object type, serializes object using that
    schema and adds an extra "type" field with name of object type.
    Deserialization is reverse.

    Example:

        class Foo(object):
            def __init__(self, foo):
                self.foo = foo

        class Bar(object):
            def __init__(self, bar):
                self.bar = bar

        class FooSchema(marshmallow.Schema):
            foo = marshmallow.fields.String(required=True)

            @marshmallow.post_load
            def make_foo(self, data, **kwargs):
                return Foo(**data)

        class BarSchema(marshmallow.Schema):
            bar = marshmallow.fields.Integer(required=True)

            @marshmallow.post_load
            def make_bar(self, data, **kwargs):
                return Bar(**data)

        class MyUberSchema(marshmallow.OneOfSchema):
            type_schemas = {
                'foo': FooSchema,
                'bar': BarSchema,
            }

            def get_obj_type(self, obj):
                if isinstance(obj, Foo):
                    return 'foo'
                elif isinstance(obj, Bar):
                    return 'bar'
                else:
                    raise Exception('Unknown object type: %s' % repr(obj))

        MyUberSchema().dump([Foo(foo='hello'), Bar(bar=123)], many=True)
        # => [{'type': 'foo', 'foo': 'hello'}, {'type': 'bar', 'bar': 123}]

    You can control type field name added to serialized object representation by
    setting `type_field` class property.
    """

    type_field = "type"
    type_field_remove = True
    type_schemas = {}

    def get_obj_type(self, obj):
        """Returns name of object schema"""
        return obj.__class__.__name__

    # override the `_serialize` method of Schema, rather than `dump`
    # this requires that we interact with a private API of marshmallow, but
    # `_serialize` is the step that happens between pre_dump and post_dump
    # hooks, so by using this rather than `load()`, we get schema hooks to work
    def _serialize(self, obj, *, many=False):
        if many and obj is not None:
            return [self._serialize(subdoc, many=False) for subdoc in obj]
        return self._dump_type_schema(obj)

    def _dump_type_schema(self, obj):
        obj_type = self.get_obj_type(obj)
        if not obj_type:
            return (
                None,
                {"_schema": "Unknown object class: %s" % obj.__class__.__name__},
            )

        type_schema = self.type_schemas.get(obj_type)
        if not type_schema:
            return None, {"_schema": "Unsupported object type: %s" % obj_type}

        schema = type_schema if isinstance(type_schema, Schema) else type_schema()

        schema.context.update(getattr(self, "context", {}))

        result = schema.dump(obj, many=False)
        if result is not None:
            result[self.type_field] = obj_type
        return result

    # override the `_deserialize` method of Schema, rather than `load`
    # this requires that we interact with a private API of marshmallow, but
    # `_deserialize` is the step that happens between pre_load and validation
    # hooks, so by using this rather than `load()`, we get schema hooks to work
    def _deserialize(
        self,
        data,
        *,
        error_store,
        many=False,
        partial=False,
        unknown=RAISE,
        index=None,
    ):
        index = index if self.opts.index_errors else None
        # if many, check for non-collection data (error) or iterate and
        # re-invoke `_deserialize` on each one with many=False
        # this is paraphrased from marshmallow.Schema._deserialize
        if many:
            if not is_collection(data):
                error_store.store_error([self.error_messages["type"]], index=index)
                return []
            else:
                return [
                    self._deserialize(
                        subdoc,
                        error_store=error_store,
                        many=False,
                        partial=partial,
                        unknown=unknown,
                        index=idx,
                    )
                    for idx, subdoc in enumerate(data)
                ]
        if not isinstance(data, Mapping):
            error_store.store_error([self.error_messages["type"]], index=index)
            return self.dict_class()

        try:
            result = self._load_type_schema(data, partial=partial, unknown=unknown)
        except ValidationError as err:
            error_store.store_error(err.messages, index=index)
            result = err.valid_data

        return result

    def _load_type_schema(self, data, *, partial=None, unknown=None):
        if not isinstance(data, dict):
            raise ValidationError({"_schema": "Invalid data type: %s" % data})

        data = dict(data)
        unknown = unknown or self.unknown

        data_type = data.get(self.type_field)
        if self.type_field in data and self.type_field_remove:
            data.pop(self.type_field)

        if not data_type:
            raise ValidationError(
                {self.type_field: ["Missing data for required field."]}
            )

        try:
            type_schema = self.type_schemas.get(data_type)
        except TypeError:
            # data_type could be unhashable
            raise ValidationError({self.type_field: ["Invalid value: %s" % data_type]})
        if not type_schema:
            raise ValidationError(
                {self.type_field: ["Unsupported value: %s" % data_type]}
            )

        schema = type_schema if isinstance(type_schema, Schema) else type_schema()

        schema.context.update(getattr(self, "context", {}))

        return schema.load(data, many=False, partial=partial, unknown=unknown)
