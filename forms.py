from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, RadioField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional

# Search Bar

class SearchRecipesForm(FlaskForm):
    pass

# from flask_ckeditor import CKEditorField
class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()
#     No idea what I was going to use this for LMAO

# ----------Profile-related------------------------------

class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    submit = SubmitField("Register")

class MetricsForm(FlaskForm):
    age = IntegerField("Age", validators=[NumberRange(3,120)])
    height = IntegerField("Height (inches)")
    weight = IntegerField("Weight (lbs)")
    gender = RadioField("Biological Sex", choices=[('Male'), ('Female')])
    allergies = MultiCheckboxField("Any allergies?",
        validators=[Optional()],
        choices = [('Nuts'), ('Dairy'), ('Gluten')])
    #     https://gist.github.com/ectrimble20/468156763a1389a913089782ab0f272e
    #
    # activity_lvl = RadioField("Activity level", choices=[
    #     ('Sedentary', 'Little to no activity; Sitting most of the day, with most movement coming from daily tasks such as household chores or grocery shopping'),
    #     ('Low', '3 or less hours of Exercise per week, in addition to daily tasks and chores'),
    #     ('Moderate', 'Exercise nearly every day; over 4 hours per week'),
    #     ('High', 'Intense Exercise nearly every day; or regular Exercise with a physically demanding job')])

    # skip = SubmitField('Skip for now', render_kw={'formnovalidate': True})
    submit = SubmitField("Save")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log in")


