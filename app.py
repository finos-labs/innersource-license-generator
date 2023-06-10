from flask import Flask, render_template, request, send_file, session
from jinja2 import Template
import textwrap
import io
import os
import jinja2

app = Flask(__name__)
app.secret_key = os.urandom(24)



# Render the clauses referring to the files in license-clauess
def render_clause(template_path, context):

    if not os.path.exists(template_path):
        return render_template('error.html', message='Invalid template path.')

    with open(template_path, 'r') as file:
        template_content = file.read()

    template = Template(template_content)
    rendered_content = template.render(context)
    #rendered_content = '\n'.join(wrapped_text)

    return rendered_content


# generate the license text
def generate_license_text(arg_form_data):
    license_text = "SOFTWARE LICENSE AGREEMENT\n\n"

    #license_text += render_template('attribution-copyright-holder.txt', copyright_holder=copyrightholder)
    license_text += render_clause('license-clauses/license-header.txt', arg_form_data)
    license_text += render_clause('license-clauses/definitions.txt', arg_form_data)
    human_readable_license = '\t1. The Copyright holder is ' + arg_form_data['organization']+ '\n'

    
    # get the scope
    scope = ""
    for x in arg_form_data['scope']:
        scope += "\n\t\t o " + x

    arg_form_data['scope'] = scope

    human_readable_license += '\t3. The Scope of this license extends to the' + scope + "\n"
    license_text += render_clause('license-clauses/scope.txt', arg_form_data)

    # Attribution conditions
    if arg_form_data['attribution'] == 'noat':
        human_readable_license += '\t2. No Attribution is given to author\n'
        license_text += render_clause('license-clauses/attribution-none.txt', arg_form_data)
    elif arg_form_data['attribution'] == 'copyat':
        human_readable_license += '\t2. Attribution is to be givem to ' + arg_form_data['copyrightholder'] + ' on redistribution\n'
        license_text += render_clause('license-clauses/attribution-copyright-holder.txt', arg_form_data)
    elif arg_form_data['attribution'] == 'orgat':
        human_readable_license += '\t2. Attribution only to the orgnization ' + arg_form_data['orgnization']
        license_text += "Attribution: to Organiztion\n"

    # Redistribution
    if arg_form_data['distribution'] == 'noredist':
        human_readable_license += "\t3. No restribution is allowed\n"
        license_text += render_clause('license-clauses/dist-none.txt', arg_form_data)
    elif arg_form_data['distribution'] == 'allowredist':
        human_readable_license += "\t3. Redistribution allowed\n"
        license_text += render_clause('license-clauses/dist-allow.txt', arg_form_data)
    elif arg_form_data['distribution'] == 'centralredist':
        human_readable_license += "\t3. Redistribution through central project only \n"
        license_text += render_clause('license-clauses/dist-central.txt', arg_form_data)

    # boundary conditions
    if arg_form_data['boundary'] == 'orgonly':
        human_readable_license += "\t4. Distribution is allowed to this organization and employees only\n"
        license_text += render_clause('license-clauses/boundary-org.txt', arg_form_data)
    elif arg_form_data['boundary'] == 'orgsubs':
        human_readable_license += "\t4. Distribution is allowed to this organization and subsidaries only\n"
        license_text += render_clause('license-clauses/boundary-org-subs.txt', arg_form_data)
    elif arg_form_data['boundary'] == 'orgsubsvend':
        human_readable_license += "\t4. Distribution is allowed to this organization, subsidaries and contracted vendors\n"
        license_text += render_clause('license-clauses/boundary-org-subs-vends.txt', arg_form_data)


    if arg_form_data['warranty'] == 'asis':
        human_readable_license += '\t5. No Warrenty is Provided'
        license_text += render_clause('license-clauses/warrenty-as-is.txt', arg_form_data)
    elif arg_form_data['warranty'] == '\tX. A 30 day internal Warrenty is provided':
        human_readable_license += '\t5. A 30 day Warrent is Provided'
        license_text += "Warranty: 30-day warranty\n"

    return license_text, human_readable_license


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate_license', methods=['POST'])
def generate_license():
    # Validate input data
    if not request.form or not all(key in request.form for key in ('attribution', 'distribution', 'warranty', 'copyright_holder', 'organization_name', 'scope[]', 'boundary')):
        return render_template('error.html', message='Invalid form data.')

    # Sanitize input data
    form_data = {
        'attribution' : request.form.get('attribution').strip(),
        'distribution' : request.form.get('distribution').strip(),
        'warranty' : request.form.get('warranty').strip(),
        'copyrightholder' : request.form.get('copyright_holder').strip(),
        'organization' : request.form.get('organization_name').strip(),
        'scope' : [x.strip() for x in request.form.getlist('scope[]')],
        'boundary' : request.form.get('boundary').strip()
    }

    # Validate scope data
    for x in form_data['scope']:
        if not x:
            return render_template('error.html', message='Invalid scope data.')
        print(x)
 
    license_text, human_readable_license = generate_license_text(form_data)
    session['form_data'] = form_data

    clauses_text = human_readable_license

    return render_template('result.html', clauses_text=clauses_text, license_text=license_text)

@app.route('/download')
def download_text_file():

    form_data = session.get('form_data', 'no data found')
    content, human_readable_text = generate_license_text(form_data) 
    filename = "License.md"

    # Create an in-memory file-like object
    file_obj = io.BytesIO()
    file_obj.write(content.encode('utf-8'))
    file_obj.seek(0)  # Move the file position to the beginning

    return send_file(
        file_obj,
        mimetype='text/plain',
        as_attachment=True,
        attachment_filename=filename
    )

app.route('/download_license')
def download_license():
    return send_file('license.pdf', as_attachment=True, attachment_filename='license.pdf')


if __name__ == '__main__':
    app.run(debug=True)
