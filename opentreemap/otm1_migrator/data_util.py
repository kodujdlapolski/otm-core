from treemap.models import User
from treemap.audit import model_hasattr


class MigrationException(Exception):
    pass


def validate_model_dict(config, model_name, data_dict):
    """
    Makes sure the fields specified in the config global
    account for all of the provided data
    """
    common_fields = config[model_name].get('common_fields', set())
    renamed_fields = set(config[model_name].get('renamed_fields', {}).keys())
    removed_fields = config[model_name].get('removed_fields', set())
    dependency_fields = set(config[model_name]
                            .get('dependencies', {}).values())
    expected_fields = (common_fields |
                       renamed_fields |
                       removed_fields |
                       dependency_fields)

    provided_fields = set(data_dict['fields'].keys())

    if expected_fields != provided_fields:
        raise Exception('model validation failure. \n\n'
                        'Expected: %s \n\n'
                        'Got: %s\n\n'
                        'Symmetric Difference: %s'
                        % (expected_fields, provided_fields,
                           expected_fields.
                           symmetric_difference(provided_fields)))


def dict_to_model(config, model_name, data_dict, instance):
    """
    Takes a model specified in the config global and a
    dict of json data and attempts to populate a django
    model. Does not save.
    """
    validate_model_dict(config, model_name, data_dict)

    common_fields = config[model_name].get('common_fields', set())
    renamed_fields = config[model_name].get('renamed_fields', {})
    dependency_fields = config[model_name].get('dependencies', {})

    model = config[model_name]['model_class']()

    identity = (lambda x: x)

    for field in (common_fields
                  .union(renamed_fields)
                  .union(dependency_fields.values())):
        transform_fn = (config[model_name]
                        .get('value_transformers', {})
                        .get(field, identity))

        transformed_value = transform_fn(data_dict['fields'][field])
        field = renamed_fields.get(field, field)
        if field in dependency_fields.values():
            field += '_id'

        setattr(model, field, transformed_value)

    if model_hasattr(model, 'instance'):
        model.instance = instance

    for mutator in config[model_name].get('record_mutators', []):
        mutator(model, data_dict['fields'])

    return model


def uniquify_username(username):
    username_template = '%s_%%d' % username
    i = 0
    while User.objects.filter(username=username).exists():
        username = username_template % i
        i += 1

    return username


def sanitize_username(username):
    # yes, there was actually a user with newlines
    # in their username
    return (username
            .replace(' ', '_')
            .replace('\n', ''))
