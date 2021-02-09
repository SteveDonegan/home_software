__author__ = 'Steve'

import os, sys
from datetime import datetime
import hashlib


from PIL import Image
from PIL.ExifTags import TAGS

def get_exif_header(filename):
    '''
        Method to return a dictionary of EXIF headers

    :param filename: filename of image
    :return: dictionary of exif headers
    '''

    try:
        ret = {}
        i = Image.open(filename)
        info = i._getexif()
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            ret[decoded] = value

    except Exception as ex:
        ret = None

    return ret


def get_checksum(data_file):
    '''
    Method to check the actual checksum of the data against the value in the checksum file TBC
    :return:
    '''

    md5 = hashlib.md5()

    try:
        datafile = open(data_file)

        for line in datafile:
            md5.update(line)

        datafile.close()

        return md5.hexdigest()

    except Exception as ex:
        raise Exception ("Could not calculate checksum for: %s (%s)" %(data_file,ex))


def get_image_details(filename):
    '''
        Method to extract basic image details

    :param filename:
    :return:
    '''
    details = {}

    #is file an image or move file
    if  os.path.splitext(os.path.basename(filename))[1] not in ['.jpg','.jpeg','.JPEG','.JPG']:
        raise Exception ('Not a valid image format')

    #get headers
    try:
        headers = get_exif_header(os.path.join(dir_to_scan,filename))

        if not headers:
            raise Exception ("Could not access EXIF headers")

    except Exception as ex:
        raise Exception("Error could not access header: %s" %ex)

    #get useful info
    try:
        details['img_date_str'] = headers['DateTime']
        details['camera'] = headers['Model']

    except Exception as ex:
        raise Exception("Could not extract info from header dict (%s)" %ex)

    #get specific year month day info
    details['year'] = None
    details['month'] = None
    details['day'] = None

    #file size
    details['size'] = os.path.getsize(filename)

    try:
        #TODO: is this consistent for all cameras i.e. following standard EXIF header
        details['year'] = headers['DateTime'].split(' ')[0].split(':')[0]
        details['month'] = headers['DateTime'].split(' ')[0].split(':')[1]
        details['day'] = headers['DateTime'].split(' ')[0].split(':')[2]

    except Exception as ex:
        raise Exception("Could not extract date info from header dict (%s)" %ex)

    #information on the file itself
    try:
        details['size'] = os.path.getsize(filename)

    except Exception as ex:
        raise Exception("Could not extract file system size (%s)" %ex)

    try:
        details['md5'] = get_checksum(filename)

    except Exception as ex:
        raise Exception("Could not extract file system size (%s)" %ex)


    return details


if __name__ == "__main__":

    dir_to_scan = sys.argv[1]
    archive_base_dir = sys.argv[2]

    cnt = 0
    dup_cnt = 0

    files_found = []
    bad_files_found = []

    for root, dirs, files in os.walk(dir_to_scan):

        for filename in files:
            cnt += 1

            try:
                details = get_image_details(os.path.join(root,filename))

                archive_dir = os.path.join(archive_base_dir, details['year'], details['month'])

            except Exception as ex:
                bad_files_found.append(filename)

            if filename not in files_found:
                files_found.append(filename)

            '''
            try:

            except Exception as ex:
                pass

            else:
                dup_cnt +=1
            '''
    print (f"Found {cnt} files {dup_cnt} duplicated ({len(bad_files_found)} bad files)!")
