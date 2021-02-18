import marshmallow as m
import marshmallow.fields as f
from marshmallow_oneofschema import OneOfSchema

from test_one_of_schema import Foo, Bar, Baz


class MySchemaWithDefaultNames(OneOfSchema):
    type_schemas = {}


class MySchemaWithCustomNames(OneOfSchema):
    type_schemas = {}

    counter = 0
    known_types = [Foo, Bar, Baz]

    def get_obj_type(self, obj):
        return self.known_classes.index(obj.__class__)

    @classmethod
    def schema_name(cls, schema_class):
        cls.counter += 1
        return str(cls.counter - 1)


@MySchemaWithCustomNames.register_one_of
@MySchemaWithDefaultNames.register_one_of
class FooSchema(m.Schema):
    value = f.String(required=True)

    @m.post_load
    def make_foo(self, data, **kwargs):
        return Foo(**data)


@MySchemaWithCustomNames.register_one_of
@MySchemaWithDefaultNames.register_one_of
class BarSchema(m.Schema):
    value = f.Integer(required=True)

    @m.post_load
    def make_bar(self, data, **kwargs):
        return Bar(**data)


@MySchemaWithCustomNames.register_one_of
@MySchemaWithDefaultNames.register_one_of
class BazSchema(m.Schema):
    value1 = f.Integer(required=True)
    value2 = f.String(required=True)

    @m.post_load
    def make_baz(self, data, **kwargs):
        return Baz(**data)


class MyVerboseSchemaWithDefaultNames(OneOfSchema):
    type_schemas = {
        "Foo": FooSchema,
        "Bar": BarSchema,
        "Baz": BazSchema,
    }


class MyVerboseSchemaWithCustomNames(OneOfSchema):
    type_schemas = {
        "0": FooSchema,
        "1": BarSchema,
        "2": BazSchema,
    }


def test_schemas_building_with_register_one_of():
    assert (
        MySchemaWithDefaultNames.type_schemas
        == MyVerboseSchemaWithDefaultNames.type_schemas
    )
    assert (
        MySchemaWithCustomNames.type_schemas
        == MyVerboseSchemaWithCustomNames.type_schemas
    )


def test_default_schema_naming():
    class SomeObjectSchema:
        pass

    assert OneOfSchema.schema_name(SomeObjectSchema) == "SomeObject"

    class AnyOtherSchemaClass:
        pass

    assert OneOfSchema.schema_name(AnyOtherSchemaClass) == "AnyOtherSchemaClass"
