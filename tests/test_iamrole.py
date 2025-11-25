# -*- coding: utf-8 -*-

import pytest
from mock import MagicMock, patch, sentinel

from botocore.exceptions import ClientError

from sceptre.connection_manager import ConnectionManager
from sceptre.stack import Stack

from resolver.aws_iamrole import AwsIAMRole, AwsIAMRoleBase
from resolver.aws_iamrole_exceptions import IAMRoleNotFoundError


region = "us-east-1"


class TestIAMRoleResolver(object):
    def test_resolve_str_arg_no_param_name(self):
        stack = MagicMock(spec=Stack)
        stack.name = "test_stack"
        stack.profile = "test_profile"
        stack.dependencies = []
        stack._connection_manager = MagicMock(spec=ConnectionManager)
        stack_iam_role_resolver = AwsIAMRole(None, stack)
        with pytest.raises(ValueError):
            stack_iam_role_resolver.resolve()

    def test_resolve_obj_arg_no_param_name(self):
        stack = MagicMock(spec=Stack)
        stack.name = "test_stack"
        stack.profile = "test_profile"
        stack.dependencies = []
        stack._connection_manager = MagicMock(spec=ConnectionManager)
        stack_iam_role_resolver = AwsIAMRole({}, stack)
        with pytest.raises(ValueError):
            stack_iam_role_resolver.resolve()

    @patch("resolver.aws_iamrole.AwsIAMRole._get_iam_role_name")
    def test_resolve_str_arg(self, mock_get_iam_role_name):
        stack = MagicMock(spec=Stack)
        stack.name = "test_stack"
        stack.profile = "test_profile"
        stack.region = region
        stack.dependencies = []
        stack._connection_manager = MagicMock(spec=ConnectionManager)
        stack_iam_role_resolver = AwsIAMRole(
            "web-InstanceRole", stack
        )
        mock_get_iam_role_name.return_value = "web-InstanceRole-1WD7WGZALMECA"
        stack_iam_role_resolver.resolve()
        mock_get_iam_role_name.assert_called_once_with(
            "web-InstanceRole",
            "/",
            region,
            "test_profile",
        )

    @patch("resolver.aws_iamrole.AwsIAMRole._get_iam_role_name")
    def test_resolve_obj_arg_no_profile(self, mock_get_iam_role_name):
        stack = MagicMock(spec=Stack)
        stack.name = "test_stack"
        stack.profile = "test_profile"
        stack.region = region
        stack.dependencies = []
        stack._connection_manager = MagicMock(spec=ConnectionManager)
        stack_iam_role_resolver = AwsIAMRole(
            {"name": "web-InstanceRole"}, stack
        )
        mock_get_iam_role_name.return_value = "web-InstanceRole-1WD7WGZALMECA"
        stack_iam_role_resolver.resolve()
        mock_get_iam_role_name.assert_called_once_with(
            "web-InstanceRole",
            "/",
            region,
            "test_profile",
        )

    @patch("resolver.aws_iamrole.AwsIAMRole._get_iam_role_name")
    def test_resolve_name_tags_self_arg_no_profile(self, mock_get_iam_role_name):
        stack = MagicMock(spec=Stack)
        stack.name = "test_stack"
        stack.profile = "test_profile"
        stack.region = region
        stack.dependencies = []
        stack._connection_manager = MagicMock(spec=ConnectionManager)
        stack_iam_role_resolver = AwsIAMRole(
            {
                "name": "web-InstanceRole"
            },
            stack,
        )
        mock_get_iam_role_name.return_value = "web-InstanceRole-1WD7WGZALMECA"
        stack_iam_role_resolver.resolve()
        mock_get_iam_role_name.assert_called_once_with(
            "web-InstanceRole",
            "/",
            region,
            "test_profile",
        )

    @patch("resolver.aws_iamrole.AwsIAMRole._get_iam_role_name")
    def test_resolve_name_prefix_self_arg_no_profile(self, mock_get_iam_role_name):
        stack = MagicMock(spec=Stack)
        stack.name = "test_stack"
        stack.profile = "test_profile"
        stack.region = region
        stack.dependencies = []
        stack._connection_manager = MagicMock(spec=ConnectionManager)
        stack_iam_role_resolver = AwsIAMRole(
            {
                "name": "web-InstanceRole",
                "prefix": "/custom/prefix/"
            },
            stack,
        )
        mock_get_iam_role_name.return_value = "web-InstanceRole-1WD7WGZALMECA"
        stack_iam_role_resolver.resolve()
        mock_get_iam_role_name.assert_called_once_with(
            "web-InstanceRole",
            "/custom/prefix/",
            region,
            "test_profile",
        )

    @patch("resolver.aws_iamrole.AwsIAMRole._get_iam_role_name")
    def test_resolve_obj_arg_profile_override(self, mock_get_iam_role_name):
        stack = MagicMock(spec=Stack)
        stack.name = "test_stack"
        stack.profile = "test_profile"
        stack.region = region
        stack.dependencies = []
        stack._connection_manager = MagicMock(spec=ConnectionManager)
        stack_iam_role_resolver = AwsIAMRole(
            {
                "name": "web-InstanceRole",
                "profile": "new_profile",
            },
            stack,
        )
        mock_get_iam_role_name.return_value = "web-InstanceRole-1WD7WGZALMECA"
        stack_iam_role_resolver.resolve()
        mock_get_iam_role_name.assert_called_once_with(
            "web-InstanceRole",
            "/",
            region,
            "new_profile",
        )

    @patch("resolver.aws_iamrole.AwsIAMRole._get_iam_role_name")
    def test_resolve_obj_arg_region_override(self, mock_get_iam_role_name):
        stack = MagicMock(spec=Stack)
        stack.name = "test_stack"
        stack.profile = "test_profile"
        stack.region = region
        stack.dependencies = []
        stack._connection_manager = MagicMock(spec=ConnectionManager)

        custom_region = "ap-southeast-1"
        assert custom_region != region

        stack_iam_role_resolver = AwsIAMRole(
            {
                "name": "web-InstanceRole",
                "region": custom_region,
                "profile": "new_profile",
            },
            stack,
        )
        mock_get_iam_role_name.return_value = "web-InstanceRole-1WD7WGZALMECA"
        stack_iam_role_resolver.resolve()
        mock_get_iam_role_name.assert_called_once_with(
            "web-InstanceRole",
            "/",
            custom_region,
            "new_profile",
        )


class MockAwsIAMRoleBase(AwsIAMRoleBase):
    """
    MockBaseResolver inherits from the abstract base class
    AwsIAMRoleBase, and implements the abstract methods. It is used
    to allow testing on AwsIAMRoleBase, which is not otherwise
    instantiable.
    """

    def __init__(self, *args, **kwargs):
        super(MockAwsIAMRoleBase, self).__init__(*args, **kwargs)

    def resolve(self):
        pass


class TestAwsIAMRoleBase(object):
    def setup_method(self, test_method):
        self.stack = MagicMock(spec=Stack)
        self.stack.name = "test_name"
        self.stack._connection_manager = MagicMock(spec=ConnectionManager)
        self.base_iam_role = MockAwsIAMRoleBase(None, self.stack)

    @patch("resolver.aws_iamrole.AwsIAMRoleBase._request_iam_role")
    def test_get_iam_role_name_with_valid_name(self, mock_request_iam_role):
        mock_request_iam_role.return_value = [
            {
                "Path": "/",
                "RoleName": "web-InstanceRole-1WD7WGZALMECA",
                "RoleId": "AROAR6211111111111111",
                "Arn": "arn:aws:iam::111111111111:role/web-InstanceRole-1WD7WGZALMECA",
                "CreateDate": "2023-04-27T00:42:11Z",
                "AssumeRolePolicyDocument": {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {
                                "Service": "ec2.amazonaws.com"
                            },
                            "Action": "sts:AssumeRole"
                        }
                    ]
                },
                "MaxSessionDuration": 3600
            }
        ]

        response = self.base_iam_role._get_iam_role_name(
            "web-InstanceRole", "/", region
        )
        assert response == "web-InstanceRole-1WD7WGZALMECA"

    @patch("resolver.aws_iamrole.AwsIAMRoleBase._request_iam_role")
    def test_get_iam_role_name_with_valid_pattern(self, mock_request_iam_role):
        mock_request_iam_role.return_value = [
            {
                "Path": "/",
                "RoleName": "web-InstanceRole-1WD7WGZALMECA",
                "RoleId": "AROAR6211111111111111",
                "Arn": "arn:aws:iam::111111111111:role/web-InstanceRole-1WD7WGZALMECA",
                "CreateDate": "2023-04-27T00:42:11Z",
                "AssumeRolePolicyDocument": {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {
                                "Service": "ec2.amazonaws.com"
                            },
                            "Action": "sts:AssumeRole"
                        }
                    ]
                },
                "MaxSessionDuration": 3600
            }
        ]

        response = self.base_iam_role._get_iam_role_name(
            "web-InstanceRole", "/", region
        )
        assert response == "web-InstanceRole-1WD7WGZALMECA"

    @patch("resolver.aws_iamrole.AwsIAMRoleBase._request_iam_role")
    def test_get_iam_role_name_with_invalid_response(
        self, mock_request_iam_role
    ):
        mock_request_iam_role.return_value = [
            {
                "CreateDate": "2023-04-27T00:42:11Z",
                "MaxSessionDuration": 3600
            }
        ]

        with pytest.raises(KeyError):
            self.base_iam_role._get_iam_role_name(None, region)

    def test_request_iam_role_with_unkown_boto_error(self):
        self.stack.connection_manager.call.side_effect = ClientError(
            {"Error": {"Code": "500", "Message": "Boom!"}}, sentinel.operation
        )

        with pytest.raises(ClientError):
            self.base_iam_role._request_iam_role(None, region)

    def test_request_iam_role_with_iam_role_not_found(self):
        self.stack.connection_manager.call.side_effect = ClientError(
            {"Error": {"Code": "IAMRoleNotFound", "Message": "Boom!"}},
            sentinel.operation,
        )

        with pytest.raises(IAMRoleNotFoundError):
            self.base_iam_role._request_iam_role(None, region)
