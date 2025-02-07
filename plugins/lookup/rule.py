# Copyright: (c) 2023, Lars Getwan <lars.getwan@checkmk.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
    name: rule
    author: Lars Getwan (@lgetwan)
    version_added: "3.5.0"
    short_description: Show rule
    description:
      - Returns details of a rule
    options:
      rule_id:
        description: The rule id.
        required: True
      server_url:
        description: URL of the Checkmk server.
        required: True
      site:
        description: Site name.
        required: True
      automation_user:
        description: Automation user for the REST API access.
        required: True
      automation_secret:
        description: Automation secret for the REST API access.
        required: True
      validate_certs:
        description: Whether or not to validate TLS cerificates.
        type: boolean
        required: False
        default: True
"""

EXAMPLES = """
- name: Get a rule with a particular rule id
  ansible.builtin.debug:
    msg: "Rule: {{ extensions }}"
  vars:
    extensions: "{{
      lookup('checkmk.general.rule',
        rule_id='a9285bc1-dcaf-45e0-a3ba-ad398ef06a49',
        server_url=server_url,
        site=site,
        automation_user=automation_user,
        automation_secret=automation_secret,
        validate_certs=False
      )
    }}"
"""

RETURN = """
  _list:
    description:
      - The details of a particular rule
    type: list
    elements: str
"""

import json

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible_collections.checkmk.general.plugins.module_utils.lookup_api import (
    CheckMKLookupAPI,
)


class LookupModule(LookupBase):
    def run(self, terms, variables, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)
        rule_id = self.get_option("rule_id")
        server_url = self.get_option("server_url")
        site = self.get_option("site")
        user = self.get_option("automation_user")
        secret = self.get_option("automation_secret")
        validate_certs = self.get_option("validate_certs")

        site_url = server_url + "/" + site

        api = CheckMKLookupAPI(
            site_url=site_url,
            user=user,
            secret=secret,
            validate_certs=validate_certs,
        )

        response = json.loads(api.get("/objects/rule/" + rule_id))

        if "code" in response:
            raise AnsibleError(
                "Received error for %s - %s: %s"
                % (
                    response.get("url", ""),
                    response.get("code", ""),
                    response.get("msg", ""),
                )
            )

        return [response.get("extensions", {})]
