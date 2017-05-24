=======================
Marshmallow-OneOfSchema
=======================

.. image:: https://travis-ci.org/maximkulkin/marshmallow-oneofschema.svg?branch=master
    :target: https://travis-ci.org/maximkulkin/marshmallow-oneofschema
    :alt: Build Status

An extenstion to Marshmallow to support schema (de)multiplexing.

Marshmallow is a fantastic library for serialization and deserialization of data.
For more on that project see its `GitHub <https://github.com/marshmallow-code/marshmallow>`_
page or its `Documentation <http://marshmallow.readthedocs.org/en/latest/>`_.

This library adds a special kind of schema that actually multiplexes other schemas
based on object type. When serializing values, it uses get_obj_type() method
to get object type name. Then it uses `type_schemas` name-to-Schema mapping
to get schema for that particular object type, serializes object using that
schema and adds an extra field with name of object type. Deserialization is reverse.

Installing
----------
::

    $ pip install marshmallow-oneofschema

Importing
---------
Here is how to import the necessary field class
::

    from marshmallow_oneofschema import OneOfSchema

Example
-------

The code below demonstrates how to setup a schema with a PolyField. For the full context check out the tests.
Once setup the schema should act like any other schema. If it does not then please file an Issue.

.. code:: python

        import marshmallow
        import marshmallow.fields
        from marshmallow_oneofschema import OneOfSchema

        class Foo(object):
            def __init__(self, foo):
                self.foo = foo

        class Bar(object):
            def __init__(self, bar):
                self.bar = bar

        class FooSchema(marshmallow.Schema):
            foo = marshmallow.fields.String(required=True)

            @marshmallow.post_load
            def make_foo(self, data):
                return Foo(**data)

        class BarSchema(marshmallow.Schema):
            bar = marshmallow.fields.Integer(required=True)

            @marshmallow.post_load
            def make_bar(self, data):
                return Bar(**data)

        class MyUberSchema(OneOfSchema):
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
                    raise Exception('Unknown object type: %s' % obj.__class__.__name__)

        MyUberSchema().dump([Foo(foo='hello'), Bar(bar=123)], many=True).data
        # => [{'type': 'foo', 'foo': 'hello'}, {'type': 'bar', 'bar': 123}]

        MyUberSchema().load([{'type': 'foo', 'foo': 'hello'},
                             {'type': 'bar', 'bar': 123}],
                            many=True).data
        # => [Foo('hello'), Bar(123)]

By default get_obj_type() returns obj.__class__.__name__, so you can just reuse that
to save some typing:

.. code:: python

        class MyUberSchema(OneOfSchema):
            type_schemas = {
                'Foo': FooSchema,
                'Bar': BarSchema,
            }

You can customize type field with `type_field` class property:

.. code:: python

        class MyUberSchema(OneOfSchema):
            type_field = 'object_type'
            type_schemas = {
                'Foo': FooSchema,
                'Bar': BarSchema,
            }

        MyUberSchema().dump([Foo(foo='hello'), Bar(bar=123)], many=True).data
        # => [{'object_type': 'Foo', 'foo': 'hello'}, {'object_type': 'Bar', 'bar': 123}]

You can set a default schema with `default_schema` class property:

.. code:: python

        class MyUberSchema(OneOfSchema):
            default_schema = BazSchema
            type_field = 'object_type'
            type_schemas = {
                'Foo': FooSchema,
                'Bar': BarSchema,
            }

        MyUberSchema().dump([Foo(foo='hello'), Bar(bar=123), Baz(baz='default')], many=True).data
        # => [{'object_type': 'Foo', 'foo': 'hello'}, {'object_type': 'Bar', 'bar': 123}, {'object_type': 'Baz', 'baz': 'default'}]


You can use resulting schema everywhere marshmallow.Schema can be used, e.g.

.. code:: python

        import marshmallow as m
        import marshmallow.fields as f

        class MyOtherSchema(m.Schema):
            items = f.List(f.Nested(MyUberSchema))

License
-------

MIT licensed. See the bundled `LICENSE <https://github.com/maximkulkin/marshmallow-oneofschema/blob/master/LICENSE>`_ file for more details.
