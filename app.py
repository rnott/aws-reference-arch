'''
Copyright 2023 Randy Nott (rnott.org)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

#!/usr/bin/env python3
import os
import dotenv

from aws_cdk import App, Environment

from reference_arch.reference_arch_stack import ReferenceArchStack

dotenv.load_dotenv()
app = App()
account = os.getenv('CDK_DEFAULT_ACCOUNT')
region = os.getenv('CDK_DEFAULT_REGION')
ReferenceArchStack(app, "ReferenceArchStack",
    # specialize this stack for the AWS Account
    # and Region that are implied by the current CLI configuration.
    env = Environment(account=account, region=region),

    # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
    )

app.synth()
