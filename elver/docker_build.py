# -*- coding: utf-8 -*-
#
#  Copyright 2018 Rafal Wojdyla.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing,
#  software distributed under the License is distributed on an
#  "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#  KIND, either express or implied.  See the License for the
#  specific language governing permissions and limitations
#  under the License.

# TODO(rav): should this optionally support setuptools.command.*

from distutils.core import Command
import docker 

class docker_build(Command):
    description = "build docker image"

    user_options = [
            ("path=", "p", "path to the directory containing the Dockerfile"),
            ("dockerfile=", None, "path within the build context to the Dockerfile"),
            ("repository=", None, "repository of the image"),
            ("tag=", "t", "a tag to add to the final image"),
            ("quiet", "q", "whether to return the status"),
            ("nocache", None, "don’t use the cache"),
            ("rm", None, "remove intermediate containers, defaults to False"),
            ("timeout=", None, "HTTP timeout"),
            ("pull", None, "downloads any updates to the FROM image in Dockerfiles"),
            ("forcerm", None,
                "always remove intermediate containers, even after unsuccessful builds"),
            ("buildargs=", None, "a dictionary of build arguments"),
            ("container-limits=", None,
            "a dictionary of limits applied to each container created by the build process." \
            " Valid keys: memory (set memory limit for build), memswap (total memory"\
            " (memory + swap), -1 to disable swap), cpushares (CPU shares (relative weight))," \
            " cpusetcpus (CPUs in which to allow execution, e.g., '0-3', '0,1' "),
            ("shmsize=", None, "size of /dev/shm in bytes. The size must be greater than 0. " \
                    "If omitted the system uses 64MB"),
            ("labels=", None, "a dictionary of labels to set on the image"),
            ("cache-from=", None, "a list of images used for build cache resolution"),
            ("target=", None, "name of the build-stage to build in a multi-stage Dockerfile"),
            ("network-mode=", None, "networking mode for the run commands during build"),
            ("squash", None, "squash the resulting images layers into a single layer"),
            ("extra-hosts=", None, "extra hosts to add to /etc/hosts in building containers, " \
                    "as a mapping of hostname to IP address")
            ]

    boolean_options = ["quiet", "nocache", "rm", "pull", "forcerm", "squash"]

    def initialize_options(self):
        self.path = None
        self.dockerfile = None
        self.repository = None
        self.tag = None
        self.quiet = None
        self.nocache = None
        self.rm = False
        self.timeout = None
        self.pull = None
        self.forcerm = None
        self.buildargs = None
        self.container_limits = None
        self.shmsize = None
        self.labels = None
        self.cache_from = None
        self.target = None
        self.network_mode = None
        self.squash = None
        self.extra_hosts = None

    def finalize_options(self):
        if self.repository is None:
            import uuid
            repository = uuid.uuid1()
            self.announce("Using a random repository %s" % repository)
            self.repository = repository
        if self.tag is None:
            self.tag = "latest"
        if self.path is None:
            self.path = "."

    def run(self):
        client = docker.from_env()
        img = client.images.build(
                path=self.path,
                dockerfile=self.dockerfile,
                tag="%s:%s" % (self.repository, self.tag),
                quiet=self.quiet,
                nocache=self.nocache,
                rm=self.rm,
                timeout=self.timeout,
                pull=self.pull,
                forcerm=self.forcerm,
                container_limits=self.container_limits,
                shmsize=self.shmsize,
                labels=self.labels,
                cache_from=self.cache_from,
                target=self.target,
                network_mode=self.network_mode,
                squash=self.squash,
                extra_hosts=self.extra_hosts
                )
        self.announce("Image built: %s" % img)
