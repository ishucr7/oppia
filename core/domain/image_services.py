# coding: utf-8
#
# Copyright 2014 The Oppia Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Service for managing operations on images."""

from core.domain import fs_domain
from core.platform import models
import feconf

gae_image_services = models.Registry.import_gae_image_services()


def get_image_dimensions(filename, exp_id):
    """Gets the dimensions of the image with the given filename

    Args:
        filename: str. The filename of the image in exploration.
        exp_id: str. ID of the exploration.

    Returns:
        tuple. Returns height and width of the image.
    """
    # Because the filepath in DEV_MODE is 'filename' whereas in PROD_MODE
    # it is 'image/filename'
    filepath = (
        filename if (
            feconf.DEV_MODE)
        else 'image/%s' % filename)

    file_system_class = (
        fs_domain.ExplorationFileSystem if (
            feconf.DEV_MODE)
        else fs_domain.GcsFileSystem)
    fs = fs_domain.AbstractFileSystem(file_system_class(exp_id))
    content = fs.get(filepath)
    height, width = gae_image_services.get_image_dimensions(content)
    return height, width


def create_compressed_versions_of_image(filename, exp_id):
    """Creates two compressed versions of the image by compressing the
    original image.

    Args:
        filename: str. The filename of the image in exploration.
        exp_id: str. ID of the exploration.
    """
    # Because the filepath in DEV_MODE is 'filename' whereas in PROD_MODE
    # it is 'image/filename'
    filepath = (
        filename if (
            feconf.DEV_MODE)
        else 'image/%s' % filename)

    filename_wo_filetype = filename[:filename.rfind('.')]
    filetype = filename[filename.rfind('.') + 1:]

    file_system_class = (
        fs_domain.ExplorationFileSystem if (
            feconf.DEV_MODE)
        else fs_domain.GcsFileSystem)
    fs = fs_domain.AbstractFileSystem(file_system_class(exp_id))

    original_image_content = fs.get(filepath)
    compressed_image_content = gae_image_services.compress_image(
        original_image_content, 0.8)
    micro_image_content = gae_image_services.compress_image(
        original_image_content, 0.7)

    compressed_image_filename = '%s_compressed.%s' % (
        filename_wo_filetype, filetype)
    compressed_image_filepath = (
        compressed_image_filename if (
            feconf.DEV_MODE)
        else 'image/%s' % compressed_image_filename)

    micro_image_filename = '%s_micro.%s' % (
        filename_wo_filetype, filetype)
    micro_image_filepath = (
        micro_image_filename if (
            feconf.DEV_MODE)
        else 'image/%s' % micro_image_filename)

    fs.commit(
        'ADMIN', compressed_image_filepath,
        compressed_image_content, mimetype='image/%s' % filetype)

    fs.commit(
        'ADMIN', micro_image_filepath,
        micro_image_content, mimetype='image/%s' % filetype)
