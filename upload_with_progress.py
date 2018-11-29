# -*- coding: utf-8 -*-

# ############################################################################
# This example demonstrates how to use the MultipartEncoderMonitor to create a
# progress bar using clint
# ############################################################################

from clint.textui.progress import Bar as ProgressBar
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
from magic import Magic
mime = Magic(mime=True)

import requests


def create_callback(encoder):
    bar = ProgressBar(expected_size=encoder.len, filled_char='▉')

    def callback(monitor):
        bar.show(monitor.bytes_read)

    return callback


def create_upload(path_to_file, field_name = ''):
    return MultipartEncoder({
        'form_field': 'value',
        'another_form_field': 'another value',
        'first_file': ('progress_bar.py', open(path_to_file, 'rb'), mime.from_file(path_to_file)),

        })


if __name__ == '__main__':
    file_path = '/var/www/html/motion/20181114-timelapse.avi'
    encoder = create_upload(file_path)
    callback = create_callback(encoder)
    monitor = MultipartEncoderMonitor(encoder, callback)
    r = requests.put('https://transfer.sh/hello.avi', data=monitor,
                      headers={'Content-Type': mime.from_file(file_path)})
    print('\nUpload finished! (Returned status {0} {1}), URL: {2}'.format(
        r.status_code, r.reason, r.text
        ))