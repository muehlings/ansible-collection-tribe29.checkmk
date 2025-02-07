# Copyright: (c) 2023, Lars Getwan <lars.getwan@checkmk.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
    name: hosts
    author: Lars Getwan (@lgetwan)
    version_added: "3.3.0"
    short_description: Get various information about a host
    description:
      - Returns a list of subhosts
      - Returns a list of hosts of the host
    options:
      effective_attributes:
        description: show all effective attributes on hosts
        type: boolean
        required: False
        default: False
      server_url:
        description: URL of the Checkmk server
        required: True
      site:
        description: site name
        required: True
      automation_user:
        description: automation user for the REST API access
        required: True
      automation_secret:
        description: automation secret for the REST API access
        required: True
      validate_certs:
        description: Wether or not to validate TLS cerificates
        type: boolean
        required: False
        default: True
"""

EXAMPLES = """
- name: Get all hosts
  ansible.builtin.debug:
    msg: "Host: {{ item.id }} in folder {{ item.extensions.folder }}, IP: {{ item.extensions.effective_attributes.ipaddress }}"
  loop: "{{
    lookup('checkmk.general.hosts',
        effective_attributes=True,
        server_url=my_server_url,
        site=my_site,
        automation_user=my_user,
        automation_secret=my_secret,
        validate_certs=False
        )
    }}"
  loop_control:
      label: "{{ item.id }}"
"""

RETURN = """
  _list:
    description:
      - A list of hosts and their attributes
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
        effective_attributes = self.get_option("effective_attributes")
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

        ret = []
        parameters = {
            "effective_attributes": effective_attributes,
        }

        response = json.loads(
            api.get("/domain-types/host_config/collections/all", parameters)
        )
        if "code" in response:
            raise AnsibleError(
                "Received error for %s - %s: %s"
                % (
                    response.get("url", ""),
                    response.get("code", ""),
                    response.get("msg", ""),
                )
            )
        ret.append(response.get("value"))

        return ret
