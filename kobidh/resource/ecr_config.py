import json
from stringcase import camelcase
from troposphere.ecr import Repository, LifecyclePolicy
from .config import Config


class ECRConfig:
    """
    Contains Elastic Container Registry configuration details
    """

    def __init__(self, config: Config):
        self.config = config
        self.default_service = "web"
        self.ecr_name = f"{self.config.name}-repository"
        self.ecr = None

    def _configure(self):
        self.ecr = Repository(
            camelcase(self.ecr_name.replace("-", "_")),
            RepositoryName=f"{self.ecr_name}/{self.default_service}",  # Change to your desired repository name
            # LifecyclePolicy=LifecyclePolicy(
            #     LifecyclePolicyText=json.dumps({
            #         "rules": [
            #             {
            #                 "rulePriority": 1,
            #                 "description": "Expire untagged images after 30 days",
            #                 "selection": {
            #                     "tagStatus": "untagged",
            #                     "countType": "sinceImagePushed",
            #                     "countUnit": "days",
            #                     "countNumber": 30,
            #                 },
            #                 "action": {"type": "expire"},
            #             }
            #         ]
            #     })
            # ),
            # RepositoryPolicyText=json.dumps({
            #     "Version": "2012-10-17",
            #     "Statement": [
            #         {
            #             "Sid": "AllowPushPull",
            #             "Effect": "Allow",
            #             "Principal": {"AWS": "*"},
            #             "Action": [
            #                 "ecr:GetDownloadUrlForLayer",
            #                 "ecr:BatchGetImage",
            #                 "ecr:BatchCheckLayerAvailability",
            #                 "ecr:PutImage",
            #                 "ecr:InitiateLayerUpload",
            #                 "ecr:UploadLayerPart",
            #                 "ecr:CompleteLayerUpload",
            #             ],
            #         }
            #     ],
            # }),
        )
        self.config.template.add_resource(self.ecr)
