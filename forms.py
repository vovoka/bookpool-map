from wtforms import Form, StringField, SelectField

class BookSearchForm(Form):
    choices = [('Title', 'Title'),
               ('Author', 'Author'),
               ('Tag', 'Tag')]
    select = SelectField('Search for books:', choices=choices)
    search = StringField('')
