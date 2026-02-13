#!/usr/bin/env python3
import aws_cdk as cdk
from stack import FastAPIInfrastructureStack

app = cdk.App()

FastAPIInfrastructureStack(
    app,
    "FastAPIInfrastructureStack",
    env=cdk.Environment(
    account=app.node.try_get_context("account"),
    region=app.node.try_get_context("region"),
    ),
)

app.synth()
