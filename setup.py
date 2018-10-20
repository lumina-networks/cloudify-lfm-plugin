#########
# Copyright (c) 2018 Lumina Communcation Systems Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  * See the License for the specific language governing permissions and
#  * limitations under the License.

from setuptools import setup
# from setuptools import find_packages

setup(

    # Do not use underscores in the plugin name.
    name='cloudify-lfm-plugin',
    version='0.1.0',
    author='Lumina Networks',
    author_email='oss-dev@luminanetworks.com',
    url="https://github.com/luminanetworks/cloudify-lfm-plugin",
    description='A Cloudify Plugin that provisions services in Lumina Flow Manager',
    long_description=open('README.md').read(),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    # This must correspond to the actual packages in the plugin.
    # packages=find_packages(exclude=['tests*']),
    packages=[
        'cloudify_fm',
        'cloudify_fm.common',
    ],
    license='LICENSE',
    zip_safe=False,
    install_requires=[
        'lfmcli>=2.0.0',
        'cloudify-plugins-common==4.3.1',  # latest: >=4.4
        'requests==2.19.1',
        'Cerberus==1.2'
        # 'cloudify-dsl-parser==4.3.1',
        # 'cloudify-rest-client==4.3.1',
        # 'cloudify-plugins-common==4.3.1'
    ],
    # test_requires=[
    #     'cloudify-common>=4.4',
    #     # 'cloudify-plugins-common>=4.3',
    #     'pyyaml',
    #     'nose',
    #     'requests'
    # ]
)
