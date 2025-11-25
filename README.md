# Overview

The purpose of this resolver is to retrieve IAM Role name from the AWS.

## Install

```shell
pip install sceptre-aws-iamrole-resolver
```
or
```shell
pip install git+https://github.com/harisfauzi/sceptre-aws-iamrole-resolver.git
```

## Available Resolvers

### aws_iamrole

Fetches the IAM ROle name from AWS with given partial name.

__Note:__ Sceptre must be run with a user or role that has access to the list IAM roles (iam:list_roles).

Syntax:

```yaml
parameter|sceptre_user_data:
  <name>: !aws_iamrole partial_role_name
```

```yaml
parameter|sceptre_user_data:
  <name>: !aws_iamrole
    name: partial_role_name
    profile: OtherAccount
```

```yaml
parameter|sceptre_user_data:
  <name>: !aws_iamrole {"name": "partial_role_name", "region": "us-east-1", "profile": "OtherAccount"}
```


#### Parameters
* name - partial role name, mandatory
* 
* region - AWS region, optional, stack region by default
* profile - AWS account profile , optional, stack profile by default

#### Example:

Retrieve the IAM Role full name given a partial name `web-Instanceiamrole`
which could return something like `web-Instanceiamrole-1WD7WGZALMECA`:
```yaml
parameters:
  iamrole: !aws_iamrole web-Instanceiamrole
```

Retrieve the IAM Role full name from another AWS account:
```yaml
parameters:
  iamroleId: !aws_iamrole
    name: TestRole
    profile: OtherAccount
```
