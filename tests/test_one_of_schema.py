import marshmallow as m
import marshmallow.fields as f
from marshmallow_oneofschema import OneOfSchema
import pytest


REQUIRED_ERROR = u'Missing data for required field.'


class Foo(object):
    def __init__(self, value=None):
        self.value = value

    def __repr__(self):
        return '<Foo value=%s>' % self.value

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.value == other.value


class FooSchema(m.Schema):
    value = f.String(required=True)

    @m.post_load
    def make_foo(self, data):
        return Foo(**data)


class Bar(object):
    def __init__(self, value=None):
        self.value = value

    def __repr__(self):
        return '<Bar value=%s>' % self.value

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.value == other.value


class BarSchema(m.Schema):
    value = f.Integer(required=True)

    @m.post_load
    def make_bar(self, data):
        return Bar(**data)


class Baz(object):
    def __init__(self, value1=None, value2=None):
        self.value1 = value1
        self.value2 = value2

    def __repr__(self):
        return '<Bar value1=%s value2=%s>' % (self.value1, self.value2)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.value1 == other.value1 \
            and self.value2 == other.value2


class BazSchema(m.Schema):
    value1 = f.Integer(required=True)
    value2 = f.String(required=True)

    @m.post_load
    def make_baz(self, data):
        return Baz(**data)


class Bat(object):
    def __init__(self, value1=None, value2=None, value3=None):
        self.value1 = value1
        self.value2 = value2
        self.value3 = value3

    def __repr__(self):
        return '<Bat value1=%s value2=%s>' % (self.value1, self.value2)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.value1 == other.value1 \
            and self.value2 == other.value2


class BatSchema(m.Schema):
    value1 = f.Integer(required=True)
    value2 = f.String(required=True)
    value3 = f.String()

    @m.post_load
    def make_bat(self, data):
        return Bat(**data)


class MySchema(OneOfSchema):
    type_schemas = {
        'Foo': FooSchema,
        'Bar': BarSchema,
        'Baz': BazSchema,
        'Bat': BatSchema,
    }


class TestOneOfSchema:
    def test_dump(self):
        foo_result = MySchema().dump(Foo('hello'))
        assert {'type': 'Foo', 'value': 'hello'} == foo_result

        bar_result = MySchema().dump(Bar(123))
        assert {'type': 'Bar', 'value': 123} == bar_result

    def test_dump_exclude(self):
        bat_result = MySchema().dump(Bat(1, 'hello', 'i like turtles'))
        assert {'type': 'Bat', 'value1': 1, 'value2': 'hello', 'value3': 'i like turtles'} == bat_result

        exclude_schema = MySchema(exclude=('value3',))
        bat_exclude_result = exclude_schema.dump(Bat(1, 'hello', 'i like turtles'))
        assert {'type': 'Bat', 'value1': 1, 'value2': 'hello'} == bat_exclude_result

        foo_result = exclude_schema.dump(Foo('hello'))
        assert {'type': 'Foo', 'value': 'hello'} == foo_result

    def test_dump_many(self):
        result = MySchema().dump([Foo('hello'), Bar(123)], many=True)
        assert [{'type': 'Foo', 'value': 'hello'},
                {'type': 'Bar', 'value': 123}] == result

    def test_dump_many_in_constructor(self):
        result = MySchema(many=True).dump([Foo('hello'), Bar(123)])
        assert [{'type': 'Foo', 'value': 'hello'},
                {'type': 'Bar', 'value': 123}] == result

    def test_load(self):
        foo_result = MySchema().load({'type': 'Foo', 'value': 'world'})
        assert Foo('world') == foo_result

        bar_result = MySchema().load({'type': 'Bar', 'value': 456})
        assert Bar(456) == bar_result

    def test_load_many(self):
        result = MySchema().load([
            {'type': 'Foo', 'value': 'hello world!'},
            {'type': 'Bar', 'value': 123},
        ], many=True)
        assert Foo('hello world!'), Bar(123) == result

    def test_load_many_in_constructor(self):
        result = MySchema(many=True).load([
            {'type': 'Foo', 'value': 'hello world!'},
            {'type': 'Bar', 'value': 123},
        ])
        assert Foo('hello world!'), Bar(123) == result

    def test_load_removes_type_field(self):
        class Nonlocal(object):
            data = None

        class MySchema(m.Schema):
            def load(self, data, *args, **kwargs):
                Nonlocal.data = data
                return super(MySchema, self).load(data, *args, **kwargs)

        class FooSchema(MySchema):
            foo = f.String(required=True)

        class BarSchema(MySchema):
            bar = f.Integer(required=True)

        class TestSchema(OneOfSchema):
            type_schemas = {
                'Foo': FooSchema,
                'Bar': BarSchema,
            }

        TestSchema().load({'type': 'Foo', 'foo': 'hello'})
        assert 'type' not in Nonlocal.data

        TestSchema().load({'type': 'Bar', 'bar': 123})
        assert 'type' not in Nonlocal.data

    def test_load_keeps_type_field(self):
        class Nonlocal(object):
            data = None
            type = None

        class MySchema(m.Schema):
            def load(self, data, *args, **kwargs):
                Nonlocal.data = data
                return super(MySchema, self).load(data, *args, **kwargs)

        class FooSchema(MySchema):
            foo = f.String(required=True)

        class BarSchema(MySchema):
            bar = f.Integer(required=True)

        class TestSchema(OneOfSchema):
            type_field_remove = False
            type_schemas = {
                'Foo': FooSchema,
                'Bar': BarSchema,
            }

        TestSchema().load({'type': 'Foo', 'foo': 'hello'})
        assert Nonlocal.data['type'] == 'Foo'

        TestSchema().load({'type': 'Bar', 'bar': 123})
        assert Nonlocal.data['type'] == 'Bar'

    def test_load_non_dict(self):
        with pytest.raises(m.ValidationError) as exc_info:
            MySchema().load(123)
        assert {} != exc_info.value

        with pytest.raises(m.ValidationError) as exc_info:
            MySchema().load('Foo')
        assert {} != exc_info.value

    def test_load_errors_no_type(self):
        with pytest.raises(m.ValidationError) as exc_info:
            MySchema().load({'value': 'Foo'})
        assert {0: {'type': [REQUIRED_ERROR]}} == exc_info.value.messages

    def test_load_errors_field_error(self):
        with pytest.raises(m.ValidationError) as exc_info:
            MySchema().load({'type': 'Foo'})
        assert {0: {'value': [REQUIRED_ERROR]}} == exc_info.value.messages

    def test_load_errors_strict(self):
        with pytest.raises(m.ValidationError) as exc_info:
            MySchema().load({'type': 'Foo'})

        assert {
            0: {
                'value': ['Missing data for required field.']
            }
        } == exc_info.value.messages

    def test_load_many_errors_are_indexed_by_object_position(self):
        with pytest.raises(m.ValidationError) as exc_info:
            MySchema().load([
                {'type': 'Foo'},
                {'type': 'Bar', 'value': 123},
            ], many=True)
        assert {0: {'value': [REQUIRED_ERROR]}} == exc_info.value.messages

    def test_load_many_errors_strict(self):
        with pytest.raises(m.ValidationError) as exc_info:
            MySchema().load([
                {'type': 'Foo', 'value': 'hello world!'},
                {'type': 'Foo'},
                {'type': 'Bar', 'value': 123},
                {'type': 'Bar', 'value': 'hello'},
            ], many=True)

        assert {1: {'value': ['Missing data for required field.']},
                3: {'value': ['Not a valid integer.']}} == exc_info.value.messages

    def test_load_partial_specific(self):
        result = MySchema().load(
            {'type': 'Foo'},
            partial=('value', 'value2',)
        )
        assert Foo() == result

        result = MySchema().load(
            {'type': 'Baz', 'value1': 123},
            partial=('value', 'value2',)
        )
        assert Baz(value1=123) == result

    def test_load_partial_any(self):
        result = MySchema().load({'type': 'Foo'}, partial=True)
        assert Foo() == result

        result = MySchema().load({'type': 'Baz', 'value1': 123}, partial=True)
        assert Baz(value1=123) == result

        result = MySchema().load({'type': 'Baz', 'value2': 'hello'}, partial=True)
        assert Baz(value2='hello') == result

    def test_load_partial_specific_in_constructor(self):
        result = MySchema(partial=('value', 'value2',)).load({'type': 'Foo'})
        assert Foo() == result

        result = MySchema(partial=('value', 'value2',))\
            .load({'type': 'Baz', 'value1': 123})
        assert Baz(value1=123) == result

    def test_load_partial_any_in_constructor(self):
        result = MySchema(partial=True).load({'type': 'Foo'})
        assert Foo() == result

        result = MySchema(partial=True).load({'type': 'Baz', 'value1': 123})
        assert Baz(value1=123) == result

        result = MySchema(partial=True).load({'type': 'Baz', 'value2': 'hello'})
        assert Baz(value2='hello') == result

    def test_validate(self):
        assert {} == MySchema().validate({'type': 'Foo', 'value': '123'})
        assert {
            0: {'value': [REQUIRED_ERROR]}
        } == MySchema().validate({'type': 'Bar'})
        assert {
            0: {'value': [REQUIRED_ERROR]}
        } == MySchema().validate({'type': 'Bar'})

    def test_validate_many(self):
        errors = MySchema().validate([
            {'type': 'Foo', 'value': '123'},
            {'type': 'Bar', 'value': 123},
        ], many=True)
        assert {} == errors

        errors = MySchema().validate([
            {'value': '123'},
            {'type': 'Bar'},
        ], many=True)
        assert {0: {'type': [REQUIRED_ERROR]},
                1: {'value': [REQUIRED_ERROR]}} == errors

        errors = MySchema().validate([
            {'value': '123'},
            {'type': 'Bar'},
        ], many=True)
        assert {0: {'type': [REQUIRED_ERROR]},
                1: {'value': [REQUIRED_ERROR]}} == errors

    def test_validate_many_in_constructor(self):
        errors = MySchema(many=True).validate([
            {'type': 'Foo', 'value': '123'},
            {'type': 'Bar', 'value': 123},
        ])
        assert {} == errors

        errors = MySchema(many=True).validate([
            {'value': '123'},
            {'type': 'Bar'},
        ])
        assert {0: {'type': [REQUIRED_ERROR]},
                1: {'value': [REQUIRED_ERROR]}} == errors

    def test_validate_partial_specific(self):
        errors = MySchema().validate(
            {'type': 'Foo'},
            partial=('value', 'value2',)
        )
        assert {} == errors

        errors = MySchema().validate(
            {'type': 'Baz', 'value1': 123},
            partial=('value', 'value2',)
        )
        assert {} == errors

    def test_validate_partial_any(self):
        errors = MySchema().validate(
            {'type': 'Foo'}, partial=True
        )
        assert {} == errors

        errors = MySchema().validate(
            {'type': 'Baz', 'value1': 123},
            partial=True
        )
        assert {} == errors

        errors = MySchema().validate(
            {'type': 'Baz', 'value2': 'hello'},
            partial=True
        )
        assert {} == errors

    def test_validate_partial_specific_in_constructor(self):
        errors = MySchema(
            partial=('value', 'value2',)
        ).validate({'type': 'Foo'})
        assert {} == errors

        errors = MySchema(
            partial=('value', 'value2',)
        ).validate({'type': 'Baz', 'value1': 123})
        assert {} == errors

    def test_validate_partial_any_in_constructor(self):
        errors = MySchema(
            partial=True
        ).validate({'type': 'Foo'})
        assert {} == errors

        errors = MySchema(
            partial=True
        ).validate({'type': 'Baz', 'value1': 123})
        assert {} == errors

        errors = MySchema(
            partial=True
        ).validate({'type': 'Baz', 'value2': 'hello'})
        assert {} == errors

    def test_using_as_nested_schema(self):
        class SchemaWithList(m.Schema):
            items = f.List(f.Nested(MySchema))

        schema = SchemaWithList()
        result = schema.load({'items': [
            {'type': 'Foo', 'value': 'hello world!'},
            {'type': 'Bar', 'value': 123},
        ]})
        assert {'items': [Foo('hello world!'), Bar(123)]} == result

        with pytest.raises(m.ValidationError) as exc_info:
            schema.load({'items': [
                {'type': 'Foo', 'value': 'hello world!'},
                {'value': 123},
            ]})
        assert {'items': {1: {0: {'type': [REQUIRED_ERROR]}}}} == exc_info.value.messages

    def test_using_as_nested_schema_with_many(self):
        class SchemaWithMany(m.Schema):
            items = f.Nested(MySchema, many=True)

        schema = SchemaWithMany()
        result = schema.load({'items': [
            {'type': 'Foo', 'value': 'hello world!'},
            {'type': 'Bar', 'value': 123},
        ]})
        assert {'items': [Foo('hello world!'), Bar(123)]} == result

        with pytest.raises(m.ValidationError) as exc_info:
            schema.load({'items': [
                {'type': 'Foo', 'value': 'hello world!'},
                {'value': 123},
            ]})
        assert {'items': {1: {'type': [REQUIRED_ERROR]}}} == exc_info.value.messages

    def test_using_custom_type_names(self):
        class MyCustomTypeNameSchema(OneOfSchema):
            type_schemas = {
                'baz': FooSchema,
                'bam': BarSchema,
            }

            def get_obj_type(self, obj):
                return {'Foo': 'baz', 'Bar': 'bam'}.get(obj.__class__.__name__)

        schema = MyCustomTypeNameSchema()
        data = [Foo('hello'), Bar(111)]
        marshalled = schema.dump(data, many=True)
        assert [{'type': 'baz', 'value': 'hello'},
                {'type': 'bam', 'value': 111}] == marshalled

        unmarshalled = schema.load(marshalled, many=True)
        assert data == unmarshalled

    def test_using_custom_type_field(self):
        class MyCustomTypeFieldSchema(MySchema):
            type_field = 'object_type'

        schema = MyCustomTypeFieldSchema()
        data = [Foo('hello'), Bar(111)]
        marshalled = schema.dump(data, many=True)
        assert [{'object_type': 'Foo', 'value': 'hello'},
                {'object_type': 'Bar', 'value': 111}] == marshalled

        unmarshalled = schema.load(marshalled, many=True)
        assert data == unmarshalled
