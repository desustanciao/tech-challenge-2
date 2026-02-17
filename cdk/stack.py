
from aws_cdk import (
    CfnOutput,
    Duration,
    IgnoreMode,
    RemovalPolicy,
    Stack,
)
from aws_cdk import (
    aws_ec2 as ec2,
)
from aws_cdk import (
    aws_ecr_assets as ecr_assets,
)
from aws_cdk import (
    aws_ecs as ecs,
)
from aws_cdk import (
    aws_ecs_patterns as ecs_patterns,
)
from aws_cdk import (
    aws_iam as iam,
)
from aws_cdk import (
    aws_logs as logs,
)
from aws_cdk import (
    aws_rds as rds,
)
from aws_cdk import (
    aws_secretsmanager as secretsmanager,
)
from constructs import Construct


class FastAPIInfrastructureStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(
            self,
            "AppVPC",
            max_azs=2,
            nat_gateways=0,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                ),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24
                )
            ],
        )


        # Build Docker image from local app directory
        image_asset = ecr_assets.DockerImageAsset(
            self,
            "FastAPIDockerImage",
            directory="./../",  # path to Dockerfile
            asset_name="FastAPIDockerImage",
            exclude=["*test*","cdk/*",".git*",".venv/*"],
            ignore_mode=IgnoreMode.DOCKER,
            target="production"
        )

        db_secret = secretsmanager.Secret(
            self,
            "DBSecret",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template='{"username":"postgres"}',
                generate_string_key="password",
                exclude_punctuation=True,
            ),
        )

        secret_key_secret = secretsmanager.Secret(
            self,
            "JwtSecretKey",
            secret_name="fastapi/jwt/secret-key",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                password_length=64,
                exclude_punctuation=True,
            ),
        )

        ecs_sg = ec2.SecurityGroup(
            self,
            "ECSSecurityGroup",
            vpc=vpc,
            allow_all_outbound=True,
        )

        rds_sg = ec2.SecurityGroup(
            self,
            "RDSSecurityGroup",
            vpc=vpc,
            allow_all_outbound=True,
        )

        rds_sg.add_ingress_rule(
            peer=ecs_sg,
            connection=ec2.Port.tcp(5432),
            description="Allow ECS to access RDS",
        )

        db_instance = rds.DatabaseInstance(
            self,
            "PostgresDB",
            engine=rds.DatabaseInstanceEngine.postgres(version=rds.PostgresEngineVersion.VER_17),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3,
                ec2.InstanceSize.MICRO,
            ),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
            multi_az=False,
            allocated_storage=20,
            max_allocated_storage=20,
            credentials=rds.Credentials.from_secret(db_secret),
            publicly_accessible=False,
            security_groups=[rds_sg],
            removal_policy=RemovalPolicy.DESTROY,
            deletion_protection=False,
            database_name="appdb",
            AllowMajorVersionUpgrade=True,
        )

        cluster = ecs.Cluster(
            self,
            "AppCluster",
            vpc=vpc,
        )

        task_role = iam.Role(
            self,
            "AppTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
        )

        db_secret.grant_read(task_role)
        secret_key_secret.grant_read(task_role)

        log_group = logs.LogGroup(
            self,
            "AppLogGroup",
            retention=logs.RetentionDays.ONE_DAY,
            removal_policy=RemovalPolicy.DESTROY,
        )

        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "FastAPIService",
            cluster=cluster,
            cpu=256,
            memory_limit_mib=512,
            desired_count=1,
            public_load_balancer=True,
            assign_public_ip=True,
            task_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC  # 👈 ADD THIS
            ),
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_docker_image_asset(image_asset),
                container_port=8000,
                task_role=task_role,
                environment={
                    "DATABASE_HOST": db_instance.db_instance_endpoint_address,
                    "DATABASE_NAME": "appdb",
                },
                secrets={
                    "DATABASE_USER": ecs.Secret.from_secrets_manager(db_secret, "username"),
                    "DATABASE_PASSWORD": ecs.Secret.from_secrets_manager(db_secret, "password"),
                    "SECRET_KEY": ecs.Secret.from_secrets_manager(secret_key_secret)
                },
                log_driver=ecs.LogDriver.aws_logs(
                    stream_prefix="fastapi",
                    log_group=log_group,
                ),
            ),
            security_groups=[ecs_sg],
        )

        scaling = fargate_service.service.auto_scale_task_count(
            min_capacity=1,
            max_capacity=4,
        )

        scaling.scale_on_cpu_utilization(
            "CpuScaling",
            target_utilization_percent=70,
        )

        fargate_service.target_group.configure_health_check(
            path="/health/live",
            healthy_http_codes="200",
            interval=Duration.seconds(30),
        )

        CfnOutput(
            self,
            "LoadBalancerURL",
            value=f"http://{fargate_service.load_balancer.load_balancer_dns_name}",
        )

        CfnOutput(
            self,
            "ECRRepositoryURI",
            value=image_asset.repository.repository_uri,
        )
