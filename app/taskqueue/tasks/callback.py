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

"""All callback related celery tasks."""

import taskqueue.celery as taskc
import utils
import utils.callback
import utils.log

LOG = utils.log.get_log()



@taskc.app.task(name="lava-boot")
def lava_boot(json_obj, job_meta, lab_name):
    utils.LOG.warn('lalalalalala-lava_boot' * 42)
    """Add boot data from a LAVA v2 boot job callback

    This is a wrapper around the actual function which runs in a Celery task.

    :param json_obj: The JSON object with the values necessary to import the
    LAVA boot data.
    :type json_obj: dictionary
    :param job_meta: The name of the LAVA lab that posted the callback.
    :type job_meta: string
    :param lab_name: The name of the LAVA lab that posted the callback.
    :type lab_name: string
    :return ObjectId The boot document object id.
    """
    return utils.callback.lava.add_boot(json_obj, job_meta, lab_name,
                                        taskc.app.conf.db_options)


@taskc.app.task(name="lava-test")
def lava_test(json_obj, job_meta, lab_name):
    utils.LOG.warn('lalalalalala-lava_test' * 42)
    """Add test data from a LAVA v2 test job callback

    This is a wrapper around the actual function which runs in a Celery task.

    :param json_obj: The JSON object with the values necessary to import the
    LAVA test data.
    :type json_obj: dictionary
    :param lab_name: The name of the LAVA lab that posted the callback.
    :type lab_name: string
    :return ObjectId The test document object id.
    """
    return utils.callback.lava.add_tests(json_obj, job_meta, lab_name,
                                         taskc.app.conf.db_options)
