# -*- coding: utf-8 -*-

import abc
import six
import logging

from botocore.exceptions import ClientError
from sceptre.resolvers import Resolver
from resolver.aws_iamrole_exceptions import IAMRoleNotFoundError

TEMPLATE_EXTENSION = ".yaml"


@six.add_metaclass(abc.ABCMeta)
class AwsIAMRoleBase(Resolver):
    """
    A abstract base class which provides methods for getting IAM Role Name.
    """

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(__name__)
        super(AwsIAMRoleBase, self).__init__(*args, **kwargs)

    def _get_iam_role_name(self, role_name, path_prefix='/', region='us-east-1', profile=None):
        """
        Attempts to get the IAM Role Name with tag:Name by ``param``
        :param role_name: The partial role name of the IAM Role in which to return.
        :type param: string
        :param path_prefix: The path prefix of the role to look for (optional).
        :type param: string
        :returns: IAM Role name.
        :rtype: str
        :raises: KeyError
        """
        response_roles = self._request_iam_role(path_prefix, region, profile)
        if response_roles is None or response_roles == []:
            self.logger.error(
                "%s - No IAM Roles found looking for: %s", self.stack.name, role_name
            )
            raise IAMRoleNotFoundError(
                "No IAM Roles found with name: {0}".format(role_name)
            )

        try:
            self.logger.debug("Got response_roles: {0}".format(response_roles))
            for role in response_roles:
                self.logger.debug("Checking role: {0}".format(role))
                if role["Path"] == path_prefix and role_name in role["RoleName"]:
                    return role["RoleName"]
        except KeyError:
            self.logger.error(
                "%s - Invalid response looking for: %s", self.stack.name, role_name
            )
            raise

    def _request_iam_role(self, path_prefix, region, profile=None):
        """
        Communicates with AWS IAM to fetch IAM Role Information.
        :returns: The list of IAM Roles in JSON block
        :rtype: dict
        :raises: resolver.exceptions.IAMRoleNotFoundError
        """
        connection_manager = self.stack.connection_manager
        region_arg = 'us-east-1'
        response_roles = []
        max_items = 100
        try:
            self.logger.debug("Calling iam.list_roles")
            kwargs = {"PathPrefix": path_prefix, "MaxItems": max_items}
            response = connection_manager.call(
                service="iam",
                command="list_roles",
                kwargs=kwargs,
                region=region_arg,
                profile=profile,
            )
            response_roles = response.get("Roles", [])
            is_truncated = response.get("IsTruncated", False)
            while is_truncated:
                marker = response.get("Marker")
                kwargs = {"PathPrefix": path_prefix, "Marker": marker, "MaxItems": max_items}
                response = connection_manager.call(
                    service="iam",
                    command="list_roles",
                    kwargs=kwargs,
                    region=region_arg,
                    profile=profile,
                )
                response_roles = response_roles + response.get("Roles", [])
                is_truncated = response.get("IsTruncated", False)
            self.logger.debug("Finished calling iam.list_roles")
        except ClientError as e:
            if "IAMRoleNotFound" in e.response["Error"]["Code"]:
                self.logger.error(
                    "%s - IAMRoleNotFound: %s", self.stack.name, kwargs
                )
                raise IAMRoleNotFoundError(e.response["Error"]["Message"])
            else:
                raise e
        except Exception as err:
            print(f"Unexpected {err}, {type(err)}")
            raise
        else:
            return response_roles


class AwsIAMRole(AwsIAMRoleBase):
    """
    Resolver for retrieving the value of IAM Role Name.
    :param argument: The partial IAM Role name to get.
    :type argument: str
    """

    def __init__(self, *args, **kwargs):
        super(AwsIAMRole, self).__init__(*args, **kwargs)

    def resolve(self):
        """
        Retrieves the value of IAM Role info
        :returns: The IAM Role name.
        :rtype: str
        """
        args = self.argument
        if not args:
            raise ValueError("Missing argument")

        instance_id = None
        self.logger.debug(
            "Resolving IAM Role with argument: {0}".format(args)
        )
        name = self.argument
        region = self.stack.region
        profile = self.stack.profile
        role_name = name
        path_prefix = '/'
        if isinstance(args, dict):
            if "name" in args:
                role_name = args["name"]
            else:
                raise ValueError("Missing Role name filter")
            if "prefix" in args:
                path_prefix = args["prefix"]
            profile = args.get("profile", profile)
            region = args.get("region", region)
        self.logger.debug("Resolving IAM Role with name pattern: {0}".format(name))
        instance_id = self._get_iam_role_name(role_name, path_prefix, region, profile)
        return instance_id
