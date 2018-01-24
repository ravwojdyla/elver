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
    description = "build a docker image"

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
                    "as a mapping of hostname to IP address"),
            ("gen-base-image=", None, "base image for auto generated dockerfile"),
            ("gen-entry-point=", None, "entry point for generated dockefile"),
            ("gen-cmd=", None, "cmd for the generated dockerifle"),
            ("gen-do-not-copy-path", None, "if set, do not copy path to the image"),
            ("gen-path-copy-dir=", None, "name of directory in the image to copy path to"),
            ("gen-requirments-file=", None, "filename of the requirments file"),
            ("gen-do-not-install-requirments", None, "do not install pip requirments")
            ]

    boolean_options = [
            "quiet",
            "nocache",
            "rm",
            "pull",
            "forcerm",
            "squash",
            "gen-do-not-copy-path"]

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
        self.gen_base_image = None
        self.gen_entry_point = None
        self.gen_cmd = None
        self.gen_do_not_copy_path = None
        self.gen_path_copy_dir = None
        self.gen_requirments_file = None
        self.gen_do_not_install_requirments = None

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
        if self.dockerfile is None:
            self.dockerfile = "Dockerfile"
        if self.gen_base_image is None:
            self.gen_base_image = "python"
        if self.gen_do_not_copy_path is None:
            self.gen_do_not_copy_path = False
        if self.gen_path_copy_dir is None:
            self.gen_path_copy_dir = "/code"
        if self.gen_requirments_file is None:
            #TODO(rav): support all the standard names of the requirments file
            self.gen_requirments_file = "requirements.txt"
        if self.gen_do_not_install_requirments is None:
            self.gen_do_not_install_requirments = False

    def __generate_docker_file(self, dockerfile, dockerfile_generated_name=".Dockerfile-generated"):
        import os.path as path
        self.announce("Dockerfile doesn't exist at %s, generating a default one" % dockerfile)
        dockerfile_generated = path.join(self.path, dockerfile_generated_name)
        with file(dockerfile_generated, "w") as f:
            content = []
            content.append("#THIS FILE WAS GENERATED BY ELVER, DO NOT CHANGE MANUALLY\n")
            content.append("FROM %s\n" % self.gen_base_image)
            if not self.gen_do_not_copy_path:
                content.append("COPY %s %s\n" % (self.path, self.gen_path_copy_dir))
            if not self.gen_do_not_install_requirments and not self.gen_do_not_copy_path:
                req_filename = path.join(self.path, self.gen_requirments_file)
                req_filename_docker = path.join(self.gen_path_copy_dir, self.gen_requirments_file)
                if path.exists(req_filename):
                    content.append("""RUN ["pip", "install", "-r", "%s"]\n""" % req_filename_docker)
            if self.gen_entry_point:
                content.append("ENTRYPOINT %s\n" % self.gen_entry_point)
            if self.gen_cmd:
                content.append("CMD %s\n" % self.gen_cmd)
            f.writelines(content)
            f.flush()
        return dockerfile_generated_name

    def run(self):
        client = docker.from_env()

        import os.path as path
        dockerfile = path.join(self.path, self.dockerfile)
        if not path.exists(dockerfile):
            self.dockerfile = self.__generate_docker_file(dockerfile)
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
