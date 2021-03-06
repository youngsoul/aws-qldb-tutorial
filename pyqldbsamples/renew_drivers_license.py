# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# This code expects that you have AWS credentials setup per:
# https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html
from logging import basicConfig, getLogger, INFO
from datetime import datetime

from pyqldbsamples.model.sample_data import SampleData, convert_object_to_ion, get_document_ids_from_dml_results
from pyqldbsamples.connect_to_ledger import create_qldb_driver
from pyqldbsamples.constants import Constants

logger = getLogger(__name__)
basicConfig(level=INFO)

VALID_FROM_DATE = datetime(2019, 4, 19)
VALID_TO_DATE = datetime(2023, 4, 19)


def verify_driver_from_license_number(driver, license_number):
    """
    Verify whether a driver exists in the system with the provided license number.

    :type driver: :py:class:`pyqldb.driver.qldb_driver.QldbDriver`
    :param driver: An instance of the QldbDriver class.

    :type license_number: str
    :param license_number: The driver's license number.

    :raises RuntimeError: If driver does not exist in the system.
    """
    logger.info("Finding person ID with license number: {}.".format(license_number))
    query = 'SELECT PersonId FROM DriversLicense AS d WHERE d.LicenseNumber = ?'
    person_id = driver.execute_lambda(lambda executor: executor.execute_statement(query,
                                                                                  convert_object_to_ion(license_number)))
    pid = next(person_id).get('PersonId')
    query = 'SELECT p.* FROM Person AS p BY pid WHERE pid = ?'
    cursor = driver.execute_lambda(lambda executor: executor.execute_statement(query, pid))
    try:
        next(cursor)
    except StopIteration:
        raise RuntimeError('Unable to find person with ID: {}'.format(pid))


def renew_drivers_license(driver, valid_from, valid_to, license_number):
    """
    Renew the ValidFromDate and ValidToDate of a driver's license.

    :type driver: :py:class:`pyqldb.driver.qldb_driver.QldbDriver`
    :param driver: An instance of the QldbDriver class.

    :type valid_from: :py:class:`datetime.datetime`
    :param valid_from: The new valid-from date.

    :type valid_to: :py:class:`datetime.datetime`
    :param valid_to: The new valid-to date.

    :type license_number: str
    :param license_number: The license number for the driver's license to renew.

    :raises RuntimeError: If no driver's license was updated.
    """
    logger.info('Renewing license with license number: {}...'.format(license_number))
    update_valid_date = 'UPDATE DriversLicense AS d SET d.ValidFromDate = ?, d.ValidToDate = ? WHERE d.LicenseNumber ' \
                        '= ?'
    cursor = driver.execute_lambda(lambda executor: executor.execute_statement(update_valid_date,
                                                                               convert_object_to_ion(valid_from),
                                                                               convert_object_to_ion(valid_to),
                                                                               convert_object_to_ion(license_number)))
    logger.info('DriversLicense Document IDs which had licenses renewed: ')
    list_of_licenses = get_document_ids_from_dml_results(cursor)
    for license in list_of_licenses:
        logger.info(license)
    return list_of_licenses


def verify_and_renew_license(driver, license_num, valid_from_date, valid_to_date):
    """
    Verify if the driver of the given license and update the license with the given dates.

    :type driver: :py:class:`pyqldb.driver.qldb_driver.QldbDriver`
    :param driver: An instance of the QldbDriver class.

    :type license_num: str
    :param license_num: The license to verify and renew.

    :type valid_from_date: :py:class:`datetime.datetime`
    :param valid_from_date: The new valid-from date.

    :type valid_to_date: :py:class:`datetime.datetime`
    :param valid_to_date: The new valid-to date.
    """
    verify_driver_from_license_number(driver, license_num)
    renew_drivers_license(driver, valid_from_date, valid_to_date, license_num)


def main(ledger_name=Constants.LEDGER_NAME):
    """
    Find the person associated with a license number.
    Renew a driver's license.
    """
    try:
        with create_qldb_driver(ledger_name) as driver:
            license_number = SampleData.DRIVERS_LICENSE[0]['LicenseNumber']
            verify_and_renew_license(driver, license_number, VALID_FROM_DATE, VALID_TO_DATE)
    except Exception as e:
        logger.exception('Error renewing drivers license.')
        raise e


if __name__ == '__main__':
    main()
