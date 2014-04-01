# Copyright (C) 2014 Linaro Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Container for all the import related functions."""

import os
import pymongo

from datetime import datetime

from models import DB_NAME
from models.defconfig import (
    DEFCONFIG_ACCEPTED_FILES,
    DefConfigDocument,
)
from models.job import JobDocument
from utils.db import save
from utils.utc import utc


BASE_PATH = '/var/www/images/kernel-ci'


def import_job_from_json(
        json_obj, database, base_path=BASE_PATH, callback=None):
    """Import a job based on the provided JSON object.

    The provided JSON object, a dict-like object, should contain at least the
    `job' and `kernel' keys. These keys will be used to traverse the directory
    structure found at the `/job/kernel' path (starting from the default
    location).

    :param json_obj: A dict-like object, that should contain the keys `job' and
                     `kernel'.
    :param database: The database where to save the parsed data.
    :param base_path: The base path where to start constructing the traverse
                      directory. It defaults to: /var/www/images/kernel-ci.
    :param callback: Optional function that will be called at the end of
                     execution.
    """
    job_dir = json_obj['job']
    kernel_dir = json_obj['kernel']

    return_code = _import_job(job_dir, kernel_dir, database, base_path)

    if callback:
        callback(return_code)


def _import_job(job, kernel, database, base_path=BASE_PATH):
    """Traverse the job dir and create the documenst to save.

    :param job: The name of the job.
    :param kernel: The name of the kernel.
    :param database: The databse where to save the parsed data.
    :param base_path: The base path where to strat the traversing.
    :return Return a status code based on the save operation.
    """
    job_dir = os.path.join(base_path, job, kernel)
    job_id = JobDocument.JOB_ID_FORMAT % (job, kernel)

    docs = []
    doc = JobDocument(job_id, job=job, kernel=kernel)
    doc.created = datetime.now(tz=utc).isoformat()

    docs.append(doc)

    if os.path.isdir(job_dir):
        docs.extend(_traverse_defconf_dir(job_dir, job_id))

    return save(database, docs)


def _traverse_defconf_dir(kernel_dir, job_id):
    """Traverse the defconfing directories.

    :param kernel_dir: The kernel dir where to start.
    :param job_id: The id of the JobDocument the defconfing will be linked to.
    :return A list of documents.
    """
    defconf_docs = []
    for defconf_dir in os.listdir(kernel_dir):
        defconf_doc = DefConfigDocument(defconf_dir)
        defconf_doc.job_id = job_id

        for dirname, subdirs, files in os.walk(
                os.path.join(kernel_dir, defconf_dir)):
            # Consider only the actual directory and its files.
            subdirs[:] = []
            for key, val in DEFCONFIG_ACCEPTED_FILES.iteritems():
                if key in files:
                    setattr(defconf_doc, val, os.path.join(dirname, key))
        defconf_docs.append(defconf_doc)
    return defconf_docs


def _import_all(base_path=BASE_PATH):
    """This function is used only to trigger the import from the command line.

    Do not use it elsewhere.
    :param base_path: Where to start traversing directories. Defaults to:
                      /var/www/images/kernel-ci.
    :return The docs to save. All docs are subclasses of BaseDocument.
    """

    docs = []

    for job_dir in os.listdir(base_path):
        job_id = job_dir
        job_dir = os.path.join(base_path, job_dir)

        for kernel_dir in os.listdir(job_dir):
            doc_id = JobDocument.JOB_ID_FORMAT % (job_id, kernel_dir)
            job_doc = JobDocument(doc_id, job=job_id, kernel=kernel_dir)
            job_doc.created = datetime.now(tz=utc).isoformat()
            docs.append(job_doc)

            kernel_dir = os.path.join(job_dir, kernel_dir)

            docs.extend(_traverse_defconf_dir(kernel_dir, doc_id))

    return docs


if __name__ == '__main__':
    connection = pymongo.MongoClient()
    database = connection[DB_NAME]

    documents = _import_all()
    save(database, documents)

    connection.disconnect()