from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    IntegerField,
    TextAreaField,
    FloatField,
    BooleanField,
    SelectField,
    HiddenField
)
from wtforms.validators import InputRequired, Length, Optional
from wtforms.widgets import TextInput, Select
from wtforms.widgets.html5 import NumberInput


class AlgorithmForm(FlaskForm):
    api_key = StringField('API Key', validators=[InputRequired()])


def set_field(p, v):
    try:
        default_value = p['default_value']
    except KeyError:
        default_value = None

    if v == 'required':
        this_validators = [InputRequired(), ]
        this_kw = {'required': True}
    else:
        this_validators = [Optional()]
        this_kw = {}

    if p['field_type'] == 'number':
        this_widget = NumberInput()
        if 'min_value' in p:
            this_widget.min = p['min_value']
        if 'max_value' in p:
            this_widget.max = p['max_value']
        if p['data_type'] == 'float':
            this_widget.step = 'any'
    elif p['field_type'] == 'select':
        this_widget = Select()
    else:
        this_widget = TextInput()

    if p['data_type'] == 'integer':
        this_field = IntegerField
        # if default_value is None:
        #    default_value = 0
    elif p['data_type'] == 'float':
        this_field = FloatField
    else:
        this_field = StringField

    if p['field_type'] == 'select':
        choices = [
            (x.strip(), x.strip()) for x in p['parameter_choices'].split(',')
        ]
        return_field = SelectField(
            label=p['display_name'],
            widget=this_widget,
            validators=this_validators,
            render_kw=this_kw,
            default=default_value,
            choices=choices
        )
    else:
        return_field = this_field(
            label=p['display_name'],
            widget=this_widget,
            validators=this_validators,
            render_kw=this_kw,
            default=default_value
        )
    return return_field


class AlgorithmCreateForm(FlaskForm):
    name = StringField(
        'Algorithm Name',
        validators=[InputRequired(), Length(max=50)],
        description='Enter a short name for the algorithm (no spaces)',
        render_kw={
            'maxlength': '50',
        },
    )
    display_name = StringField(
        'Display Name',
        validators=[InputRequired(), Length(max=255)],
        description='Enter a more descriptive name for the algorithm',
        render_kw={
            'maxlength': '255',
        },
    )
    description = TextAreaField(
        render_kw={'rows': 5}
    )
    version = StringField(
        'Version',
        validators=[InputRequired(), Length(max=50)],
        description='Enter a version string (e.g.: "0.0.1", "beta")',
        default='0.0.1',
        render_kw={
            'maxlength': '50',
        },
    )
    homepage = StringField(
        'Algorithm Website',
        validators=[Length(max=512)],
        description='Include a URL where someone could go for documentation',
        render_kw={
            'maxlength': '512',
        },
    )
    private = BooleanField(
        description=(
            'Make this algorithm unlisted (if publishing '
            'to the Algorithm Registry)'
        )
    )
    license = SelectField(
        choices=[
            ('MIT', 'MIT'),
            ('BSD', 'BSD-3-Clause'),
            ('GNU AGPLv3', 'GNU AGPLv3'),
            ('GNU GPLv3', 'GNU GPLv3'),
            ('GNU LGPLv3', 'GNU LGPLv3'),
            ('Mozilla', 'Mozilla'),
            ('Apache', 'Apache'),
            ('The Unlicense', 'The Unlicense'),
            ('Proprietary', 'Proprietary'),
            ('Other', 'See LICENSE File')
        ],
        description=(
            'See https://choosealicense.com/licenses/ '
            'for info on various open source licenses'
        )
    )
    update_readme = BooleanField(label="Also update README file")
    parameters = HiddenField()
    outputs = HiddenField()
    deleted_parameters = HiddenField()
    deleted_outputs = HiddenField()


class AlgorithmParameterForm(FlaskForm):
    name = StringField(
        'Parameter Name',
        validators=[InputRequired(), Length(max=50)],
        description='Enter a unique short name for the parameter (no spaces)',
        render_kw={
            'maxlength': '50',
            'data-parsley-notin': 'parameter',
            'data-parsley-notin-message': (
                'This value must be unique; another parameter has this name')
        }
    )
    original_name = HiddenField()
    required = BooleanField(
        default=True,
        description=(
            'Require a value for this parameter'
        )
    )
    display_name = StringField(
        'Display Name',
        validators=[InputRequired(), Length(max=255)],
        description='Enter a more descriptive name for the parameter',
        render_kw={
            'maxlength': '255',
        },
    )
    description = TextAreaField(
        render_kw={'rows': 3}
    )
    data_type = SelectField(
        choices=[
            ('string', 'String'),
            ('integer', 'Integer'),
            ('float', 'Float'),
            ('array', 'Array')
        ],
        description='Select the type of data this parameter will accept',
        render_kw={
            'onchange': 'selectFieldType("parameter", false)'
        }
    )
    field_type = SelectField(
        choices=[
            ('text', 'Text'),
            ('number', 'Number'),
            ('select', 'Select'),
            # ('range', 'Range'),
            # ('hidden', 'Hidden')
        ],
        description=(
            'Select the type of form field that would be '
            'displayed for this parameter'
        )
    )
    help_text = TextAreaField(
        description=(
            'Enter some information that would help a user know how to '
            'enter a value for this parameter'
        ),
        render_kw={'rows': 3}
    )
    min_value = FloatField(
        'Minimum Value',
        description=(
            'Set the smallest value of this parameter (number '
            'parameter types only)'
        ),
        render_kw={
            'data-parsley-type': 'number',
            'data-parsley-lt': '#parameterForm #max_value',
            'data-parsley-lt-message': (
                'Value must be less than "Maximum Value"'),
            'step': 'any'
        },
        widget=NumberInput()
    )
    max_value = FloatField(
        'Maximum Value',
        description=(
            'Set the largest value of this parameter (number '
            'parameter types only)'
        ),
        render_kw={
            'data-parsley-type': 'number',
            'data-parsley-gt': '#parameterForm #min_value',
            'data-parsley-gt-message': (
                'Value must be greater than "Minimum Value"'),
            'step': 'any'
        },
        widget=NumberInput()
    )
    default_value = StringField(
        validators=[Length(max=512)],
        description=(
            'Set the default value of this parameter'
        ),
        render_kw={
            'maxlength': '512',
            'data-parsley-intif': '#parameterForm #data_type option:selected',
            'data-parsley-intif-message': (
                'If Data Type is "Integer" or "Float", this must be a number'
            ),
            'data-parsley-defaultinchoices': (
                '#parameterForm #parameter_choices'
            ),
            'data-parsley-defaultinchoices-message': (
                'The Default Value must be one of the parameter choices'
            ),
            'step': 'any'
        }
    )
    custom_validation = StringField(
        validators=[Length(max=255)],
        description=(
            'Enter any custom validation rules'
        ),
        render_kw={
            'maxlength': '255',
        },
    )
    parameter_choices = StringField(
        validators=[Length(max=255)],
        description=(
            'If this is a "select" parameter type, enter a '
            'comma-delimited list of choices'
        ),
        render_kw={
            'maxlength': '255',
            'data-parsley-ifselect': (
                '#parameterForm #field_type option:selected'
            ),
            'data-parsley-ifselect-message': (
                'If Field Type is "Select", you must enter a list of choices'
            ),
            'data-parsley-choicestype': (
                '#parameterForm #data_type option:selected'
            ),
            'data-parsley-choicestype-message': (
                'If Data Type is "Integer" or "Float", '
                'all choices must be numbers'
            ),
            'data-parsley-validate-if-empty': 'true'
        },
    )
    sort_order = HiddenField()


class AlgorithmOutputForm(FlaskForm):
    name = StringField(
        'Output Name',
        validators=[InputRequired(), Length(max=50)],
        description='Enter a unique short name for the output (no spaces)',
        render_kw={
            'maxlength': '50',
            'data-parsley-notin': 'output',
            'data-parsley-notin-message': (
                'This value must be unique; another output has this name')
        }
    )
    original_name = HiddenField()
    display_name = StringField(
        'Display Name',
        validators=[InputRequired(), Length(max=255)],
        description='Enter a more descriptive name for the output',
        render_kw={
            'maxlength': '255',
        },
    )
    description = TextAreaField(
        render_kw={'rows': 3}
    )
    data_type = SelectField(
        choices=[
            ('string', 'String'),
            ('integer', 'Integer'),
            ('float', 'Float'),
            ('array', 'Array')
        ],
        description='Select the type of data this output will produce',
    )
    sort_order = HiddenField()
