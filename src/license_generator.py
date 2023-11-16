import os
import pathlib
from typing import Dict, List, Tuple
from jinja2 import Template


THIS_FOLDER = pathlib.Path().resolve()
LICENSE_CLAUSES_FOLDER = THIS_FOLDER.joinpath("license-clauses")  # templates folder relative to this file
REQUIRED_FIELDS = ('attribution', 'distribution', 'warranty', 'copyright_holder',
                   'organization_name', 'scope', 'boundary')
MAX_LENGTH = 1024


def sanitize_text(text: str) -> str:
    return text.replace('\b', '').strip()[:MAX_LENGTH]  # remove backspace, limit length


def sanitize_input(form: Dict) -> Dict:
    result = {}
    for key, value in form.items():
        if '[]' in key:
            result[key.replace('[]', '')] = [sanitize_text(_) for _ in form.getlist(key)]
        else:
            result[key] = sanitize_text(value)
    return result


def check_missing_fields(form: Dict) -> List[str]:
    """
    Finds which data fields are missing
    :param form: dictionary that comes from input form
    :return: list of missing data fields
    """
    missing_keys = []
    for key in REQUIRED_FIELDS:
        temp = form.get(key)
        if temp is None:
            missing_keys.append(key)
            print(key)
    return missing_keys


def render_clause(template_file: str, context: Dict) -> str:
    """
        Render the clauses referring to the files in license-clauses
    :param template_file: file name of template, assumed to be inside LICENSE_CLAUSES_FOLDER
    :param context:
    :return:
    """

    with open(os.path.join(LICENSE_CLAUSES_FOLDER, template_file), 'r') as file:
        template_content = file.read()

    template = Template(template_content)
    rendered_content = template.render(context)

    return rendered_content


def generate_license_text(arg_form_data: Dict) -> Tuple[str, str]:
    """
    Generate the license text from provided form data
    :param arg_form_data: dictionary that contains form data
    :return: tuple with two strings - license and human-readable license
    """

    license_text = "SOFTWARE LICENSE AGREEMENT\n\n"

    # license_text += render_template('attribution-copyright-holder.txt', copyright_holder=copyrightholder)
    license_text += render_clause('license-header.txt', arg_form_data)
    license_text += render_clause('definitions.txt', arg_form_data)
    human_readable_license = '\t1. The Copyright holder is ' + arg_form_data['organization_name'] + '\n'

    # get the scope
    scope = ""
    for x in arg_form_data['scope']:
        scope += "\n\t\t o " + x

    arg_form_data['scope'] = scope

    human_readable_license += '\t3. The Scope of this license extends to the' + scope + "\n"
    license_text += render_clause('scope.txt', arg_form_data)

    # Attribution conditions
    if arg_form_data['attribution'] == 'noat':
        human_readable_license += '\t2. No reference to maintainers\n'
        license_text += render_clause('attribution-none.txt', arg_form_data)
    elif arg_form_data['attribution'] == 'copyat':
        human_readable_license += '\t2. Attribution is to be given to ' + arg_form_data[
            'copyright_holder'] + '\n'
        license_text += render_clause('attribution-authors.txt', arg_form_data)
    elif arg_form_data['attribution'] == 'orgat':
        human_readable_license += '\t2. Attribution to this project in ' + arg_form_data['organization_name'] + '\n'
        license_text += render_clause('attribution-org-project.txt', arg_form_data)

    # Redistribution
    if arg_form_data['distribution'] == 'noredist':
        human_readable_license += "\t3. No restribution is allowed\n"
        license_text += render_clause('dist-none.txt', arg_form_data)
    elif arg_form_data['distribution'] == 'allowredist':
        human_readable_license += "\t3. Redistribution allowed\n"
        license_text += render_clause('dist-allow.txt', arg_form_data)
    elif arg_form_data['distribution'] == 'centralredist':
        human_readable_license += "\t3. Redistribution through central project only \n"
        license_text += render_clause('dist-central.txt', arg_form_data)

    # boundary conditions
    if arg_form_data['boundary'] == 'orgonly':
        human_readable_license += "\t4. Distribution is allowed to this organization and employees only\n"
        license_text += render_clause('boundary-org.txt', arg_form_data)
    elif arg_form_data['boundary'] == 'orgsubs':
        human_readable_license += "\t4. Distribution is allowed to this organization and subsidaries only\n"
        license_text += render_clause('boundary-org-subs.txt', arg_form_data)
    elif arg_form_data['boundary'] == 'orgsubsvend':
        human_readable_license += "\t4. Distribution is allowed to this organization, subsidaries and contracted vendors\n"
        license_text += render_clause('boundary-org-subs-vends.txt', arg_form_data)

    # warrenty clauses
    if arg_form_data['warranty'] == 'asis':
        human_readable_license += '\t5. No Warranty is Provided\n'
        license_text += render_clause('warranty-as-is.txt', arg_form_data)
    elif arg_form_data['warranty'] == 'security':
        human_readable_license += '\t5. Critical Security fixes will be provided\n'
        license_text += render_clause('warranty-security-fixes.txt', arg_form_data)
    elif arg_form_data['warranty'] == 'bug':
        human_readable_license += '\t5. Critical Bug fixes will be supported\n'
        license_text += render_clause('warranty-bug-fixes.txt', arg_form_data)

    # Innersource authorizing body
    if arg_form_data['authbody'] == 'Other':
        arg_form_data['authbody'] = arg_form_data['Authbody_name']
    elif arg_form_data['authbody'] == 'ISC':
        arg_form_data['authbody'] = 'Inner Source Committee' 
    elif arg_form_data['authbody'] == 'OSPO':
        arg_form_data['authbody'] = 'OSPO' 

    human_readable_license += '\t6. All exceptions will esculated to ' + arg_form_data['authbody'] + '\n'
    license_text += render_clause('authorizing-body.txt', arg_form_data)

    return license_text, human_readable_license
